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
"""Basic objects representation."""

from termcolor import colored

from gandishell.utils import APIKEY


class DataObject(dict):
    """Ancestor of all Gandi-related objects, for common things."""
    hidden_keys = ['id']  # Showed by template
    str_tmpl = "* {ttype}(" + colored('{id}',
                                      'yellow', attrs=['bold']) + "): {data}"

    def __str__(self):
        ttype = self.__class__.__name__
        data = ''
        for key, value in self.items():
            if key not in self.hidden_keys:
                data += "\n*\t{}: {}".format(colored(key,
                                                     'grey', attrs=['bold']),
                                             value)
        return self.str_tmpl.format(ttype=colored(ttype,
                                                  'red', attrs=['bold']),
                                    data=data, **self)

    def __repr__(self):
        tmpl = "{name}({content})"
        name = self.__class__.__name__
        content = dict.__repr__(self)
        return tmpl.format(name=name, content=content)


class Account(DataObject):
    """The account itself."""

    hidden_keys = ['id',  # Showed by template
                   'share_definition', 'products',  # Useless
                   'resources', 'rating_enabled'
                   ]

    def __init__(self, api):
        super().__init__(**api.hosting.account.info(APIKEY))

    def refresh(self, api):
        """Get fresh data about account state."""
        self.clear()
        self.update(**api.hosting.account.info(APIKEY))


class Operation(DataObject):
    """The operation itself."""
    pass
