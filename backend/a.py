import smtplib
from email.message import EmailMessage
import ssl # Import the SSL module

# --- Configuration ---
receiver_email = "nghiem2468@gmail.com"
sender_email = "transchatdevteam@gmail.com"
# For security, store your password securely (e.g., environment variables)
# If using Gmail, this should be an App Password, not your regular password
password = "@" 

# Create the email message object
msg = EmailMessage()
msg.set_content("This is the body of the email.")
msg['Subject'] = "A Test Email from Python"
msg['From'] = sender_email
msg['To'] = receiver_email

# Define the SMTP server details for Gmail
smtp_server = "smtp.gmail.com"
port = 587 # Port 587 is typically used with TLS

# Create a secure SSL context
context = ssl.create_default_context()

try:
    # Connect to the server and send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context) # Secure the connection with TLS
        server.login(sender_email, password) # Log in to the account
        server.send_message(msg) # Send the message
    print("Email sent successfully!")

except smtplib.SMTPAuthenticationError:
    print("Authentication failed. Check your username/password or App Password settings.")
except Exception as e:
    print(f"An error occurred: {e}")

