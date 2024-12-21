from server import *

def test_currency():
    exchange = CurrencyExchange(api_key)
    exchange_rate = exchange.getCurrency('CAD')

    assert type(exchange_rate) == float