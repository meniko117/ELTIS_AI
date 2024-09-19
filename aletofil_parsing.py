import os
import re
from bs4 import BeautifulSoup

# Specify the folder containing HTML files
folder_path = r'C:\Users\134\Downloads\Telegram Desktop\ChatExport_алетофилы'
output_file = os.path.join(folder_path, 'all_info.txt')
unique_names_file = os.path.join(folder_path, 'unique_from_names.txt')

# Create a list to store tuples of (number, filename)
file_list = []

# Set to store unique names
unique_names = set()

# Iterate through all files in the specified folder
for filename in os.listdir(folder_path):
    # Check if the file has an .html extension and matches the pattern 'name{number}.html'
    if filename.endswith('.html'):
        # Extract the number from the file name using regex
        number = int(re.findall(r'\d+', filename)[0])
        # Add the (number, filename) tuple to the file list
        file_list.append((number, filename))

# Sort the file list by the extracted number (first element of each tuple)
file_list.sort()

# Create/open the output files in write mode
with open(output_file, 'w', encoding='utf-8') as outfile, open(unique_names_file, 'w', encoding='utf-8') as namefile:
    # Iterate over the sorted file list
    for number, filename in file_list:
        file_path = os.path.join(folder_path, filename)
        
        # Open and parse the HTML file
        with open(file_path, 'r', encoding='utf-8') as infile:
            soup = BeautifulSoup(infile, 'html.parser')
            
            # Write a separator for each file in the main output file
            outfile.write(f"--- File: {filename} ---\n\n")

            # Extract relevant content from the HTML file
            messages = soup.find_all(class_="message default clearfix")
            
            b_details = ""  # Initialize b_details

            # Process each message
            for message in messages:
                date = message.find(class_="pull_right date details")
                name = message.find(class_="from_name")
                text = message.find(class_="text")
                body_details = message.find(class_="body details")

                if body_details:
                    b_details = body_details.get_text(strip=True)

                # Check if date, name, and text are present
                if date and name and text:
                    # Extract the date and time from the 'title' attribute of the date element
                    date_time = date.get('title', '')  # Get the 'title' attribute

                    outfile.write(f"Date and Time: {date_time}\n")
                    if b_details:
                        outfile.write(f"Details: {b_details}\n")
                    outfile.write(f"From: {name.get_text(strip=True)}\n")
                    outfile.write(f"Message: {text.get_text(separator='\n', strip=True)}\n")
                    outfile.write("\n---\n\n")  # Separator between messages

                    # Add the 'from_name' information to the set of unique names
                    unique_names.add(name.get_text(strip=True))

    # Write the unique 'from_name' values to the separate file
    for unique_name in sorted(unique_names):
        namefile.write(f"{unique_name}\n")




######################################################################
# send the text by 1000 lines chunks to LLM to get the resume
import os
import time



###########
# Claude API

import os
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env file
load_dotenv()

client = anthropic.Anthropic(
    # Use the API key from environment variables
    api_key=os.getenv("ANTHROPIC_API_KEY")
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
##########


# Path to the txt file created earlier
input_file = r'C:\Users\134\Downloads\Telegram Desktop\ChatExport_алетофилы\all_info.txt'

# Folder to save the outputs
summary_folder = os.path.join(os.path.dirname(input_file), 'Summary')

# Create the "Summary" folder if it doesn't exist
os.makedirs(summary_folder, exist_ok=True)

# Read the saved txt file and split by 1000 lines
with open(input_file, 'r', encoding='utf-8') as infile:
    lines = infile.readlines()

# Split lines into chunks of 1000
chunk_size = 1000
chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]

# Record the start time for the entire process
total_start_time = time.time()

# Iterate through each chunk and pass it to the send_message function
for idx, chunk in enumerate(chunks, start=1):
    # Join the lines of the chunk into a single string
    chunk_text = ''.join(chunk)
    
    # Send the chunk to the send_message function
    output = send_message('''Here is the first 1000 messages from the chat. Please, 
                          make a summary who is supporting what position in the discussion add to the summary a 
list of strong points of every person and provide the exact quote for each including date. 
Formulate this position and provide the exact 
quatation to prove that. Be noted that exact quatation also is required to find the message in the text.
Double check that the output summary should be stricly Russian. ''' + ''.join(chunk_text))[0].text
    
    # Define the output filename with a sequential number
    output_file = os.path.join(summary_folder, f'summary_{idx}.txt')
    
    # Save the output in the Summary folder
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(output)

    print(f"Processed chunk {idx} and saved to {output_file}")

print("Processing complete.")


# Measure the total time for processing
total_end_time = time.time()
total_duration = total_end_time - total_start_time
print(f"Total processing time: {total_duration:.2f} seconds.")


####################################################################
# concatenate all the summaries in one text file
import os
import re

# Define the folder path
folder_path = r"C:\Users\134\Downloads\Telegram Desktop\ChatExport_алетофилы\Summary"

# Create an empty string to hold the concatenated content
all_text = ""

# Create a list to store tuples of (number, file_name)
file_list = []

# Loop through all files in the folder
for file_name in os.listdir(folder_path):
    # Check if the file is a .txt file and follows the pattern summary_<number>.txt
    if file_name.endswith(".txt") and re.match(r"summary_\d+\.txt", file_name):
        # Extract the number from the file name using regex
        number = int(re.findall(r"\d+", file_name)[0])
        # Add the (number, file_name) tuple to the file list
        file_list.append((number, file_name))

# Sort the file list by the extracted number (first element of each tuple)
file_list.sort()

# Iterate over the sorted file list
for number, file_name in file_list:
    # Multiply the number by 1000
    sequential_thousand = number * 1000
    
    # Add an empty line, the header, and another empty line before each file content
    all_text += f"\n--------- {sequential_thousand} сообщений ---------\n\n"
    
    # Construct the full file path
    file_path = os.path.join(folder_path, file_name)
    
    # Open and read the content of the txt file
    with open(file_path, 'r', encoding='utf-8') as file:
        all_text += file.read() + "\n"  # Add a newline after the file content

# Print the concatenated content (for demonstration purposes)
print(all_text)

# Optionally, you can save the concatenated content to a new file
output_file = os.path.join(folder_path, "concatenated_output.txt")
with open(output_file, 'w', encoding='utf-8') as output:
    output.write(all_text)
    
    
    
    
    
from docx import Document

# Define the path to the text file and the output Word document
folder_path = r"C:\Users\134\Downloads\Telegram Desktop\ChatExport_алетофилы\Summary\concatenated_output.txt"
output_path = r"C:\Users\134\Downloads\Telegram Desktop\ChatExport_алетофилы\Summary\output_document.docx"

# Create a new Document object
doc = Document()

# Open and read the text file
with open(folder_path, 'r', encoding='utf-8') as file:
    # Read all lines from the file
    lines = file.readlines()
    
    # Add lines to the Word document
    for line in lines:
        doc.add_paragraph(line.strip())

# Save the document
doc.save(output_path)

print(f"Document saved as {output_path}")


####################################################################
# analyze summary dynamics over time in chat

folder_path = r"C:\Users\134\Downloads\Telegram Desktop\ChatExport_алетофилы\Summary\concatenated_output.txt"


# Open and read all lines from the txt file
with open(folder_path, 'r', encoding='utf-8') as file:
    all_text_summary = file.read()

# Use regex to replace multiple consecutive newlines with a single newline
cleaned_text_summary = re.sub(r'\n{3,}', '\n\n', all_text_summary)


# Split the cleaned text into lines
lines = cleaned_text_summary.splitlines()

# Get the first 1000 lines
first_1000_lines = lines[:1000]

# Join the first 1000 lines into a single string
first_1000_text = '\n'.join(first_1000_lines)



dynamics_summary = send_message('''You are provided with a long text summary of a chat that covers various philosophical and religious questions. Different participants express their viewpoints throughout the discussion. Analyze the text and follow these instructions:

Identify and list the dynamics of differing perspectives by categorizing them according to:

Name of the person
Point(s) of view
Citation supporting the viewpoint (if available)
Date of the citation (if available)
Ensure that:

All participant names mentioned in the provided text are included. 
Cross-check against the following list to verify that all names are covered:
Alon
Baruch Shlepakov
Benyamin
Dani
Deleted Account
Eitan
Eitan K
Eli Greencorn
Eli Greencorn via @Shrug_mv_Bot
Ilya
Israel Hm
Jakobas Karmelis
Kirill Prozumentik
Leonid
Levi I. Rits
M G
Menahem Remez
Mikhail Frolov
Mordechai Dror
Vladyslav Horovyi
Yohanan Momot
Илья Бельник
Максим Смирнов
Реувен Губерман
אליהו
𝕊𝕖𝕟𝕕𝕖𝕣 𝕃𝕚𝕡𝕤𝕜𝕪 🇮🇱
🦴💎 ronipla
Pay special attention that the names mentioned from first 30% to 60% of the text are not missed in the summary.
List all points of view for each participant.
Include citations and dates for each viewpoint if they are provided. 
The final output summary must be in Russian.

Here is the text to analyze:''' + first_1000_text)





dynamics_summary = send_message('''You are provided with a long text summary of a chat that covers various philosophical and religious questions. 
                                Different participants express their viewpoints throughout the discussion.
                                Analyze the text and follow these instructions:

Get the list of the persons ivolved and provide the list of all main points of a speicfic person.

Ensure that:

All participant names mentioned in the provided text are included. 
Cross-check against the following list to verify that all names are covered:
Alon
Baruch Shlepakov
Benyamin
Dani
Deleted Account
Eitan
Eitan K
Eli Greencorn
Eli Greencorn via @Shrug_mv_Bot
Ilya
Israel Hm
Jakobas Karmelis
Kirill Prozumentik
Leonid
Levi I. Rits
M G
Menahem Remez
Mikhail Frolov
Mordechai Dror
Vladyslav Horovyi
Yohanan Momot
Илья Бельник
Максим Смирнов
Реувен Губерман
אליהו
𝕊𝕖𝕟𝕕𝕖𝕣 𝕃𝕚𝕡𝕤𝕜𝕪 🇮🇱
🦴💎 ronipla
Pay special attention that the names mentioned from first 30% to 60% of the text are not missed in the summary.
List all points of view for each participant.
Include citations and dates for each viewpoint if they are provided. 
The final output summary must be in Russian.

Here is the text to analyze:''' + first_1000_text)


######################################################################
# get all messages per name
import os
import re
from bs4 import BeautifulSoup

# Specify the folder containing HTML files
folder_path = r'C:\Users\134\Downloads\Telegram Desktop\ChatExport_алетофилы'

# Create a list to store tuples of (number, filename)
file_list = []

# Dictionary to store unique names and their corresponding file handles
user_files = {}

# Iterate through all files in the specified folder
for filename in os.listdir(folder_path):
    # Check if the file has an .html extension and matches the pattern 'name{number}.html'
    if filename.endswith('.html'):
        # Extract the number from the file name using regex
        number = int(re.findall(r'\d+', filename)[0])
        # Add the (number, filename) tuple to the file list
        file_list.append((number, filename))

# Sort the file list by the extracted number (first element of each tuple)
file_list.sort()

# Process each file and group messages by 'from_name'
for number, filename in file_list:
    file_path = os.path.join(folder_path, filename)
    
    # Open and parse the HTML file
    with open(file_path, 'r', encoding='utf-8') as infile:
        soup = BeautifulSoup(infile, 'html.parser')
        
        # Extract relevant content from the HTML file
        messages = soup.find_all(class_="message default clearfix")
        
        b_details = ""  # Initialize b_details

        # Process each message
        for message in messages:
            date = message.find(class_="pull_right date details")
            name = message.find(class_="from_name")
            text = message.find(class_="text")
            body_details = message.find(class_="body details")

            if body_details:
                b_details = body_details.get_text(strip=True)

            # Check if date, name, and text are present
            if date and name and text:
                # Extract the 'from_name'
                user_name = name.get_text(strip=True)
                # Create or open the file corresponding to this user
                if user_name not in user_files:
                    user_file_path = os.path.join(folder_path, f"{user_name}.txt")
                    user_files[user_name] = open(user_file_path, 'w', encoding='utf-8')

                user_file = user_files[user_name]

                # Extract the date and time from the 'title' attribute of the date element
                date_time = date.get('title', '')  # Get the 'title' attribute

                # Write the message information to the user's file
                user_file.write(f"Date and Time: {date_time}\n")
                if b_details:
                    user_file.write(f"Details: {b_details}\n")
                user_file.write(f"Message: {text.get_text(separator='\n', strip=True)}\n")
                user_file.write("\n---\n")  # Separator between messages

# Close all the user files after processing
for file in user_files.values():
    file.close()

