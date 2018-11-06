import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics
from fbprophet.plot import plot_cross_validation_metric
from fbprophet.plot import add_changepoints_to_plot
import numpy as np
import pandas as pd
import json, csv
from sqlalchemy import create_engine
from collections import Sequence
from collecting_data_sql2 import save_forecast_array, save_mistakes_e


def create_forecast(tick):
    engine = create_engine('sqlite:///stock_base.db')
    df = pd.read_sql_query('select formatted_date, close from tickers where tick = :tick', engine, params={'tick':tick.upper()})
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df.ds)
    df['y'] = np.log(df['y'])
    m1 = Prophet(growth='linear', seasonality_mode='multiplicative', n_changepoints = 5, changepoint_prior_scale=0.01, changepoint_range = 0.8)
    m1.fit(df)
    #работает кросс-валидация и получаем таблицу df_p со значениями ошибок
    df_cv = cross_validation(m1, initial='1500 days', period='90 days', horizon = '50 days')
    df_p = performance_metrics(df_cv, rolling_window=1)

    n_forecast = 50
    future1 = m1.make_future_dataframe(periods=n_forecast)

    forecast1 = m1.predict(future1)
    forecast1 = forecast1[forecast1['ds'].dt.dayofweek < 5]

    #итоговая таблица с фактом и прогнозом forecast1_norm
    forecast1_norm = pd.concat([
            forecast1['ds'],
            np.exp(df['y']),
            np.exp(forecast1[['yhat', 'yhat_lower', 'yhat_upper']])
        ], axis=1)


    forecast_array=forecast1_norm.values[-50:]
    save_forecast_array(forecast_array, tick)
        #рисуем график и сохраняем в формате png
    forecast_graph = forecast1_norm.set_index('ds')
    n_history = 100
    forecast_graph[-n_history-n_forecast:-n_forecast][['yhat']].plot(figsize=(20, 5))
    plt.plot(forecast_graph[-n_forecast:].index, forecast_graph[-n_forecast:][['yhat']])
    plt.plot(forecast_graph[-n_history-n_forecast:-n_forecast].index, forecast_graph[-n_history-n_forecast:-n_forecast][['y']])
    plt.fill_between(forecast_graph[-n_forecast:].index, forecast_graph[-n_forecast:]['yhat_lower'], forecast_graph[-n_forecast:]['yhat_upper'], color='b', alpha=0.2)
    plt.xlabel('date')
    plt.ylabel('close price')
    plt.title('Prophet forecast')
    plt.legend(['smoothed time series', 'forecast time series', 'actual time series'], loc = 'upper left')
    graph_name = '{}.png'.format(tick.upper())
    plt.savefig(graph_name)
    r = df_p.values[0]
    save_mistakes_e(engine, tick, r[1], r[2], r[3], r[4], r[5], graph_name)
