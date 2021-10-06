# Import dependencies
import subprocess
import json
from pprint import pprint
from dotenv import load_dotenv
from eth_account.account import Account
import os

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")
print(mnemonic)

# Import constants.py and necessary functions from bit and web3
from constants import *
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3, middleware, Account
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy


# setting up Web3, PoA middleware, and gas price strategies 
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.set_gas_price_strategy(medium_gas_price_strategy)


 
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = f'php hd-wallet-derive.php -g --mnemonic="{mnemonic}" --coins="{coin}" --numderive={numderive} --format=json'
    print (command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {
    ETH: derive_wallets(mnemonic,ETH, 3),
    BTCTEST: derive_wallets(mnemonic,BTCTEST, 3)
}

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)

    if coin == BTC:
        return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether")
        gasEstimate =w3.eth.estimatedGas({"to":to, "from":account, "amount":value})
        return{
            "to":to,
            "from":account,
            "gas":gasEstimate,
            "gas price":w3.eth.generate_gas_price(),
            "nonce":w3.eth.getTransactionCount(account),
            "chainID":w3.eth.chain_id
        }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount,BTC)])


# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw = create_tx(coin, account.address, to, amount)
        signed = account.signTransaction(raw)
        return w3.eth.send_raw_transaction(signed.raw)
    if coin == BTCTEST:
        raw = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw)
        return NetworkAPI.broadcast_tx_testnet(signed)
    

pprint(coins)
