from server import *

def test_crypto_API():
    # return jsonify({"message": request.json.get('currency')})
    actual = crypto.getCrypto("bitcoin", "usd")

    
    assert actual['bitcoin']['usd'] != None # This is the expected response from the API


test_crypto_API()
