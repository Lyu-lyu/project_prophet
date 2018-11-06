from yahoofinancials import YahooFinancials
from datetime import date, timedelta
from sqlalchemy import create_engine, Column, Date, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
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
        return '<Ticker {} {}>'.format(self.formatted_date, self.close)

class Forecast(Base):
    __tablename__ = 'forecasts'
    id = Column(Integer, primary_key=True)
    tick = Column(String(6))
    future_date = Column(Date)
    yhat = Column(Float)
    
    def __init__(self, ticker_name, future_date=None, yhat=None):
        self.tick = ticker_name
        self.yhat = yhat
        self.future_date = future_date

    def __repr__(self):
        return '<Forecast {} {} {}>'.format(self.tick, self.future_date, self.yhat)
    
class Mistake(Base):
    __tablename__ = 'mistakes'
    id = Column(Integer, primary_key=True)
    tick = Column(String(6))
    mse = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)
    mape = Column(Float)
    coverage = Column(Float)
    graph_name = Column(String(100))

    def __init__(self, ticker_name, mse=None, rmse=None, mae=None, mape=None, coverage=None, graph_name=None):
        self.tick = ticker_name
        self.mse = mse
        self.rmse = rmse
        self.mae = mae
        self.mape = mape 
        self.coverage=coverage
        self.graph_name=graph_name

    def __repr__(self):
        return '<Mistake {} {} {} {} {} {} {} {}>'.format(self.tick, self.mse, self.rmse, self.mae, self.mape, self.coverage, self.graph_name)


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

def save_forecast_array(forecast_array,ticker_name):

    Base.metadata.create_all(bind=engine)
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    
    Forecast.query.filter(Forecast.tick==ticker_name).delete()
    db_session.commit()

    for f in forecast_array: 
        save_forecast(engine, ticker_name, f[0], f[2])

def save_forecast (engine, ticker_name, future_date, yhat):

    Base.metadata.create_all(bind=engine)
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()

    row = Forecast (ticker_name, future_date, yhat)
    db_session.add(row)
    db_session.commit()

def check_forecast(engine,ticker_name):
    
    Base.metadata.create_all(bind=engine)
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    today = date.today()
    delta = timedelta(20)
    date_20= today + delta   
    result = Forecast.query.filter(Forecast.tick==ticker_name).order_by(Forecast.future_date.desc()).first()
        
    if result is not None and result.future_date >= (date_20):
        return True
    else:
        return False

def save_mistakes_e (engine, ticker_name, mse, rmse, mae, mape, coverage, graph_name):
    
    Base.metadata.create_all(bind=engine)
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    Mistake.query.filter(Mistake.tick==ticker_name).delete()
    db_session.commit()

    row = Mistake (ticker_name, mse, rmse, mae, mape, coverage, graph_name)
    db_session.add(row)
    db_session.commit()

def main():

    engine = create_engine('sqlite:///stock_base.db') 
    result = engine.execute('select distinct tick from tickers')
    print('Есть данные по следующим тикерам:')   
    for row in result:
        print(row.tick)
    #     ticker_renew(row.tick)
    
    tick = input('Введите тикер: ').upper()
    if check_forecast(engine,tick):
        print('Есть прогноз')
    else:
        print('Нет прогноза')
        
   
if __name__ == '__main__':
    main()