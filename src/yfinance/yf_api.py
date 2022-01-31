import requests

url = "https://yfapi.net/v6/finance/quote"

querystring = {"symbols":"AAPL,BTC-USD,EURUSD=X"}

headers = {
    'x-api-key': "EtSo3o9TpK9FEirwkSbK19BqCxfUEY139X6kkfew"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)