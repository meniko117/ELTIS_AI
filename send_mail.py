import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(smtp_server_ip, smtp_port, user, app_password, recipients, subject, body):
    try:
        # Set up the server with IP address
        server = smtplib.SMTP(smtp_server_ip, smtp_port)
        server.starttls()  # Secure the connection, if using port 587

        # Log in to the server
        server.login(user, app_password)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail(user, recipients, msg.as_string())
        print("Email sent successfully.")

    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    
    finally:
        server.quit()

# Example usage
smtp_server = "mx.eltis.com" #'192.168.20.220' #'mail2.eltis.intra' #xch01.eltis.intra' #'smtp.office365.com' # 
smtp_port = 465
user = 'm.smirnov@eltis.com'  #"ELTIS\\smirnov"
password = 'Qazqwe11'
recipients = ['m.smirnov@eltis.com']
subject = 'Test Email'
body = 'This is a test email.'

send_email(smtp_server, smtp_port, user, password, recipients, subject, body)
