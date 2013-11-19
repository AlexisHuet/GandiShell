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
"""Various useful fonctions used everywhere."""

from configparser import ConfigParser
from contextlib import contextmanager
from socket import error as SocketError
from types import FunctionType
from xmlrpc.client import Fault, ServerProxy

from termcolor import colored

CONFIG = ConfigParser()
CONFIG.read('config.ini')

ENDPOINT = CONFIG['MAIN']['ENDPOINT']
APIKEY = CONFIG['MAIN']['APIKEY']
PROMPT = colored('(', attrs=['blink']) + 'g)'
VERSION = 0.1

def ask_string(name, default=None):
    """Ask a string to the user."""
    inpt = str(input("Please provide {} (str)".format(name)))  #pylint: disable=W0141
    while inpt == '':
        inpt = str(input("Please provide NOT EMPTY {} (str)".format(name)))  #pylint: disable=W0141
        if default is not None:
            return default
    return inpt

def ask_int(name, default=0, choices=None):
    """Ask an int to the user."""
    tmpl = "Please provide {} (int) (default: {})"
    inpt = input(tmpl.format(name, default))  #pylint: disable=W0141
    if inpt == '':
        inpt = default
    else:
        try:
            inpt = int(inpt)
        except ValueError:
            inpt = ask_int('correct (int!!) ' + name, default, choices)
        if choices:
            if type(choices) is FunctionType:
                if not choices(inpt):
                    warning("{} does not fit constraint".format(inpt))
                    inpt = ask_int('valid ' + name, default, choices)
            elif inpt not in choices:
                warning("{} is not in {}".format(inpt, choices))
                inpt = ask_int('correct ({})'.format(
                    str(choices)) + name, default, choices)
    return inpt

def get_api():
    """Simple accessor to the api."""
    if DEBUG:
        return ServerProxy(ENDPOINT, use_datetime=True, verbose=True)
    else:
        return ServerProxy(ENDPOINT, use_datetime=True)


def bold(text):
    """Print text in bold."""
    print(colored(text, attrs=['bold']))


def debug(text):
    """Print text in green, for debugging."""
    print(colored(text, 'yellow'))


def info(text):
    """Print text underlined."""
    print(colored(text, attrs=['underline']))


def error(text):
    """Print text in bold red with exclamation marks, for errors."""
    print(colored('/!\\ ' + text + ' /!\\',
          'yellow', 'on_red',  attrs=['bold']))


def warning(text):
    """Print text in bold red for warning."""
    print(colored(text, 'red', attrs=['bold']))


def print_iter(toprint):
    """Print all elements of a list or of a dict."""
    if isinstance(toprint, list):
        for elem in toprint:
            print(elem)
    elif isinstance(toprint, dict):
        for elem in toprint.values():
            print(elem)
    else:
        info(toprint)

def welcome(account):
    """Print the welcome message."""
    # nice iso human-readable date
    date = account['date_credits_expiration']
    # Account identity
    idty = colored(" {fullname} - ", attrs=['bold'])
    idty += colored("({handle}) ", attrs=['dark'])
    idty = idty.center(79, '=')
    # credits and monetary value
    cred = colored("{credits:,}", 'yellow')
    cred += " credit left until " + colored("{date}", 'green')
    cost = "Avg cost: {average_credit_cost:.6f} => {value:.2f}€ last."
    value = account['credits'] * account['average_credit_cost']
    # license details
    gpl = """GandiShell {} Copyright © 2013 Alexis Huet
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain \
conditions.""".format(VERSION)
    bold(gpl)
    # Let's go !
    msg = '\n'.join([idty, cred, cost])
    print(msg.format(**dict(account, value=value, date=date)))

@contextmanager
def catch_fault():
    """A decorator to catch xmlprc.Fault, and just print it."""
    try:
        yield
    except Fault as exc:
        error("An XMLRPC error {} occured: {}".format(
                    exc.faultCode, exc.faultString))
    except SocketError as exc:
        error("A socket error occured: ({}) - {}".format(
                    exc.errno, exc.strerror))


try:
    DEBUG = CONFIG.getint('MAIN', 'DEBUG')
except ValueError as exc:
    warning(exc)
    DEBUG = 2
