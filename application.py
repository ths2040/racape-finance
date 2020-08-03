###---- TODO LIST ----###
# Fix time difference
# Sign in page
# Extra date on stocks graph
2. # Update Totals table using SQL
1. #Update home page with SQL
# Dynamically create pie chart for positions
3. # Sample data for home page
# Create dummy data for demo
# Select functionality from zing chart
# work on speed maybe
# Form validation wallet and savings
# Heroku


import cs50
import yfinance
import time
import datetime
import os
import requests
import urllib.parse
from cs50 import SQL
import csv
from starter_code import get_date, get_data, get_price
from flask import Flask, jsonify, redirect, render_template, request

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True


exact_date = datetime.datetime.today()
current_date = ("%s/%s/%s" % (exact_date.month, exact_date.day, exact_date.year))
#print(current_date)
last_accessed = ""


#print(last_accessed)

SIGNED_IN = False
DEMO = True
db = ""


@app.route("/demo", methods=["POST"])
def demo():

    global SIGNED_IN
    SIGNED_IN = True
    return redirect('/')


@app.route("/sign_in", methods=["POST"])
def sign_in():

    global SIGNED_IN, DEMO

    password = request.form.get("password")

    if not password:
        return render_template("error.html")

    with open('password.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if  password in row:
                SIGNED_IN = True
                DEMO = False
                return redirect('/')
            else:
                return render_template("error.html", message="Incorrect username or password")

@app.route("/", methods=["GET"])
def get_index():

    global db

    if not SIGNED_IN:
        return render_template("sign_in.html")

    if DEMO == False:
        db = SQL("sqlite:///finance.db")
    else:
        db = SQL("sqlite:///demo.db")


    #GET DATA FROM DATABASE FOR CHART
    stock_data = []
    savings_data = []
    wallet_data = []
    rows = db.execute("SELECT * FROM totals")
    for row in rows:
        if row['location'] == 'stocks':
            try:
                stock_data.append([row['date'], float(row['balance'].replace(',',''))])
            except:
                stock_data.append([row['date'], row['balance']])
        if row['location'] == 'savings':
            savings_data.append([row['date'], row['balance']])
        if row['location'] == 'wallet':
            wallet_data.append([row['date'], row['balance']])
    #print(dates)
    #print(values)

    return render_template("/index.html", stock_data=stock_data[::10], savings_data=savings_data, wallet_data=wallet_data)


@app.route("/stocks", methods=["GET"])
def get_stocks():

    global last_accessed
    with open('last_accessed.csv') as f:
        last_accessed = f.read()[:-1]

    #UPDATE POSITIONS AND TOTALS
    date_format = "%m/%d/%Y"
    la = datetime.datetime.strptime(last_accessed, date_format)
    cd = datetime.datetime.strptime(current_date, date_format)
    print(la)
    print(cd)
    if  cd != la:
        update_stocks(last_accessed)
        update_positions()

    #GET DATA FROM DATA BASE
    values = []         #needed to get latest balance
    data = []           #data for chart
    rows = db.execute("SELECT * FROM stocks")
    for row in rows:
        values.append(row['balance'])
        try:
            data.append([row['date'], float(row['balance'].replace(',',''))])
        except:
            data.append([row['date'], row['balance']])

    #STOCKS TOTAL
    stocks_total = values[-1]

    #GET LATEST POSITIONS
    positions = []
    rows = db.execute("SELECT * FROM positions")
    for row in rows:
        positions.append([row['ticker'], row['quantity-owned'], row['price'], row['cost'], row['gain']])

    #RETURN TEMPLATE WITH DATA
    return render_template("/stocks.html",
        date=current_date,
        data=data,
        stocks_total=stocks_total,
        positions=positions)

def update_positions():
    print("UPDATING POSITIONS...")

    #GET PRICES FROM API AND UPDATE PRICES / GAIN
    tickers = []
    costs = []
    quantities = []
    total = 0
    rows = db.execute("SELECT * FROM positions")
    for row in rows:
        tickers.append(row['ticker'])
        costs.append(row['cost'])
        quantities.append(row['quantity-owned'])

    for ticker, cost, quantity in zip(tickers, costs, quantities):

        try:
            price = round(float(get_price(ticker)), 3)
        except:
            print('ERROR--%s--' % ticker)
            continue
        gain = round((float(price) * quantity) - cost, 3)
        total += price
        db.execute("UPDATE positions SET price = ? WHERE ticker = ?", (price, ticker))
        db.execute("UPDATE positions SET gain = ? WHERE ticker = ?", (gain, ticker))


def update_stocks(last_accessed):
    print("UPDATING STOCKS...")
    #ITERATE THROUGH DATES

    date_format = "%m/%d/%Y"
    cd = datetime.datetime.strptime(current_date, date_format)
    la = datetime.datetime.strptime(last_accessed, date_format)

    d =  cd - la
    days = d.days
    print(days)

    for i in range(days):
        date = la + datetime.timedelta(days= i + 1)
        print(date)
        #GET TIMESTAMP FOR TOTAL
        timestamp = datetime.datetime.timestamp(date) * 1000
        print(timestamp)

        #GET TICKERS
        tickers = []
        quantities = []
        total = 0
        rows = db.execute("SELECT * FROM positions")
        for row in rows:
            tickers.append(row['ticker'])
            quantities.append(row['quantity-owned'])

        #GET PRICE OF EACH STOCK AND UPDATE TOTAL AT EACH DATE
        for ticker, quantity in zip(tickers, quantities):
            try:
                price = round(float(get_price(ticker, get_date(date.year, date.month, date.day))), 3)
                total += price * quantity
            except:
                total = None
        if total is not None:
            db.execute("INSERT INTO stocks (Date, Balance) VALUES(?, ?)", (timestamp, round(total)))
            db.execute("INSERT INTO totals (date, location, balance) VALUES(?, ?, ?)", (timestamp, 'stocks', round(total)))

    #UPDATE LAST ACCESSED
    with open('last_accessed.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(current_date.split())


@app.route("/savings", methods=["GET"])
def get_savings():

    #GET DATA FROM DATA BASE
    values = []         #needed to get latest balance
    data = []           #data for chart
    rows = db.execute("SELECT * FROM savings")
    for row in rows:
        values.append(row['balance'])
        data.append([row['date'], row['balance']])
    #print(data)

    #SAVINGS TOTAL
    savings_total = values[-1]

    return render_template("/savings.html", data = data, savings_total=savings_total)


@app.route("/update_savings", methods=["POST"])
def update_savings():

    #GET DATA FROM FORM
    new_amount = request.form.get("new_amount")
    deposit = request.form.get("deposit")
    withdrawl = request.form.get("withdrawl")

    #GET TIMESTAMP FOR DATA
    timestamp = (datetime.datetime.now().timestamp() * 1000)

    #GET LATEST BALANCE
    values = []
    rows = db.execute("SELECT * FROM savings")
    for row in rows:
        values.append(row['balance'])

    #BOOLEAN TO DEAL WITH DEPOSIT WITHDRAWL OR TOTAL
    if new_amount and not deposit and not withdrawl:
        total = int(new_amount)
    elif not new_amount and deposit and not withdrawl:
        total = values[-1] + int(deposit)
    elif not new_amount and not deposit and withdrawl:
        total = values[-1] - int(withdrawl)
    else:
        return render_template("/error.html")

    #INSERT DATA INTO DATABASE
    db.execute("INSERT INTO savings (Date, Balance) VALUES(?, ?)", (timestamp, total))
    db.execute("INSERT INTO totals (date, location, balance) VALUES(?, ?, ?)", (timestamp, 'savings', total))


    return redirect('/savings')


@app.route("/wallet", methods=["GET"])
def get_wallet():

    #GET DATA FROM DATA BASE
    values = []         #needed to get latest balance
    data = []           #data for chart
    rows = db.execute("SELECT * FROM wallet")
    for row in rows:
        values.append(row['balance'])
        data.append([row['date'], row['balance']])
    #print(data)

    #WALLET TOTAL
    wallet_total = values[-1]

    return render_template("/wallet.html", data = data, wallet_total=wallet_total)


@app.route("/update_wallet", methods=["POST"])
def update_wallet():

    #GET DATA FROM FORM
    new_amount = request.form.get("new_amount")
    deposit = request.form.get("deposit")
    withdrawl = request.form.get("withdrawl")

    #GET TIMESTAMP FOR DATA
    timestamp = (datetime.datetime.now().timestamp() * 1000)

    #GET LATEST BALANCE
    values = []
    rows = db.execute("SELECT * FROM wallet")
    for row in rows:
        values.append(row['balance'])

    #BOOLEAN TO DEAL WITH DEPOSIT WITHDRAWL OR TOTAL
    if new_amount and not deposit and not withdrawl:
        total = int(new_amount)
    elif not new_amount and deposit and not withdrawl:
        total = values[-1] + int(deposit)
    elif not new_amount and not deposit and withdrawl:
        total = values[-1] - int(withdrawl)
    else:
        return render_template("/error.html")

    #INSERT DATA INTO DATABASE
    db.execute("INSERT INTO wallet (Date, Balance) VALUES(?, ?)", (timestamp, total))
    db.execute("INSERT INTO totals (date, location, balance) VALUES(?, ?, ?)", (timestamp, 'wallet', total))

    return redirect('/wallet')


@app.route("/testing", methods=["GET"])
def test():

    #GET DATA FROM DATABASE FOR CHART
    stock_data = []
    savings_data = []
    wallet_data = []
    rows = db.execute("SELECT * FROM totals")
    for row in rows:
        if row['location'] == 'stocks':
            stock_data.append([row['date'], row['balance']])
        if row['location'] == 'savings':
            savings_data.append([row['date'], row['balance']])
        if row['location'] == 'wallet':
            wallet_data.append([row['date'], row['balance']])

    return render_template("/testing.html", stock_data=stock_data, savings_data=savings_data, wallet_data=wallet_data)
