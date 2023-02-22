"""A model part of the bookmark manager.
This version creates an internal tree from node objects.
The bookmark tree is stored into a file in the json format.
"""
import os
import json

import exceptions
from nodes import RootBookmarks
from nodes import Folder
from nodes import Url


class MyJSONEncoder(json.JSONEncoder):
    """Customisation of user class encoding: RootBookmarks, Folder, Url"""
    def default(self, obj):
        if isinstance(obj, Folder | Url):
            return obj.__dict__  # for serialisation return an object's dict instead of the object
        elif isinstance(obj, RootBookmarks):    # for RootBookmarks a recursive ref to the object has to eliminate
            obj_copy = obj.__dict__.copy()  # make a swallow copy of the tree dict
            del obj_copy['nodes_dict']   # remove the dict of all nodes from json image (for the copy only!!!)
            return obj_copy  # for serialisation return an object's dict instead of the object (edited copy !)
        else:
            super().default(obj)


class TreeModel:
    def __init__(self):
        self.root = RootBookmarks()     # create the unique bookmark's tree object
        self.root.nodes_dict['roots'] = self.root  # initialisation of the dict of all nodes in the tree
        self.current_tree = ''  # name of the current tree and json filename
        self.cwd = os.getcwd()  # current working directory

    def save_current_tree(self):
        """Save the tree to the self.current_tree json file"""
        with open(self.current_tree, "w") as write_file:
            json.dump(self.root, write_file, cls=MyJSONEncoder)

    def check_folder(self, name):
        """Check if the named node exists, and it's a folder. Return a tuple (True/False, None/error message)"""
        try:
            self.root.check_folder(name)
            return (True, None)  # True if OK, None is second formal return value for compatibility
        except (exceptions.NodeNotExist, exceptions.FolderNotExist) as e:
            return (False, e)   # the node doesn't exist of is not a folder, False and error message return

    def output_children_names(self, children):
        """Output children names from incoming list of th children objects"""
        for x in children:
            name = x.__dict__['name']   # get next children name
            if 'children' in x.__dict__:    # folders must have the 'children' key
                name = '(' + name + ')'  # parentheses for folder child elements
            print(name, end=' ')
        print()

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


    def get_children(self, name):
        """Return a nested list of child objects of the node 'name'.
        If the node is an url then return None.
        If node does not exist then raise NodeNotExist"""
        node = self.root.check_node(name)  # return an object or raise NodeNotExist
        if 'children' in node.__dict__:
            result = []
            for x in node.children:     # iteration within a child list
                nested_name = x.name  # a name of the nested object
                res = self.get_children(nested_name)  # recursion
                result.append(res)  # add a child name and list to the result
            return name, result   # for folder return a tuple (name, [children])
        else:
            return name, None  # for url return a tuple (name, None)

    def get_node_content(self, name):
        """Return the node content dict of the node 'name'"""
        node_object = self.root.nodes_dict[name]  # get the node instance
        node_content = node_object.__dict__.copy()   # make a local dict copy of the node

        # ---- check if the node is a folder ----
        if 'children' in node_content:  # any folder has a children list
            # ---- prepare the node content dict ----
            name_list = []      # prepare an empty name children list
            for x in node_content['children']:  # get the names of the children list
                name_list.append(x.__dict__['name'])
            node_content['children'] = name_list

        return node_content

    def add_node(self, attr_dict, node_type):
        """Add a folder or url to the tree, parameters come from input dict.
        node_type = True for a folder creation otherwise url."""
        self.root.add_node(attr_dict, node_type)  # call an appropriated nodes method
        self.save_current_tree()  # save the updated current root

    def update_node(self, name, attr_dict):
        """Update a folder or url with <name> in the internal tree, parameters from input dict."""
        self.root.update_node(name, attr_dict)  # call an appropriated nodes method
        self.save_current_tree()  # save the updated current root

    def delete_node(self, name):
        """Delete a node from the current tree, name as parameter"""
        self.root.delete_node(name)     # call a nodes method
        self.save_current_tree()    # save the updated current root

    def create_database(self, name):
        """Create a new database with 'name', if 'name' already exists then FileExistsError exception.
        Create also an empty bookmark tree and return it
        """
        with open(name, 'x') as f:     # open a new file as exclusive, of FileExistsError if such a file exists
            pass    # ask for file recreating , see a controller logic
        self.current_tree = name    # store the name of the current bookmark tree
        self.save_current_tree()  # save a new tree to the json file

    def delete_database(self, name):
        """Delete the database file"""
        os.remove(name)

    def dict_into_object(self, dct):
        """Convert a dict into an object. Add the item (key, value) to the node's dict. Recursively."""
        i = 0  # an index in the children list
        for x in dct['children']:   # an iteration of child objects
            if 'children' in x:     # this object 'x' has a child list, so it is a folder
                self.dict_into_object(x)    # recursion call for the nested child list
                the_node = Folder(**x)  # get a Folder object from dict json attributes
            else:  # an url found
                the_node = Url(**x)  # get an Url object from dict json attributes

            dct['children'][i] = the_node  # put the object to the children list
            self.root.nodes_dict[the_node.__dict__['name']] = the_node  # add an item 'name, object' to the node's dict
            i += 1
        return dct     # return the dict where dicts are replaced by equivalent objects - nodes

    def open_database(self, name):
        """Open a database if it exists, read and extract it into a bookmark tree."""
        # ---- read json database ----
        with open(name, 'r') as f:   # open the tree image file, or FileNotFoundError exception
            tree_image = json.load(f)   # read the json image and then close the file, image is a dict
        self.current_tree = name    # set the current tree name

        # ---- update the root from the json image ----
        self.root.update_root(**tree_image)

        # ---- decode nested dictionaries from json image to the original objects and add it to the node's list ----
        dct = self.root.__dict__  # start from the root children
        self.dict_into_object(dct)  # decode nested dictionaries recursively

    # ---- section of format conversions

    def _chrome_into_object(self, dt):
        """Conversation of chrome json structure to the internal node tree. Recursively and in-place."""
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
                self.root.add_node(attr_dict, node_type)  # call an appropriated nodes method
                self._chrome_into_object(attr_dict)  # recursion
            else:
                node_type = False  # this is an url
                self.root.add_node(attr_dict, node_type)  # call an appropriated nodes method

            # an object has been created and added
            del dt['children'][0]  # remove a dict of the added node
            init_len -= 1
        # return dct  # return the dict where dicts are replaced by equivalent objects - nodes

    def convert_chrome(self, filename: str) -> tuple[bool, str]:
        """Convert Chrome bookmark JSON filename to the current tree. Return (True/False, error message)"""
        # ---- open and load JSON file of Chrome bookmarks, the file exists
        with open(filename, 'r', encoding='utf-8') as f:   # open the tree image fail, or FileNotFoundError exception
            source_file = json.load(f)   # read the json image and then close the file, image is a dict
            # print(source_file)  # for debug only

        # ---- extract the roots dict only, checksum, sync_metadata and version attrs do not use
        chrome_keys = list(source_file)     # get chrome main keys of the bookmark object
        if 'checksum' and 'roots' and 'version' not in chrome_keys:   # if keys don't exist that is wrong file format
            return False, f'Source file {filename} has wrong format'

        # ---- this is a chrome bookmark file ----
        # ---- remove unnecessary attrs from source structure: checksum, version, sync_metadata ----
        chrome_roots = source_file['roots']    # roots names and values dictionary only - (name: root), ...
        # ---- prepare a dict to create our internal root from source data
        tree_image = {}  # clear a attrs dict
        tree_image['children'] = list(chrome_roots.values())  # get a root children list, DO NOT VIEW !!!
        self.root.update_root(**tree_image)   # update the current tree with source values

        # ---- decode nested dictionaries from json image to the original objects and add it to the node's list ----
        dt = self.root.__dict__  # start from the root children
        self._chrome_into_object(dt)  # decode nested dictionaries recursively

        self.save_current_tree()  # save the updated current root

        return True, ''

    def convert_mozilla(self, filename: str) -> tuple[bool, str]:
        """Convert Mozilla bookmark filename to the current tree. Return (True/False, error message)"""
        return True, ''
