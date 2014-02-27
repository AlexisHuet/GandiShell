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
"""
Implementation of syntaxic analysis with pyparsing.

 BNF:
 <command> ::= <instance> "." <inst_action> [<params>]
             | <type> "." <type_action> [<params>]

 <instance> ::= <type> "(" <id> ")"
 <inst_action> ::= "connect" | "delete" | "info" | "start" | "stop"
                 | "reboot" | "disk_attach" | "disk_detach"'

 <type> ::= "Account" | "Datacenter" | "Disk" | "Iface" | "Image"
          | "Ip" | "Operation" | "VirtualMachine"
 <type_action> ::= "count" | "list" | "create"

 <params> ::= "(" <param> [, <param>] ")"
 <param> ::= alphanum
 <id> ::= nums
"""

from pyparsing import (
    CaselessKeyword,
    Empty,
    Group,
    Suppress,
    Word,
    ZeroOrMore,
    alphanums,
    nums,
)

from gandishell.objects import (
    Account, Datacenter, Disk,
    Image, Ip, Iface,
    Operation, VirtualMachine as VM,
)

CMD_TO_TYPE = {
    'account': Account,
    'datacenter': Datacenter,
    'disk': Disk,
    'iface': Iface,
    'image': Image,
    'ip': Ip,
    'operation': Operation,
    'vm': VM,
}


def convert_int(toks):
    """Token to integer converter."""
    return [int(toks[0])]


def convert_type(toks):
    """Token to type converter."""
    return [CMD_TO_TYPE[toks[0]]]

ID = Suppress("(") + Word(nums).setResultsName('id') + Suppress(")")

TYPE = CaselessKeyword("account") |\
    CaselessKeyword("datacenter") |\
    CaselessKeyword("disk") |\
    CaselessKeyword("iface") |\
    CaselessKeyword("image") |\
    CaselessKeyword("ip") |\
    CaselessKeyword("operation") |\
    CaselessKeyword("vm")
TYPE = TYPE.setResultsName('type').setParseAction(convert_type)

INSTANCE = Group(TYPE + ID.setResultsName('id').setParseAction(convert_int))
INSTANCE = INSTANCE.setResultsName('instance')

TYPE_ACTION = CaselessKeyword("count") |\
    CaselessKeyword("list") |\
    CaselessKeyword("create")
TYPE_ACTION = TYPE_ACTION.setResultsName('type_action')

INST_ACTION = CaselessKeyword("connect") |\
    CaselessKeyword("delete") |\
    CaselessKeyword("info") |\
    CaselessKeyword("start") |\
    CaselessKeyword("stop") |\
    CaselessKeyword("reboot") |\
    CaselessKeyword("disk_attach") |\
    CaselessKeyword("disk_detach")
INST_ACTION = INST_ACTION.setResultsName('inst_action')

PARAM = Word(alphanums).setResultsName('param')
PARAMS = Group(
    Suppress("(") + PARAM + ZeroOrMore(Suppress(",") + PARAM) + Suppress(")")
    | Empty()
).setResultsName('params')

COMMAND = INSTANCE + Suppress(".") + INST_ACTION + PARAMS |\
    TYPE + Suppress(".") + TYPE_ACTION + PARAMS
COMMAND = Group(COMMAND).setResultsName('command')


def parse_command(line):
    """Parse the given line to return tokens."""
    COMMAND.validate()
    tokens = COMMAND.parseString(line)
    return tokens
