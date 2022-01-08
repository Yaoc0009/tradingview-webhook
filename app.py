import json, config, ccxt
from flask import Flask, request
app = Flask(__name__)
creds = config.CREDENTIALS

# get the ftx exchange instance
exchange_id = 'ftx'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': creds['api_key'],
    'secret': creds['secret'],
    "headers": {
        "FTX-SUBACCOUNT": creds['account']
    }
})

# create function to create order via single json request
def order(req):
    data = req.get_json()
    try:
        #create buy market order
        order = exchange.create_order(data['symbol'], data['type'], data['side'], data['amount'], data['price'], data['params'])
    except Exception as e:
        return {'error': str(e)}
    return order

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/webhook", methods=['POST'])
def webhook():
    # print(request.data)
    data = json.loads(request.data)

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error", 
            "message": "invalid passphrase"
        }
    return {
        "code": "success",
        "message": data
    }