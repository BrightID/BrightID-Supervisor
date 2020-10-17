from web3.middleware import geth_poa_middleware
from arango import ArangoClient
from eth_keys import keys
from web3 import Web3
import config
import time

db = ArangoClient().db('_system')
w3 = Web3(Web3.WebsocketProvider(
    config.WS_URL, websocket_kwargs={'timeout': 60}))

if config.WS_URL.count('rinkeby') > 0 or config.WS_URL.count('idchain') > 0:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)


def priv2addr(private_key):
    pk = keys.PrivateKey(bytes.fromhex(private_key))
    return pk.public_key.to_checksum_address()


def send_transaction(func):
    transaction = func.buildTransaction({
        'nonce': w3.eth.getTransactionCount(priv2addr(config.PRIVATE_KEY)),
        'from': priv2addr(config.PRIVATE_KEY),
        'value': 0,
        'gas': config.GAS,
        'gasPrice': config.GAS_PRICE
    })
    signed = w3.eth.account.sign_transaction(transaction, config.PRIVATE_KEY)
    raw_transaction = signed.rawTransaction.hex()
    tx_hash = w3.eth.sendRawTransaction(raw_transaction).hex()
    rec = w3.eth.waitForTransactionReceipt(tx_hash)
    print('status: {0}, tx_hash: {1}\n'.format(rec['status'], tx_hash))
    return {'status': rec['status'], 'tx_hash': tx_hash}


def stop(contract):
    print("stop the contract because of the conflict")
    stopped = contract.functions.stopped().call()
    if not stopped:
        func = contract.functions.stop()
        send_transaction(func)


def check_propose_requests(fb, tb):
    contexts = db.collection('contexts').all().batch()
    for context in contexts:
        if 'contractAddress' not in context or not context.get('idsAsHex'):
            continue
        print('\ncontext: {}'.format(context['_key']))
        print('checking events from block {} to block {}'.format(fb, tb))
        context_contract = w3.eth.contract(
            address=context['contractAddress'],
            abi=config.STOPPABLE_CONTEXT_CONTRACT_ABI)
        proposeds = context_contract.events.Proposed.createFilter(
            fromBlock=fb, toBlock=tb, argument_filters=None
        ).get_all_entries()
        for proposed in proposeds:
            context_id = proposed['args']['addr'].lower()
            print('checking proposed request\tcontext_name: {0}, context_id: {1}'.format(
                context['_key'], context_id))

            tx_hash = proposed.get('transactionHash')
            tx = w3.eth.getTransaction(tx_hash)
            data = context_contract.decode_function_input(tx.get('input'))
            req_context_ids = [cid.lower() for cid in data[1].get('addrs')]

            c = db.collection(context['collection']).find(
                {'contextId': context_id})
            if c.empty():
                print('the context id not found')
                stop(context_contract)
                break

            _id = c.batch()[0]['user']
            c = db.collection('verifications').find({'user': _id, 'name': context['verification']})
            if c.empty():
                print('user can not be verified for this context')
                stop(context_contract)
                break

            c = db.collection('users').find({'_key': _id})
            user = c.batch()[0]
            c = db.collection('sponsorships').find(
                {'_from': 'users/{}'.format(user['_key'])})
            if c.empty():
                print('user is not sponsored')
                stop(context_contract)
                break

            c = db.collection(context['collection']).find(
                {'user': user['_key']})
            context_ids = [r['contextId'] for r in sorted(
                c.batch(), key=lambda i: i['timestamp'], reverse=True)]
            if context_ids[len(context_ids) - len(req_context_ids):] != req_context_ids:
                print('the context ids are not matched')
                stop(context_contract)
                break
            print('no confilict\n')
    return tb


if __name__ == '__main__':
    fb = w3.eth.getBlock('latest').number - (config.CONFIRMATION + 1)
    while True:
        tb = w3.eth.getBlock('latest').number - config.CONFIRMATION
        if not fb < tb:
            time.sleep(1)
            continue
        fb = check_propose_requests(fb, tb)
