'''
This is purposely verbose so you can see what your options might be.
'''
'''
This is purposely verbose so you can see what your options might be.
'''

import csv
import certifi
import datetime
import urllib.request

base_url = 'https://query1.finance.yahoo.com/v7/finance/download'


def get_data(symbol, start, end, interval='1d', events='history'):
    url = '%s/%s?period1=%s&period2=%s&interval=%s&events=%s' % (
        base_url, symbol, int(start), int(end), interval, events
    )
    data = urllib.request.urlopen(url, cafile=certifi.where())
    datalines = [str(line) for line in data]
    print(url)

    return csv.DictReader(datalines)

def get_date(year, month, day):
    # you'll notice I moved the int-ing to get_data

    # after some inspection, I found that the timestamps Yahoo uses
    # are set to 1:41:12
    # I'm not sure if the time is significant, but setting them
    # explicitly to midnight didn't help, so I tried 13, 41, 12
    # AND IT WORKED!
    # :)
	return datetime.datetime.timestamp(
	           datetime.datetime(year, month, day, 13, 41, 12)
	       )

#GET CURRENT DATE
exact_date = datetime.datetime.today()

s_year, s_month, s_day = exact_date.year, exact_date.month, exact_date.day
e_year, e_month, e_day = exact_date.year, exact_date.month, exact_date.day

start_date = get_date(s_year, s_month, s_day)
end_date = get_date(e_year, e_month, e_day)

#data = get_data('NFLX', start_date, end_date)

'''
Note that you can also do something like

m, d, y = map(int '4/14/2020'.split('/'))

start_date = get_date(y, m, d)
'''

'''
print(data.fieldnames)

while True:
    try:
        datum = next(data)

        print(datum['Open'])
    except StopIteration:
        break
'''
'''
data is an iterable of ordered dicts (the type returned by the DictReader)
you can iterate over them in any way you are used to

for datum in data: # for example

or the more typical way to iterate over something like this is

while True:
    try:
        datum = next(data)
    except StopIteration:
        break


next is a builtin Python function that gives you the next item
it will raise a StopIteration error when the iterator is exhausted
so you just chedk for that and break out of the infinite loop

NOTE that when you get data for one day like this you only get one line

I think...

so you could just do

stock_data = next(data)

'''

def get_price(ticker, date = get_date(s_year, s_month, s_day)):
    try:
        data = get_data(ticker, date, date)
        datum = next(data)
        return(datum['Open'])

    except:
        print("COULD NOT GET PRICE for %s at %d" % (ticker, date))
        pass
