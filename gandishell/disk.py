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
"""Stuffs to represent a disk."""

from gandishell.objects import DataObject, Operation

from gandishell.utils import APIKEY, info, catch_fault


class Disk(DataObject):
    """The disk itself."""

    class_token = ['count', 'list']
    instance_token = ['delete', 'info']
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def count(cls, api):
        """Count the number of existing disks."""
        info("Counting Disk")
        with catch_fault():
            res = api.hosting.disk.count(APIKEY)
            return "Disk count: {}".format(res)

    @classmethod
    def list(cls, api):
        """Get a list of existing disks."""
        res = {}
        with catch_fault():
            for disk in api.hosting.disk.list(APIKEY):
                res[disk['id']] = Disk(**disk)
            return res

    ########### id only commands ###########
    def delete(self, api):
        """Delete this disk."""
        info("Deleting Disk {}".format(self['id']))
        with catch_fault():
            res = api.hosting.disk.delete(APIKEY, self['id'])
            ope = Operation(**res)
            return ope

    def info(self, api):
        """Get info about this disk."""
        info("Info about Disk {}".format(self['id']))
        with catch_fault():
            res = api.hosting.disk.info(APIKEY, self['id'])
            return Disk(**res)
