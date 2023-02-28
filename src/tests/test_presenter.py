"""Tests for a Presenter module"""

import os
from unittest import mock

import exceptions as e
from view_interface import View
from model_interface import Model
from presenter import Presenter

from common import VALID_CHARS

class TestPresenter:
    """Testing class for a Presenter module."""

    pres = Presenter()

    def test_init_class(self):
        """Test of instance initialisation."""
        assert isinstance(self.pres.view, View)
        assert isinstance(self.pres.model, Model)
        assert self.pres.menu_items == self.pres.START_MENU

    def test_exit_of_loop(self):
        assert self.pres.exit_of_loop() == (False, '')

    def test_create_tree(self):
        # ---- a successful case ----
        correct_name = 'New database'  # correct name of a new database
        cwd = os.getcwd()
        # mock methods
        self.pres.view = mock.MagicMock(name='view', spec=View)  # mock View interface
        self.pres.model = mock.MagicMock(name='model', spec=Model)  # mock Model interface

        self.pres.view.main_header = "TEST HEADER CREATE TREE"  # set a mocking method header
        self.pres.model.cwd = cwd  # current directory for test
        self.pres.view.input_line.return_value = correct_name  # mock a user input

        result = self.pres.create_tree()  # test of the method

        # test results
        assert self.pres.view.output_header.call_args.args == (self.pres.view.main_header,)  # header output
        assert self.pres.view.input_line.call_args.args == (
            "Input a name of a new bookmark's tree",
            VALID_CHARS)
        assert self.pres.model.create_database.call_count == 1
        assert self.pres.model.delete_database.call_count == 0
        assert self.pres.model.create_database.call_args.args == (correct_name,)
        assert self.pres.menu_items == self.pres.MAIN_MENU
        assert self.pres.view.output_string.call_args.args == (f'Current database is <{correct_name}> {chr(10)}',)
        assert result is True  # success

        # ---- a break or incorrect name case ----
        self.pres.view.reset_mock()
        self.pres.model.reset_mock()
        self.pres.view.input_line.return_value = None  # mock a user input

        result = self.pres.create_tree()  # test of the method

        assert self.pres.model.create_database.call_count == 0
        assert result is False  # not success

        # ---- the database exists, overwrite case ----
        # mock methods
        self.pres.view.reset_mock()
        self.pres.model.reset_mock()
        self.pres.view.input_line.return_value = correct_name  # mock a user input
        self.pres.model.create_database.side_effect = [FileExistsError, None]  # 1st - exception, 2nd - None
        self.pres.view.input_yes_or_no.return_value = True

        result = self.pres.create_tree()  # test of the method

        assert self.pres.view.input_yes_or_no.call_args.args == (
            f'Do you want to overwrite bookmark tree <{correct_name}>? All data will be lost... (Yes/No)',)
        assert self.pres.model.create_database.call_count == 2
        assert self.pres.model.delete_database.call_count == 1
        assert self.pres.model.create_database.call_args.args == (correct_name,)
        assert self.pres.menu_items == self.pres.MAIN_MENU
        exp_str_1 = f'File <{correct_name}> already exists in the work directory {self.pres.model.cwd}'
        exp_str_2 = f'Current database is <{correct_name}> {chr(10)}'
        assert self.pres.view.output_string.call_args_list == [((exp_str_1,),), ((exp_str_2,),)]
        assert result is True  # success

        # ---- the database exists, keeping case ----
        # mock methods
        self.pres.view.reset_mock()
        self.pres.model.reset_mock()
        self.pres.model.create_database.side_effect = FileExistsError  # exception only
        self.pres.view.input_yes_or_no.return_value = False

        result = self.pres.create_tree()  # test of the method
        # test results
        assert self.pres.view.input_yes_or_no.call_args.args == (
            f'Do you want to overwrite bookmark tree <{correct_name}>? All data will be lost... (Yes/No)',)
        assert self.pres.model.create_database.call_count == 1
        assert self.pres.model.delete_database.call_count == 0
        exp_str_1 = f'File <{correct_name}> already exists in the work directory {self.pres.model.cwd}'
        exp_str_2 = f'Keep an existing bookmark tree <{correct_name}> {chr(10)}'
        assert self.pres.view.output_string.call_args_list == [((exp_str_1,),), ((exp_str_2,),)]
        assert result is True  # success

    def test_open_tree(self):
        # ---- a successful case ----
        correct_name = 'Opening database'  # correct name of a new database
        cwd = os.getcwd()
        # mock methods
        self.pres.view = mock.MagicMock(name='view', spec=View)  # mock View interface
        self.pres.model = mock.MagicMock(name='model', spec=Model)  # mock Model interface

        self.pres.view.main_header = "TEST HEADER OPEN TREE"  # set a mocking method header
        self.pres.model.cwd = cwd  # current directory for test
        self.pres.view.input_line.return_value = correct_name  # mock a user input

        result = self.pres.open_tree()  # test of the method

        # test results
        assert self.pres.view.output_header.call_args.args == (self.pres.view.main_header,)  # header output
        assert self.pres.view.input_line.call_args.args == (
            "Input the name of the bookmark's tree",
            VALID_CHARS)
        assert self.pres.model.open_database.call_count == 1
        assert self.pres.model.open_database.call_args.args == (correct_name,)
        assert self.pres.menu_items == self.pres.MAIN_MENU
        assert self.pres.view.output_string.call_args.args == (f'Current database is <{correct_name}> {chr(10)}',)
        assert result is True  # success

        # ---- a break or incorrect name case ----
        self.pres.view.reset_mock()
        self.pres.model.reset_mock()
        self.pres.view.input_line.return_value = None  # mock a user input

        result = self.pres.open_tree()  # test of the method

        assert self.pres.model.open_database.call_count == 0
        assert result is False  # not success

        # ---- the database does not exist ----
        # mock methods
        self.pres.view.reset_mock()
        self.pres.model.reset_mock()
        self.pres.view.input_line.return_value = correct_name  # mock a user input
        self.pres.model.open_database.side_effect = FileNotFoundError  # exception

        result = self.pres.open_tree()  # test of the method

        assert self.pres.model.open_database.call_count == 1
        assert self.pres.model.open_database.call_args.args == (correct_name,)

        exp_str = f'File <{correct_name}> does not exist in the work directory {self.pres.model.cwd}{chr(10)}'
        assert self.pres.view.output_string.call_args.args == (exp_str,)
        assert result is False  # error

    def test_add_bookmark_folder(self):
        # ---- common params ----
        new_node = 'New folder'  # correct name of a new database
        parent_node = 'Parent folder'
        get_children_none = False, ()
        get_children_folder = True, ('item1', 'item2')
        attr_dict = {'name': new_node, 'parent_name': parent_node}  # args to add node
        node_type = True

        # ---- add a folder successfully ----
        # mock methods
        self.pres.view = mock.MagicMock(name='view', spec=View)  # mock View interface
        self.pres.model = mock.MagicMock(name='model', spec=Model)  # mock Model interface
        self.pres.view.main_header = "TEST HEADER ADD BOOKMARK"  # set a mocking method header
        # input_line params
        self.pres.view.input_line.side_effect = [new_node, parent_node]  # 2 calls for this case
        prompt_1 = "Input a name of the new bookmark", VALID_CHARS
        prompt_2 = "Input a name of the parent folder for a new bookmark", VALID_CHARS
        # yes_or_no params
        self.pres.view.input_yes_or_no.return_value = True  # folder for this case
        yes_or_no_prompt = f'Do you want to add a folder (yes), otherwise an url bookmark (no)? (Yes/No)'
        # get_children params
        self.pres.model.get_children.side_effect = [e.NodeNotExists(new_node), get_children_folder]  # 2 calls

        result = self.pres.add_bookmark()  # test of the method

        assert self.pres.view.output_header.call_args.args == (self.pres.view.main_header,)  # header output
        assert self.pres.view.input_line.call_args_list == [(prompt_1,), (prompt_2,), ]  # input_line args
        assert self.pres.view.input_yes_or_no.call_args.args == (yes_or_no_prompt,)  # yes_or_no arg
        assert self.pres.model.get_children.call_count == 2
        assert self.pres.model.add_node.call_count == 1
        assert self.pres.model.add_node.call_args.args == (attr_dict, node_type)
        assert result is True

        # ---- break at new node input ----
        self.pres.view.reset_mock(side_effect=True)  # reset side_effect from the previous case
        self.pres.model.reset_mock()
        self.pres.view.input_line.return_value = None  # break for this case
        result = self.pres.add_bookmark()  # test of the method
        assert result is False

        # ---- wrong nome of a new node ----
        self.pres.view.reset_mock()  # reset side_effect from the previous case
        self.pres.model.reset_mock()
        self.pres.view.input_line.return_value = ''  # invalid chars in the name
        result = self.pres.add_bookmark()  # test of the method
        assert result is False

        # ---- new node already exists ----
        self.pres.view.reset_mock()  # reset
        self.pres.model.reset_mock(side_effect=True)  # reset
        self.pres.view.input_line.return_value = new_node  # valid new name
        # get_children params
        self.pres.model.get_children.return_value = get_children_none  # name exists

        result = self.pres.add_bookmark()  # test of the method
        exp_str = f'Bookmark <{new_node}> already exists {chr(10)}'
        assert self.pres.view.output_string.call_args.args == (exp_str,)
        assert result is False


    def test_add_bookmark_url(self):
        pass
