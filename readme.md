
# MailProtect : Your Email Spam Protection

## Overview
This project is a spam detection and email protection system that uses a linear  model to classify messages as spam or not spam. The system includes a web application for spam detection and a script for processing emails and marking spam.

## Motivation
Email spam is a significant issue, with billions of spam emails sent daily. Spam emails can lead to phishing attacks, malware infections, and data breaches. According to recent statistics:
 - Over 50% of all email traffic is spam.
 - Phishing attacks account for 90% of data breaches.
 - The average cost of a data breach is $3.86 million.
This project aims to provide a robust solution for detecting and managing spam emails, helping to protect users from potential threats.

## Project Structure
```
app.py
credentials.txt
data/
    spam.csv
model.py
notebooks/
    spam-detection.ipynb
protection.py
readme.md
requirements.txt
test/
    test.py
models/
    tfid_vectorizer.pkl
    logistic_regression.pkl
```

## How to Run the Project
### Prerequisites
Python 3.x
Required Python packages (listed in `requirements.txt`)
### Installation
1. Clone the repository:
```
git clone https://github.com/your-repo/spam-detection.git
cd spam-detection
```
2. Install the required packages:
```
pip install -r requirements.txt
```

### Running the Web Application
To test the web application for spam detection:
Execute the app.py script:
```
streamlit run app.py
```
Open your web browser and navigate to the URL provided by Streamlit.

### Running the Email Protection Script
The email protection script can be run in two modes: normal mode and job mode.

#### Normal Mode
You can run the script once .
Ensure your email credentials are stored in `credentials.txt` in the format username:password.
Execute the `protection.py` script:
```
python protection.py
```
#### Job Mode
You can execute a cron job to fetch and process emails in every 5 mins.
Ensure your email credentials are stored in `credentials.txt` in the format username:password.
Execute the `protection.py` script with the --job argument:
In job mode, the script will run periodically (every 5 minutes by default) to fetch and process emails.
```
python protection.py --job
```


### How the protection script works 
1. **Load Credentials**: The script loads email credentials from `credentials.txt`.
2. **Connect to Email Provider**: It connects to the email provider's IMAP server using the credentials.
3. **Fetch Emails**: The script fetches unseen emails from the inbox.
4. **Extract Email Content**: It extracts the subject and body of each email.
5. **Detect Spam**: The script uses the pre-trained logistic regression model and TF-IDF vectorizer to classify emails as spam or not spam.
6. **Mark Spam**: If an email is classified as spam, it is marked accordingly in the inbox and stored in the Spam/Junk folder.

### How to enable IMAP server connection for Gmail
To enable imap mail reading in gmail you need to :

1) Enable `less secure apps` feature : https://myaccount.google.com/lesssecureapps?pli=1

2) Enable Imap setting in Gmail(Not Google) Gmail Settings -> Forwarding and POP / IMAP -> IMAP Access to Enable IMAP

### License
This project is licensed under the MIT License. See the LICENSE file for more details.

