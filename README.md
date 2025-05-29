# Introducing Captain Ticker

Captain Ticker is a simple and imperfect proof of concept (POC). It serves as a local virtual assistant in the form of a chatbot.

# POC Objectives

- Develop basic chatbot features including a conversation management system
- UI design with Streamlit
- Mistral AI LLM API integration
- Function calling support to get real-time information from external APIs (use case implementation: stock market news via Yahoo Finance API)
- Work in progress: Support for agentic AI with Mistral Agent capabilities

# How to Get a Mistral API Key

1. Sign up on the Mistral AI platform (https://mistral.ai/)
2. Create an API key in your account dashboard
3. Enter this API key in the application sidebar by copying and pasting

# Working Overview

- The application uses Streamlit's chat interface components
- API calls are made to Mistral's chat completions endpoint through Mistral AI python SDK
- User messages and AI responses are stored in the session state
- Basic error handling for API failures
- Clean sidebar design for configuration options

# App Features

- **User-friendly interface** with a clean chat layout
- **Model selection** from Mistral's available models
- **Temperature control** to adjust response creativity
- **Chat history** that persists during your session
- **Save conversations** with custom topic names
- **Rename topics** as needed
- **Load previous conversations** from a dropdown menu
- **Delete unwanted conversations**
- **Persistent storage** that survives app restarts

# Design Considerations

1. **Data Persistence**: Uses both in-memory (session state) and disk storage for reliability
2. **User Experience**: Clean, intuitive UI with appropriate feedback messages
3. **Error Handling**: Gracefully handles edge cases like empty conversations or corrupted files
4. **Performance**: Efficient loading/saving with minimal overhead
5. **UI Organization**: Well-structured sidebar for all management functions

# Security Note

- Conversations are stored locally on the user's machine
- API keys remain only in session state and are never saved to disk

## Disabling Streamlit Telemetry

To verify that telemetry is disabled:

1. Monitor network traffic using browser developer tools when the app starts
2. Check the terminal output for any messages about telemetry

[Streamlit Documentation on Telemetry](https://docs.streamlit.io/library/advanced-features/configuration#telemetry)

> Disabled by default when cloning the repo. See the .streamlit folder + config.toml

# Implementation Details

## 1. File Storage System

- Uses Python's `pathlib` for cross-platform file handling
- Creates a dedicated directory for storing conversations
- Uses pickle serialization for efficient storage

## 2. Session State Management

- Automatically loads saved conversations on startup
- Provides graceful handling of corrupted files
- Initializes with a default topic name

## 3. Topic Management UI

- Allows users to set/change the name of the current conversation
- Pre-fills with current topic name for easy renaming

## 4. Save/New Conversation Controls

- Uses columns for a cleaner UI layout
- Provides visual feedback on successful actions
- Creates a fresh conversation with default settings

## 5. Conversation Management Actions

- Only shows the conversations section when saved conversations exist
- Provides dropdown selection of available conversations
- Includes Load and Delete options with appropriate logic
- Handles edge cases like deleting the currently active conversation

## 6. Tools aka Function Calling

A single function implemented to get stock options calls given a ticker and optionally the number of options to retrieve.

Function definition given to LLM:
```python
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
```

Corresponding function header:
```
def get_stock_options(symbol: str, topX=5) -> str:
    """Fetches the top X stock option calls for a given stock symbol.
    Args:
        symbol (str): The stock ticker symbol, like AAPL, GOOGL, or TSLA.
        topX (int): The number of top options to fetch. Default is 5.
    Returns:
        str: A formatted string with the top X stock option calls.
    """
```

## 7. Mistral Agent

work in progress


# Run the app

````
uv venv -p 3.11
source .venv/bin/activate
uv sync

streamlit run mistral_chat_app.py 
````

# Demo 

# Usage Workflow

1. Start a new conversation with the Mistral AI model
2. Enter a descriptive name in the "Topic Name" field
3. Click "Save Conversation" to store it
4. Start a new conversation or load previous ones as needed
5. Rename conversations by changing the name and saving again
6. Test function calling or agent mode

## Sample prompts

> do you have real time access to stock market informations?

> please list your tools

**Trigger function calling**
> ok, show me last 10 calls options for ... let's say apple

> how did you find the mapping between Apple and AAPL ? I didn't mention it

> For Captain Ticker, the Stock Market Superhero, suggest 3 yfinance function headers (just the names) to clobber bad investments and save portfolios!

> thanks buddy!


## Demo video

[![Demo video Captain Ticker - function calling](https://raw.githubusercontent.com/Siffrein/mistral_chat/main/assets/thumbnail_captain_ticker.png)](https://raw.githubusercontent.com/Siffrein/mistral_chat/main/assets/demo_captain_ticker.mp4)


# Side notes 

## Stock call option definition

A stock option call, often simply referred to as a "call option," is a financial contract that gives the buyer the right,
but not the obligation, to purchase a stock at a predetermined price (known as the strike price) within a specific time period.

**Why use call options**

- Leverage: Call options allow investors to control a larger number of shares with a smaller amount of capital.
- Speculation: Investors can speculate on the price movement of a stock without having to buy the stock outright.
- Hedging: Companies and investors can use call options to hedge against potential price increases in the underlying stock.
