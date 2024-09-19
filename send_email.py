import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Load environment variables from .env file
load_dotenv()

# SMTP server details
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))  # Convert to integer
user = os.getenv('SMTP_USER')
password = os.getenv('SMTP_PASSWORD')

# Email details
from_addr = os.getenv('FROM_EMAIL')
to_addr = os.getenv('TO_EMAIL')
subject = os.getenv('EMAIL_SUBJECT')
body = os.getenv('EMAIL_BODY')

# Create the email message
msg = MIMEMultipart()
msg['From'] = from_addr
msg['To'] = to_addr
msg['Subject'] = subject

# Attach the body of the email
msg.attach(MIMEText(body, 'plain'))

# File to attach
file_path = os.getenv('ATTACHMENT_PATH')
file_name = os.path.basename(file_path)

# Add the file attachment with correct MIME type for Excel files
try:
    with open(file_path, "rb") as attachment:
        # Create a MIMEBase object for the Excel file
        part = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        part.set_payload(attachment.read())

        # Encode file in ASCII characters for email transmission
        encoders.encode_base64(part)

        # Add the necessary headers to specify it as an attachment with the correct file name
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={file_name}",
        )

        # Attach the file to the email
        msg.attach(part)
except Exception as e:
    print(f"Failed to attach file: {e}")
    exit(1)

# Send the email
try:
    # Connect to the SMTP server (unencrypted connection)
    server = smtplib.SMTP(smtp_server, smtp_port)

    # No encryption (do not call starttls)
    
    # Log in to the email account
    server.login(user, password)

    # Send the email
    server.sendmail(from_addr, to_addr, msg.as_string())
    
    # Disconnect from the server
    server.quit()

    print("Email sent successfully with Excel attachment!")
except Exception as e:
    print(f"Failed to send email: {e}")
