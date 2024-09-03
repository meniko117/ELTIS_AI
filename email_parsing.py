import imaplib
from email.parser import BytesParser
from email.policy import default
import chardet
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

# Establish connection to the email server
url = "mx.eltis.com"
user, password = (user, password)

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
for msg_id in msg_id_list[len(msg_id_list)-20:]:
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






# def convert_unicode_escape(obj):
#     if isinstance(obj, str):
#         return obj.encode('utf-8').decode('unicode_escape')
#     elif isinstance(obj, dict):
#         return {k: convert_unicode_escape(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_unicode_escape(item) for item in obj]
#     else:
#         return obj


# # Load JSON data
# data = json.loads('C:\\Users\\134\Documents\\inbox_email.json')

# # Convert all elements in the JSON
# converted_data = convert_unicode_escape(emails)    
    


formatted_date = date.today().strftime("%d_%m_%Y")

    
# Specify the file path where you want to save the JSON data
file_path = fr'C:\Users\134\Documents\ЭЛТИС\Почта\почта_20_сообщений_inbox_{formatted_date}.json'

#  date to compare with
given_date = datetime(2024, 8, 28, 0, 0, 0)  #- timedelta(days=3)

# Filter the emails dictionary
filtered_emails = {key: value for key, value in emails.items() if datetime.strptime(value['date'], '%Y-%m-%d %H:%M:%S') >= given_date}


#last_20_items = dict(list(emails.items()))

# Writing the dictionary to a JSON file
with open(file_path, 'w', encoding='utf-8') as json_file:
    json.dump(filtered_emails, json_file, ensure_ascii=False, indent=4)
   

# # список mail boxes
# result, mailboxes = conn.list()
# for mailbox in mailboxes:
#     print(mailbox.decode())