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
"""Stuffs to represent a datacenter."""

from gandishell.objects import DataObject

from gandishell.utils import APIKEY


class Datacenter(DataObject):
    """The image itself."""

    class_token = ['list']
    instance_token = []
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def list(cls, api):
        """Get a list of existing datacenters."""
        res = {}
        for datacenter in api.hosting.datacenter.list(APIKEY):
            res[datacenter['id']] = Datacenter(**datacenter)
        return res
