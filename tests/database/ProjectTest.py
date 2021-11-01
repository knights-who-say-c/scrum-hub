import base64
import tempfile
import unittest
import os
import psycopg2
from scrumhub.database import Project


class ProjectTest(unittest.TestCase):

    def setUp(self) -> None:
        self.repo_name = 'testrepo'
        self.commit_id = None
        self.branch_name = 'master'

    # def test_create_project(self):
    #     uuid = Project.create_project('name', 'owner', [])
    #     self.assertIsNotNone(uuid)
    #
    # def test_get_projects(self):
    #     name = 'name'
    #     owner = 'owner'
    #
    #     results = Project.get_projects(project_name=name, owner_name=owner)
    #
    #     self.assertEqual(results[0][1:], (name, owner, []))

    def test_create_repo(self):
        try:
            response = Project.create_repo('testrepo')
        except:
            response = Project.get_repo('testrepo')
        data = response.get('repositoryMetadata')
        self.branch_name = data.get('defaultBranchName', 'master')
        self.repo_name = data.get('repositoryName')
        self.assertEqual(response.get('ResponseMetadata', {}).get('HTTPStatusCode', -1), 200)

    def test_upload_repo(self):
        response = Project.init_commit(self.repo_name, self.branch_name)
        self.commit_id = response['commitId']
        with tempfile.TemporaryFile() as fd:
            fd.write(b'Hello world!')
            fd.seek(0)
            encoded = base64.b64encode(fd.read())

        response = Project.put_file(self.repo_name, self.branch_name, self.commit_id, f'{self.repo_name}/test.txt',
                                    encoded)
        self.assertEqual(response.get('ResponseMetadata', {}).get('HTTPStatusCode', -1), 200)

    def test_delete_repo(self):
        response = Project.delete_repo('testrepo')
        self.assertEqual(response.get('ResponseMetadata', {}).get('HTTPStatusCode', -1), 200)


if __name__ == '__main__':
    unittest.main()
