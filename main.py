from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import requests
import json
import urllib3

## run cd C:\Users\jefft\Downloads\clientportal.gw
## then bin\run.bat root\conf.yaml
## after that go to localhost:5000 and login
## re-authentication must occur once every day

# list of all market data fields: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#market-data-fields

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = "https://localhost:5000/v1/api/"

def confirm_status():
    endpoint = 'iserver/auth/status'

    auth_req = requests.get(url=base_url+endpoint, verify=False)
    print(auth_req)
    print(auth_req.text)

confirm_status()

def get_contract_data():
    endpoint = "iserver/secdef/search"
    params = {
        'symbol': 'AAPL', # stock symbol
        'secType': "STK", # STK stands for stock
        'name': False # if True, symbol searches for company name instead of stock symbol
    }
    request_url = base_url + endpoint
    conid_req = requests.post(url=request_url, verify=False, params=params)

    conid_json = json.dumps(conid_req.json()[0], indent=2) ## 0 index is for NASDAQ
    print(conid_json)

get_contract_data()

def get_market_data():
    endpoint = "iserver/marketdata/snapshot"
    conids = '265598' #AAPL
    fields = '55,31'
    params = {
        'conids': conids,
        'fields': fields
    }

    request_url = base_url + endpoint
    market_data_req = requests.get(url=request_url, params=params, verify=False)

    print(market_data_req)
    print(market_data_req.text)

get_market_data()