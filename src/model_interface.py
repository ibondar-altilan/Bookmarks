"""Interface between Presenter class and Model implementations."""

import typing as t

class ModelProtocol(t.Protocol):
    """Prototype class of Model."""

    tree_name: str

    # ---- database section ----
    def create_database(self, name: str):
        """Create an empty bookmark structure and a file to keep the database.

        :exceptions: FileExistsError if given filename exists

        :param name: name of the new database, filename for it
        :return: nothing
        """

    def open_database(self, name: str):
        """Open a database, read and extract it into a bookmark tree.

        :exception: FileNotFoundError if the filename does not exist

        :param name: name and filename of the deleting database
        :return: nothing
        """

    def delete_database(self, name):
        """Delete the database file.

        :exception: FileNotFoundError if the filename does not exist

        :param name: name and filename of the deleting database
        :return: nothing
        """


    # ---- nodes section ----
    def add_node

    def update_node

    def delete_node

    def get_node(self, name: str) -> dict:
        """Get a node content.
        Replace children objects with their names for folder children list

        :param name: node name
        :return: dictionary {field_name: field_value} of the node
        """


    # ---- convertors section ----
    def convert_chrome(self, filename: str) -> tuple[bool, str]:
        """Convert Chrome bookmark JSON filename to the current tree. Return (True/False, error message)

        :param filename: Google bookmark filename to convert
        :return: (True, empty string)  or (False, error message)
        """

    def convert_mozilla(self, filename: str) -> tuple[bool, str]:
        """Convert Mozilla bookmark filename to the current tree. Return (True/False, error message).

        :param filename: Mozilla bookmark filename to convert
        :return: (True, empty string)  or (False, error message)
        """
        return False, 'Implementation of the Mozilla format will be done later.\n'

