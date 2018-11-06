from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Date, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import func
from datetime import datetime
from prophet_last import create_forecast
from collecting_data_sql2 import check_forecast, save_forecast_array, ticker_renew

Base = declarative_base()
engine = create_engine('sqlite:///stock_base.db')
Base.metadata.create_all(bind=engine)
db_session = scoped_session(sessionmaker(bind=engine))
Base.query = db_session.query_property()


def main():

    engine = create_engine('sqlite:///stock_base.db') 
    result = engine.execute('select distinct tick from tickers')
    print('Есть данные по следующим тикерам:')   
    for row in result:
        print(row.tick)
    #   ticker_renew(row.tick)
    
    tick = input('Введите тикер: ').upper()
    if check_forecast(engine,tick):
        print('Есть прогноз')
    else:
        ticker_renew(tick)
        print('Нет прогноза')
        create_forecast(tick)
        print('Нет прогноза')
if __name__ == '__main__':
    main()