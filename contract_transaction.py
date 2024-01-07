"""Library imports"""
import logging
import os
from web3 import Web3
from dotenv import load_dotenv
from abifetch import fetch_abi


# Configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
load_dotenv("general.env")

w3 = Web3(Web3.HTTPProvider(os.environ.get("INFURA_URL")))
logging.info("Connection to web3 node: %s", w3.is_connected())

MAX_PRIORITY_FEE_PER_GAS = 2
MAX_FEE_PER_GAS = 20
GAS_LIMIT = 70000

# Wallets
send_account = w3.eth.account.from_key(os.environ.get("METAMASK_WALLET1_PK"))
receive_account = w3.eth.account.from_key(os.environ.get("METAMASK_WALLET2_PK"))

# ABI fetch and initializing contract
while True:
    contract_address = str(input("Enter contract address: "))
    if contract_address.startswith("0x"):
        break

abi = fetch_abi(contract_address, os.environ.get("ETHERSCAN_APIKEY"))
contract = w3.eth.contract(address=contract_address, abi=abi)

# Display available functions
functions = contract.all_functions()
formatted_functions = {}
read_functions = []
write_functions = []

for func in functions:
    func_name = func.abi["name"]
    func_state_mutability = func.abi["stateMutability"]
    func_inputs = [func_type["type"] for func_type in func.abi["inputs"]]
    formatted_func = f"{func_name}({', '.join(func_inputs)})"

    if func_state_mutability == "view":
        read_functions.append(formatted_func)
    else:
        write_functions.append(formatted_func)

while True:
    if input("Display available functions? (y/n): ") == "y":
        print("Read Functions:")
        for i, func in enumerate(read_functions, 1):
            print(f"{i}. {func}")

        print("\nWrite Functions:")
        for i, func in enumerate(write_functions, 1):
            print(f"{i}. {func}")

        break
    else:
        pass


# Choose function
while True:
    choose_mutability = str(
        input("Would you like to run a read or write contract? (r/w): ")
    )
    if choose_mutability == "r":
        choose_function = int(input("Which function do you want to run?: "))
        variable_func = read_functions[choose_function - 1]
        break
    if choose_mutability == "w":
        choose_function = int(input("Which function do you want to run?: "))
        variable_func = write_functions[choose_function - 1]
        break

function_name = variable_func.split("(")[0]
function_inputs = variable_func.split("(")[1].strip(")").split(", ")

# Token Decimals and Symbol
decimals = contract.functions.decimals().call()
symbol = contract.functions.symbol().call()

# Input function arguments
if function_inputs[0] == "":
    pass
else:
    print(f"Function inputs: {function_inputs}")

function_arg = []

if function_inputs[0] == "":
    function_arg = []
elif (
    function_inputs[0] == "address"
    and function_inputs[1] == "address"
    and function_inputs[2] == "uint256"
):
    function_arg.append(str(input("Enter address (1): ")))
    function_arg.append(str(input("Enter address (2): ")))
    function_arg.append(
        int(float(input("Enter amount(in {symbol}): ")) * (10**decimals))
    )
elif function_inputs[0] == "address" and function_inputs[1] == "address":
    function_arg.append(str(input("Enter address (1): ")))
    function_arg.append(str(input("Enter address (2): ")))
elif function_inputs[0] == "address" and function_inputs[1] == "uint256":
    function_arg.append(str(input("Enter address: ")))
    function_arg.append(
        int(float(input(f"Enter amount(in {symbol}): ")) * (10**decimals))
    )
elif function_inputs[0] == "address":
    function_arg.append(str(input("Enter address: ")))
elif function_arg[0] == "uint256":
    function_arg.append(
        int(float(input("Enter amount(in {symbol}): ")) * (10**decimals))
    )
else:
    pass

# Build txn
if choose_mutability == "r":
    functionR = getattr(contract.functions, function_name)
    print(functionR(*function_arg).call())
else:
    functionW = getattr(contract.functions, function_name)
    txn = functionW(*function_arg).build_transaction(
        {
            "chainId": 1,
            "gas": GAS_LIMIT,
            "maxFeePerGas": w3.to_wei(f"{MAX_FEE_PER_GAS}", "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(f"{MAX_PRIORITY_FEE_PER_GAS}", "gwei"),
            "nonce": w3.eth.get_transaction_count(send_account.address),
        }
    )

    # Sign and send
    if input("send the transaction: y/n?\n") == "y":
        signed_tx = w3.eth.account.sign_transaction(txn, private_key=send_account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logging.info("Txn Hash: %s", tx_hash.hex())
    else:
        logging.info("Transaction aborted")
