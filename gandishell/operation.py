#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Representation of Operations."""

from gandishell.objects import DataObject
from gandishell.utils import (APIKEY,
                              info,
                              catch_fault)


class Operation(DataObject):
    """The operation itself."""

    class_token = ['count', 'list']
    instance_token = ['info']
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def count(cls, api):
        """Get the number of existing Operation."""
        info("Counting Operation")
        with catch_fault():
            res = api.operation.count(APIKEY)
            return "Operation count: {}".format(res)

    @classmethod
    def list(cls, api):
        """Get a list of existing Operation."""
        res = {}
        with catch_fault():
            for oper in api.operation.list(APIKEY):
                res[oper['id']] = Operation(**oper)
            return res

    ########### id only commands ###########
    def info(self, api):
        """Get info about this Operation."""
        info("Info about Operation {}".format(self['id']))
        with catch_fault():
            res = api.operation.info(APIKEY, self['id'])
            return Operation(**res)
