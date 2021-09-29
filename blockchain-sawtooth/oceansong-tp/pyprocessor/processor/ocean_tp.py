import traceback
import sys
import hashlib
import logging
import tokenlib
import json
import ast
import requests
from requests.auth import HTTPBasicAuth
from colorlog import ColoredFormatter
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

import time


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = "oceansong"
manager = tokenlib.TokenManager(secret="OCEANSONG")
# TP_URL = "tcp://172.20.0.2:4004" #Validator url
# vpls = 'UIT'

def _hash(data):
    '''Compute the SHA-512 hash and return the result as hex characters.'''
    return hashlib.sha512(data).hexdigest()

def _valid_token(token):
    try:
        manager.parse_token(token)
        return True
    except:
        return False
    

# Prefix for simplewallet is the first six hex digits of SHA-512(TF name).
sw_namespace = _hash(FAMILY_NAME.encode('utf-8'))[0:6]

class OceanTransactionHandler(TransactionHandler):
    '''                                                       
    Transaction Processor class for the OCEANSONG transaction family.       
                                                              
    This with the validator using the accept/get/set functions.
    It implements functions to REGISTER and APPLY rules for any devices.
    '''

    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        '''This implements the apply function for this transaction handler.
                                                              
           This function does most of the work for this class by processing
           a single transaction for the OCEANSONG transaction family.   
        '''  
        file = open("./measureTP/TimeHandle.txt","a+")
        startMeasure = time.time()                                                 
        # Unpack transaction
        # Get the payload and extract information.
        header = transaction.header
        print ("Transaction Payload is: {}".format(transaction.payload.decode()))
        # Example Payload
        # add-device@eyJleHBpcmVzIjogMTYzMDM4MjA5NS41ODQ0NTMzLCAicG
        # 9pbnQiOiAib2Y6MDAwMDAwMDAwMDAwMDAwMy8yIiwgIm5hbWUiOiAibm
        # 9kZTMyIiwgInZwbHMiOiAiUEhVWUVOIiwgInNhbHQiOiAiNmY2ZWMyIiw
        # gIm1hYyI6ICI3QTpBMTozQjowMTo3OTo1NSJ9NMNGxjLReaCAjx-SkjZG
        # sQ-5234VCZH3nT_YJEtnKCo=@{'point': 'of:0000000000000003/2',
        #  'vpls': 'PHUYEN', 'name': 'node32', 'mac': '7A:A1:3B:01:7
        # 9:55'}

        # Split by '@' to get sub-element
        payload_list = transaction.payload.decode().split("@")
        # Example Payload List is
        # ['add-device', 'eyJleHBpcmVzIjogMTYzMDM4MjA5NS41ODQ0NTMzLCAicG9
        # pbnQiOiAib2Y6MDAwMDAwMDAwMDAwMDAwMy8yIiwgIm5hbWUiOiAibm9kZTMyIi
        # wgInZwbHMiOiAiUEhVWUVOIiwgInNhbHQiOiAiNmY2ZWMyIiwgIm1hYyI6ICI3Q
        # TpBMTozQjowMTo3OTo1NSJ9NMNGxjLReaCAjx-SkjZGsQ-5234VCZH3nT_YJEtn
        # KCo=', "{'point': 'of:0000000000000003/2', 'vpls': 'PHUYEN', 'n
        # ame': 'node32', 'mac': '7A:A1:3B:01:79:55'}"]

        command = payload_list[0] #string
        # Token generated from Client
        token = payload_list[1] #string
        data = payload_list[2] #JSON

        # Get the public key sent from the client.
        from_key = header.signer_public_key

        # Perform the command.
        LOGGER.info("Command = "+ command)

        if command == "register":
            self._register(context, token, data, from_key)
        elif command == "model-request":
            self._model_request(context, token, data, from_key)
        elif command == "model-verify":
            self._model_verify(context, token, data, from_key)
        elif command == "task-assign":
            self._task_assign(context, token, data, from_key)
        else:
            LOGGER.info("Unhandled action. " +
                "Command should be register, model-request, or task-assign")
        stopMeasure = time.time()
        file.write("{}\t{}\n".format(command, str(stopMeasure-startMeasure)))
        file.close()

    def _register(self, context, token, data, from_key):
        node_address = self._get_master_address(from_key)
        LOGGER.info('Got Registration from {} has address {} '.format(
            from_key, node_address))

        current_entry = context.get_state([node_address])
        if current_entry == []:
            if (_valid_token(token) == True):
                LOGGER.info('Creating new node {} '.format(from_key))
                dataList = []
                # "data" variable contain information about node (name, entrypoint, mac, vpls)
                # Split subdata in "data" variable
                # Replace single-quote in "data" to double-quote
                data = data.replace("\'","\"")
                # After that, convert data from string to JSON format.
                json_data = json.loads(data)

                # Do something with json_data
                # In register case, i add a new key-value to json_data before store it
                json_data['token'] = token

                #Generate JSON data to store at entry point
                json_set_to_store = json_data
                json_data_to_store = json.dumps(json_set_to_store)
                dataList.append(json_data_to_store)
                #Store data to BlockChain
                state_data = str(dataList).encode('utf-8')
                addresses = context.set_state({node_address: state_data})

                if len(addresses) < 1:
                    raise InternalError("State Error")
            else:
                raise InvalidTransaction("Token has expired or another problem with token. Try again")
        else:
        
            raise InvalidTransaction("This node have registered with BlockChain. Transaction Register is invalid")
        
        
    def _model_request(self, context, token, data, from_key):
        node_address = self._get_master_address(from_key)
        LOGGER.info('Got a Model Request from {} at address'.format(
            from_key, node_address))
        
        current_entry = context.get_state([node_address])
        # Check entrypoint at master_address
        if current_entry != []:
            # Decode data from current_entry[0]. It's type is "bytes"
            # Convert from bytes to an array of JSON
            dataList = ast.literal_eval(current_entry[0].data.decode('utf-8'))
            tokenOnStateData = json.loads(dataList[0])['token']
            if ((_valid_token(token) == True) & (token==tokenOnStateData)):
                # "data" variable contain information about node (name, entrypoint, mac, vpls)
                # Replace single-quote in "data" to double-quote
                data = data.replace("\'","\"")
                json_data = json.loads(data)

                # Get sub-data
                nodeId = json_data['nodeId']
                taskCategory = json_data['taskCategory']
                globalModel = json_data['globalModel']
                evalCriteria = json_data['evaluation criteria']
                reputation = json_data['reputation']

                # Do something with sub-data

                #Generate JSON data to store at entry point
                json_set_to_store = json_data # Without any processing with json_data
                json_data_to_store = json.dumps(json_set_to_store)
                dataList.append(json_data_to_store)
                #Store data to BlockChain
                state_data = str(dataList).encode('utf-8')
                addresses = context.set_state({node_address: state_data})

                if len(addresses) < 1:
                    raise InternalError("State Error")
            else:
                raise InvalidTransaction("Token has expired or another problem with token. Try again or update token")
        else:
            raise InvalidTransaction("You must register first to have a token")

    def _model_verify(self, context, token, data, from_key):
        node_address = self._get_master_address(from_key)
        LOGGER.info('Got a Model Verification from {} at address'.format(
            from_key, node_address))
        current_entry = context.get_state([node_address])
        if current_entry != []:
            # Decode data from current_entry[0]. It's type is "bytes"
            # Convert from bytes to an array of JSON
            dataList = ast.literal_eval(current_entry[0].data.decode('utf-8'))
            tokenOnStateData = json.loads(dataList[0])['token']
            if ((_valid_token(token) == True) & (token==tokenOnStateData)):
                data = data.replace("\'","\"")
                json_data = json.loads(data)
                print("json_data: {}".format(json_data))

                # Get sub-data
                contributorID = json_data['contributorID']
                aggregatorID = json_data['aggregatorID']
                modelHash = json_data['modelHash']
                modelQuality = json_data['modelQuality']

                # Do something with sub-data

                #Generate JSON data to store at entry point
                json_set_to_store = json_data # Without any processing with json_data
                json_data_to_store = json.dumps(json_set_to_store)
                dataList.append(json_data_to_store)
                #Store data to BlockChain
                state_data = str(dataList).encode('utf-8')
                addresses = context.set_state({node_address: state_data})

                if len(addresses) < 1:
                    raise InternalError("State Error")
            else:
                raise InvalidTransaction("Token has expired or another problem with token. Try again or update token")
        else:
            raise InvalidTransaction("You must register first to have a token")

    def _task_assign(self, context, token, data, from_key):
        node_address = self._get_master_address(from_key)
        LOGGER.info('Got a Task Assigning from {} at address'.format(
            from_key, node_address))
        current_entry = context.get_state([node_address])
        if current_entry != []:
            # Decode data from current_entry[0]. It's type is "bytes"
            # Convert from bytes to an array of JSON
            dataList = ast.literal_eval(current_entry[0].data.decode('utf-8'))
            tokenOnStateData = json.loads(dataList[0])['token']
            if ((_valid_token(token) == True) & (token==tokenOnStateData)):
                data = data.replace("\'","\"")
                json_data = json.loads(data)
                print("json_data: {}".format(json_data))

                # Get sub-data
                modelRequester = json_data['model-requester']
                modelParticipants = json_data['model-participants']
                communicationRound = json_data['communication-round']

                # Do something with sub-data

                #Generate JSON data to store at entry point
                json_set_to_store = json_data # Without any processing with json_data
                json_data_to_store = json.dumps(json_set_to_store)
                dataList.append(json_data_to_store)
                #Store data to BlockChain
                state_data = str(dataList).encode('utf-8')
                addresses = context.set_state({node_address: state_data})

                if len(addresses) < 1:
                    raise InternalError("State Error")
            else:
                raise InvalidTransaction("Token has expired or another problem with token. Try again or update token")
        else:
            raise InvalidTransaction("You must register first to have a token")

    def _get_master_address(self, from_key):
        return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(from_key.encode('utf-8'))[0:64]


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

def main(argv):
    '''Entry-point function for the simplewallet transaction processor.'''
    verbose_level = 0
    setup_loggers(verbose_level=verbose_level)
    try:
        # Register the transaction handler and start it.
        processor = TransactionProcessor(url=sys.argv[1])

        handler = OceanTransactionHandler(sw_namespace)

        processor.add_handler(handler)

        processor.start()

    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

# FOR DEBUG: un-comment this code

# def main():
#     '''Entry-point function for the simplewallet transaction processor.'''
#     setup_loggers()
#     try:
#         # Register the transaction handler and start it.
#         processor = TransactionProcessor('tcp://172.21.0.2:4004')

#         handler = OceanTransactionHandler(sw_namespace)

#         processor.add_handler(handler)

#         processor.start()

#     except KeyboardInterrupt:
#         pass
#     except SystemExit as err:
#         raise err
#     except BaseException as err:
#         traceback.print_exc(file=sys.stderr)
#         sys.exit(1)
# main()