import ccxt
import os

exchange = ccxt.coinbase({
    'apiKey': os.getenv('COINBASE_API_KEY'),
    'secret': os.getenv('COINBASE_API_SECRET'),
    'enableRateLimit': True
})
markets = exchange.load_markets()

monitor_symbols = ['BTC/EUR', 'ZRX/EUR']

prices = {}



try:
    while True:
        # for wanted_symbol in monitor_symbols:
        #     ticker = exchange.fetch_ticker(wanted_symbol)
        #     # print(f'{wanted_symbol} {ticker["close"]}')

        balance = exchange.fetch_balance()

        total_nonzero = {k: v for k, v in balance['total'].items() if v != 0}
        # print(total_nonzero)
        for currency in total_nonzero.keys():
            eur_symbol = f'{currency}/EUR'
            if eur_symbol in exchange.markets.keys():
                ticker = exchange.fetch_ticker(eur_symbol)
                # print(f'{eur_symbol} {ticker["close"]}')
                prices[eur_symbol] = ticker["close"]

        if prices:
            total_eur = 0
            for currency, amount in total_nonzero.items():
                price = prices[f'{currency}/EUR']
                eur_value = amount * price
                print(f'{currency}={eur_value} EUR @ {price} EUR')
                total_eur += eur_value
            print(f'total={total_eur} EUR')


except KeyboardInterrupt as exc:
    print('bye')
