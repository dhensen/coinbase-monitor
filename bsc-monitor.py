import os
import time
import requests
from collections import defaultdict
from dataclasses import dataclass

TOKEN_ACCOUNT_BALANCE_ADDR = ("https://api.bscscan.com/api"
                              "?module=account"
                              "&action=tokenbalance"
                              "&contractaddress={contract_address}"
                              "&address={address}"
                              "&tag=latest"
                              "&apikey={api_key}")

API_KEY = os.getenv('BSC_API_KEY', 'M5X443JUB88HN79X5AEA6GIPSVIQ8ND6RB')

COINMARKETCAP_LOUD_ID = 12048
COINMARKETCAP_ZOO_ID = 11556

LOUD_CONTRACT_ADDR = '0x3d0E22387DdfE75D1AEa9D7108a4392922740B96'
ZOO_CONTRACT_ADDR = '0x7fFC1243232da3Ac001994208E2002816b57c669'
MY_BSC_WALLET_ADDR = '0xD7cE4dC62FD08Df073aD90A74dc678ba47D8e8D8'


@dataclass
class TokenData:
    contract_addr: str
    token_name: str


TOKEN_DATA = {
    COINMARKETCAP_ZOO_ID:
    TokenData(contract_addr=ZOO_CONTRACT_ADDR, token_name='ZOO'),
    COINMARKETCAP_LOUD_ID: TokenData(contract_addr=LOUD_CONTRACT_ADDR, token_name='LOUD'),
}


def get_coinmarkercap_listing(listing_id):
    response = requests.get(
        ' https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest',
        params={
            'id': listing_id,
            'convert': 'EUR'
        },
        headers={
            'Accept': 'application/json',
            'X-CMC_PRO_API_KEY': 'a1ddf0e6-47b4-4814-8028-0eff5effc446'
        })
    # "start=1&limit=5000&convert=USD"
    data = response.json()
    # print(data)

    try:
        return data['data'][str(listing_id)]
    except KeyError:
        raise RuntimeError('listing not found, maybe increase limit')


def get_token_account_balance(contract_address, address):
    response = requests.get(
        TOKEN_ACCOUNT_BALANCE_ADDR.format(contract_address=contract_address,
                                          address=address,
                                          api_key=API_KEY))

    data = response.json()
    # example response:
    # {'status': '1', 'message': 'OK', 'result': '272044663553674254747'}
    # print(data)

    amount = int(data['result']) / (10**18)
    # print(amount)
    return amount


class Reporter:
    def __init__(self) -> None:
        self.EUR_amount_started = {12048: 32.0, 11556: 23}
        self.EUR_current = {}

    def report(self):
        self.report_for_token(COINMARKETCAP_LOUD_ID)
        self.report_for_token(COINMARKETCAP_ZOO_ID)

    def get_token_data(self, token_id) -> TokenData:
        return TOKEN_DATA[token_id]

    def report_for_token(self, token_id):
        token_data = self.get_token_data(token_id)
        balance = get_token_account_balance(token_data.contract_addr, MY_BSC_WALLET_ADDR)
        coin_listing_data = get_coinmarkercap_listing(token_id)

        price = coin_listing_data['quote']['EUR']['price']
        last_updated = coin_listing_data['quote']['EUR']['last_updated']

        self.EUR_current[token_id] = balance * price
        if token_id not in self.EUR_amount_started:
            self.EUR_amount_started[token_id] = self.EUR_current[token_id]
        percentage_diff = 100 * (self.EUR_current[token_id] -
                                 self.EUR_amount_started[token_id]
                                 ) / self.EUR_amount_started[token_id]
        print(
            f'{token_data.token_name}: {balance} EUR: {balance * price} %: {percentage_diff}% [updated: {last_updated}] '
        )


if __name__ == "__main__":
    import traceback
    reporter = Reporter()
    while True:
        try:
            reporter.report()
        except KeyboardInterrupt:
            print('user stopped script')
            break
        except Exception as exc:
            traceback.print_exc()

        try:
            time.sleep(600)
        except KeyboardInterrupt:
            print('user stopped script')
            break
