# Copyright 2015 Metaswitch Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest

from nose.tools import *
from mock import patch, Mock, call, ANY

from pycalico.netns import (create_veth, remove_veth, veth_exists,
                            IP_CMD_TIMEOUT, CalledProcessError)


class TestVeth(unittest.TestCase):

    @patch("pycalico.netns.check_call", autospec=True)
    def test_create_veth(self, m_check_call):
        """
        Test creating a veth (pair).
        """
        create_veth("veth1", "temp_name")
        check_call_1 = call(['ip', 'link', 'add', "veth1", 'type',
                             'veth','peer', 'name', "temp_name"],
                            timeout=IP_CMD_TIMEOUT)
        check_call_2 = call(['ip', 'link', 'set', "veth1", 'up'],
                            timeout=IP_CMD_TIMEOUT)
        m_check_call.assert_has_calls([check_call_1, check_call_2])

    @patch("pycalico.netns.veth_exists", autospec=True)
    @patch("pycalico.netns.check_call", autospec=True)
    def test_remove_veth_success(self, m_check_call, m_veth_exists):
        """
        Test remove_veth returns True for successfully removing a veth.
        """
        m_veth_exists.return_value = True;
        self.assertTrue(remove_veth("veth1"))
        m_veth_exists.assert_called_once_with("veth1")
        m_check_call.assert_called_once_with(['ip', 'link', 'del', "veth1"],
                                             timeout=IP_CMD_TIMEOUT)

    @patch("pycalico.netns.veth_exists", autospec=True)
    @patch("pycalico.netns.check_call", autospec=True)
    def test_remove_veth_no_veth(self, m_check_call, m_veth_exists):
        """
        Test remove_veth returns False when veth doesn't exist.
        """
        m_veth_exists.return_value = False;
        self.assertFalse(remove_veth("veth1"))
        m_veth_exists.assert_called_once_with("veth1")
        self.assertFalse(m_check_call.called)

    @patch('__builtin__.open', autospec=True)
    @patch("pycalico.netns.check_call", autospec=True)
    def test_veth_exists_true(self, m_check_call, m_open):
        """
        Test veth_exists returns True if no error occurs.
        """
        self.assertTrue(veth_exists("veth1"))
        m_open.assert_called_once_with(os.devnull, 'w')
        m_check_call.assert_called_once_with(["ip", "link", "show", "veth1"],
                                             stderr=ANY,
                                             stdout=ANY)

    @patch('__builtin__.open', autospec=True)
    @patch("pycalico.netns.check_call", autospec=True)
    def test_veth_exists_false(self, m_check_call, m_open):
        """
        Test veth_exists returns True if no error occurs.
        """
        m_check_call.side_effect = CalledProcessError(1, "test")
        self.assertFalse(veth_exists("veth1"))
        m_open.assert_called_once_with(os.devnull, 'w')
        m_check_call.assert_called_once_with(["ip", "link", "show", "veth1"],
                                             stderr=ANY,
                                             stdout=ANY)

