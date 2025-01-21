import json
import os
from datetime import datetime

# Function to create a new conversation JSON file
def create_new_conversation(user_id, bot_name="JuanGPT"):
    conversation_id = str(user_id) + "_" + datetime.now().strftime("%Y%m%d%H%M%S")
    conversation_data = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "bot_name": bot_name,
        "messages": []
    }
    
    # Create a folder for conversations if it doesn't exist
    if not os.path.exists('conversations'):
        os.makedirs('conversations')
    
    # Save the conversation to a JSON file
    with open(f'conversations/{conversation_id}.json', 'w') as file:
        json.dump(conversation_data, file, indent=4)
    
    return conversation_id

# Function to add a message to the conversation
def add_message_to_conversation(conversation_id, sender, content):
    file_path = f'conversations/{conversation_id}.json'
    
    # Open the conversation JSON file and update it
    with open(file_path, 'r') as file:
        conversation_data = json.load(file)
    
    message = {
        "sender": sender,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Append the new message
    conversation_data["messages"].append(message)
    
    # Save the updated conversation back to the file
    with open(file_path, 'w') as file:
        json.dump(conversation_data, file, indent=4)
