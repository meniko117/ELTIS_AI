# This script extracts Named Entities from PDFs using Anthropic's Haiku model.
import os
import PyPDF2
import pandas as pd
import anthropic
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv(dotenv_path='.env.txt')  # Specify the path if not named .env

# Access the API keys
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Function to extract Named Entities using Anthropic's Haiku model
def extract_ner(text):
    message = client.messages.create(
        model= "claude-3-haiku-20240307" ,  # You can switch to"claude-3-5-sonnet-20240620" if needed
        max_tokens=4096,  # Adjust tokens as required
        messages=[
            {"role": "user", "content": f"Extract and list all named entities from the following text:\n\n{text}. Do not add any comments. Give just a list of named entities separated by comma. If there are no named entities return just empty space. Do not add any comments."}
        ]
    )
    
    # Check if the response has content
    if hasattr(message, 'content') and message.content:
        return message.content[0].text  # Return the content directly
    else:
        return ""  # Return an empty string if there's no content

# Function to extract NER from the first page and other pages of the PDF
def extract_ner_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            first_page_ner = []
            other_pages_ner = []

            if len(reader.pages) > 0:
                # First page NER
                first_page_text = reader.pages[0].extract_text()
                first_page_ner = extract_ner(first_page_text)

                # NER for other pages
                other_pages_text = ""
                for i in range(1, len(reader.pages)):
                    other_pages_text += reader.pages[i].extract_text() + "\n"
                other_pages_ner = extract_ner(other_pages_text)

            return first_page_ner, other_pages_ner

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None, None

# Function to process PDF files
def process_pdf_files(base_dir, num_files):
    data = []
    file_count = 0

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".pdf"):
                full_path = os.path.join(root, file)
                print(f"Processing: {full_path}")

                # Extract NER from the PDF
                first_page_ner, other_pages_ner = extract_ner_from_pdf(full_path)

                if first_page_ner is not None and other_pages_ner is not None:
                    # Append the data
                    data.append({
                        "File name": file,
                        "Full path to the file": full_path,
                        "NER on the first page": first_page_ner,
                        "NER on other pages": other_pages_ner
                    })

                file_count += 1
                if num_files != "all" and file_count >= num_files:
                    return data

    return data

# Main execution
if __name__ == "__main__":
    base_dir = r"C:\Users\134\saved_pages\ELTIS_site"
    
    # Ask user for the number of files to process
    num_files_input = input("Enter the number of files to process (or 'all' for all files): ")
    num_files = int(num_files_input) if num_files_input.isdigit() else "all"

    # Process PDF files
    data = process_pdf_files(base_dir, num_files)

    # Create a DataFrame and save to Excel
    df = pd.DataFrame(data)
    output_file = r"C:\Users\134\saved_pages\extracted_ner_data.xlsx"
    df.to_excel(output_file, index=False)

    print(f"NER data saved to {output_file}")