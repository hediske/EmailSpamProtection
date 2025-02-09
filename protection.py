import argparse
import imaplib
import email
import logging
from email.header import decode_header
import pickle
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import schedule
import time
import dns.resolver

providers = {
    'gmail': {'imap_url': 'imap.gmail.com', 'smtp_url': 'smtp.gmail.com'},
    'outlook': {'imap_url': 'outlook.office365.com', 'smtp_url': 'smtp.office365.com'},
    'yahoo': {'imap_url': 'imap.mail.yahoo.com', 'smtp_url': 'smtp.mail.yahoo.com'}
}



#Credentials
def load_credentials(filepath):
    try:
        with open(filepath, 'r') as file:
            credentials = file.readline().split(":")
            user = credentials[0]
            password = credentials[1]
            print("Loaded Credentials")
            return user, password
    except Exception as e:
        print("Failed to load credentials: {}".format(e))
        raise

def get_email_provider(user):
    domain = user.split('@')[-1]
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = records[0].exchange
        mx_server = str(mx_record).rstrip(".")
        print(mx_server)
        if 'GOOGLE' in mx_server:
            return 'gmail'
        elif 'outlook' in mx_server:
            return 'outlook'
        elif 'yahoodns' in mx_server:
            return 'yahoo'
        else :
            raise Exception("Invalid email : only supporting Gmail , Yahoo and Outlook")
    except Exception as e:
        print("Failed to get the email provider: {}".format(e))
        raise
        


def connect_to_imap(user, password, provider):
    try:
        imap_url = providers[provider]['imap_url']
        mail = imaplib.IMAP4_SSL(imap_url, port=993)
        mail.login(user, password)
        print("Connected to IMAP")
        return mail
    except Exception as e:
        print("Failed to connect to IMAP: {}".format(e))
        raise


def logout(mailer):
    try:
        mailer.logout()
        print("Logged out")
    except Exception as e:
        print("Failed to logout: {}".format(e))
        raise


def get_headers(email_message):
    try:
        subject, encoding = decode_header(email_message["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
        return subject
    except Exception as e:
        print("Failed to get headers: {}".format(e))
        raise



def get_body(msg):
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True).decode(errors="ignore")

            elif content_type == "text/html":
                html_content = part.get_payload(decode=True).decode(errors="ignore")
                body = extract_text_from_html(html_content) 

    else:
        if msg.get_content_type() == "text/plain":
            body = msg.get_payload(decode=True).decode(errors="ignore")
        elif msg.get_content_type() == "text/html":
            html_content = msg.get_payload(decode=True).decode(errors="ignore")
            body = extract_text_from_html(html_content)
    # print (body)
    return clean_email_text(body)

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def clean_email_text(text):
    cleaned_text = re.sub(r'[\r\n\t]', ' ', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


def fetch_emails(mailer):
    try:
        mailer.select('inbox')
        status , messages=mailer.search(None, 'UNSEEN')
        if status != 'OK':
            print("Failed to search emails")
            return
        email_ids = messages[0].decode().split()
        # print(email_ids)
        print(f"Fetching {len(email_ids)} emails...")
        emails = []
        for mail in tqdm(email_ids, desc="Fetching Emails", unit="email"):
            _, msg_data = mailer.fetch(mail,"(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    email_message = email.message_from_bytes(response_part[1])
                    header = get_headers(email_message)
                    body = get_body(email_message)
                    emails.append({"id" : mail , "header":  header, "body": body})
        print("\nFetching complete!")
        return emails
    except Exception as e:
        print("Failed to fetch emails: {}".format(e))
        raise

def detect_spam(emails, model, vectorizer):
    results= []
    try:
        for email in tqdm(emails, desc="Detecting Spam", unit="email"):
            body = [email["body"]]
            body_vect = vectorizer.transform(body)
            subject = [email["header"]]
            subject_vect = vectorizer.transform(subject)
            prediction = model.predict(body_vect)
            prediction = model.predict(subject_vect) if prediction[0] == 0 else prediction
            if prediction[0] == 1:
                results.append({"id": email["id"],"spam":"False"})
            else:
                results.append( {"id": email["id"],"spam":"True"})
        print("Spam Check complete!")
        return results
    except Exception as e:
        print("Failed to detect spam: {}".format(e))
        raise

def get_models():
    try:
        with open("./models/logistic_regression.pkl","rb") as file:
            model = pickle.load(file)
        with open("./models/tfid_vectorizer.pkl","rb") as file:
            vectorizer = pickle.load(file)
        return model, vectorizer
    except Exception as e:
        print("Failed to load models: {}".format(e))
        raise


def mark_spam(mailer, spam_list):
    count = 0
    try:
        for email in tqdm(spam_list, desc="Marking Spam", unit="email"):
            email_id = email["id"]

            if email["spam"] == "True":
                mailer.store(email_id,"+X-GM-LABELS",'\\spam') 
                mailer.copy(email_id,"\\junk")
                count += 1
                print(f"Moved email {email_id} to Spam folder")  

            mailer.store(email_id, '-FLAGS', '\\Seen')

        print("Marking complete!")
        print(f"Marked {count} emails")
        return count
    except Exception as e:
        print("Failed to mark spam: {}".format(e))
        raise


def fetch_and_process(mailer):
    emails = fetch_emails(mailer)
    model,vectorizer=get_models()
    spam_list = detect_spam(emails, model, vectorizer)
    print(spam_list)
    mark_spam(mailer, spam_list)


#main
def main():
    user,password = load_credentials('credentials.txt')
    provider = get_email_provider(user)
    mailer = connect_to_imap(user, password, provider)
    fetch_and_process(mailer)
    logout(mailer)


def job(n = 5):
    user,password = load_credentials('credentials.txt')
    provider = get_email_provider(user)
    mailer = connect_to_imap(user, password, provider)
    schedule.every(n).minutes.do(fetch_and_process, mailer)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email spam filter script")
    parser.add_argument("--job", action="store_true", help="Run in scheduled job mode")
    args = parser.parse_args()
    if args.job:
        job()
    else:
        main()