"""Imports the requests library to make API calls to Etherscan.io API""" ""
import requests


def fetch_abi(contract_address: str, api_key: str) -> dict:
    """Fetches the ABI of a smart contract from Etherscan.io API"""
    api_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}"
    try:
        fetch = requests.get(api_endpoint, timeout=10)
        abi = fetch.json()["result"]
        print(abi)
        return abi
    except requests.exceptions.RequestException as error:
        raise type(error)(f"Error fetching ABI: {error}") from error


if __name__ == "__main__":
    fetch_abi("0x1234567891234567891234567891234567891234", "YourApiKeyToken")
