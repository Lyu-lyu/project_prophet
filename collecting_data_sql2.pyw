import json, csv
from yahoofinancials import YahooFinancials
from datetime import date, timedelta
from sqlalchemy import create_engine, Column, Date, Integer, String, Float
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///stock_base.db')
Base.metadata.create_all(bind=engine)
db_session = scoped_session(sessionmaker(bind=engine))
Base.query = db_session.query_property()

class Ticker(Base):
    __tablename__ = 'tickers'
    id = Column(Integer, primary_key=True)
    tick = Column(String(5))
    formatted_date = Column(Date)
    close = Column(Float)

    def __init__(self, ticker_name, date=None, close=None):
        self.tick = ticker_name
        self.close = close
        self.formatted_date = date
        if date is not None:
            self.formatted_date = datetime.strptime(date, '%Y-%m-%d')
     
    def get_ticker_data(self, start_date, today):
        yahoo_financials = YahooFinancials(self.tick) #taking rates by company ticker  
        js_array = yahoo_financials.get_historical_price_data(start_date, today, 'daily') #getting all history data
        price_array = js_array[self.tick]['prices']
        return price_array
    
    def __repr__(self):
        return '<Ticker {} {} {}>'.format(self.formatted_date, self.close)

    
def save_to_file(ticker, spreadsheet):
    filename = '{}.csv'.format(ticker)
    with open (filename, 'w', encoding = 'utf-8', newline = '') as file_data:
        fields = ['formatted_date', 'close']
        writer = csv.DictWriter(file_data, fields, delimiter=';',extrasaction='ignore')
        writer.writeheader()
        for price_str in spreadsheet:
            writer.writerow(price_str)

def ticker_renew(ticker):
    Base.metadata.create_all(bind=engine)
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    t = Ticker(ticker_name=ticker)
    today = date.today().strftime('%Y-%m-%d')
    first_string = t.query.filter(Ticker.tick == t.tick).order_by(Ticker.formatted_date.desc()).first()
    if first_string == None: 
        start_date = '2000-01-01'
    else:
        start_date = (first_string.formatted_date + timedelta(1)).strftime('%Y-%m-%d') 

    prices = t.get_ticker_data(start_date, today)
    for i in prices:
        date_for_search = datetime.strptime(i['formatted_date'], '%Y-%m-%d').date()
        db_data = t.query.filter(Ticker.tick == t.tick, Ticker.formatted_date == date_for_search).first()
        if db_data == None: 
            tmp = Ticker(ticker_name = t.tick, date = i['formatted_date'], close = i['close'])
            # поиск в базе тикера с наибольшей датой и сравнение даты с today. Дозапись в базу отсутствующих данных. 
            db_session.add(tmp)
                
    db_session.commit()


def main():
    engine = create_engine('sqlite:///stock_base.db') 
    result = engine.execute('select distinct tick from tickers')
    print('Есть данные по следующим тикерам:')   
    for row in result:
        print(row.tick)
        ticker_renew(row.tick)
    #tick = input('Введите тикер: ').upper()
    #ticker_renew(tick)

if __name__ == '__main__':
    main()