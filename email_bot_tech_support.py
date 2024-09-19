import os
from dotenv import load_dotenv
import imaplib
from email.parser import BytesParser
from email.policy import default
import chardet
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import pandas as pd

from llama_index.core import StorageContext, load_index_from_storage
import anthropic

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time

# Load environment variables from .env file
load_dotenv()

try:
    while True:

        # get the file with the latest snapshot
        
        def get_latest_snapshot(folder_path):
            # Define a regular expression pattern to match the file names with timestamps
            file_pattern = r"tech_support_snapshot_(\d{8}_\d{6})\.xlsx"
            
            latest_file = None
            latest_timestamp = None
            
            # Iterate through the files in the specified folder
            for file_name in os.listdir(folder_path):
                # Check if the file matches the expected pattern
                match = re.match(file_pattern, file_name)
                if match:
                    # Extract the timestamp from the file name
                    file_timestamp_str = match.group(1)
                    file_timestamp = datetime.strptime(file_timestamp_str, "%Y%m%d_%H%M%S")
                    
                    # Update the latest file if this one has a more recent timestamp
                    if latest_timestamp is None or file_timestamp > latest_timestamp:
                        latest_timestamp = file_timestamp
                        latest_file = file_name
            
            # Return the full path to the latest file
            if latest_file:
                return os.path.join(folder_path, latest_file)
            else:
                return None
        
        
        folder = r"C:\Users\134\Documents\ЭЛТИС\Техподдержка"
        #TODO!
        #latest_snapshot_file = get_latest_snapshot(folder)
        latest_snapshot_file =r"C:\Users\134\Documents\ЭЛТИС\Техподдержка\tech_support_snapshot_20240917_140028.xlsx"
        
        emails_latest_snapshot_df = pd.read_excel(latest_snapshot_file, index_col=None)
        
        
        def extract_number_from_brackets(text):
            # Use a regular expression to find the number inside square brackets
            match = re.search(r'\[(\d+)\]', text)
            
            # If a match is found, extract the number and return the number + 1
            if match:
                number_in_brackets = int(match.group(1))
                return number_in_brackets + 1
            else:
                return 1
        
        ###########################################################################
        # read email box
        ###########################################################################
        
        # Establish connection to the email server
        url = os.getenv('EMAIL_SERVER')
        user = os.getenv('EMAIL_USER')
        password = os.getenv('EMAIL_PASSWORD')
        
        try:
            conn = imaplib.IMAP4_SSL(url, 993)
            conn.login(user, password)
        except imaplib.IMAP4.error as e:
            print(f"Login failed: {e}")
            exit(1)
        
        # Select the mailbox (e.g., 'INBOX')
        conn.select('INBOX')
        # for "SENT" folder
        #conn.select('&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-') 
        
        # Search for all emails in the selected mailbox
        results, data = conn.search(None, 'ALL')
        msg_ids = data[0]
        msg_id_list = msg_ids.split()
        
        # Initialize a dictionary to store email details
        emails = {}
        
        def decode_content(content):
            if isinstance(content, str):
                return content
            elif isinstance(content, bytes):
                # Try to detect the encoding
                detected = chardet.detect(content)
                encoding = detected['encoding'] or 'utf-8'
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    # If decoding fails, try with 'ignore' error handling
                    return content.decode(encoding, errors='ignore')
            else:
                return str(content)
        
        def strip_html(content):
            # Remove HTML tags
            soup = BeautifulSoup(content, "html.parser")
            return soup.get_text(separator=' ', strip=True)
        
        # Iterate through all email IDs. Last 20 emails.
        for msg_id in msg_id_list[len(msg_id_list)-10:]:
            try:
                # Fetch each email by its ID
                result, data = conn.fetch(msg_id, "(RFC822)")
        
                # Extract the raw email content from the fetch response
                raw_email = data[0][1]
        
                # Use BytesParser to parse the raw email
                parser = BytesParser(policy=default)
                msg = parser.parsebytes(raw_email)
        
                # Extract the subject, sender, and date details
                subject = decode_content(msg['subject'])
                from_ = decode_content(msg['from'])
                date_str = msg['date']
                
                # Convert date string to datetime object
                date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
                
                # Format date as string
                formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
        
                # Initialize body variable
                body = ""
        
                # Retrieve the body of the email
                if msg.is_multipart():
                    # Iterate through email parts to find the text/plain or text/html part
                    for part in msg.iter_parts():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
        
                        if "attachment" not in content_disposition:
                            payload = decode_content(part.get_payload(decode=True))
                            if content_type == "text/plain":
                                body += payload
                            elif content_type == "text/html":
                                body += strip_html(payload)
                else:
                    # If the email is not multipart, extract the payload directly
                    content_type = msg.get_content_type()
                    payload = decode_content(msg.get_payload(decode=True))
                    if content_type == "text/plain":
                        body = payload
                    elif content_type == "text/html":
                        body = strip_html(payload)
        
                # Store the email details in the dictionary
                emails[msg_id.decode()] = {
                    'subject': subject,
                    'from': from_,
                    'date': formatted_date,
                    'body': body.strip()
                }
            except Exception as e:
                print(f"Error processing email {msg_id}: {str(e)}")
        
        # Logout and close the connection
        conn.logout()
        
        
        emails_df = pd.DataFrame(emails).T
        emails_df.rename_axis("Index", inplace=True)
        emails_df = emails_df.reset_index().rename(columns={"Index": "Index"})
        
        emails_df["Index"] = emails_df["Index"].astype(int)
        
        # check what emails were not replied
        emails_not_replied = emails_df.merge(
                                    emails_latest_snapshot_df[["from", "date", "tech_support_bot", "reply_date", "reply_content"]],
                                    on=['from', 'date'],  # Specify both columns to merge on
                                    how='left',           # Use 'left' join to keep all rows from `emails_df`
                                    indicator=True        # Add a column to indicate merge status
                                )
        #emails_not_replied = emails_not_replied[emails_not_replied["tech_support_bot"].isna()]
        
        emails_not_replied = emails_not_replied[
                                            emails_not_replied["tech_support_bot"].isna() &
                                            emails_not_replied["subject"].str.contains(r"\[техподдержка\]", na=False)]
                                                
        
        # iterate over the list of not replied emails
        for i in range(len(emails_not_replied)):
            #print(emails_not_replied[["body"]].iloc[i])
        
        #############
        
            
            # if the email is a chain of emails get the last message from the email
            def extract_until_from(text):
                # Convert text to lowercase to handle case-insensitive search
                lower_text = text.lower()
                # Find the position of the first occurrence of "from"
                from_index = lower_text.find("from")
                
                # If "from" is found, slice the string up to that point, else return the entire text
                if from_index != -1:
                    return text[:from_index]
                else:
                    return text
                
                
             # get the latest email text
            email_content = extract_until_from(emails_not_replied["body"].iloc[i])   
            
            #TODO! test
            #email_content =  "Какие коды вызова для адреса коммутатра 3?"
            
            ###########################################################################
            # query the index from llama index to the relevant information
            ###########################################################################
            
            # Path to save the index
            PERSIST_DIR = "./my_test_storage"
            
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            
            index = load_index_from_storage(storage_context)
            
            
            def query_index(index, question):
                query_engine = index.as_query_engine(
                    similarity_top_k=3,  # Get top 3 most relevant results
                    response_mode="no_text"  # This will return the raw Node objects
                )
                
                response = query_engine.query(question)
                
                # Initialize an empty string to store concatenated results
                concatenated_results = ""
                
                # Iterate over the response nodes and concatenate the results
                for i, node in enumerate(response.source_nodes, 1):
                    # Concatenate the answer number and the text from the node
                    concatenated_results += f"Answer {i}:\n{node.node.text}\n\n"
                
                # Optionally, you can return or print the concatenated result
                print(concatenated_results)
                return concatenated_results
            
            
              
            # Your question
            
            # Query the index
            relevant_info_from_documentation = query_index(index, email_content)
            
            ###########################################################################
            # query LLM
            ###########################################################################
            
            client = anthropic.Anthropic(
                # Use the API key from environment variables
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            
            def send_message(text_to_send):
                message = client.messages.create(
                    model="claude-3-5-sonnet-20240620",  # You can switch to "claude-3-5-sonnet-20240620" "claude-3-opus-20240229" if needed
                    max_tokens=4096,  # Adjust tokens as required
                    messages=[
                        {"role": "user", "content": text_to_send}
                    ]
                )
                return message.content
            
            text_to_send_tech_support = f''' Imagine you are a technical support employee.
            You are receiving a customer question and you are also provided with information from tehcnical documentation. 
            This information is separated by Answer 1, Answer 2, Answer 3 lables with decreasing relevance.
            Please, reply to the customer in Russian.
            Question:
            {email_content}
            
            Information from technical documentation: {relevant_info_from_documentation}'''
            
            claude_reply_tech_support = send_message(text_to_send_tech_support)
            
            ###########################################################################
            # send reply to the customer
            ###########################################################################
            
            
            # Email details
            from_addr = "m.smirnov@eltis.com"
            to_addr = emails_not_replied["from"].iloc[i]
            subject = "Re:ответ техподдрежки " + " " + str(extract_number_from_brackets (emails_not_replied["subject"].iloc[i])) + emails_not_replied["subject"].iloc[i]
            body = (claude_reply_tech_support[0].text + "\n" +
                        "_________________________" + "\n" +
                        emails_not_replied["subject"].iloc[i] + "\n" +
                        emails_not_replied["from"].iloc[i] + "\n" +
                        emails_not_replied["date"].iloc[i] + "\n" +
                        emails_not_replied["body"].iloc[i] )
                    
            
            # SMTP server details
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT'))  # Convert to integer
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = subject
            
            # Attach the body of the email
            msg.attach(MIMEText(body, 'plain'))
            
            try:
                # Connect to the SMTP server (unencrypted connection)
                server = smtplib.SMTP(smtp_server, smtp_port)
            
                # No encryption (do not call starttls)
                
                # Log in to the email account
                server.login(smtp_user, smtp_password)
            
                # Send the email
                server.sendmail(from_addr, to_addr, msg.as_string())
                
                # Disconnect from the server
                server.quit()
            

                
                # Get the current timestamp
                current_timestamp = datetime.now()
                
                # Format the timestamp to remove characters not suitable for file names
                timestamp_str = current_timestamp.strftime("%Y%m%d_%H%M%S")
                
                #TODO! label only the message which is replied not the whole column
                emails_df ["tech_support_bot"] = "reply sent"
                #emails_df.loc[emails_df.index[-1], 'reply_date'] = current_timestamp
                
                filtered_index = emails_df[(emails_df["from"] == emails_not_replied["from"].iloc[i]) & (emails_df["date"] == emails_not_replied["date"].iloc[i])].index
                
                emails_df.loc[filtered_index, 'reply_date'] = current_timestamp
                emails_df.loc[filtered_index, 'reply_content'] = claude_reply_tech_support[0].text
                
                
                
                emails_df.to_excel(rf"C:\Users\134\Documents\ЭЛТИС\Техподдержка\tech_support_snapshot_{timestamp_str}.xlsx", index=False, index_label="Index")
                print("Email sent successfully!")
                time.sleep(2)
                
                
            except Exception as e:
                print(f"Failed to send email: {e}")
            
        time.sleep(5)  # Sleep for a short period to prevent the loop from running too fast
except KeyboardInterrupt:
    print("Loop interrupted by user.")

    
    