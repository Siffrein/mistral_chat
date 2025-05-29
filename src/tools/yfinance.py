#import yfinance as yf

def get_stock_options(symbol: str, topX=5) -> str:
    """Fetches the top X stock option calls for a given stock symbol.
    Args:
        symbol (str): The stock ticker symbol, like AAPL, GOOGL, or TSLA.
        topX (int): The number of top options to fetch. Default is 5.
    Returns:
        str: A formatted string with the top X stock option calls.
    """
    # Check if the symbol is valid
    if not isinstance(symbol, str) or not symbol.isalpha():
        return "Invalid stock symbol. Please provide a valid ticker symbol."
    # Check if topX is a positive integer
    if not isinstance(topX, int) or topX <= 0:
        return "Invalid value for topX. Please provide a positive integer."
    # Check if yfinance is installed
    try:
        import yfinance as yf
    except ImportError:
        return "yfinance is not installed. Please install it to use this function."
    # Check if the symbol is available in yfinance
    try:
        stock = yf.Ticker(symbol)
        if not stock.info:
            return f"No data available for {symbol}."
    except Exception as e:
        return f"Error fetching data for {symbol}: {e}"
    # Fetch the options data
    try:
        stock = yf.Ticker(symbol)
        options_dates = stock.options
        if not options_dates:
            return f"No options data available for {symbol}."

        first_date = options_dates[0]
        options_chain = stock.option_chain(first_date)

        calls = options_chain.calls[['strike', 'lastPrice', 'volume']].head(topX)
        #print(type(calls)) - to_string
        #return f"Top 5 call options for {symbol} expiring {first_date}:\n\n{calls.to_markdown(index=False)}"
        return f"""
            Top {topX} calls options for {symbol} expiring {first_date}:\n\n{calls.to_markdown(index=False)}
            \n
            Source: Yahoo Finance API via yfinance python package.
            """
        #return f"Top 5 call options for {symbol} expiring {first_date}:\n\n{calls.to_json(index=False)}"
    except Exception as e:
        return f"Error fetching options for {symbol}: {e}"

