import csv
import random
import smtplib
from email.mime.text import MIMEText

class Entry:
    name = ""
    email = ""
    address = ""
    pick = None

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

def send_email(entry):
    body = """
    Hello {},
    
    You have been selected to be {}'s secret santa! Please send your gift to {}.
    
    Happy Holidays!""".format(entry.name, entry.pick.name, entry.pick.address)

    msg = MIMEText(body)
    msg['Subject'] = "Secret Santa"
    msg['From'] = sender
    msg['To'] = entry.email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

def main():
    entries = generate_entries("2023.csv")
    pool = entries
    for entry in entries:
        pool = entry.select_pick(pool)
        print(entry.name + " has " + entry.pick.name)

if __name__ == '__main__':
    main()