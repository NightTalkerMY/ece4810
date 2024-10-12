import email.message
import time
import imaplib
import email
import os
from twilio.rest import Client

class EmergencyCommandHandler:
    def __init__(self, gmail_username, gmail_password, twilio_sid, twilio_auth_token, to_number, from_number):
        self.username = gmail_username
        self.password = gmail_password
        self.client = Client(twilio_sid, twilio_auth_token)
        self.to_number = to_number
        self.from_number = from_number
        self.mail = None
        self.last_checked = -1

    # Connect to Gmail IMAP
    def login_gmail(self):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        self.mail.login(self.username, self.password)
        self.mail.list()
        self.mail.select("Notes")
        result, uidlist = self.mail.search(None, "ALL")
        latest_email_id = uidlist[0].split()[-1]
        self.last_checked = latest_email_id

    # Fetches the latest command from email
    def fetch_command(self):
        self.mail.list()
        self.mail.select("Notes")
        result, uidlist = self.mail.search(None, "ALL")
        latest_email_id = uidlist[0].split()[-1]
        
        if latest_email_id == self.last_checked:
            return None  # No new email, return None

        self.last_checked = latest_email_id
        result, data = self.mail.fetch(latest_email_id, "(RFC822)")

        # Try to extract command for Apple devices
        voice_command = email.message_from_string(data[0][1].decode('utf-8'))
        command = str(voice_command.get_payload()).lower().strip()

        # Try to extract command for Android devices
        message = (email.message_from_bytes(data[0][1]))
        for part in message.walk():
            if part.get_content_type() == "text/plain":  # Plain text part
                text = part.get_payload(decode=True).decode('utf-8')  # Decode to get the actual text
                return text.strip().lower()  # Strip unnecessary whitespaces and return the useful text
        
        return command.lower()  # If no Android message found, return the Apple one

    # Initiate an emergency call
    def initiate_emergency_call(self):
        self.client.calls.create(
            twiml="""
            <Response>
                <!-- Play an audio file -->
                <Play>https://tangelo-grasshopper-6988.twil.io/assets/10%20Oct%2C%204.20%20pm_.mp3</Play>
            </Response>
            """,
            to=self.to_number,
            from_=self.from_number
        )

    # Main loop for processing commands
    def run(self):
        self.login_gmail()  # Log in to Gmail
        while True:
            try:
                command = self.fetch_command()
                if command and "help" in command:
                    self.initiate_emergency_call()
            except TypeError:
                pass
            except Exception as exc:
                print(f"Received an exception while running: {exc}\nRestarting...")
            time.sleep(1)  # Polling every second


if __name__ == '__main__':
    # Credentials and configurations
    gmail_username = "williamteder6123@gmail.com"
    gmail_password = "sawe bthp talo iqkk"
    twilio_sid = "AC639825d63f4a13d8f776dbafef75deb8"
    twilio_auth_token = "4f215deacdb67727242eefee6aae4c96"
    to_number = "+601163371919"
    from_number = "+18645284638"

    # Create an instance of the handler and run it
    handler = EmergencyCommandHandler(gmail_username, gmail_password, twilio_sid, twilio_auth_token, to_number, from_number)
    handler.run()
