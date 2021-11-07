import base64
import tempfile

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

    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
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


def create_repo(repo_name, repo_desc=''):
    tags = {}
    client = boto3.client('codecommit')
    response = client.create_repository(repositoryName=repo_name,
                                        repositoryDescription=repo_desc,
                                        tags=tags)
    response['repositoryMetadata']['defaultBranchName'] = 'master'

    return response


def get_repo(repo_name):
    client = boto3.client('codecommit')
    response = client.get_repository(repositoryName=repo_name)

    return response


def delete_repo(repo_name):
    client = boto3.client('codecommit')
    response = client.delete_repository(repositoryName=repo_name)

    return response


def put_file(repo_name, branch_name, parent_commit_id, file_path, file_content):
    """Adds or updates a file in a branch in an AWS CodeCommit repository, and
    generates a commit for the addition in the specified branch.

    Parameters
    ----------
    repo_name : str
        The name of the repository where you want to add or update the file.
    branch_name : str
        The name of the branch where you want to add or update the file. If
        this is an empty repository, this branch is created.
    parent_commit_id : str
        The full commit ID of the head commit in the branch where you want to
        add or update the file. If this is an empty repository, no commit ID is
        required. If this is not an empty repository, a commit ID is required.
    file_path : str
        The name of the file you want to add or update, including the relative
        path to the file in the repository.
    file_content : bytes
        The content of the file, in Base64-encoded binary object format.

    Returns
    -------
    response : dict
        {"blobId": "string", "commitId": "string", "treeId": "string"}.
    """
    client = boto3.client('codecommit')
    response = client.put_file(repositoryName=repo_name,
                               branchName=branch_name,
                               fileContent=file_content,
                               filePath=file_path,
                               parentCommitId=parent_commit_id)

    return response


def init_commit(repo_name, branch_name):
    client = boto3.client('codecommit')
    with tempfile.TemporaryFile() as fd:
        fd.seek(0)
        encoded = base64.b64encode(fd.read())
    header = {
        'repositoryName': repo_name,
        'branchName': branch_name,
        'putFiles': [
            {
                'filePath': '.init',
                'fileContent': encoded
            }
        ]
    }
    response = client.create_commit(**header)

    return response


def create_commit(repo_name, branch_name, source_folder=None):
    client = boto3.client('codecommit')
    header = {
        'repositoryName': repo_name,
        'branchName': branch_name
    }

    if source_folder is not None:
        parent_folder = os.path.join(source_folder, repo_name)
        putfile_list = []
        for (root, folders, files) in os.walk(parent_folder):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, mode='r+b') as file_obj:
                    file_content = file_obj.read()
                putfile_entry = {'filePath': str(file_path).replace(parent_folder, ''),
                                 'fileContent': file_content}
                putfile_list.append(putfile_entry)
                header['putFiles'] = putfile_list

    response = client.create_commit(**header)

    return response


def mount_repo(repo_name):
    repo_dir = tempfile.mkdtemp()

    return repo_dir


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
