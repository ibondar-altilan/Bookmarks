"""A model part of the bookmark manager.
This version creates an internal tree from node objects.
The bookmark tree is stored into a file in the json format.
"""
import os
import json
import datetime
import sys

import exceptions
from time_convert import stamp_to_string
from nodes import RootBookmarks
from nodes import Folder
from nodes import Url


class MyJSONEncoder(json.JSONEncoder):
    """Overwrite the default JSON encoder class from the json module

    """
    def default(self, obj: Folder | Url | RootBookmarks):
        """Customize the encoding of the following custom classes: Root Bookmarks, Folder, Url.

        :param obj: a tree object that is being serialized
        :return: a dictionary of the input object to encode by json.py
        """
        if isinstance(obj, Folder | Url):
            return obj.__dict__  # for serialisation return an object's dict instead of the object
        elif isinstance(obj, RootBookmarks):    # for RootBookmarks a recursive ref to the object has to eliminate
            obj_copy = obj.__dict__.copy()  # make a swallow copy of the tree dict
            del obj_copy['nodes_dict']   # remove the dict of all nodes from json image (for the copy only!!!)
            return obj_copy  # for serialisation return an object's dict instead of the object (edited copy !)
        else:
            super().default(obj)  # the object does not need to be transformed


class ModelJSON:
    """Implementation of a Model module with an internal tree structure.
    Storing a tree database in JSON format.

    """
    def __init__(self):
        """Constructor method.
        """
        self.root = RootBookmarks()     # create the unique bookmark's tree object
        self.root.nodes_dict['roots'] = self.root  # {'roots': self.root object}  is the first record to the nodes dict
        self.tree_name = ''  # name of the current tree and database filename (json format)
        self.cwd = os.getcwd()  # current working directory

    def _save_tree(self):
        """Save the tree to the self.current_tree json file

        :return: nothing
        """
        with open(self.tree_name, "w") as write_file:
            json.dump(self.root, write_file, cls=MyJSONEncoder)

    def check_folder(self, name):
        """Check if the named node exists, and it's a folder. Return a tuple (True/False, None/error message)"""
        try:
            self.root.check_folder(name)
            return (True, None)  # True if OK, None is second formal return value for compatibility
        except (exceptions.NodeNotExist, exceptions.FolderNotExist) as e:
            return (False, e)   # the node doesn't exist of is not a folder, False and error message return

    def get_child_names(self, name: str) -> tuple[bool, tuple[str, ...]]:
        """Return True and the list of child names of the node <name>.
        If the node is an url then return False, empty tuple for url node.
        If node does not exist then raise NodeNotExist"""
        node = self.root.check_node(name)  # return an object or raise NodeNotExist
        if 'children' in node.__dict__:  # this is a folder
            children = tuple([child.name for child in node.children])
            return True, children  # return Tree, tuple of child's names
        else:
            return False, ()  # return False, empty tuple for url node

    def add_node(self, attr_dict: dict, node_type: bool):
        """Add a folder or url to the tree, parameters come from input dict.
        node_type = True for a folder creation otherwise url."""
        self.root.add_node(attr_dict, node_type)  # call an appropriated nodes method
        self._save_tree()  # save the updated current root

    # ---- nodes section ----
    def update_node(self, name, attr_dict):
        """Update a folder or url with <name> in the internal tree, parameters from input dict."""
        self.root.update_node(name, attr_dict)  # call an appropriated nodes method
        self._save_tree()  # save the updated current root

    def delete_node(self, name):
        """Delete a node from the current tree, name as parameter"""
        self.root.delete_node(name)     # call a nodes method
        self._save_tree()    # save the updated current root

    def get_node(self, name: str) -> dict:
        """Get a node content.
        Replace children objects with their names for folder children list

        :param name: node name
        :return: dictionary {field_name: field_value} of the node
        """
        node_object = self.root.nodes_dict[name]  # get the node instance
        node_content = node_object.__dict__.copy()   # local copy of the node's dict

        # ---- check if the node is a folder ----cl
        if 'children' in node_content:  # any folder has a children list
            # ---- replace objects with their names ----
            children_list = [x.name for x in node_content['children']]  # get children names
            node_content['children'] = children_list  # put children names instead of objects

        return node_content

    # ---- database section ----
    def create_database(self, name: str):
        """Create an empty bookmark structure and a file to keep the database.

        :exceptions: FileExistsError if given filename exists

        :param name: name and filename of the new database
        :return: nothing
        """
        with open(name, 'x') as f:     # open a new file as exclusive, of c if such a file exists
            pass    # ask for file recreating , see a controller logic
        self.tree_name = name    # store the name of the current bookmark tree
        self._save_tree()  # save a new tree to the json file

    def delete_database(self, name: str):
        """Delete the database file.

        :exception: FileNotFoundError if the filename does not exist

        :param name: name and filename of the deleting database
        :return: True if success otherwise False
        """
        os.remove(name)

    def open_database(self, name: str):
        """Open a database, read and extract it into a bookmark tree.

        :exception: FileNotFoundError if the filename does not exist

        :param name: name and filename of the deleting database
        :return: nothing
        """

        def _dict_into_object(dct: dict) -> dict:
            """Convert a dict into an object. Add the item (key, value) to the node's dict. Recursively.

            :param dct: input dictionary
            :return: intermediate dictionary during the recursion executes
            """
            i = 0  # an index in the children list
            for x in dct['children']:  # an iteration of children
                if 'children' in x:  # item has a child list, so it is a folder
                    _dict_into_object(x)  # recursion call for the nested child list
                    the_node = Folder(**x)  # crate a Folder object from dict json attributes
                else:  # an url found
                    the_node = Url(**x)  # create an Url object from dict json attributes

                dct['children'][i] = the_node  # put the object to the children list
                self.root.nodes_dict[the_node.name] = the_node  # add an pair 'name: object' to the global node's dict
                i += 1
            return dct  # return the dict where dicts are replaced by equivalent objects - nodes

        # ---- body of the open_database() ----
        # ---- read json database ----
        with open(name, 'r') as f:   # open the tree image file, or FileNotFoundError exception
            tree_image = json.load(f)   # read the json image and then close the file, image is a dict
        self.tree_name = name    # set the current tree name

        # ---- update the root from the json image ----
        self.root.update_root(**tree_image)

        # ---- decode nested dictionaries from json image to the original objects and add it to the node's list ----
        dt = self.root.__dict__  # start from the root children
        _dict_into_object(dt)  # decode nested dictionaries recursively

    # ---- section of format conversions
    def _chrome_into_object(self, dt):
        """Conversation of chrome json structure to the internal node tree.
        Inner recursion for convert_chrome method, in-place conversion

        :param dt: a dictionary with chrome json structure
        :return: intermediate dictionary during recursion execution
        """
        init_len = len(dt['children'])  # an initial length of the input dict
        while init_len:
            attr_dict = dt['children'][0]  # get first child from the list and remove it

            # remove non-using data fields of chrome format
            attr_dict.pop('meta_info', None)  # remove a <meta_info> list if it presents

            # modify source structure to internal
            attr_dict['name'] = self.root.name_double(attr_dict['name'])    # replace 'name' with 'name(i)' if doubled
            attr_dict['id_no'] = attr_dict.pop('id')  # replace key 'id' with 'id_no' keeping its value
            attr_dict['parent_name'] = dt['name']  # set parent name for child object
            if attr_dict.pop('type') == 'folder':
                node_type = True  # this is a folder
                if attr_dict['name'] != 'roots':  # skip format conversion for roots folder
                    # convert timestamps of the folder
                    attr_dict['date_added'] = stamp_to_string(int(attr_dict['date_added']), 'google')
                    attr_dict['date_modified'] = stamp_to_string(int(attr_dict['date_modified']), 'google')
                self.root.add_node(attr_dict, node_type)  # call an appropriated nodes method
                self._chrome_into_object(attr_dict)  # recursion
            else:
                node_type = False  # this is an url
                # convert timestamp of the url
                attr_dict['date_added'] = stamp_to_string(int(attr_dict['date_added']), 'google')
                self.root.add_node(attr_dict, node_type)  # call an appropriated nodes method

            # an object has been created and added
            del dt['children'][0]  # remove a dict of the added node
            init_len -= 1
        # return dct  # return the dict where dicts are replaced by equivalent objects - nodes

    def convert_chrome(self, filename: str) -> tuple[bool, str]:
        """Convert Chrome bookmark JSON filename to the current tree. Return (True/False, error message)

        :param filename: Google bookmark filename to convert
        :return: (True, empty string)  or (False, error message)
        """
        # ---- open and load JSON file of Chrome bookmarks, the file exists
        with open(filename, 'r', encoding='utf-8') as f:   # open the tree image file, or raise FileNotFoundError
            source_file = json.load(f)   # read the json image and then close the file, image is a dict

        # ---- extract the roots dict only, checksum, sync_metadata and version attrs do not use
        chrome_keys = list(source_file)     # get chrome main keys of the bookmark object
        if 'checksum' and 'roots' and 'version' not in chrome_keys:   # if keys don't exist that is wrong file format
            return False, f'Source file {filename} has wrong format'

        # ---- this is a chrome bookmark file ----
        # ---- remove unnecessary attrs from source structure: checksum, version, sync_metadata ----
        chrome_roots = source_file['roots']    # roots names and values dictionary only - (name: root), ...
        # ---- prepare a dict to create our internal root from source data
        tree_image = dict()  # clear attrs dict
        tree_image['children'] = list(chrome_roots.values())  # get a root children list, DO NOT VIEW !!!
        self.root.update_root(**tree_image)   # update the current tree with source values

        # ---- decode nested dictionaries from json image to the original objects and add it to the node's list ----
        dt = self.root.__dict__  # start from the root children
        self._chrome_into_object(dt)  # decode nested dictionaries recursively

        self._save_tree()  # save the updated current root

        return True, ''

    def convert_mozilla(self, filename: str) -> tuple[bool, str]:
        """Convert Mozilla bookmark filename to the current tree. Return (True/False, error message).

        :param filename: Mozilla bookmark filename to convert
        :return: (True, empty string)  or (False, error message)
        """
        return False, 'Implementation of the Mozilla format will be done later.\n'
