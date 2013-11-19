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
"""Representation of an IP address."""

from objects import DataObject
from utils import (APIKEY,
                   info,
                   catch_fault)


class Ip(DataObject):
    """An IP address."""

    class_token = ['count', 'list']
    instance_token = ['info']
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def count(cls, api):
        """Get the number of existing IPs."""
        info("Counting IPs")
        with catch_fault():
            res = api.hosting.ip.count(APIKEY)
            return "IP count: {}".format(res)

    @classmethod
    def list(cls, api):
        """Get a list of existing IPs."""
        res = {}
        with catch_fault():
            for ip_addr in api.hosting.ip.list(APIKEY):
                res[ip_addr['id']] = Ip(**ip_addr)
            return res

    ########### id only commands ###########
    def info(self, api):
        """Get info about this IP."""
        info("Info about IP {}".format(self['id']))
        with catch_fault():
            res = api.hosting.ip.info(APIKEY, self['id'])
            return Ip(**res)
