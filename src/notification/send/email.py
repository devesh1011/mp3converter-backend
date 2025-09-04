import smtplib
from smtplib import SMTPDataError
import os
from email.message import EmailMessage
import json


def notification(message):
    try:
        messaege = json.loads(message)
        mp3_fid = messaege["mp3_fid"]
        sender_addr = os.environ.get("GMAIL_ADDRESS")
        sender_pass = os.environ.get("GMAIL_PASSWORD")
        receiver_addr = messaege["username"]

        msg = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")
        msg["Subject"] = "MP3 Download"
        msg["From"] = sender_addr
        msg["To"] = receiver_addr

        session = smtplib.SMTP("smtp.gmail.com")
        session.starttls()
        session.login(user=sender_addr, password=sender_pass)
        session.send_message(msg=msg, from_addr=sender_addr, to_addrs=receiver_addr)
        session.quit()
        print("Mail Sent")
    except Exception as err:
        print(err)
        raise SMTPDataError(code=500, msg="Email Server error")
