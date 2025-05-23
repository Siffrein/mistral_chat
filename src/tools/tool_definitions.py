import functools
from tools.yfinance import get_stock_options

# tool def : get_stock_options
def load_tools():
    tools_functions = [
        {
            "type": "function",
            "function": {
                "name": "get_stock_options",
                "description": get_stock_options.__doc__.split('\n')[0],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The stock ticker symbol, like AAPL, GOOGL, or TSLA."
                        },
                        "topX": {
                            "type": "integer",
                            "description": "The number of top options to fetch. Default is 5.",
                            "default": 5
                        }
                    },
                    "required": ["symbol"]
                }               
            }
        }
    ]

    return tools_functions

def load_tools_mapping():
    names_to_functions = {
        'get_stock_options': functools.partial(get_stock_options)    
    }
    return names_to_functions
