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

from gandishell.objects import Account
from gandishell.datacenter import Datacenter
from gandishell.disk import Disk
from gandishell.image import Image
from gandishell.ip import Ip
from gandishell.iface import Iface
from gandishell.vm import VirtualMachine as VM
from gandishell.utils import (get_api, PROMPT,
                              debug, info, warning, welcome,
                              print_iter, catch_fault
                              )


#pylint: disable=R0904
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
            self.disks, self.images, self.vms = None, None, None
            self.ips, self.ifaces = None, None
            self.stored_objects = {
                Disk: self.disks,
                Image: self.images,
                Ip: self.ips,
                Iface: self.ifaces,
                VM: self.vms,
            }
            for i in [VM, Disk, Image, Ip, Iface]:
                self.stored_objects[i] = i.list(self.api)
                info("{} loaded.".format(i.__name__))

    def command_handler(self, line, ttype):
        """Parse the line and run the selected method on the given type."""
        tokens = split(line)
        # No arguments : print out available actions
        if len(tokens) is 0:
            info("Possible actions are : {}".format(' '.join(ttype.all_token)))
            return
        # Class action : execute it
        if tokens[0] in ttype.class_token:
            res = getattr(ttype, tokens[0])(self.api)
            print_iter(res)
        # Instance action : we need an id
        elif tokens[0] in ttype.instance_token:
            try:
                obj_id = int(tokens[1])
            except ValueError:
                warning("Bad input.")
                return
            except IndexError:
                warning("'{}' is not a complete command".format(tokens))
                return
            try:
                obj = self.stored_objects[ttype][obj_id]
            except KeyError as exc:
                warning("Unknow id: {}".format(exc))
                return
            try:
                ope = getattr(obj, tokens[0])(self.api, *tokens[2:])
                print(ope)
            except TypeError as exc:
                warning("Bad arguments : {}".format(exc))
            # Refresh internal data, except for read-only commands.
            if ttype in self.stored_objects \
                    and tokens[0] not in ['count', 'info', 'list']:
                debug('refreshing {}'.format(ttype.__name__))
                self.stored_objects[ttype] = ttype.list(self.api)
        else:
            warning("Unknow command : {}.".format(tokens[0]))

    # pylint: disable=W0613,R0913
    def complete_handler(self, text, line, begidx, endidx, ttype):
        """Propose coherent completions for a given type."""
        completions = []
        tokens = split(line)
        # Empty line: propose all token
        if len(tokens) == 1:
            completions = ttype.all_token[:]
        # There is a first token
        elif len(tokens) == 2:
            token = tokens[1]
            # Is it a complete token that need an id ?
            if token in ttype.instance_token:
                completions = [str(key) + ' ' for key in
                               self.stored_objects[ttype].keys()]
            # Or do we need to complete ? (can implicitely be empty)
            elif token not in ttype.all_token:
                completions = [f + ' ' for f in ttype.all_token
                               if f.startswith(token)]
            # Implicit else: the token is already complete
        # Complete ids when they are ambiguous
        elif len(tokens) == 3:
            token = tokens[2]
            # double str(key) is not very clean, but works
            completions = [str(key) + ' ' for key in
                           self.stored_objects[ttype].keys()
                           if str(key).startswith(token)]
        return completions

    ############### Small commands without arguments ################
    def do_account_info(self, line):
        """account_info [refresh] : Show acount data."""
        if line:
            debug('Refreshing account info')
            self.account.refresh(self.api)
        print(self.account)

    def do_EOF(self, line):  # pylint: disable=C0103,W0613,R0201
        """Just say good-bye at end."""
        print("\n*{:-^77}*".format("- See U Soon - .{}".format(line)))
        return True

    ############## Datacenter ##############
    def do_datacenter(self, line):
        """datacenter command : execute specified command"""
        self.command_handler(line, Datacenter)

    def complete_datacenter(self, text, line, begidx, endidx):
        """Autocompletion for the datacenter command."""
        return self.complete_handler(text, line, begidx, endidx, Datacenter)

    ############# Disk Images ##############
    def do_image(self, line):
        """image command [id] : execute specified command [on image]"""
        self.command_handler(line, Image)

    def complete_image(self, text, line, begidx, endidx):
        """Autocompletion for the image command."""
        return self.complete_handler(text, line, begidx, endidx, Image)

    ################ Disks #################
    def do_disk(self, line):
        """disk command [id] : execute specified command [on a disk]"""
        self.command_handler(line, Disk)

    def complete_disk(self, text, line, begidx, endidx):
        """Autocompletion for the disk command."""
        return self.complete_handler(text, line, begidx, endidx, Disk)

    ################ Iface #################
    def do_iface(self, line):
        """iface command [id] : execute specified command [on a iface]"""
        self.command_handler(line, Iface)

    def complete_iface(self, text, line, begidx, endidx):
        """Autocompletion for the iface command."""
        return self.complete_handler(text, line, begidx, endidx, Iface)

    ################ IP #################
    def do_ip(self, line):
        """ip command [id] : execute specified command [on a ip]"""
        self.command_handler(line, Ip)

    def complete_ip(self, text, line, begidx, endidx):
        """Autocompletion for the ip command."""
        return self.complete_handler(text, line, begidx, endidx, Ip)

    ########### Virtual Machines ###########
    def do_vm(self, line):
        """vm command [id] : execute specified command [on a specified VM]"""
        self.command_handler(line, VM)

    def complete_vm(self, text, line, begidx, endidx):
        """Autocompletion for the vm command."""
        return self.complete_handler(text, line, begidx, endidx, VM)
