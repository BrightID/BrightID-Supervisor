import config
config.WS_URL = ''
config.PRIVATE_KEY = ''

from eth_keys import keys
import unittest
import random
import run
import string
import time
import requests


class TestUpdate(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestUpdate, self).__init__(*args, **kwargs)
        self.IDS_AS_HEX = True
        self.GAS = 500 * 10**3
        self.GAS_PRICE = 20 * 10**9
        self.CONTRACT_ADDRESS = '0xADCFBa0937132565f87F2005489E9AFb2493baf4'
        self.CONTRACT_ABI = '[{"anonymous": false,"inputs": [{"indexed": false,"internalType": "contract IERC20","name": "supervisorToken","type": "address"},{"indexed": false,"internalType": "contract IERC20","name": "proposerToken","type": "address"}],"name": "MembershipTokensSet","type": "event"},{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "previousOwner","type": "address"},{"indexed": true,"internalType": "address","name": "newOwner","type": "address"}],"name": "OwnershipTransferred","type": "event"},{"inputs": [{"internalType": "bytes32","name": "context","type": "bytes32"},{"internalType": "address[]","name": "addrs","type": "address[]"},{"internalType": "uint8","name": "v","type": "uint8"},{"internalType": "bytes32","name": "r","type": "bytes32"},{"internalType": "bytes32","name": "s","type": "bytes32"}],"name": "propose","outputs": [],"stateMutability": "nonpayable","type": "function"},{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "addr","type": "address"}],"name": "Proposed","type": "event"},{"inputs": [],"name": "renounceOwnership","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "contract IERC20","name": "_supervisorToken","type": "address"},{"internalType": "contract IERC20","name": "_proposerToken","type": "address"}],"name": "setMembershipTokens","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint256","name": "_waiting","type": "uint256"},{"internalType": "uint256","name": "_timeout","type": "uint256"}],"name": "setTiming","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "start","outputs": [],"stateMutability": "nonpayable","type": "function"},{"anonymous": false,"inputs": [],"name": "Started","type": "event"},{"inputs": [],"name": "stop","outputs": [],"stateMutability": "nonpayable","type": "function"},{"anonymous": false,"inputs": [{"indexed": false,"internalType": "address","name": "stopper","type": "address"}],"name": "Stopped","type": "event"},{"anonymous": false,"inputs": [{"indexed": false,"internalType": "uint256","name": "waiting","type": "uint256"},{"indexed": false,"internalType": "uint256","name": "timeout","type": "uint256"}],"name": "TimingSet","type": "event"},{"inputs": [{"internalType": "address","name": "newOwner","type": "address"}],"name": "transferOwnership","outputs": [],"stateMutability": "nonpayable","type": "function"},{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "addr","type": "address"}],"name": "Verified","type": "event"},{"inputs": [{"internalType": "bytes32","name": "context","type": "bytes32"},{"internalType": "address[]","name": "addrs","type": "address[]"}],"name": "verify","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "address","name": "","type": "address"}],"name": "history","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "","type": "address"}],"name": "isRevoked","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "owner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "bytes32","name": "","type": "bytes32"}],"name": "proposals","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "proposerToken","outputs": [{"internalType": "contract IERC20","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "stopped","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "supervisorToken","outputs": [{"internalType": "contract IERC20","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "timeout","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "","type": "address"}],"name": "verifications","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "waiting","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"}]'
        self.VERIFIER_TOKEN = '0xF6b23cD9187C991f3768410329b767E9D53e17Ce'
        # this account should have a supervisor token and be the owner of the contract
        self.PRIVATE_KEY = 'EEBED6AE74B73BE44F4706222344E1D90363F64DA2C31B58B29F7A39EB6BFB43'
        self.CONTEXT = ''.join(random.choices(string.ascii_uppercase, k=5))
        self.CONTEXT_ID = run.w3.eth.account.create(
            'SIFTALFJAFJMOHSEN').address.lower()
        self.CONTEXT_ID_2 = run.w3.eth.account.create(
            'SIFTALFJAFJMOHSEN').address.lower()
        self.USER = 'v7vS3jEqXazNUWj-5QXmrBL8x5XCp3EksF7uVGlijll'
        self.variables = run.db.collection('variables')
        self.users = run.db.collection('users')
        self.contexts = run.db.collection('contexts')
        self.sponsorships = run.db.collection('sponsorships')
        self.verifications = run.db.collection('verifications')
        self.contract = run.w3.eth.contract(
            address=self.CONTRACT_ADDRESS,
            abi=self.CONTRACT_ABI)
        self.context = {
            '_key': self.CONTEXT,
            'ethName': self.CONTEXT,
            'collection': self.CONTEXT,
            'verification': self.CONTEXT,
            'contractAddress': self.CONTRACT_ADDRESS,
            'totalSponsorships': 2,
            'idsAsHex': self.IDS_AS_HEX
        }

    def setUp(self):
        try:
            self.DB_LB = self.variables.get('LAST_PROPOSE_LOG')['value']
        except:
            self.DB_LB = run.w3.eth.getBlock('latest').number - 1
            self.variables.insert({
                '_key': 'LAST_PROPOSE_LOG',
                'value': self.DB_LB
            })
        self.contexts.insert(self.context)

        self.users.insert({
            '_key': self.USER
        })

        self.verifications.insert({
            'name': self.CONTEXT,
            'user': self.USER,
            'timestamp': time.time()
        })

        self.context_collection = run.db.create_collection(self.CONTEXT)
        self.context_collection.insert({
            'user': self.USER,
            'contextId': self.CONTEXT_ID,
            'timestamp': int(time.time())
        })

        self.sponsorships.insert({
            '_from': 'users/{0}'.format(self.USER),
            '_to': 'contexts/{0}'.format(self.CONTEXT),
        })

    def tearDown(self):
        time.sleep(30)
        try:
            self.contexts.delete(self.CONTEXT)
        except:
            pass
        try:
            self.users.delete(self.USER)
        except:
            pass
        try:
            run.db.delete_collection(self.CONTEXT)
        except:
            pass
        try:
            r = self.sponsorships.find(
                {'_from': 'users/{}'.format(self.USER)}).batch()[0]
            self.sponsorships.delete(r['_key'])
        except:
            pass
        try:
            r = self.verifications.find(
                {'name': '{}'.format(self.CONTEXT)}).batch()[0]
            self.verifications.delete(r['_key'])
        except:
            pass
        self.variables.update({
            '_key': 'LAST_PROPOSE_LOG',
            'value': self.DB_LB
        })
        self.start()

    def priv2addr(self, private_key):
        pk = keys.PrivateKey(bytes.fromhex(private_key))
        return pk.public_key.to_checksum_address()

    def send_transaction(self, func):
        transaction = func.buildTransaction({
            'nonce': run.w3.eth.getTransactionCount(
                self.priv2addr(self.PRIVATE_KEY)),
            'from': self.priv2addr(self.PRIVATE_KEY),
            'value': 0,
            'gas': self.GAS,
            'gasPrice': self.GAS_PRICE
        })
        signed = run.w3.eth.account.sign_transaction(
            transaction, self.PRIVATE_KEY)
        raw_transaction = signed.rawTransaction.hex()
        tx_hash = run.w3.eth.sendRawTransaction(raw_transaction).hex()
        rec = run.w3.eth.waitForTransactionReceipt(tx_hash)
        return {'status': rec['status'], 'tx_hash': tx_hash}

    def start(self):
        print("\nstart the contract again")
        stopped = self.contract.functions.stopped().call()
        if stopped:
            func = self.contract.functions.start()
            self.send_transaction(func)

    def test_supervisor(self):
        print('submitting a proposal')
        fb = run.w3.eth.getBlock('latest').number - 1
        req = 'http://localhost:8529/brightid5/verifications/{0}/{1}?signed=eth'.format(
            self.CONTEXT, self.CONTEXT_ID)
        res = requests.get(req).json()['data']
        func = self.contract.functions.propose(
            bytes(self.CONTEXT, 'ascii'),
            [run.w3.toChecksumAddress(self.CONTEXT_ID)],
            res['sig']['v'],
            '0x' + res['sig']['r'],
            '0x' + res['sig']['s']
        )
        print(self.send_transaction(func))
        # waiting
        time.sleep(30)
        print('\nrun check_propose_requests')
        tb = run.w3.eth.getBlock('latest').number
        run.check_propose_requests(fb, tb)
        stopped = self.contract.functions.stopped().call()
        self.assertEqual(stopped, False)

        print('make the user unsponsored')
        r = self.sponsorships.find(
            {'_from': 'users/{}'.format(self.USER)}).batch()[0]
        self.sponsorships.delete(r['_key'])
        print('run check_propose_requests again')
        run.check_propose_requests(fb, tb)
        stopped = self.contract.functions.stopped().call()
        self.assertEqual(stopped, True)
        self.start()

        print('make the user unverified')
        self.sponsorships.insert({
            '_from': 'users/{0}'.format(self.USER),
            '_to': 'contexts/{0}'.format(self.CONTEXT),
        })
        r = self.verifications.find(
            {'name': '{}'.format(self.CONTEXT)}).batch()[0]
        self.verifications.delete(r['_key'])
        print('run check_propose_requests again')
        run.check_propose_requests(fb, tb)
        stopped = self.contract.functions.stopped().call()
        self.assertEqual(stopped, True)
        self.start()

        print('insert a context id with lower timestamp in the context')
        self.users.update({
            '_key': self.USER,
            'verifications': [self.CONTEXT],
        })
        self.context_collection.insert({
            'user': self.USER,
            'contextId': self.CONTEXT_ID_2,
            'timestamp': 1
        })
        print('run check_propose_requests again')
        run.check_propose_requests(fb, tb)
        stopped = self.contract.functions.stopped().call()
        self.assertEqual(stopped, True)
        self.start()

        print('remove the proposed context id')
        r = self.context_collection.find(
            {'contextId': self.CONTEXT_ID}).batch()[0]
        self.context_collection.delete(r['_key'])
        print('run check_propose_requests again')
        run.check_propose_requests(fb, tb)
        stopped = self.contract.functions.stopped().call()
        self.assertEqual(stopped, True)


if __name__ == '__main__':
    unittest.main()
