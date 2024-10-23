import anthropic
import os
import sys
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
import openai
import re
import pandas as pd
import json
from dotenv import load_dotenv

####################################################
# get relevant info from Index
####################################################

load_dotenv(dotenv_path='.env.txt') 
# Access the API keys
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Set your OpenAI API key
openai.api_key = OPENAI_API_KEY

def load_paths_config():
    try:
        # Try to get the directory of the current file (works in scripts)
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # If __file__ is not defined (e.g., in Jupyter), use the current working directory
        current_dir = os.getcwd()
    
    #paths_file = os.path.join('.\paths.json')
    try:
        with open('paths.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading paths.json: {e}")
        return {}

# Use the function
paths_config = load_paths_config()

# Replace hardcoded values:

output_folder = load_paths_config().get("Output Folder")

if output_folder in ["проиндексированные_документы", './проиндексированные_документы']:
    PERSIST_DIR = os.path.join(os.getcwd(), "проиндексированные_документы")
else:
    PERSIST_DIR = output_folder
    
def query_index(question):
    # Read the XLSX file
    df = pd.read_excel('./text_search.xlsx')
    
    # Initialize an empty set to hold unique index names to query
    index_names = set()
    
    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        keywords = row['Ключевые слова']
        index_name = row['Название файла с инструкцией']
        
        # Split the keywords into a list (assuming they are separated by commas or semicolons)
        keyword_list = re.split(r',|;', str(keywords))
        
        # Check if any keyword is in the question
        for keyword in keyword_list:
            keyword = keyword.strip()
            if keyword and keyword.lower() in question.lower():
                index_names.add(index_name)
                break  # If a keyword matches, no need to check the rest for this row

    # If no matching indexes found, you might want to use a default index or handle accordingly
    if not index_names:
        print("No matching keywords found in question.")
        return ""

    concatenated_results = ""
    
    # Iterate over the index names and query each index
    for index_name in index_names:
        # Construct the index directory path
        index_dir = os.path.join(PERSIST_DIR, index_name)
        
        # Check if the index directory exists
        if not os.path.exists(index_dir):
            print(f"Index directory '{index_dir}' does not exist.")
            continue
        
        # Load the index from storage
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
        
        query_engine = index.as_query_engine(
            similarity_top_k=int(paths_config.get('Relevant Parts', 3)),
            response_mode="no_text"
        )
        
        response = query_engine.query(question)
        
        # Iterate over the response nodes and concatenate the results
        for i, node in enumerate(response.source_nodes, 1):
            # Concatenate the answer number and the text from the node
            concatenated_results += f"From index '{index_name}', Answer {i}:\n{node.node.text}\n\n"
    
    # Print concatenated results only if "Include Quotes" in paths_config is TRUE
    if paths_config.get("Include Quotes", False):
        print(concatenated_results)
    
    # Return the concatenated results
    return concatenated_results

####################################################
# query LLM
####################################################
client = anthropic.Anthropic(
    api_key=OPENAI_API_KEY
)

def send_message(text_to_send):
    message = client.messages.create(
        #TODO! implement logic of selecting a model
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": text_to_send}
        ]
    )
    return message.content


def format_claude_reply(reply):
    # Extract the text from the TextBlock
    text = reply[0].text
    
    # Split the text into lines
    lines = text.split('\n')
    
    # Format each line
    formatted_lines = []
    for line in lines:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Add appropriate indentation for list items
        if line.startswith('-'):
            line = '  ' + line
        elif line[0:2].isdigit() and line[2] == '.':
            line = line
        elif line.startswith('   -'):
            line = '    ' + line
        
        formatted_lines.append(line)
    
    # Join the formatted lines back together
    formatted_text = '\n'.join(formatted_lines)
    
    return formatted_text

def query_llm(text_to_send_tech_support):
    # Get info from Index
    relevant_info_from_documentation = query_index(text_to_send_tech_support)
    
    RAG_user_query = f'''{paths_config.get('System Prompt', '')}
    Question: {text_to_send_tech_support}
    Information from technical documentation: {relevant_info_from_documentation}'''

    claude_reply_tech_support = format_claude_reply(send_message(RAG_user_query))
    return claude_reply_tech_support

if __name__ == "__main__":
    # This block is for testing purposes when running the script directly
    test_query = "В чем назначение АРМ?"
    response = query_llm(test_query)
    print(response)