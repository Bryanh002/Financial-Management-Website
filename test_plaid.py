from server import *

#test that link token is a valid sandbox link token
def test_plaid_link_token_valid():
    actual = (plaid_client.create_link_token()["link_token"])[:12]
    expected = "link-sandbox"
    assert actual == expected

#test that link token is a valid length
def test_plaid_link_token_length():
    actual = len(plaid_client.create_link_token()["link_token"])
    expected = 49
    assert actual == expected


