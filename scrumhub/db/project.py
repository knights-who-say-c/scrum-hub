import base64
import tempfile
from pathlib import PurePath

import boto3
import json
import os

import botocore.exceptions
import psycopg2 as pg
from flask import Flask, request

DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
PORT = os.environ.get('PORT')

app = Flask(__name__)


class Project:
    """Container object for representing scrumhub projects."""

    def __init__(self, uuid, project_name, owner_name, contrib_names=None):
        self._uuid = uuid
        self._name = project_name
        self._owner = owner_name
        self._contributors = contrib_names if contrib_names is not None else []

    @property
    def uuid(self) -> str:
        """Project unique identifier."""
        return self._uuid

    @property
    def name(self) -> str:
        """Project name."""
        return self._name

    @property
    def owner(self) -> str:
        """Project owner."""
        return self._owner

    @property
    def contributors(self) -> list:
        """List of project contributors."""
        return self._contributors

    @property
    def latest_commit_id(self):
        """Most recent commit id."""
        client = boto3.client('codecommit')

        try:
            response = client.get_branch(repositoryName=self.uuid,
                                         branchName='main')
            commit_id = response['branch']['commitId']

        except botocore.exceptions.ClientError as error:

            if error.response['Error']['Code'] == 'BranchDoesNotExistException':
                commit_id = None

            else:
                raise error

        return commit_id

    def cursor(self):
        """Return a new Cursor object pointing to the project's filesystem."""
        return Cursor(self)

    def get_file(self, file_path):
        """Download a single file from the project repository.

        Parameters
        ----------
        file_path : str
            The name of the file you want to download, including the relative
            path to the file in the repository.
        """
        response = _get_file(repo_name=self.uuid,
                             file_path=file_path,
                             commit_specifier=self.latest_commit_id)

        return response

    def put_file(self, file_content, file_path, file_description):
        """Upload and commit a single file to the project repository.

        Parameters
        ----------
        file_content : bytes
            The content of the file, in Base64-encoded binary object format.
        file_path : str
            The name of the file you want to add or update, including the
            relative path to the file in the repository.
        file_description : str
            The description of the file you want to add or update.
        """
        response = _put_file(repo_name=self.uuid,
                             branch_name='main',
                             file_content=file_content,
                             file_path=file_path,
                             file_description=file_description,
                             parent_commit_id=self.latest_commit_id)

        return response

    def delete_file(self, file_path):
        """Delete and commit a single file on the project repository.

        Parameters
        ----------
        file_path : str
            The name of the file you want to add or update, including the
            relative path to the file in the repository.
        """
        response = _delete_file(repo_name=self.uuid,
                                branch_name='main',
                                file_path=file_path,
                                parent_commit_id=self.latest_commit_id)

        return response


class Cursor:

    def __init__(self, parent: Project):
        self.project = parent
        self._commit_id = self.project.latest_commit_id
        self._cur = PurePath('/')
        self.metadata = _get_folder(repo_name=self.project.uuid,
                                    commit_specifier=self._commit_id,
                                    folder_path=str(self._cur))

    def name(self):
        """The final path component name."""
        return self._cur.name

    def path(self):
        return str(self._cur)

    def back(self):
        """Move the cursor up to the parent directory."""
        return str(self._cur.parent)

    def goto(self, path):
        """Go to the specified directory."""

        if isinstance(path, PurePath):
            _cur = '/' / path

        elif path in self.subdir_names():
            _cur = self._cur / path

        else:
            _cur = '/' / PurePath(path)

        try:
            self.metadata = _get_folder(repo_name=self.project.uuid,
                                        commit_specifier=self._commit_id,
                                        folder_path=str(_cur))
        except botocore.exceptions.ClientError:
            raise FileNotFoundError('The requested file was not found on the server.')

        self._cur = _cur

    def get_file(self):
        pass

    def subdir_names(self):
        """Returns a list of subfolder names within the current directory."""
        return [d['relativePath'] for d in self.subdir_metadata()]

    def file_names(self):
        """Returns a list of file names within the current directory.

        Returns
        -------
        files : list of str
            List of dict objects containing metadata about each file.
        """
        return [f['relativePath'] for f in self.file_metadata()]

    def subdir_metadata(self):
        """Returns a list of subfolder metadata within the current directory."""
        return self.metadata.get('subFolders', [])

    def file_metadata(self):
        """Returns a list of file metadata within the current directory.

        Returns
        -------
        files : list of dict
            List of dict objects containing metadata about each file.
        """
        return self.metadata.get('files', [])


def create_project(project_name, owner_name, contrib_names):
    """Create a new project on the database and setup the AWS repository.

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
    uuid = _create_project_db(project_name, owner_name, contrib_names)
    response = _create_project_repo(repo_name=uuid, repo_desc=project_name)

    return uuid


def get_project(uuid):
    """Query existing project on the database by its uuid.

    Parameters
    ----------
    uuid : str
        UUID of the project.

    Returns
    -------
    proj : Project
        A project object containing metadata and functions. If no matching
        projects were found, then None is returned.
    """
    sql_string = f"SELECT * FROM public.project WHERE id = '{uuid}'"
    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
    conn.autocommit = True

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_string)
                results = cur.fetchone()

    finally:
        conn.close()

    return Project(*results) if results else None


def get_my_projects(owner):
    """Query existing project on the database by its owner.

    Parameters
    ----------
    owner : str
        owner of the project(s).

    Returns
    -------
    project_list : [Project]
        A project object containing metadata and functions. If no matching
        projects were found, then None is returned.
    """
    sql_string = f"SELECT * FROM public.project WHERE owner = '{owner}'"
    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
    conn.autocommit = True

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_string)
                results = cur.fetchall()

    finally:
        conn.close()

    project_list = []
    for proj in results:
        project_list.append(Project(*proj))

    return project_list


def search_project(project_name):
    """Query existing projects on the database by project name.

        Parameters
        ----------
        project_name : str
            Name of the project.

        Returns
        -------
        proj : Project
            List containing entries from the project database table that
            matched the project_name argument.
        """
    sql_string = f"SELECT * FROM public.project WHERE name = '{project_name}'"
    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
    conn.autocommit = True

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_string)
                results = cur.fetchone()

    finally:
        conn.close()

    return Project(*results) if results else None


def delete_project(uuid):
    """Delete an existing project by its uuid.

    Parameters
    ----------
    uuid : str
        UUID of the project.
    """
    _delete_project_db(uuid)
    _delete_project_repo(uuid)


def _create_project_db(project_name, owner_name, contrib_names):
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
                  f"(gen_random_uuid(), '{project_name}', '{owner_name}', ARRAY {contrib_names}::text[])"
                  f"RETURNING id;")
    # Connect to the database
    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
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
                uuid = cur.fetchone()[0]

    finally:
        # Ensure the connection is closed
        conn.close()

    return uuid


def _delete_project_db(uuid):
    """Delete an existing project on the database by its uuid.

    Parameters
    ----------
    uuid : str
        UUID of the project.
    """
    sql_string = f"DELETE FROM public.project WHERE id = '{uuid}'"
    conn = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD, sslmode='prefer')
    conn.autocommit = True

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql_string)

    finally:
        conn.close()


def _create_project_repo(repo_name, repo_desc=''):
    tags = {}
    client = boto3.client('codecommit')
    response = client.create_repository(repositoryName=repo_name,
                                        repositoryDescription=repo_desc,
                                        tags=tags)
    response['repositoryMetadata']['defaultBranchName'] = 'main'

    return response


def _get_project_repo(repo_name):
    client = boto3.client('codecommit')
    response = client.get_repository(repositoryName=repo_name)

    return response


def _delete_project_repo(repo_name):
    """Deletes the specified repo from AWS."""
    client = boto3.client('codecommit')
    response = client.delete_repository(repositoryName=repo_name)

    return response


def _get_folder(repo_name, commit_specifier, folder_path):
    """Returns the contents of a specified folder in a repository.

    Parameters
    ----------
    repo_name : str
        The name of the repository.
    commit_specifier : str, optional
        A fully qualified reference used to identify a commit that contains the
        version of the folder's content to return. A fully qualified reference
        can be a commit ID, branch name, tag, or reference such as HEAD. If no
        specifier is provided, the folder content is returned as it exists in
        the HEAD commit.
    folder_path : str
        The fully qualified path to the folder whose contents are returned,
        including the folder name. For example, /examples is a fully-qualified
        path to a folder named examples that was created off of the root
        directory (/) of a repository.
    Returns
    -------
    response : dict
        See the API for details on response syntax.
    """
    client = boto3.client('codecommit')
    kwargs = {
        'repositoryName': repo_name,
        'folderPath': folder_path
    }

    if commit_specifier:
        kwargs['commitSpecifier'] = commit_specifier

    response = client.get_folder(**kwargs)

    return response


def _get_file(repo_name, commit_specifier, file_path):
    """Downloads a file in a branch in an AWS CodeCommit repository, and
    generates a commit for the addition in the specified branch.

    Parameters
    ----------
    repo_name : str
        The name of the repository where you want to add or update the file.
    commit_specifier : str, optional
        A fully qualified reference used to identify a commit that contains the
        version of the folder's content to return. A fully qualified reference
        can be a commit ID, branch name, tag, or reference such as HEAD. If no
        specifier is provided, the folder content is returned as it exists in
        the HEAD commit.
    file_path : str
        The name of the file you want to add or update, including the relative
        path to the file in the repository.

    Returns
    -------
    response : dict
        {"blobId": "string", "commitId": "string", "fileContent": blob,
        "fileMode": "string", "filePath": "string", "fileSize": number}.
    """
    client = boto3.client('codecommit')
    kwargs = {
        'repositoryName': repo_name,
        'filePath': file_path
    }

    if commit_specifier:
        kwargs['commitSpecifier'] = commit_specifier

    try:
        response = client.get_file(**kwargs)

    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'FileDoesNotExistException':
            raise FileNotFoundError('The requested file was not found on the server.')

        else:
            raise error

    return response


def _put_file(repo_name, branch_name, parent_commit_id, file_content, file_path, file_description):
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
    file_content : bytes
        The content of the file, in binary object format.
    file_path : str
        The name of the file you want to add or update, including the relative
        path to the file in the repository.
    file_description : str
        A description of the contents of the file being added or updated.

    Returns
    -------
    response : dict
        {'commitId': 'string', 'blobId': 'string', 'treeId': 'string'}.
    """
    client = boto3.client('codecommit')
    kwargs = {
        'repositoryName': repo_name,
        'branchName': branch_name,
        'fileContent': file_content,
        'filePath': file_path,
        'commitMessage': file_description
    }

    if parent_commit_id:
        kwargs['parentCommitId'] = parent_commit_id

    response = client.put_file(**kwargs)

    return response


def _delete_file(repo_name, branch_name, parent_commit_id, file_path):
    """Deletes a specified file from a specified branch. A commit is created on
    the branch that contains the revision. The file still exists in the commits
    earlier to the commit that contains the deletion.

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

    Returns
    -------
    response : dict
        {'blobId': 'string', 'commitId': 'string', 'filePath': 'string',
        'treeId': 'string'}.
    """
    client = boto3.client('codecommit')
    kwargs = {
        'repositoryName': repo_name,
        'branchName': branch_name,
        'parent_commit_id': parent_commit_id,
        'filePath': file_path
    }

    response = client.delete_file(**kwargs)

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


if __name__ == '__main__':
    project = search_project('test-project')
    cur = project.cursor()
    print(cur.file_metadata())
