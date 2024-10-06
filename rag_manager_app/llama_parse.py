# bring in our LLAMA_CLOUD_API_KEY
from dotenv import load_dotenv
load_dotenv()

# bring in deps
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

from dotenv import load_dotenv
import os
import json
import nest_asyncio
nest_asyncio.apply()

# https://cloud.llamaindex.ai/parse

LLAMA_CLOUD_API_KEY = LLAMA_CLOUD_API_KEY


# Load variables from .env file
load_dotenv()

api_key = os.getenv('LLAMA_CLOUD_API_KEY')
print(api_key)  # Output will


# Set API key
os.environ['LLAMA_CLOUD_API_KEY'] = LLAMA_CLOUD_API_KEY

# Load configuration from paths.json with explicit encoding to handle Unicode characters
with open(r"C:\Users\134\paths.json", 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

source_folder = config["Source Files Folder"]
markdown_folder = config["Markdown Folder"]

# Ensure the markdown folder exists# bring in our LLAMA_CLOUD_API_KEY
from dotenv import load_dotenv
load_dotenv()


# bring in deps
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

from dotenv import load_dotenv
import os

import json

import nest_asyncio
nest_asyncio.apply()

# https://cloud.llamaindex.ai/parse

LLAMA_CLOUD_API_KEY = LLAMA_CLOUD_API_KEY


# Load variables from .env file
load_dotenv()

api_key = os.getenv('LLAMA_CLOUD_API_KEY')
print(api_key)  # Output will


# Set API key
os.environ['LLAMA_CLOUD_API_KEY'] = LLAMA_CLOUD_API_KEY

# Access the API key
api_key = os.getenv('LLAMA_CLOUD_API_KEY')
print(api_key)  # Output will be your API key


# Load configuration from paths.json with explicit encoding to handle Unicode characters
with open(r"paths.json", 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

source_folder = config["Source Files Folder"]
markdown_folder = config["Markdown Folder"]

# Ensure the markdown folder exists
os.makedirs(markdown_folder, exist_ok=True)

# set up parser
parser = LlamaParse(
    result_type="markdown"  # "markdown" and "text" are available
)

# use SimpleDirectoryReader to parse our files
file_extractor = {".pdf": parser}

# Get all PDF files in the source folder
pdf_files = [f for f in os.listdir(source_folder) if f.endswith('.pdf')]

for pdf_file in pdf_files:
    input_file_path = os.path.join(source_folder, pdf_file)
    documents = SimpleDirectoryReader(input_files=[input_file_path], file_extractor=file_extractor).load_data()
    
    # Create output file path with the same name as the input file
    output_file = os.path.join(markdown_folder, os.path.splitext(pdf_file)[0] + ".md")
    
    # Initialize an empty string to hold the concatenated markdown content
    all_markdown_content = ""
    
    # Iterate over the list of documents and concatenate their content
    for doc in documents:
        markdown_content = doc.text
        all_markdown_content += markdown_content + "\n\n"  # Add newlines to separate the content
    
    # Save the concatenated markdown content to a single file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_markdown_content)
    
    print(f"Markdown content saved successfully to {output_file}.")

if not pdf_files:
    print("No PDF files found in the source folder.")
os.makedirs(markdown_folder, exist_ok=True)

# set up parser
parser = LlamaParse(
    result_type="markdown"  # "markdown" and "text" are available
)

# use SimpleDirectoryReader to parse our files
file_extractor = {".pdf": parser}

# Get all PDF files in the source folder
pdf_files = [f for f in os.listdir(source_folder) if f.endswith('.pdf')]

for pdf_file in pdf_files:
    input_file_path = os.path.join(source_folder, pdf_file)
    documents = SimpleDirectoryReader(input_files=[input_file_path], file_extractor=file_extractor).load_data()
    
    # Create output file path with the same name as the input file
    output_file = os.path.join(markdown_folder, os.path.splitext(pdf_file)[0] + ".md")
    
    # Initialize an empty string to hold the concatenated markdown content
    all_markdown_content = ""
    
    # Iterate over the list of documents and concatenate their content
    for doc in documents:
        markdown_content = doc.text
        all_markdown_content += markdown_content + "\n\n"  # Add newlines to separate the content
    
    # Save the concatenated markdown content to a single file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(all_markdown_content)
    
    print(f"Markdown content saved successfully to {output_file}.")

if not pdf_files:
    print("No PDF files found in the source folder.")