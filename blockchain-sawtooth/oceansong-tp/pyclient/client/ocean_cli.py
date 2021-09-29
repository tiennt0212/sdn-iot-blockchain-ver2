import argparse
import getpass
import logging
import os
import sys
import traceback
import pkg_resources
import json

from colorlog import ColoredFormatter

from client.ocean_client import OceanClient

DISTRIBUTION_NAME = 'oceansong'

REST_API_URL = 'http://172.21.0.3:8008' #IP of REST-API
# REST_API_URL = os.environ.get('REST_API_URL')

def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)
    clog.setLevel(logging.DEBUG)
    return clog

def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def add_register_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'register',
        help='register new Node with BlockChain',
        parents=[parent_parser])

    parser.add_argument(
        'fileInfo',
        type=str,
        help='file JSON contain data of this device')

    parser.add_argument(
        'nodeKey',
        type=str,
        help='the key of master node')

def add_modelrequest_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'model-request',
        help='send request to get Global Model from A-node',
        parents=[parent_parser])

    parser.add_argument(
        'token',
        type=str,
        help='text-file only contain token of this Node')

    parser.add_argument(
        'dataFile',
        type=str,
        help='JSON-file contain infomation about request')

    parser.add_argument(
        'nodeKey',
        type=str,
        help='the node key')

def add_modelverify_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'model-verify',
        help='verify a Model have been trained by this Node',
        parents=[parent_parser])

    parser.add_argument(
        'token',
        type=str,
        help='text-file only contain token of this Node')

    parser.add_argument(
        'dataFile',
        type=str,
        help='JSON-file contain infomation about verification')

    parser.add_argument(
        'nodeKey',
        type=str,
        help='the node key')

def add_taskassign_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'task-assign',
        help='verify a Model have been trained by this Node',
        parents=[parent_parser])

    parser.add_argument(
        'token',
        type=str,
        help='text-file only contain token of this Node')

    parser.add_argument(
        'dataFile',
        type=str,
        help='JSON-file contain infomation about verification')

    parser.add_argument(
        'nodeKey',
        type=str,
        help='the node key')

def create_parent_parser(prog_name):
    '''Define the -V/--version command line options.'''
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    '''Define the command line parsing for all the options and subcommands.'''
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to manage your IoT device',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_register_parser(subparsers, parent_parser)
    add_modelrequest_parser(subparsers, parent_parser)
    add_modelverify_parser(subparsers, parent_parser)
    add_taskassign_parser(subparsers, parent_parser)

    return parser

def _get_keyfile(customerName):
    '''Get the private key for a customer.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, customerName)

def _get_pubkeyfile(customerName):
    '''Get the public key for a customer.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.pub'.format(key_dir, customerName)

def do_register(args):
    '''Implements the "register" subcommand by calling the client class.'''
    keyfile = _get_keyfile(args.nodeKey)

    with open(args.fileInfo) as file:
        info = json.load(file)

    client = OceanClient(baseUrl=REST_API_URL, keyFile=keyfile)

    response = client.register(info)

    print("Response: {}".format(response))

def do_model_request(args):
    keyfile = _get_keyfile(args.nodeKey)

    with open(args.token) as file:
        token = file.read()
        # Token has specify character '\n'
        # I have to remove '\n' by strip()
        token = token.strip()

    with open(args.dataFile) as file:
        infoRequest = json.load(file)

    client = OceanClient(baseUrl=REST_API_URL, keyFile=keyfile)

    response = client.model_request(token, infoRequest)

    print("Response: {}".format(response))

def do_model_verify(args):
    keyfile = _get_keyfile(args.nodeKey)

    with open(args.token) as file:
        token = file.read()
        # Token has specify character '\n'
        # I have to remove '\n' by strip()
        token = token.strip()

    with open(args.dataFile) as file:
        infoVerify = json.load(file)

    client = OceanClient(baseUrl=REST_API_URL, keyFile=keyfile)

    response = client.model_verify(token, infoVerify)

    print("Response: {}".format(response))

def do_task_assign(args):
    keyfile = _get_keyfile(args.nodeKey)
    with open(args.token) as file:
        token = file.read()
        # Token has specify character '\n'
        # I have to remove '\n' by strip()
        token = token.strip()

    with open(args.dataFile) as file:
        infoAssign = json.load(file)

    client = OceanClient(baseUrl=REST_API_URL, keyFile=keyfile)
    
    response = client.task_assign(token, infoAssign)

    print("Response: {}".format(response))

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    '''Entry point function for the client CLI.'''
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    verbose_level = 0

    setup_loggers(verbose_level=verbose_level)

    # Get the commands from cli args and call corresponding handlers
    if args.command == 'register':
        do_register(args)
    elif args.command == 'model-request':
        do_model_request(args)
    elif args.command == 'model-verify':
        do_model_verify(args)
    elif args.command == 'task-assign':
        do_task_assign(args)
    else:
        raise Exception("Invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
