import unittest
import os
import psycopg2
from scrumhub.database import Project


class ProjectTest(unittest.TestCase):

    def test_create_project(self):
        uuid = Project.create_project('name', 'owner', [])
        self.assertIsNotNone(uuid)

    def test_get_projects(self):
        name = 'name'
        owner = 'owner'

        results = Project.get_projects(project_name=name, owner_name=owner)

        self.assertEqual(results[0][1:], (name, owner, []))


if __name__ == '__main__':
    unittest.main()
