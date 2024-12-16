import re
import time


def fetch_email(mail_client, email_id):
    result, data = mail_client.fetch(email_id, "(RFC822)")

    if result != "OK":
        raise Exception("Failed to fetch email")

    for item in data:
        if isinstance(item, tuple) and isinstance(item[1], bytes):
            return item[1].decode("utf-8")

    raise Exception("Failed to fetch email")


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
    email_msg = fetch_email(mail_client, latest_email_id)

    # Extract the confirmation code
    match = re.search(rf"{code_text} <b>(\d+)</b>", email_msg)
    confirmation_code = match.group(1) if match else None

    return confirmation_code
