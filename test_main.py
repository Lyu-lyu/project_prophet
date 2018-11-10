from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Date, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import func
from datetime import datetime
from prophet_last import create_forecast
from collecting_data_sql2 import check_forecast, save_forecast_array, ticker_renew
import sqlite3
from yahoofinancials import YahooFinancials


Base = declarative_base()
engine = create_engine('sqlite:///stock_base.db')
Base.metadata.create_all(bind=engine)
db_session = scoped_session(sessionmaker(bind=engine))
Base.query = db_session.query_property()


def ask_user():
    tick = input('Введите тикер: ').upper()
    if check_forecast(engine,tick):
        print('Есть прогноз')
    
    else:
        ticker_renew(tick)
        print('Нет прогноза, подождите')
        create_forecast(tick)
        print('Нет прогноза, подождите')
    return tick


def give_list_of_tickers():
    engine = create_engine('sqlite:///stock_base.db') 
    result = engine.execute('select distinct tick from tickers')
    print('Есть данные по следующим тикерам:')   
    for row in result:
        print(row.tick)
    

def give_forecast_table (tick):
    engine = create_engine('sqlite:///stock_base.db') 
    forecast_table = engine.execute('select * from forecasts where tick =?', tick)
    return forecast_table
    
def give_mistakes_table (tick):
    engine = create_engine('sqlite:///stock_base.db') 
    mistakes_table = engine.execute ('select tick, mse, rmse, mae, mape, coverage from mistakes where tick = ?', tick)
    return mistakes_table


def give_graph (tick):
    graph_name = '{}.png'.format(tick.upper())
    graph_read = open('/home/luda/project/' + graph_name, 'rb')
    return graph_read


def main():
    
    give_list_of_tickers()
    
    tick=ask_user()    
    future = give_forecast_table(tick)
    mistakes = give_mistakes_table(tick)
    pic = give_graph(tick)
    for row in mistakes: 
        print (row) 

if __name__ == '__main__':
    main()