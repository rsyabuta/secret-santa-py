import csv
import random
import smtplib
import argparse
import os
from email.mime.text import MIMEText

class Entry:
    name = ""
    email = ""
    address = ""
    pick = ""
    
    def __init__(self, name, email, address):
        self.name = name
        self.email = email
        self.address = address
    
    def select_pick(self, pool):
        cleaned_pool = [x for x in pool if x.name != self.name]
        # Make sure the last person doesn't get themselves
        if len(cleaned_pool) == 2:
            i = 1
        else:
            i = random.randrange(len(cleaned_pool))
        self.pick = cleaned_pool[i]
        return [x for x in pool if x != cleaned_pool[i]]

def generate_entries(file):
    with open(file) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        entries = []
        for row in csv_reader:
            entries.append(Entry(row["Name"], row["Email"], row["Address"]))
    return entries

def generate_pool(entries):
    pool = []
    for entry in entries:
        pool.append(entry.name)
    return pool

def generate_email(entry):
    return """Hello {},

You have been selected to be {}'s secret santa! Please send your gift to {} or {}.

Happy Holidays!""".format(entry.name, entry.pick.name, entry.pick.address, entry.pick.email)

def send_email(entry, smtp_server, smtp_port, username, password):
    """Send email to entry with their secret santa assignment"""
    msg = MIMEText(generate_email(entry))
    msg['Subject'] = 'Secret Santa Assignment'
    msg['From'] = username
    msg['To'] = entry.email
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        print(f"Email sent to {entry.name} ({entry.email})")
        return True
    except Exception as e:
        print(f"Failed to send email to {entry.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Secret Santa assignment generator')
    parser.add_argument('csv_file', help='Path to CSV file with participants')
    parser.add_argument('--send-emails', action='store_true', 
                        help='Send emails to participants')
    parser.add_argument('--smtp-server', default='smtp.gmail.com',
                        help='SMTP server address (default: smtp.gmail.com)')
    parser.add_argument('--smtp-port', type=int, default=587,
                        help='SMTP server port (default: 587)')
    
    args = parser.parse_args()
    
    # Generate assignments
    entries = generate_entries(args.csv_file)
    pool = entries
    for entry in entries:
        pool = entry.select_pick(pool)
        if not args.send_emails:
            print(entry.name + " has " + entry.pick.name)
    
    # Send emails if requested
    if args.send_emails:
        username = os.environ.get('SMTP_USERNAME')
        password = os.environ.get('SMTP_PASSWORD')
        
        if not username or not password:
            print("\nError: SMTP_USERNAME and SMTP_PASSWORD environment variables must be set")
            print("Example: export SMTP_USERNAME='your_email@gmail.com'")
            print("         export SMTP_PASSWORD='your_app_password'")
            return
        
        print(f"\nSending emails via {args.smtp_server}...")
        for entry in entries:
            send_email(entry, args.smtp_server, args.smtp_port, username, password)

if __name__ == '__main__':
    main()