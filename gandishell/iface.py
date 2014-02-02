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
"""Representation of an Interface."""

from gandishell.objects import DataObject
from gandishell.utils import (APIKEY,
                              info,
                              catch_fault)


class Iface(DataObject):
    """An Interface."""

    class_token = ['count', 'list']
    instance_token = ['info']
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def count(cls, api):
        """Get the number of existing Interfaces."""
        info("Counting Interfaces")
        with catch_fault():
            res = api.hosting.iface.count(APIKEY)
            return "Interface count: {}".format(res)

    @classmethod
    def list(cls, api):
        """Get a list of existing Interfaces."""
        res = {}
        with catch_fault():
            for iface in api.hosting.iface.list(APIKEY):
                res[iface['id']] = Iface(**iface)
            return res

    ########### id only commands ###########
    def info(self, api):
        """Get info about this Interface."""
        info("Info about Interface {}".format(self['id']))
        with catch_fault():
            res = api.hosting.iface.info(APIKEY, self['id'])
            return Iface(**res)
