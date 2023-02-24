"""Tests of Model module implementation with internal tree and JSON storage."""

import json
import os, os.path
import sys

import exceptions
from model_json import ModelJSON
from nodes import RootBookmarks
from nodes import Folder
from nodes import Url



class TestModulJSON:
    """Testing class for internal and JSON Model class"""

    jm = ModelJSON()

    def test_init_class(self):
        assert isinstance(self.jm.root, RootBookmarks)
        assert self.jm.root.nodes_dict == {'roots': self.jm.root}
        assert self.jm.tree_name == ''
        assert self.jm.cwd == os.getcwd()

    def test_save_delete_db(self):
        """Test of saving and deleting database."""
        self.jm.tree_name = 'new_database.json'
        try:
            open(self.jm.tree_name, 'x')  # open a new file as exclusive
        except FileExistsError:
            os.remove(self.jm.tree_name)  # delete this file if it exists
        self.jm._save_tree()
        assert os.path.isfile(self.jm.tree_name)
        self.jm.delete_database(self.jm.tree_name)  # delete this file

    def test_create_database(self):
        # check if filename exists
        filename = 'new_db.json'
        if not os.path.isfile(filename):
            # create this file
            f = open(filename, 'w')
            f.close()
        # check exception if input filename already exists
        try:
            self.jm.create_database(filename)
        except FileExistsError as e:
            print('\nException FileExistsError raised successfully', e, file=sys.stderr)
        os.remove(filename)  # delete this file
        # check database creating
        filename = 'new_database.json'
        self.jm.create_database(filename)
        assert os.path.isfile(self.jm.tree_name)
        os.remove(filename)  # delete this file

    def test_add_node(self):
        filename = 'database.json'
        if os.path.isfile(filename):
            os.remove(filename)  #  remove the filename if it exists
        self.jm.create_database(filename)  # create an empty db

        # add a folder to the roots
        attr_folder = {'name': 'folder', 'parent_name': 'roots',}
        self.jm.add_node(attr_folder, True)
        # add an url to the previous folder
        attr_url = {'name': 'URL', 'parent_name': 'folder',
                    'url': 'www.url.com', 'icon': 'ICON', 'keywords': 'old keys'}
        self.jm.add_node(attr_url, False)
        # check results
        # folder <roots> first
        node_name = 'roots'
        expected = {'name': 'roots', 'parent_guid': None,
                    'children': ['folder'],}
        expected_nodes_list = ['roots', 'folder', 'URL']
        node_object = self.jm.root.nodes_dict[node_name]  # get the node instance
        node_content = node_object.__dict__.copy()  # local copy of the node's dict
        # ---- replace objects with their names ----
        children_list = [x.name for x in node_content['children']]  # get children names
        node_content['children'] = children_list  # put children names instead of objects
        # assert block
        assert node_content['name'] == expected['name']
        assert node_content['parent_guid'] == expected['parent_guid']
        assert node_content['children'] == expected['children']
        assert type(node_content['guid']) is str
        assert len(node_content['guid']) == 36
        assert type(node_content['date_added']) is str
        assert len(node_content['date_added']) == 19
        assert type(node_content['date_modified']) is str
        assert len(node_content['date_modified']) == 19
        nodes_list = [x for x in node_content['nodes_dict'].keys()]  # names of the global node list
        assert nodes_list == expected_nodes_list

        # folder <folder> second
        parent_guid = node_content['guid']  # keep the guid of parent node from the previous test
        node_name = 'folder'
        expected = {'name': 'folder', 'parent_guid': parent_guid,
                    'children': ['URL'], }
        expected_nodes_list = ['roots', 'folder', 'URL']
        node_object = self.jm.root.nodes_dict[node_name]  # get the node instance
        node_content = node_object.__dict__.copy()  # local copy of the node's dict
        # ---- replace objects with their names ----
        children_list = [x.name for x in node_content['children']]  # get children names
        node_content['children'] = children_list  # put children names instead of objects
        # assert block
        assert node_content['name'] == expected['name']
        assert node_content['parent_guid'] == expected['parent_guid']
        assert node_content['children'] == expected['children']
        assert type(node_content['guid']) is str
        assert len(node_content['guid']) == 36
        assert type(node_content['date_added']) is str
        assert len(node_content['date_added']) == 19
        assert type(node_content['date_modified']) is str
        assert len(node_content['date_modified']) == 19

        # url <URL> third
        parent_guid = node_content['guid']  # keep the guid of parent node from the previous test
        node_name = 'URL'
        expected = {'name': 'URL', 'parent_guid': parent_guid,
                    'url': 'www.url.com', 'icon': 'ICON', 'keywords': 'old keys', }
        expected_nodes_list = ['roots', 'folder', 'URL']
        node_object = self.jm.root.nodes_dict[node_name]  # get the node instance
        node_content = node_object.__dict__.copy()  # local copy of the node's dict
        # assert block
        assert node_content['name'] == expected['name']
        assert node_content['parent_guid'] == expected['parent_guid']
        assert type(node_content['guid']) is str
        assert len(node_content['guid']) == 36
        assert type(node_content['date_added']) is str
        assert len(node_content['date_added']) == 19
        assert node_content['url'] == expected['url']
        assert node_content['icon'] == expected['icon']
        assert node_content['keywords'] == expected['keywords']


        os.remove(filename)  # delete this file

    def test_get_node(self):
        # wrong input name
        name = 'not exist'
        try:
            self.jm.get_node(name) == {}
        except KeyError as e:
            print('\nWrong input parameter:', e, file=sys.stderr)
