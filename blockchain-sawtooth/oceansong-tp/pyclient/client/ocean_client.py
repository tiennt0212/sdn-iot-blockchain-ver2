
import hashlib
import base64
import random
import requests
from requests.api import request
from requests.models import Response
import yaml
import tokenlib
import json
import array as arr
import time
import string

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

# The Transaction Family Name
FAMILY_NAME = 'oceansong'

def _hash(data):
    return hashlib.sha512(data).hexdigest()

def _generate_token(info):
    manager = tokenlib.TokenManager(secret="OCEANSONG")
    token = manager.make_token(info)
    return token;

class OceanClient(object):
    '''Client simple wallet class.

    This supports register and transfer data functions.
    '''

    def __init__(self, baseUrl, keyFile=None):
        '''Initialize the client class.

           This is mainly getting the key pair and computing the address.
        '''

        self._baseUrl = baseUrl

        if keyFile is None:
            self._signer = None
            return

        try:
            with open(keyFile) as fd:
                privateKeyStr = fd.read().strip()
        except OSError as err:
            raise Exception('Failed to read private key {}: {}'.format(
                keyFile, str(err)))

        try:
            privateKey = Secp256k1PrivateKey.from_hex(privateKeyStr)
        except ParseError as err:
            raise Exception('Failed to load private key: {}'.format(str(err)))

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(privateKey)

        self._publicKey = self._signer.get_public_key().as_hex()

        self._address = _hash(FAMILY_NAME.encode('utf-8'))[0:6] + \
            _hash(self._publicKey.encode('utf-8'))[0:64]

    # For each valid cli command in _cli.py file,
    # add methods to:
    # 1. Do any additional handling, if required
    # 2. Create a transaction and a batch
    # 3. Send to rest-api
    
    def _wait_for_commit(self, batchID=None, contentType=None):
        '''Send a REST command to the Validator via the REST API.'''

        if self._baseUrl.startswith("http://"):
            url = "{}/{}".format(self._baseUrl, "batch_statuses")
        else:
            url = "http://{}/{}".format(self._baseUrl, "batch_statuses")

        headers = {}

        if contentType is not None:
            headers['Content-Type'] = contentType
        
        params = {'id': batchID, 'wait':5}
        try:
            if batchID is not None:
                result = requests.get(url, params=params, headers=headers )

            if not result.ok:
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))

        except BaseException as err:
            raise Exception(err)

        return result.text

    def register(self, info):
        # I have infomation of that device, so i generate a token from it.
        token=_generate_token(info)
        
        # Next, i add token and info into an array "data"
        data=list((token, info))
        
        #Finally, send data to _wrap_and_send with command "add-device"
        #to notice that "I want to add this device to my network"
        responseRegister = self._wrap_and_send(
            "register",
            data)

        # Check success of this transaction.
        # If success, save token
        json_response = json.loads(responseRegister)
        link = json_response["link"]
        waitCommit = requests.get(link, params = {'wait':5})
        if ("COMMITTED" in str(waitCommit.content)):
            filepath = './data/.secret/token' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
            mode = 'w+'
            f = open(filepath, mode)
            f.write(token)
            f.close()
            return responseRegister
        
        return "Has some problem"

    def model_request(self, token, infoRequest):
        # Client send token and info to request model.
        # First step, append token and info
        data = list((token, infoRequest))
        
        return self._wrap_and_send(
            "model-request",
            data
        )

    def model_verify(self, token, infoVerify):
        # Calculate Hash from file
        sha512 = hashlib.sha512()
        BUF_SIZE = 65536 #64KB
        with open(infoVerify['modelFile'], 'rb') as f:
            fb = f.read(BUF_SIZE)
            while len(fb) > 0:
                sha512.update(fb)
                fb = f.read(BUF_SIZE)
        
        # Add new element modelHash
        infoVerify['modelHash'] = sha512.hexdigest()

        # Delete element 'modelFile'
        del infoVerify['modelFile']

        print(infoVerify)

        data = list((token, infoVerify))
        
        return self._wrap_and_send(
            "model-verify",
            data
        )

    def task_assign(self, token, infoTask):
        data = list((token, infoTask))
        
        return self._wrap_and_send(
            "task-assign",
            data
        )
    
    def _send_to_restapi(self,
                         suffix,
                         data=None,
                         contentType=None):
        '''Send a REST command to the Validator via the REST API.'''

        if self._baseUrl.startswith("http://"):
            url = "{}/{}".format(self._baseUrl, suffix)
        else:
            url = "http://{}/{}".format(self._baseUrl, suffix)

        headers = {}

        if contentType is not None:
            headers['Content-Type'] = contentType

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if not result.ok:
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))

        except BaseException as err:
            raise Exception(err)

        return result.text

    def _wrap_and_send(self,
                       action,
                       values):
        '''Create a transaction, then wrap it in a batch.     
                                                              
           Even single transactions must be wrapped into a batch.
        ''' 

        # Generate a csv utf-8 encoded string as payload
        rawPayload = action
        # print("Values is:", values)
        # print("Values 0 is:", values[0])
        # print("Values 1 is:", values[1])
        # i = 0
        for val in values:
            rawPayload = "@".join([rawPayload, str(val)])
            # i+=1

        # print("Loop {} time".format(i))

        payload = rawPayload.encode()

        # Construct the address where we'll store our state
        address = self._address
        inputAddressList = [address]
        outputAddressList = [address]

        # if "transfer" == action:
        #     toAddress = _hash(FAMILY_NAME.encode('utf-8'))[0:6] + \
        #     _hash(values[1].encode('utf-8'))[0:64]
        #     inputAddressList.append(toAddress)
        #     outputAddressList.append(toAddress)

        # Create a TransactionHeader
        header = TransactionHeader(
            signer_public_key=self._publicKey,
            family_name=FAMILY_NAME,
            family_version="1.0",
            inputs=inputAddressList,
            outputs=outputAddressList,
            dependencies=[],
            payload_sha512=_hash(payload),
            batcher_public_key=self._publicKey,
            nonce=random.random().hex().encode()
        ).SerializeToString()

        # Create a Transaction from the header and payload above
        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        transactionList = [transaction]

        # Create a BatchHeader from transactionList above
        header = BatchHeader(
            signer_public_key=self._publicKey,
            transaction_ids=[txn.header_signature for txn in transactionList]
        ).SerializeToString()

        #Create Batch using the BatchHeader and transactionList above
        batch = Batch(
            header=header,
            transactions=transactionList,
            header_signature=self._signer.sign(header))

        #Create a Batch List from Batch above
        batch_list = BatchList(batches=[batch])

        # Send batch_list to rest-api
        return self._send_to_restapi(
            "batches",
            batch_list.SerializeToString(),
            'application/octet-stream')

