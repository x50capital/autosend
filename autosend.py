import json
import time
import logging
import web3
from web3 import Web3
from eth_account import Account

logging.basicConfig(filename="autosend.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE = "config.json"
def load_config(filename=CONFIG_FILE):
    with open(filename, "r") as file:
        return json.load(file)

config = load_config()
LINEA_RPC_URL = config["rpc_url"]
w3 = Web3(Web3.HTTPProvider(LINEA_RPC_URL))

def load_wallets(filename="wallets.json"):
    with open(filename, "r") as file:
        return json.load(file)

ERC20_ABI = '''[
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},
    {"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}
]'''

def get_token_balance(wallet_address, token_address):
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    return token_contract.functions.balanceOf(wallet_address).call()

def send_tokens(private_key, token_address, recipient, amount):
    sender = Account.from_key(private_key).address
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
    nonce = w3.eth.get_transaction_count(sender)
    gas_price = w3.eth.gas_price * config["gas_price_multiplier"]
    txn = token_contract.functions.transfer(recipient, amount).build_transaction({
        "from": sender,
        "gas": config["gas_limit"],
        "gasPrice": gas_price,
        "nonce": nonce
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    logging.info(f"Transaction sent: {tx_hash} | From: {sender} | To: {recipient} | Amount: {amount} | Token: {token_address}")
    return w3.to_hex(tx_hash)

if __name__ == "__main__":
    wallets = load_wallets()
    monitored_tokens = config["monitored_tokens"]
    previous_balances = {}

    while True:
        for wallet in wallets:
            private_key = wallet["private_key"]
            sender = Account.from_key(private_key).address
            recipient = wallet["recipient"]

            for token in monitored_tokens:
                balance = get_token_balance(sender, token)
                if sender not in previous_balances:
                    previous_balances[sender] = {}
                previous_balance = previous_balances[sender].get(token, 0)

                if balance > previous_balance:
                    amount_to_send = balance - previous_balance
                    tx_hash = send_tokens(private_key, token, recipient, amount_to_send)
                    print(f"Sent {amount_to_send} of {token} from {sender} to {recipient}. Tx: {tx_hash}")
                    logging.info(f"Sent {amount_to_send} of {token} from {sender} to {recipient}. Tx: {tx_hash}")

                previous_balances[sender][token] = balance

        time.sleep(30)
