import anthropic
import os
import sys
from llama_index.core import StorageContext, load_index_from_storage

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
import openai
import re  # Import regex for handling special characters
import pandas as pd

####################################################
# get relevant info from Index
####################################################

# Set your OpenAI API key
openai.api_key = open_ai_key

# Path to save the index
PERSIST_DIR = "./my_test_storage"

storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)

index = load_index_from_storage(storage_context)



def query_index(question):
    # Read the CSV file
    df = pd.read_excel(r'C:/Users/134/Documents/ЭЛТИС/Техподдержка/text_search.xlsx')
    
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
            similarity_top_k=3,  # Get top 3 most relevant results
            response_mode="no_text"  # This will return the raw Node objects
        )
        
        response = query_engine.query(question)
        
        # Iterate over the response nodes and concatenate the results
        for i, node in enumerate(response.source_nodes, 1):
            # Concatenate the answer number and the text from the node
            concatenated_results += f"From index '{index_name}', Answer {i}:\n{node.node.text}\n\n"
    print (concatenated_results)
    # Return the concatenated results
    return concatenated_results





####################################################
# query LLM
####################################################
client = anthropic.Anthropic(
    api_key=anthropic_key_key,
)

def send_message(text_to_send):
    message = client.messages.create(
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



if __name__ == "__main__":
    
    # query from the user
    text_to_send_tech_support = sys.stdin.read().strip()
    #get info from Index
    relevant_info_from_documentation = query_index(text_to_send_tech_support)
    
    RAG_user_query = f''' Imagine you are a technical support employee.
    You are receiving a customer question and you are also provided with information from tehcnical documentation. 
    This information is separated by Answer 1, Answer 2, Answer 3 lables with decreasing relevance.
    Please, reply to the customer in Russian.
    Question: {text_to_send_tech_support}
    
    Information from technical documentation: {relevant_info_from_documentation}'''

    claude_reply_tech_support = format_claude_reply(send_message(RAG_user_query))
    # Reconfigure stdout to handle UTF-8 encoding
    #sys.stdout.reconfigure(encoding='utf-8')
    
    print(claude_reply_tech_support)