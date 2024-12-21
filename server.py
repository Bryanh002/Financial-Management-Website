# source /Users/tnappy/node_projects/quickstart/python/bin/activate
# Read env vars from .env file
import os
import datetime as dt
import time
import json
import requests
from typing import List, Dict


from flask import Flask, request, jsonify
from flask_cors import CORS

# plaid product imports
import plaid
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.investments_transactions_get_request_options import InvestmentsTransactionsGetRequestOptions
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.api import plaid_api


app = Flask(__name__)
CORS(app, origins=["*"])

# plaid class for accessing personal bank information
class PlaidApi:
    def __init__(self):
        self.access_token = None
        self.client = None
        self.configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={'clientId': "65f4cb4f80911b001bb3d8a3",'secret': "203f364603d192dacdb16bb52c691e",'plaidVersion': '2020-09-14'})
    
    #configures plaid client
    def configClient(self):
        self.client = plaid_api.PlaidApi(plaid.ApiClient(self.configuration))
    
    #creates the link token to allow user authentication
    def create_link_token(self):
        #create requests to create a link token that meets the apps capabilities
        request = LinkTokenCreateRequest(
            products=[Products("investments"),Products("transactions")],
            client_name="Finance App",
            country_codes=[CountryCode("US"), CountryCode("CA")],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id=str(time.time()))
        )
        response = self.client.link_token_create(request)
        return response.to_dict()

    #exchange public token for access token to prove user authentication
    def exchange_public_token(self, public_token):
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = self.client.item_public_token_exchange(exchange_request)
        self.access_token = exchange_response['access_token']
        return True

    #returns users accounts and their balances
    def get_balance(self):
        request = AccountsBalanceGetRequest(access_token=self.access_token)
        response = self.client.accounts_balance_get(request)
        return response.to_dict()["accounts"]

    #get users investments 
    def get_holdings(self):
        request = InvestmentsHoldingsGetRequest(access_token=self.access_token)
        response = self.client.investments_holdings_get(request)
        return response.to_dict()

    #get user investment transactions from the last two years
    def get_investments_transactions(self, start_date, end_date):
        request = InvestmentsTransactionsGetRequest(
            access_token=self.access_token,
            start_date=start_date,
            end_date=end_date,
            options=InvestmentsTransactionsGetRequestOptions()
        )
        response = self.client.investments_transactions_get(request)
        return response.to_dict()
    
#create and configure plaid object
plaid_client = PlaidApi()
plaid_client.configClient()

#create routes to create, exchange, and user bank info
@app.route('/plaid/create_link_token', methods=['POST'])
def create_link_token_route():
    return jsonify(plaid_client.create_link_token())

@app.route('/plaid/set_access_token', methods=['POST'])
def set_access_token_route():
    public_token = request.form['public_token']
    return jsonify(plaid_client.exchange_public_token(public_token))

@app.route('/plaid/balance', methods=['GET'])
def balance_route():
    return jsonify(plaid_client.get_balance())

@app.route('/plaid/holdings', methods=['GET'])
def holdings_route():
    return jsonify(plaid_client.get_holdings())

@app.route('/plaid/investments_transactions', methods=['GET'])
def investments_transactions_route():
    return jsonify(plaid_client.get_investments_transactions(dt.date(2022, 3, 18), dt.date(2024, 3, 17)))

#Recieve Stock Information
#Stock Class

class StockHandling:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_stock_data(self, StockSymbol):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={StockSymbol}&apikey={self.api_key}"
        r = requests.get(url)
        data = r.json()

        processed_data = []
        for timestamp, values in data["Time Series (Daily)"].items():
            high = values["2. high"]
            low = values["3. low"]
            processed_data.append({
                "date": (timestamp),
                "high": (high),
                "low": (low)
            })

        return processed_data

stock_manager = StockHandling(api_key='CZVOZ53BI8F8RAW1')

@app.route('/stocks', methods=['GET','POST'])
def get_stocks():

    StockSymbol = request.json['symbol']
    processed_data = stock_manager.get_stock_data(StockSymbol)

    return jsonify(processed_data)

#-----------News API Call START-----------#
#API Token (under Nick's email): Beyvdl3NmzIFfMxS3wi84TTNz9gCryUXRqZ8ku8d
#API Token (backup): XMTEaeSw37w4lO83tEVcSC76YNUcXezQ1yZAt0tH
class newsAPI:
    def getNews(self):
        self.url = f'https://api.marketaux.com/v1/news/all?api_token=Beyvdl3NmzIFfMxS3wi84TTNz9gCryUXRqZ8ku8d&limit=3&industries=Technology&countries=us&language=en'
        
        callApi = requests.get(self.url) #Call API to get data
        dataFromApi = callApi.json()     #Convert to JSON FILE
        
        newsArticles = [] #A list to hold the articles from the news API
        
        if dataFromApi['data'] == []: #['data'] is a list; Check if the list is empty (no articles found)
            print("No articles found")
        else:
            for articles in dataFromApi['data']:     #'articles' is a dictionary within the list "data"
                newsArticles.append({'title' : articles['title'], 
                    'description' : articles['description'],
                    'url' : articles['url']}
                )

        return (newsArticles)

@app.route('/news', methods=['GET'])
def gettingNewsArticles():
    getNewsArticles = newsAPI()
    return jsonify(getNewsArticles.getNews())
#-----------News API Call END----------#

# Class for the Currency Exchange
class CurrencyExchange:
    def __init__(self, api_key: str, base_currency: str = 'USD'):
        self.__api_key = api_key
        self.__url = f'https://v6.exchangerate-api.com/v6/{self.__api_key}/latest/{base_currency}'

    def getCurrency(self, user_input):
        response = requests.get(self.__url)
        data = response.json()
        exchange_rate = data['conversion_rates'][user_input]
        # return jsonify([{currency: rate} for currency, rate in exchange_rate.item()])
        return (exchange_rate)

api_key = 'f0362b71add9afc93d0b5d6c'
exchange = CurrencyExchange(api_key)

@app.route('/currency', methods=['POST'])
def getCurrency():
    user_input = request.json.get('currency')
    return jsonify(exchange.getCurrency(user_input))


########## CRYPTO API SECTION ##########

crypto_api_key ='CG-tbkrxSEsGY6NBzZZgtPD1Fd1'

# Class for the Currency Exchange
class CryptoExchange:
    def __init__(self):
        
        print("Initiate CryptoExchange Class")

    def getCrypto(self, coin, currency):
        headers = {"api-key": crypto_api_key}
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies={currency}&include_market_cap=true'
        response = requests.get(url, headers=headers)
        return response.json()

crypto = CryptoExchange()

# CRYPTO POST API REQUEST
# Header must be JSON 
# Body must contain two values
# coin: "bitcoin", or other string values for coins
# currency: "usd", "eur", "cad", etc.
@app.route('/crypto', methods=['POST'])
def getCrypto():
    # return jsonify({"message": request.json.get('currency')})
    user_coin = request.json.get('coin')
    user_currency = request.json.get('currency')
    return crypto.getCrypto(user_coin, user_currency)

# CRYPTO GET API REQUEST
# For testing purposes
# Returns the current price of bitcoin in USD
@app.route('/crypto/bitcoin', methods=['GET'])
def getBitcoinUSD():
    # return jsonify({"message": request.json.get('currency')})
    return crypto.getCrypto("bitcoin", "usd")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 

