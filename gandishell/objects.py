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

from getpass import getpass
from subprocess import call
from termcolor import colored

from gandishell.utils import (APIKEY,
                              ask_int, ask_string,
                              bold, error, info, warning,
                              catch_fault, print_iter
                              )


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


class Image(DataObject):
    """The image itself."""

    class_token = ['list']
    instance_token = ['info']
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def list(cls, api):
        """Get a list of existing disks images."""
        res = {}
        for image in api.hosting.image.list(APIKEY):
            res[image['id']] = Image(**image)
        return res

    @classmethod
    def filter(cls, api, datacenter_id):
        """Select an image by filtering on his name."""
        images = {k: v for k, v in cls.list(api).items()
                  if v['datacenter_id'] == datacenter_id}
        for k, v in images.items():
            print(k, v)
        while len(images) > 1:
            _ = "an id or a keyword, as we still have {} possible disk images."
            keyword = ask_string(_.format(len(images)), '')
            try:
                keyword = int(keyword)
                if keyword not in images:
                    warning("{} is not a valid id".format(keyword))
                else:
                    image = images[keyword]
                    break
            except ValueError:
                filtered = {k: v for k, v in images.items()
                            if keyword in v['label']}
                if not len(filtered):
                    warning("No label contains \"{}\"".format(keyword))
                    continue
                elif len(filtered) is 1:
                    image = filtered.popitem()[1]
                    break
                else:
                    images = filtered
                    for _, v in images.items():
                        print(v)
                    continue
        info('Image selected :')
        print(image)
        return image['disk_id']

    ########### id only commands ###########
    def info(self, api):
        """Get info about this disk image."""
        info("Info about Image {}".format(self['id']))
        with catch_fault():
            res = api.hosting.image.info(APIKEY, self['id'])
        return Image(**res)


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
