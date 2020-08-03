from cs50 import SQL
import time
import datetime
import csv
import random
from starter_code import get_date

db = SQL("sqlite:///demo.db")

#GET TIMESTAMP FOR DATA
#timestamp = (datetime.datetime.now().timestamp() * 1000)
def date_to_timestamp():
    totals = db.execute("SELECT * FROM stocks")
    for row in totals:
        og_date = row['date']
        date = row['date'].split('/')

        month = int(date[0])
        day = int(date[1])
        year = int(date[2])

        dt = datetime.datetime(year, month, day)

        timestamp = (time.mktime(dt.timetuple()) * 1000)
        print("Date: %s, Timestamp: %d" % (date, timestamp))

        db.execute("UPDATE stocks SET date = ? WHERE date = ?", (timestamp, og_date))

def savings_to_totals():
    #ADD SAVINGS DATA TO TOTALS
    savings_data = db.execute("SELECT * FROM savings")
    for row in savings_data:
        date = row['date']
        balance = row['balance']
        db.execute("INSERT INTO totals (date, location, balance) VALUES(?, ?, ?)", (date, 'savings', balance))

def wallet_to_totals():
    #ADD WALLET DATA TO TOTALS
    wallet_data = db.execute("SELECT * FROM wallet")
    for row in wallet_data:
        date = row['date']
        balance = row['balance']
        db.execute("INSERT INTO totals (date, location, balance) VALUES(?, ?, ?)", (date, 'wallet', balance))

def stocks_to_totals():
    #ADD STOCK DATA TO TOTALS
    stock_data = db.execute("SELECT * FROM stocks")
    for row in stock_data:
        date = row['date']
        balance = row['balance']
        db.execute("INSERT INTO totals (date, location, balance) VALUES(?, ?, ?)", (date, 'stocks', balance))
        print("%s %s" % (date, balance))

def manipulate_stocks():
    stock_data = db.execute("SELECT * FROM stocks")
    for row in stock_data:
        og_balance = row['balance']
        balance = str(float(og_balance.replace(',','')) - 1000)
        db.execute("UPDATE stocks SET balance = ? WHERE balance = ?", (balance, og_balance))
        print("%s %s" % (og_balance, balance))


def delete_stocks():
    db.execute("DELETE FROM totals WHERE location = 'stocks'")

def delete_wallet():
    db.execute("DELETE FROM totals WHERE location = 'wallet'")

def delete_savings():
    db.execute("DELETE FROM totals WHERE location = 'savings'")


def generate_wallet_data():
    #Generate data over range of dates with range of posible dollar amounts
    1456790400000
    start = datetime.date(2016, 3, 1)
    print(start)
    end = datetime.date(2020, 5, 22)
    print(end)
    delta = end - start
    print(delta.days)

    data = []
    for i in range(delta.days):
        date = start + datetime.timedelta(days= i + 1)
        print(date)
        balance = random.randint(0, 500)
        print(balance)
        data.append([date, balance])
    for element in data[::10]:
        date = element[0]
        timestamp = get_date(date.year, date.month, date.day) * 1000
        balance = element[1]
        db.execute("INSERT INTO wallet (date, balance) VALUES(?, ?)", (timestamp, balance))

def generate_savings_data():
    #Generate data over range of dates with range of posible dollar amounts
    1456790400000
    start = datetime.date(2016, 3, 1)
    print(start)
    end = datetime.date(2020, 5, 22)
    print(end)
    delta = end - start
    print(delta.days)

    data = []
    for i in range(delta.days):
        date = start + datetime.timedelta(days= i + 1)
        print(date)
        balance = i + random.randint(0, 100) + 2000
        print(balance)
        print(i)
        data.append([date, balance])
    for element in data[::10]:
        date = element[0]
        timestamp = get_date(date.year, date.month, date.day) * 1000
        balance = element[1]
        db.execute("INSERT INTO savings (date, balance) VALUES(?, ?)", (timestamp, balance))



#generate_savings_data()
stocks_to_totals()
