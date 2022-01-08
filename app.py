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
def order(symbol, side, amount, type='market', price=None, params={}):
   
    try:
        #create buy market order
        print("sending order, {} - {} {} {}".format(type, side, amount, symbol))
        order = exchange.create_order(symbol=symbol, side=side, amount=amount, type=type, price=price, params=params)
    except Exception as e:
        print("error: {}".format(e))
        return False
    return order

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/webhook", methods=['POST'])
def webhook():
    # print(request.data)
    data = json.loads(request.data)

    # simple alert authentication
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error", 
            "message": "invalid passphrase"
        }

    # prevent alerts from other exchanges
    if data['exchange'] != 'FTX':
        return {
            "code": "error", 
            "message": "invalid exchange"
        }

    symbol = str(data['ticker']).upper()
    if 'PERP' in symbol:
        symbol = symbol.replace('PERP', '/USD:USD')
    elif 'USD' in symbol:
        symbol = symbol.replace('USD', '/USD')
    else:
        return False

    side = data['strategy']['order_action']
    amount = data['strategy']['order_contracts']

    print(symbol, amount, side)
    order_response = order(symbol, side, amount)

    if order_response:
        return {
            "code": "success",
            "message": "order executed",
            "info": order_response
        }
    else:
        print('order failed')
        return {
            "code": "error",
            "message": "order failed"
        }