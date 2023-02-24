"""The module for the bookmark project.
It contents a node-type classes

Class Node is a basic class for the bookmark's nodes
Possible inputs are guid, parent_guid, name:
    guid: a global unique identifier of the node, if is omitted, than calculates under the node creation
    parent_guid: a guid of the parent node, assigning at the node insertion into the tree
    name: name of the node, if is omitted then the name is the same as guid

Class RootBookmarks (from Node) creates the root node of the tree
An instance of root node is unique by using Singleton class

Class Bookmark (from Node) is a parent class for Folder and Url classes
Possible inputs are id_no, date_added:
    id_no: a simple integer id number of entity, for compatibility with Chrome
    date_added: a date of entity creation (by default set to current datetime)

Class Folder (from Bookmark) is a folder entity, might have children entities
Attributes:
    self.guid
    self.parent_guid
    self.name
    self.id_no
    self.date_added: str
    self.children   # a list of children entities
    self.date_modified: str # a date of folder modify, for compatibility with Chrome

Class Url (from Bookmark) is an url entity, without children
Attributes:
    self.guid
    self.parent_guid
    self.name
    self.id_no
    self.date_added: str
    self.url    # URL of the bookmark
    self.icon   # small graphic icon of the URL
    self.keywords   # the keywords for the URL content
"""

import uuid
from datetime import datetime

import exceptions


class Node(object):
    """The base class of nodes for bookmark's tree"""

    def __init__(self, guid: str = '', parent_guid: str = '', name: str = ''):
        # set guid, if empty - generate a new guid
        if guid:
            self.guid = guid
        else:
            self.guid = str(uuid.uuid4())

        self.parent_guid = parent_guid  # define at the inserting to the tree

        # set name
        if name:
            self.name = name
        else:
            self.name = self.guid  # by default the name of node is guid

    def update(self, **kwargs):
        """Changing of guid, parent_guid and name, exceeded argument(s) will raise TypeError"""
        if 'guid' in kwargs:
            self.guid = kwargs.pop('guid')
        if 'parent_guid' in kwargs:
            self.parent_guid = kwargs.pop('parent_guid')
        if 'name' in kwargs:
            self.name = kwargs.pop('name')
        if kwargs:
            raise TypeError(f'{len(kwargs)} exceeded argument(s) was/were given')


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RootBookmarks(Node, metaclass=Singleton):
    """The root class for bookmark's tree"""

    def __init__(self):
        self.nodes_dict = {}    # dict of all nodes in the tree: {'name': <object>,,,}
        self.children: list = list()  # create the list of child objects
        today = datetime.today().replace(microsecond=0)  # get today datetime object
        self.date_added = datetime.isoformat(today)  # insert the current datetime as a string
        self.date_modified = datetime.isoformat(today)  # insert the current datetime as a string
        # default values for name and parent_guid, no parent_guid for the root
        super().__init__(name='roots', parent_guid=None)

    def update_root(self, **kwargs):
        """Here only root children list is changed"""
        self.children = kwargs.pop('children')
        self.date_added = kwargs.pop('date_added')
        self.date_modified = kwargs.pop('date_modified')
        super().update(**kwargs)

    def name_double(self, name):
        """Check if a name already exists in the common name dict.
         If so, return 'name(i)' where i = 1,2, ... n, otherwise return 'name'"""
        i = 1  # initial copy name number
        new_name = name  # an initial name for search
        while new_name in self.nodes_dict:
            new_name = f'{name} ({i})'
            i += 1
        return new_name


    def check_node(self, name):
        """Check if the node 'name' is in the nodes.dict. Return an object of the node or raise NodeNotExist"""
        if name in self.nodes_dict:
            return self.nodes_dict[name]  # the node 'name' exists, return a node object
        else:
            raise exceptions.NodeNotExist(name)   # a named node does not exist, NodeNotExist error

    def check_folder(self,name):
        """Check if the node 'name' is in the nodes.dict. If not then raise NodeNotExist
        If OK then check if the node is a folder. Return an object of the folder or raise FolderNotExist"""
        node_object = self.check_node(name)    # get the node object if it exists or raise NodeNotExist

        # ---- check if it is a folder, return an object if OK, or raise FolderNotExist ----
        if 'children' in node_object.__dict__:  # any folder must have a child list
            return node_object  # OK, return folder object
        else:
            raise exceptions.FolderNotExist(name)  # a named folder does not exist, FolderNotExist error

    def add_node(self, attr_dict, node_type):
        """Add a folder or url to the tree, parameters from input dict.
        node_type = True for a folder creation otherwise url."""

        # replace the parent name with the parent guid
        parent_node = self.nodes_dict[attr_dict['parent_name']]  # get a parent object
        attr_dict['parent_guid'] = parent_node.__dict__['guid']  # get the parent guid and set it to args
        del attr_dict['parent_name']  # remove the unnecessary argument

        # create a node, folder or url
        if node_type:
            new_node = Folder(**attr_dict)  # create a new folder instance
        else:
            new_node = Url(**attr_dict)  # create a new url instance

        # modify the parent's children list and common nodes dict
        parent_node.children.append(new_node)  # add new node object to the parent child list
        self.nodes_dict[new_node.name] = new_node  # add new node object to the node's dict

    def update_node(self, name, attr_dict):
        """Update a folder or url with <name> in the internal tree, parameters from input dict.
        Modifying of the node's datestamp will be added later"""

        node_object = self.nodes_dict[name]  # get the node object

        # here will be an update of the node's datestamp, add the current date to attr_dict

        node_object.update(**attr_dict)  # update a node instance

        if name != attr_dict['name']:
            # a node name should be changed, update the common node's dict
            del self.nodes_dict[name]  # delete old (name: obj) pair from the node's dict
            self.nodes_dict[attr_dict['name']] = node_object  # add updated node object to the node's dict


    def delete_node(self, name):
        """Delete a node from the current tree, the name of the object being deleted comes as an arg"""
        node_object = self.check_node(name)  # get the node instance if the node exists or NodeNotExist error

        # ---- check if the node is non-empty folder ----
        if 'children' in node_object.__dict__:    # any folder must have a child list
            if node_object.children:    # it's a folder and its child list is not empty
                raise exceptions.FolderNotEmpty(name)   # can not delete a non-empty folder, FolderNotEmpty error

        # ---- find a list of children and delete the reference to the node ----
        parent_guid = node_object.parent_guid   # get the parend guid of the node
        for x in self.nodes_dict.values():  # search within the common dict of nodes
            if x.guid == parent_guid:
                children = x.children   # get the child list of the parent node
                children.remove(node_object)    # delete the node's object from the parent's child list
        del self.nodes_dict[name]   # remove the node from global node dict


class Bookmark(Node):
    """Parent class for Folder and Url classes"""

    def __init__(self, id_no=0, date_added='', **kwargs):
        self.id_no = id_no  # for compatibility with Chrome , will be assigned later
        # set date_added for compatibility with Chrome , might be updated later
        if not date_added:  # date_added parameter is omitted, set it from today datetime
            today = datetime.today().replace(microsecond=0)    # get today datetime object
            self.date_added = datetime.isoformat(today)  # insert the current datetime as a string
        else:
            self.date_added = date_added
        super().__init__(**kwargs)

    def update(self, **kwargs):
        """Here only id_no and date_added are changed"""
        if 'id_no' in kwargs:
            self.id_no = kwargs.pop('id_no')
        if 'date_added' in kwargs:
            self.date_added = kwargs.pop('date_added')
        super().update(**kwargs)


class Folder(Bookmark):
    """Child class of Bookmark class"""

    def __init__(self, children=None, date_modified='', **kwargs):
        if not children:
            self.children = []   # default value of mutable args evaluated at the FIRST CALL only !!!
        else:
            self.children = children  # save an incoming list
        # set date_added for compatibility with Chrome , might be updated later
        if not date_modified:  # date_added parameter is omitted, set it from today datetime
            today = datetime.today().replace(microsecond=0)  # get today datetime object
            self.date_modified = datetime.isoformat(today)  # insert the current datetime as a string
        else:
            self.date_modified = date_modified
        super().__init__(**kwargs)

    def update(self, **kwargs):
        """Here only children list and date_modified are changed"""
        if 'children' in kwargs:
            self.children = kwargs.pop('children')
        if 'date_modified' in kwargs:
            self.date_modified = kwargs.pop('date_modified')
        super().update(**kwargs)


class Url(Bookmark):
    """Child class of Bookmark class"""

    def __init__(self, url='', icon='', keywords='', **kwargs):
        self.url: str = url
        self.icon: str = icon
        self.keywords: str = keywords
        super().__init__(**kwargs)

    def update(self, **kwargs):
        """Here only url, icon, keywords are changed"""
        if 'url' in kwargs:
            self.url = kwargs.pop('url')
        if 'icon' in kwargs:
            self.icon = kwargs.pop('icon')
        if 'keywords' in kwargs:
            self.keywords = kwargs.pop('keywords')
        super().update(**kwargs)

