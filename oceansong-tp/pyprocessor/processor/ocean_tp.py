import traceback
import sys
import hashlib
import logging
import tokenlib
import json
import ast
import requests
from requests.auth import HTTPBasicAuth

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

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
        # Unpack transaction
        # Get the payload and extract information.
        header = transaction.header
        # print ("Transaction Payload is: {}".format(transaction.payload.decode()))
        payload_list = transaction.payload.decode().split("@")
        # print ("Payload list is: {}".format(payload_list))
        command = payload_list[0] #string
        # print ("Command is: {}".format(command))
        token = payload_list[1] #string
        # print ("Token is: {}".format(token))
        data = payload_list[2] #JSON
        # print ("Data is: {}".format(data))

        # Get the public key sent from the client.
        from_key = header.signer_public_key

        # Perform the command.
        LOGGER.info("Command = "+ command)

        if command == "add-device":
            self._add_device(context, token, data, from_key)
        else:
            LOGGER.info("Unhandled action. " +
                "Command should be add-device or expulse-device")

    def _add_device(self, context, token, data, from_key):
        master_address = self._get_master_address(from_key)
        LOGGER.info('Got the key {} and the master address {} '.format(
            from_key, master_address))
        
        if (_valid_token(token) == False):
            raise InternalError("Invalid token")
            
        current_entry = context.get_state([master_address])
        if current_entry == []:
            LOGGER.info('No previous Master, creating new Master {} '.format(from_key))
            dataList = []
        else:
            # dataList = current_entry.decode('utf-8')
            dataList = ast.literal_eval(current_entry[0].data.decode('utf-8'))
        
        #Split subdata in "data" variable
        # Replace single-quote in "data" to double-quote
        data = data.replace("\'","\"")
        # print(data)
        json_data = json.loads(data)
        # print(json_data)
        name = json_data['name']
        # print ("Name is: {}".format(name))
        point = json_data['point']
        # print ("Point is: {}".format(point))
        mac = json_data['mac']
        # print ("Mac is: {}".format(mac))
        vpls = json_data['vpls']
        
        #From this data, use ONOS API in order to add this host to VLAN
        # json_set = {"interfaces":[{"name": name,"connect point": point,"mac": mac}]}
        json_set = {"interfaces":[{"name": name,"connect point": point}]}
        json_data = json.dumps(json_set) #Dumps to string
        
        print(json_data)
        url = 'http://172.20.0.7:8181/onos/vpls/vpls/interfaces/' + vpls #API URL
        headers = {'Content-Type':'application/json' , 'Accept':'application/json'}
        LOGGER.info('Connecting to Onos REST-API')
        response = requests.post(url, data=json_data, auth=('onos', 'rocks'), headers=headers)
        LOGGER.info('Status code return {}'.format(response.status_code))
        
        if(response.status_code <250):
            #Generate JSON data to store at entry point
            json_set_to_store = {"name":name ,"point":point ,"mac": mac,"token":token}
            json_data_to_store = json.dumps(json_set_to_store)
            dataList.append(json_data_to_store)
            #Store data to BlockChain
            state_data = str(dataList).encode('utf-8')
            addresses = context.set_state({master_address: state_data})
            if len(addresses) < 1:
                raise InternalError("State Error")
        else:
            raise InternalError('Error, please check your data information')
        

    def _get_master_address(self, from_key):
        return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(from_key.encode('utf-8'))[0:64]



def setup_loggers():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

def main(argv):
    '''Entry-point function for the simplewallet transaction processor.'''
    setup_loggers()
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
