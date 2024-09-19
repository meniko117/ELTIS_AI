# bring in our LLAMA_CLOUD_API_KEY
from dotenv import load_dotenv
load_dotenv()

# bring in deps
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

from dotenv import load_dotenv
import os

import nest_asyncio
nest_asyncio.apply()

# https://cloud.llamaindex.ai/parse

# Load environment variables from .env file
load_dotenv()

# Set API key from environment variable
os.environ['LLAMA_CLOUD_API_KEY'] = os.getenv('LLAMA_CLOUD_API_KEY')

# set up parser
parser = LlamaParse(
    result_type="markdown"  # "markdown" and "text" are available
)

# use SimpleDirectoryReader to parse our file
file_extractor = {".pdf": parser}
input_file = os.getenv('INPUT_FILE_PATH')
documents = SimpleDirectoryReader(input_files=[input_file], file_extractor=file_extractor).load_data()
print(documents)

output_folder = os.getenv('OUTPUT_FOLDER')
output_file = os.path.join(output_folder, "dpu5000_kedc_markdown.md")

# Initialize an empty string to hold the concatenated markdown content
all_markdown_content = ""

# Iterate over the list of documents and concatenate their content
for doc in documents:
    # Access the content of the document correctly
    markdown_content = doc.text  # Adjust according to the actual attribute
    
    # Concatenate the markdown content
    all_markdown_content += markdown_content + "\n\n"  # Add newlines to separate the content

# Save the concatenated markdown content to a single file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(all_markdown_content)

print(f"Markdown content saved successfully to {output_file}.")