import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fbprophet import Prophet
from io import StringIO
from io import BytesIO
import base64
plt.style.use('fivethirtyeight')
from fbprophet.diagnostics import performance_metrics
from fbprophet.diagnostics import cross_validation, performance_metrics
from fbprophet.plot import plot_cross_validation_metric

def analysis(df):
    #df = pd.read_csv('./doc/all_stocks_5yrBTC-USDT_stock_data.csv')
    img = BytesIO() 
    plt.figure()  # needed to avoid adding curves in plot
    plt.plot(df.index, df['Close'])
    plt.title("Closing price")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

def plot(x):
    img = BytesIO()
    plt.figure()  # needed to avoid adding curves in plot
    plt.title("Forcasting for 60 days")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    return graph_url 

def CleanData(df):
    df.reset_index(inplace=True)
    p_df = df.drop(['Open', 'High', 'Low','Volume', 'Adj Close'], axis=1)
    p_df.rename(columns={'Close': 'y', 'Date': 'ds'}, inplace=True)
    return p_df

def Ph(df):
    df = CleanData(df)
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    return model, forecast

def PlotPhModel(df):
    model, forecast = Ph(df)
    img = BytesIO()
   # sns.set_style("dark") 
    plt.figure()  # needed to avoid adding curves in plot
    model.plot(forecast, xlabel='Date', ylabel='Price (USD)')
    
    plt.title('Price Forecast (USD)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    return graph_url 

def PlotPhComp(df):
    model, forecast = Ph(df)
    img = BytesIO()
    plt.figure()  # needed to avoid adding curves in plot
    model.plot_components(forecast)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    return graph_url 


    

 

    
