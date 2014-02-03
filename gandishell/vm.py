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
"""Representation of a virtual machine."""

from getpass import getpass
from subprocess import call

from gandishell.datacenter import Datacenter
from gandishell.disk import Disk
from gandishell.image import Image
from gandishell.objects import DataObject, Operation
from gandishell.utils import (APIKEY,
                              ask_int, ask_string,
                              bold, error, info, print_iter,
                              catch_fault)


class VirtualMachine(DataObject):
    """The virtual-machine itself."""

    class_token = ['count', 'list', 'create']
    instance_token = ['connect', 'delete', 'info', 'start', 'stop', 'reboot',
                      'disk_attach', 'disk_detach']
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def count(cls, api):
        """Get the number of existing VM."""
        info("Counting VM")
        with catch_fault():
            res = api.hosting.vm.count(APIKEY)
            return "VM count: {}".format(res)

    @classmethod
    def list(cls, api):
        """Get a list of existing VM."""
        res = {}
        with catch_fault():
            for vmach in api.hosting.vm.list(APIKEY):
                res[vmach['id']] = VirtualMachine(**vmach)
            return res

    ########### id only commands ###########
    def connect(self, api):
        """Automatically start an ssh connection."""
        info("Starting SSH session...")
        with catch_fault():
            infos = api.hosting.vm.info(APIKEY, self['id'])
            ifaces = infos['ifaces']
            ips = []
            for iface in ifaces:
                for _ in iface['ips']:
                    ips.append(_['ip'])
            if len(ips) is 0:
                error("No address IP for this VM (?!?)")
                return
            elif len(ips) > 1:
                info("We have {} possible IP :".format(len(ips)))
                for _, addr in enumerate(ips):
                    bold("#{} : {}".format(_, addr))
                ip_addr = ips[ask_int('an ip id', choices=range(len(ips)))]
            else:
                ip_addr = ips.pop()
            login = ask_string('login')
            info("Running 'ssh {}@{}'".format(login, ip_addr))
            call(['ssh', '{}@{}'.format(login, ip_addr)])

    def delete(self, api):
        """Delete this VM."""
        info("Deleting VM {}".format(self['id']))
        with catch_fault():
            res = api.hosting.vm.delete(APIKEY, self['id'])
            ope = Operation(**res)
            return ope

    def info(self, api):
        """Get info about this VM."""
        info("Info about VM {}".format(self['id']))
        with catch_fault():
            res = api.hosting.vm.info(APIKEY, self['id'])
            return VirtualMachine(**res)

    def start(self, api):
        """Start this VM."""
        info("Starting VM {}".format(self['id']))
        with catch_fault():
            res = api.hosting.vm.start(APIKEY, self['id'])
            ope = Operation(**res)
            return ope

    def stop(self, api):
        """Stop this VM."""
        info("Stopping VM {}".format(self['id']))
        with catch_fault():
            res = api.hosting.vm.stop(APIKEY, self['id'])
            ope = Operation(**res)
            return ope

    def reboot(self, api):
        """Reboot this VM."""
        info("Rebooting VM {}".format(self['id']))
        with catch_fault():
            res = api.hosting.vm.reboot(APIKEY, self['id'])
            ope = Operation(**res)
            return ope

    ########### Attach/Detach ##############

    def disk_attach(self, api, disk_id):
        """Attach a disk to this VM."""
        with catch_fault():
            disk = Disk(api.hosting.disk.info(APIKEY, int(disk_id)))
            info('Disk({}) found'.format(disk_id))
            res = api.hosting.vm.disk_attach(APIKEY, self['id'], disk['id'])
            return Operation(**res)

    def disk_detach(self, api, disk_id):
        """Detach a disk from this VM."""
        with catch_fault():
            disk = Disk(api.hosting.disk.info(APIKEY, int(disk_id)))
            info('Disk({}) found'.format(disk_id))
            res = api.hosting.vm.disk_detach(APIKEY, self['id'], disk['id'])
            return Operation(**res)

    ############## VM makers ###############
    @classmethod
    def create(cls, api):
        """Create a new VM. We use user input to know his configuration."""
        print_iter(Datacenter.list(api))
        datacenter_id = ask_int('datacenter id', 1)
        disk_spec = {'datacenter_id': datacenter_id,
                     'name': ask_string('system disk name')}
        vm_spec = {'datacenter_id': datacenter_id,
                   'hostname': ask_string('hostname'),
                   'memory': ask_int('memory', 256,
                                     lambda x: (x >= 256 and x % 64 == 0)),
                   'cores': ask_int('core number', 1),
                   'bandwidth': ask_int('bandwidth', default=10240),
                   'ip_version': ask_int('ip version', 4, [4, 6]),
                   'password': getpass(
                       'Please provide a password (not echoed)')}
        while len(vm_spec['password']) < 8:
            vm_spec['password'] = getpass('Password minimum length is 8')
        image = Image.filter(api, datacenter_id)
        with catch_fault():
            ope = api.hosting.vm.create_from(APIKEY, vm_spec,
                                             disk_spec, image)
            return ope
