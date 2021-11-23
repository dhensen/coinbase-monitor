import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone

import requests

from recorder import DataRecorder

API_BASE_URL = "https://api.snowtrace.io/api"
TOKEN_ACCOUNT_BALANCE_ADDR = (f"{API_BASE_URL}"
                              "?module=account"
                              "&action=tokenbalance"
                              "&contractaddress={contract_address}"
                              "&address={address}"
                              "&tag=latest"
                              "&apikey={api_key}")

API_KEY = os.getenv('SNOWTRACE_API_KEY', '3Y6G6A3JP7F45SZ1YNR4A9DBWTSNWBSB1T')

COINMARKETCAP_TIME_ID = 11585
# COINMARKETCAP_ZOO_ID = 11556

TIME_CONTRACT_ADDR = '0xb54f16fb19478766a268f172c9480f8da1a7c9c3'
MEMO_CONTRACT_ADDR = '0x136acd46c134e8269052c62a67042d6bdedde3c9'

MY_AVAX_WALLET_ADDR = '0xD7cE4dC62FD08Df073aD90A74dc678ba47D8e8D8'


@dataclass
class TokenData:
    contract_addr: str
    staked_contract_addr: str
    token_name: str


TOKEN_DATA = {
    # COINMARKETCAP_TIME_ID:
    # TokenData(contract_addr=TIME_CONTRACT_ADDR, token_name='TIME'),
    COINMARKETCAP_TIME_ID:
    TokenData(contract_addr=TIME_CONTRACT_ADDR,
              staked_contract_addr=MEMO_CONTRACT_ADDR,
              token_name='TIME'),
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

    amount = int(data['result']) / (
        10**9
    )  # TODO: exponent should be amount of decimals which differs per token
    # print(amount)

    return amount


class Reporter:
    def __init__(self) -> None:
        # TIME amount started: 0.126952242 is approx 1000 euro
        self.EUR_amount_started = {COINMARKETCAP_TIME_ID: 1000}
        self.EUR_current = {}
        self.recorder = DataRecorder('wonderland-time-staking-stats')

    def report(self):
        self.report_for_token(COINMARKETCAP_TIME_ID)
        # self.report_for_token(COINMARKETCAP_ZOO_ID)

    def get_token_data(self, token_id) -> TokenData:
        return TOKEN_DATA[token_id]

    def report_for_token(self, token_id):
        token_data = self.get_token_data(token_id)
        balance = get_token_account_balance(token_data.contract_addr,
                                            MY_AVAX_WALLET_ADDR)
        staked_balance = get_token_account_balance(
            token_data.staked_contract_addr, MY_AVAX_WALLET_ADDR)
        coin_listing_data = get_coinmarkercap_listing(token_id)

        price = coin_listing_data['quote']['EUR']['price']
        last_updated = coin_listing_data['quote']['EUR']['last_updated']

        self.EUR_current[token_id] = balance * price
        # print(self.EUR_current[token_id])
        if token_id not in self.EUR_amount_started:
            self.EUR_amount_started[token_id] = self.EUR_current[token_id]

        percentage_diff = 0
        if self.EUR_amount_started[token_id]:
            percentage_diff = 100 * (self.EUR_current[token_id] -
                                     self.EUR_amount_started[token_id]
                                     ) / self.EUR_amount_started[token_id]
        total_balance = balance + staked_balance
        print(
            f'{token_data.token_name}: {balance} EUR: {balance * price} %: {percentage_diff}% [updated: {last_updated}] '
        )

        now = datetime.now(tz=timezone.utc)
        now_str = now.isoformat()
        self.recorder.add_record(timestamp=now_str,
                                 token_name=token_data.token_name,
                                 eur_price=price,
                                 amount=balance,
                                 staked_amount=staked_balance,
                                 total_amount=total_balance,
                                 total_eur_amount=total_balance * price)


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
            time.sleep(60 * 60 * 1)  # every hour
        except KeyboardInterrupt:
            print('user stopped script')
            break
