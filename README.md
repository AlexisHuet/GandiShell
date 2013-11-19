GandiShell
==========

Manage your Gandi's hosted virtualmachine inside a shell

Disclaimer
----------

You need a valid gandi account with credits available to use
this software, see http://www.gandi.net
If you don't understand what it is, you probably don't need
this software ;-)

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

The author of this program is just a Gandi client, with no
more connection to this company.
This is homemade alpha software, you should not rely on it
for production purposes.

> YOU SHOULD READ THE CODE BEFORE EXECUTING IT.

How it works
------------

- Go to https://www.gandi.net/admin/api_key to obtain your api key
and copy it in the config.ini file.
- run ./gandishell/shell.py
GandiShell will show your account information on startup.
- Type your command. You can use the TAB key for autocompletion.
Examples:

    Get the list of avaible images:
    (g)image list
    Get details about one particular image:
    (g)image info 42
    Create a new VirtualMachine with interactive questions:
    (g)vm create
    Easy ssh connection to a VM:
    (g)vm connect 4242

Some working features are :

- autocompletion
- account_info
- datacenter : list
- disk : count/delete/info/list
- image : list/info
- ip : count/list/info
- iface : count/list/info
- vm : count/list/create/delete/info/start/stop/reboot/connect/disk_attach/disk_detach

Some of the missing features are :

- see http://doc.rpc.gandi.net/hosting/index.html
- ip : update
- iface : create/delete/update
- vm: iface_detach/iface_attach and all VM modifications.
