import pytest
from server import StockHandling 



def test_get_stock_data():
    # You would put your actual API key here for the test
    api_key = "CZVOZ53BI8F8RAW1"
    stock_handling = StockHandling(api_key)

    # Make the actual API call
    result = stock_handling.get_stock_data("IBM")  # Use a common stock symbol for testing
    
    # Assert that we get a list of results
    assert isinstance(result, list)
    
    # If there's data, let's verify the structure and types of the first entry
    if result:
        first_entry = result[0]
        assert 'date' in first_entry and isinstance(first_entry['date'], str)
        # Attempt to convert 'high' and 'low' to float to ensure they are number-like strings
        high = float(first_entry['high'])
        low = float(first_entry['low'])
        assert isinstance(high, float)
        assert isinstance(low, float)