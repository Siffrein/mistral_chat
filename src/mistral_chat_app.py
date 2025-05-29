import streamlit as st
#import requests
from mistralai import Mistral
import json
#import os
import pickle
from datetime import datetime
from pathlib import Path
from tools.tool_definitions import load_tools, load_tools_mapping
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# from dotenv import load_dotenv
# # Load environment variables from .env file
# load_dotenv()

# Disable Streamlit telemetry before any other imports or operations
# This prevents any data from being sent to Snowflake/Fivetran
# replaced in favor of .streamlit folder + config.toml
#os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
#os.environ["STREAMLIT_SERVER_TELEMETRY"] = "false"

###
## Init stuff
###

# Create data directory if it doesn't exist
CONVERSATIONS_DIR = Path("saved_conversations")
CONVERSATIONS_DIR.mkdir(exist_ok=True)

# Set page configuration
st.set_page_config(
    page_title="Chat with Captain Ticker",
    page_icon="🦸‍♂️",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "conversations" not in st.session_state:
    # Load existing conversations if available
    st.session_state.conversations = {}
    for file_path in CONVERSATIONS_DIR.glob("*.pkl"):
        try:
            with open(file_path, "rb") as f:
                conversation = pickle.load(f)
                topic_name = file_path.stem
                st.session_state.conversations[topic_name] = conversation
        except Exception:
            # Skip corrupted files
            pass

if "current_topic" not in st.session_state:
    st.session_state.current_topic = "New Conversation"


###
## Sidebar setup
###

# Sidebar for API key input and conversation management
with st.sidebar:
    st.title("Mistral AI Chat")
    st.session_state.api_key = st.text_input("Enter your Mistral API Key:", type="password")
    
    # Model selection
    # mistral-small-2503 mistral-large-2411
    model_options = [
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest"
    ]
    selected_model = st.selectbox("Pick a Model:", model_options)
    
    # Temperature slider
    temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    # Conversation management section
    st.markdown("---")
    st.subheader("Conversation Management")
    
    # Topic naming/renaming
    topic_name = st.text_input("Topic Name:", value=st.session_state.current_topic)
    
    col1, col2 = st.columns(2)
    
    # Save current conversation
    with col1:
        if st.button("Save Conversation"):
            if st.session_state.messages:
                # Save to session state
                st.session_state.conversations[topic_name] = st.session_state.messages.copy()
                st.session_state.current_topic = topic_name
                
                # Save to disk
                with open(CONVERSATIONS_DIR / f"{topic_name}.pkl", "wb") as f:
                    pickle.dump(st.session_state.messages, f)
                
                st.success(f"Saved as '{topic_name}'")
            else:
                st.warning("Nothing to save")
    
    # Clear current conversation
    with col2:
        if st.button("New Conversation"):
            st.session_state.messages = []
            st.session_state.current_topic = "New Conversation"
            #st.experimental_rerun()
            #st.experimental_user
    
    # Load existing conversations
    if st.session_state.conversations:
        st.subheader("Saved Conversations")
        selected_conversation = st.selectbox(
            "Select a conversation:",
            options=list(st.session_state.conversations.keys()),
            format_func=lambda x: x
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Load"):
                st.session_state.messages = st.session_state.conversations[selected_conversation].copy()
                st.session_state.current_topic = selected_conversation
                #st.experimental_rerun()
        
        with col2:
            if st.button("Delete"):
                # Remove from session state
                st.session_state.conversations.pop(selected_conversation, None)
                
                # Remove from disk
                file_path = CONVERSATIONS_DIR / f"{selected_conversation}.pkl"
                if file_path.exists():
                    file_path.unlink()
                
                if selected_conversation == st.session_state.current_topic:
                    st.session_state.messages = []
                    st.session_state.current_topic = "New Conversation"
                
                #st.experimental_rerun()


###
## Functions
###

# Function to call Mistral API - prereq : temperature defined
def query_mistral(messages, model, api_key, temperature=temperature, **kwargs):
    # useless since switching to mistral ai python sdk
    #url = "https://api.mistral.ai/v1/chat/completions"
       
    # headers = {
    #     "Content-Type": "application/json",
    #     "Accept": "application/json",
    #     "Authorization": f"Bearer {api_key}"
    # }
    
    # data = {
    #     "model": model,
    #     "messages": messages,
    #     "temperature": temperature,
    #     **kwargs
    # }
  
    try:
        client = Mistral(api_key=api_key)
        #response = requests.post(url, headers=headers, data=json.dumps(data))
        response = client.chat.complete(
            model = model,
            messages = messages,
            temperature = temperature,
            tools=kwargs.get("tools", None),
            tool_choice=kwargs.get("tool_choice", "auto")
            #stream=True  # Uncomment if you want to stream responses
        )


        #logger.info(f"Payload:\n {json.dumps(data, indent=4)}")
        resp = response.model_dump_json()  #response.choices[0]
        
        #logger.info(f"API response:\n {json.dumps(resp, indent=4)}")
        logger.info(f"API response:\n {resp}")
        
        #response.raise_for_status()  # Raise exception for 4XX/5XX errors

        #choice = response.json()["choices"][0]
        choice = response.choices[0]
        #tool_call = choice["message"]["tool_calls"][0] if choice["message"]["tool_calls"] else None
        tool_call = choice.message.tool_calls[0] if choice.message.tool_calls else None
        logger.info(f"Tool call type: {type(tool_call)}")
        #logger.info(f"Tool_call:\n {json.dumps(tool_call, indent=4)}")
        logger.info(f"Tool_call:\n {tool_call}")
        
        if tool_call:
            # tool function called
            #tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            function_params = json.loads(tool_call.function.arguments)
            print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)
            names_to_functions = load_tools_mapping()
            function_result = names_to_functions[function_name](**function_params)
            #function_result
            logger.info(f"function_result:\n {function_result}\n")
            
            tool_answer = {
                "role":"assistant",
                #"prefix":True, 
                #"name":function_name, 
                "content":function_result, 
                #"tool_call_id":tool_call['id']
            }

            #messages.append(tool_answer)
            logger.info(f"Tool answer:\n {json.dumps(tool_answer, indent=4)}")

            #query_mistral(messages, model, api_key, temperature=temperature)
            return function_result
        
        # No tool function called
        else:
            #resp = response.json()["choices"][0]["message"]["content"]
            resp = response.choices[0].message.content
            logger.info(f"No tool called:\n {resp}")
            return resp

    #except requests.exceptions.RequestException as e:
    except Exception as e:
        return f"Error: {str(e)}"


###
## Main Chat Interface
###
st.title(f"Chat with Captain Ticker 🦸‍♂️ -> 📉 : {st.session_state.current_topic}")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for new message
if prompt := st.chat_input("Type your message here... Example: What are the top 5 GOOGL stock options calls ?"):
    # Don't allow sending messages if API key is not provided
    if not st.session_state.api_key:
        st.error("Please enter your Mistral API key in the sidebar.")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    logger.info(f"User input: {prompt}")

    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get messages in the format required by Mistral API
    mistral_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    
    # Display assistant response with a spinner while waiting
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_mistral(
                mistral_messages,
                selected_model,
                st.session_state.api_key,
                temperature,
                tools=load_tools(),
                tool_choice="auto"
            )
            logger.info(f"Assistant response:\n {response}")
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Add a footer
st.markdown("---")
st.caption(f"Captain Ticker is proudly fueled by Mistral AI 🇫🇷 • {datetime.now().strftime('%Y-%m-%d')}")