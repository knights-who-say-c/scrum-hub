import boto3
import json
import os

import psycopg2 as pg
from flask import Flask, request

DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
PORT = os.environ.get('PORT')

app = Flask(__name__)


class Project:

    def __init__(self):
        pass


def create_project(project_name, owner_name, contrib_names):
    """Create a new project on the database.

    Parameters
    ----------
    project_name : str
        Name of the project.
    owner_name : str
        Owner name or id.
    contrib_names : list of strings
        Contributor names or ids.

    Returns
    -------
    uuid : str
        Returns a uuid string if project creation was successful, otherwise
        return an empty string.
    """
    # SQL string to insert a new project into the database
    sql_string = (f"INSERT INTO public.project "
                  f"(id, name, owner, contributors) "
                  f"VALUES "
                  f"(gen_random_uuid(), '{project_name}', '{owner_name}', ARRAY{contrib_names});")
    # Connect to the database
    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='require')
    # Enable the connection object to automatically commit queries so that
    # multiple queries may be sent with the same connection
    conn.autocommit = True
    # Return value
    uuid = ''

    try:
        # Connection context manager
        with conn:
            # Cursor context manager for executing queries on the server
            with conn.cursor() as cur:
                # Execute the insertion
                cur.execute(sql_string)

    finally:
        # Ensure the connection is closed
        conn.close()

    return uuid


def get_projects(project_id=None, project_name=None, owner_name=None):
    """Query existing projects on the database.

    Parameters
    ----------
    project_id : str
        UUID for the desired project.
    project_name : str
        Name of the project.
    owner_name : str
        Owner name or id.

    Returns
    -------
    out : list of tuples
        Query results from the given search parameters. If no matching projects
        were found, then an empty list is returned.
    """
    sql_string = f"SELECT * FROM public.project WHERE "
    args = []

    if project_id:
        args.append(f"id = {project_id}")

    if project_name:
        args.append(f"id = {project_name}")

    if owner_name:
        args.append(f"id = {owner_name}")

    sql_string += " AND ".join(args)

    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='require')
    conn.autocommit = True
    results = []

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_string)
                results = cur.fetchall()

    finally:
        conn.close()

    return results


def create_repo(name):
    s3_bucket = os.environ.get('S3_BUCKET')
    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')
    repo_name = name
    repo_desc = ''
    tags = {}

    codecommit = boto3.client('codecommit')
    response = codecommit.create_repository(repositoryName=repo_name,
                                            repositoryDescriptio=repo_desc,
                                            tags=tags)

    return response


@app.route('/sign_s3/')
def sign_s3():
    # aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    # aws_secret_key = os.environ.get('AWS_SECRET_KEY')
    s3_bucket = os.environ.get('S3_BUCKET')
    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')

    codecommit = boto3.client('codecommit')

    presigned_post = codecommit.generate_presigned_post(
        Bucket=s3_bucket,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": file_type}
        ],
        ExpiresIn=3600
    )

    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (s3_bucket, file_name)
    })
