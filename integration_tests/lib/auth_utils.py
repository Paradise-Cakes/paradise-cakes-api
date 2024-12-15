import email as email_reader
import re
import time


def get_user_confirmation_code_from_email(mail_client, subject_filter, code_text):
    time.sleep(10)  # Wait for the email to arrive
    mail_client.noop()  # Re-sync the mailbox

    result, data = mail_client.search(None, f'(SUBJECT "{subject_filter}")')

    if result != "OK":
        raise Exception("No emails found with the specified subject")

    # Get the most recent email
    email_ids = sorted(data[0].split(), key=int)
    latest_email_id = email_ids[-1]

    # Fetch the email
    result, data = mail_client.fetch(latest_email_id, "(RFC822)")
    print(data)
    print(data[0][1])
    raw_email = data[0][1].decode("utf-8")
    msg = email_reader.message_from_string(raw_email)
    payload = None

    # Handle multipart emails
    if msg.is_multipart():
        for part in msg.get_payload():
            # Check if this part is text/html
            if part.get_content_type() == "text/html":
                payload = part.get_payload(
                    decode=True
                ).decode()  # Decode bytes to string
                break
    else:
        # Single-part email (assume plain text)
        payload = msg.get_payload(decode=True).decode()

    # Extract the confirmation code
    match = re.search(rf"{code_text} <b>(\d+)</b>", payload)
    confirmation_code = match.group(1) if match else None

    return confirmation_code
