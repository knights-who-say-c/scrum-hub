import os
import psycopg2 as pg

DATABASE_URL = os.environ['DATABASE_URL']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']


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
        Returns a uuid string if project creation was successful, None otherwise.
    """
    sql_string = f"INSERT INTO public.project " \
                 f"(id, name, owner, contributors) " \
                 f"VALUES " \
                 f"(gen_random_uuid(), '{project_name}', '{owner_name}', ARRAY{contrib_names});"

    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='require')
    conn.autocommit = True
    uuid = None

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_string)

    finally:
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
