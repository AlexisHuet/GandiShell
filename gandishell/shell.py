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
"""Allow to manage Gandi's VM from a shell."""


from cmd import Cmd
from shlex import split

from pyparsing import ParseException

from gandishell.objects import (Account, Disk,
                                Image, Ip, Iface,
                                Operation, VirtualMachine as VM)
from gandishell.parsing import CMD_TO_TYPE, parse_command
from gandishell.utils import (get_api, PROMPT,
                              debug, info, error, warning, welcome,
                              catch_fault, print_iter
                              )


#pylint: disable=R0904,R0902
class GandiShell(Cmd):
    """
    The GandiShell is a line-oriented command interpreter that let you
    manage your Gandi hosted virtual machines.
    """
    api = get_api()
    prompt = PROMPT

    def __init__(self):
        with catch_fault():
            super().__init__()
            self.account = Account(self.api)
            welcome(self.account)
            # Map this type of objects to a self variable
            self.disks, self.images, self.ips = None, None, None
            self.ifaces, self.operations, self.vms = None, None, None
            self.stored_objects = {
                Disk: self.disks,
                Image: self.images,
                Ip: self.ips,
                Iface: self.ifaces,
                Operation: self.operations,
                VM: self.vms,
            }
            for i in [Disk, Image, Ip, Iface, Operation, VM]:
                self.stored_objects[i] = i.list(self.api)
                info("{} loaded.".format(i.__name__))

    def default(self, line):
        try:
            parse_result = parse_command(line)
            if 'instance' in parse_result['command']:
                klass = parse_result['command']['instance']['type']
                iid = parse_result['command']['instance']['id'][0]
                methodname = parse_result['command']['inst_action']
                obj = self.stored_objects[klass][iid]
                method = getattr(obj, methodname)
                print(method(self.api))
            else:
                klass = parse_result['command']['type']
                iid = None
                methodname = parse_result['command']['type_action']
                method = getattr(klass, methodname)
                result = method(self.api)
                print_iter(result)
        except ParseException as pex:
            warning(str(pex))

    def completedefault(self, text, line, begidx, endidx):
        debug('completedefault')

    def completenames(self, text, *ignored):
        try:
            debug(text + str(ignored))
            parse_result = parse_command(text)
        except ParserException as pex:
            debug(str(pex))
            debug(str(pex.msg))
            debug(str(pex.pstr))
        except Exception as exc:
            error(exc)
        finally:
            res = [x + '.' for x in CMD_TO_TYPE.keys() if x.startswith(text)]
            res += Cmd.completenames(self, text, *ignored)
            debug(res)
            return res

    def do_EOF(self, line):  # pylint: disable=C0103,W0613,R0201
        """Just say good-bye at end."""
        print("\n*{:-^77}*".format("- See U Soon - .{}".format(line)))
        return True
