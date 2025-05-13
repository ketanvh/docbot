import os
import requests
import sys
import traceback
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables and set up debug functionality
load_dotenv()
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes", "y"]

def debug_log(message):
    if DEBUG:
        print(f"DEBUG [OpenAI Service]: {message}")

def call_azure_openai_api(endpoint, api_key, deployment_name, messages):
    """
    Calls the Azure OpenAI REST API to get a response from a deployed model.

    Args:
        endpoint (str): The Azure OpenAI endpoint.
        api_key (str): The API key for authentication.
        deployment_name (str): The name of the deployed model.
        messages (list): A list of messages for the chat completion.

    Returns:
        dict: The response from the Azure OpenAI API.
    """
    debug_log(f"Making REST API call to Azure OpenAI deployment: {deployment_name}")
    url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version=2023-05-15"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "messages": messages,
        "max_tokens": 100,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    debug_log("REST API call completed successfully")
    return response.json()

def call_azure_openai_api_v2(endpoint, api_key, deployment_name, messages):
    """
    Calls the Azure OpenAI API using the AzureOpenAI client for GPT-4.0.

    Args:
        endpoint (str): The Azure OpenAI endpoint.
        api_key (str): The API key for authentication.
        deployment_name (str): The name of the deployed model.
        messages (list): A list of messages for the chat completion.

    Returns:
        dict: The response from the Azure OpenAI API.
    """
    debug_log(f"Making SDK API call to Azure OpenAI deployment: {deployment_name}")
    # Updated parameters for AzureOpenAI client
    client = AzureOpenAI(
        api_key=api_key,
        api_version="2023-05-15",
        azure_endpoint=endpoint,
        azure_deployment=deployment_name
    )
    response = client.chat.completions.create(
        deployment_id=deployment_name,
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )
    debug_log("SDK API call completed successfully")
    return response

def get_completion(query, context, history=None):
    """
    Get completion from Azure OpenAI based on query, context, and chat history.
    
    Args:
        query (str): User's question
        context (str): Context from PDF/websites
        history (list): Previous chat history
    
    Returns:
        str: AI-generated response
    """
    debug_log(f"Getting completion for query: {query[:50]}...")
    
    if history is None:
        history = []
    
    # Get Azure OpenAI settings from environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
    
    debug_log(f"Using endpoint: {endpoint}, deployment: {deployment_name}, API version: {api_version}")
    
    # Get system prompt from environment variable
    system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant answering questions based on provided documents.")
    
    if not endpoint or not api_key or not deployment_name:
        debug_log("Missing OpenAI configuration")
        return "Error: Azure OpenAI settings are not configured properly. Please check your .env file."
    
    try:
        debug_log("Creating AzureOpenAI client")
        
        # Use the correct parameter names as per your working code
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        debug_log("Client created successfully")
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add relevant context if available
        if context:
            debug_log(f"Adding context to messages (length: {len(context)} characters)")
            messages.append({
                "role": "system", 
                "content": f"Use the following information to answer the user's question. If the information doesn't contain the answer, say that you don't know based on the provided documents:\n\n{context}"
            })
        
        # Add chat history
        debug_log(f"Adding chat history (entries: {len(history)})")
        recent_history = history[-6:] if len(history) > 6 else history
        for message in recent_history:
            if message["role"] != "system":  # Skip system messages in history
                messages.append({"role": message["role"], "content": message["content"]})
        
        # Add current query if not already in messages
        if not any(m["content"] == query and m["role"] == "user" for m in messages):
            messages.append({"role": "user", "content": query})
        
        # Get completion - Use deployment_id here as per API requirements
        debug_log(f"Sending request to OpenAI API with {len(messages)} messages")
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        debug_log("Response received successfully")
        return response.choices[0].message.content
    
    except Exception as e:
        debug_log(f"ERROR: Exception in get_completion: {str(e)}")
        if DEBUG:
            debug_log("Full traceback:")
            traceback.print_exc(file=sys.stdout)
        
        return f"Sorry, I encountered an error when generating a response. Error details: {str(e)}"