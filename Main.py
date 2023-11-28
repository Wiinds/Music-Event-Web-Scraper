import requests
import selectorlib
import smtplib, ssl
import sqlite3
import os
import time

url = "http://programmer100.pythonanywhere.com/tours/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


sqltest = "INSERT INTO events VALUES (?,?,?)"  

test_entry = [('tigers', 'leftwood', '2078-07-19'), 
              ('wolf', 'eastwood', '2077-12-3'),
              ('luke', 'leftwood', '2078-04-9')]

test_entry2 = ('turtle', 'eastwood', '2077-09-3')

class Event:
    #get data and format it as text
    def scrape(self, url):
        response = requests.get(url, headers=HEADERS)
        source = response.text
        return source

    #get information from the data 
    def extract(self, source):
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value

class Datafetch:
    def __init__(self, database_path):
        self.conn = sqlite3.connect(database_path)
        
    #store the data in the database 
    def store(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO events VALUES (?,?,?)", row)
        self.conn.commit()


    def read(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        band, city, date = row
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
        row = cursor.fetchall()
        print(row)
        return row


class Email:
    #send email when new event is added    
    def send(self, message):
        host = "smtp.gmail.com"
        port = 465
        username = "jeremyabraham17@gmail.com"
        password = os.getenv("PROJECTSHOWCASE")
        receiver = "jeremyabraham17@gmail.com"
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, message)
        print("Email was sent!")


if __name__ == "__main__":
    while True:
        event = Event()
        scraped = event.scrape(url)
        extracted = event.extract(scraped)
        print(extracted)
        
        if extracted != "No upcoming tours":
            db = Datafetch(database_path="events.db")
            row = db.read(extracted)
            # if item is not in the rows, store it and send a email
            if not row:
                db.store(extracted)
                email = Email()
                email.send(message="New Event was found!")    
        time.sleep(3)




