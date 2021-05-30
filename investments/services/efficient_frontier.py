import numpy as np
import datetime as dt
from numpy.core.fromnumeric import mean
from numpy.lib.function_base import cov
from pandas_datareader import data as pdr
from scipy.linalg.special_matrices import convolution_matrix 
import scipy.optimize as sc
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as opy

def get_data(stocks, start, end):
    stock_data = pdr.get_data_yahoo(stocks, start=start, end=end)
    stock_data = stock_data['Close']

    returns = stock_data.pct_change()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    return mean_returns, cov_matrix

def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns*weights)*252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return returns, std

def negative_sr(weights, mean_returns, cov_matrix, risk_free_rate = 0):
    p_returns, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
    return - (p_returns - risk_free_rate)/p_std

def adjust_weights(weights):
    sum_weights = np.sum(np.array(weights))
    return [weight / sum_weights for weight in weights]

def portfolio_variance(weights, mean_returns, cov_matrix):
    return portfolio_performance(weights, mean_returns, cov_matrix)[1]

def portfolio_return(weights, mean_returns, cov_matrix):
    return portfolio_performance(weights, mean_returns, cov_matrix)[0]

def maximize_sr(mean_returns, cov_matrix, risk_free_rate = 0, constraint_set=(0, 1)):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    result = sc.minimize(negative_sr, num_assets*[1./num_assets], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return result

def minimize_variance(mean_returns, cov_matrix, risk_free_rate = 0, constraint_set=(0, 1)):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    result = sc.minimize(portfolio_variance, num_assets*[1./num_assets], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return result 

def get_results(func, mean_returns, cov_matrix, risk_free_rate = 0, constraint_set=(0, 1)):
    portfolio = func(mean_returns, cov_matrix, risk_free_rate)
    returns, std = portfolio_performance(portfolio['x'], mean_returns, cov_matrix)
    allocation = pd.DataFrame(portfolio['x'], index = mean_returns.index, columns=['allocation'])
    return returns, std, allocation

def efficient_optimization(mean_returns, cov_matrix, return_target, constraint_set=(0, 1)):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = (
        {'type': 'eq', 'fun': lambda x: portfolio_return(x, mean_returns, cov_matrix) - return_target},
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    )
    bound = constraint_set
    bounds = tuple(bound for asset in range(num_assets))
    eff_opt = sc.minimize(portfolio_variance, num_assets*[1./num_assets], args=args, method="SLSQP", bounds=bounds, constraints=constraints)
    return eff_opt

def calculated_results(mean_returns, cov_matrix, risk_free_rate = 0, constraint_set=(0,1)):
    max_sr_returns, max_sr_std, max_sr_allocation = get_results(maximize_sr, mean_returns, cov_matrix, risk_free_rate, constraint_set)
    min_vol_returns, min_vol_std, min_vol_allocation = get_results(minimize_variance, mean_returns, cov_matrix, risk_free_rate, constraint_set)

    target_returns = np.linspace(min_vol_returns, max_sr_returns, 20)
    efficient_list = []
    for target in target_returns:
        efficient_list.append(efficient_optimization(mean_returns, cov_matrix, target)['fun'])

    max_sr_returns, max_sr_std = round(max_sr_returns*100, 2), round(max_sr_std*100, 2)
    min_vol_returns, min_vol_std = round(min_vol_returns*100, 2), round(min_vol_std*100, 2)

    return max_sr_returns, max_sr_std, max_sr_allocation, min_vol_returns, min_vol_std, min_vol_allocation, efficient_list, target_returns

def ef_graph(mean_returns, cov_matrix, returns, std, risk_free_rate = 0, constraint_set=(0, 1)):
    max_sr_returns, max_sr_std, max_sr_allocation, min_vol_returns, min_vol_std, min_vol_allocation, efficient_list, target_returns = calculated_results(mean_returns, cov_matrix, risk_free_rate, constraint_set)

    max_sharpe_ratio = go.Scatter(
        name='Maximum Sharpe Ratio',
        mode='markers',
        x=[max_sr_std],
        y=[max_sr_returns],
        marker=dict(color='red', size=14, line=dict(width=3, color='black'))
    )

    min_vol_ratio = go.Scatter(
        name='Minimum Volatility',
        mode='markers',
        x=[min_vol_std],
        y=[min_vol_returns],
        marker=dict(color='green', size=14, line=dict(width=3, color='black'))
    )

    current_portfolio = go.Scatter(
        name='Current Portfolio',
        mode='markers',
        x=[std],
        y=[returns],
        marker=dict(color='blue', size=14, line=dict(width=3, color='black'))
    )

    ef_curve = go.Scatter(
        name='Efficient Frontier',
        mode='lines',
        x=[round(ef_std*100, 2) for ef_std in efficient_list],
        y=[round(target*100, 2) for target in target_returns],
        line=dict(color='black', width=4, dash='dashdot')
    )

    data = [max_sharpe_ratio, min_vol_ratio, ef_curve, current_portfolio]
    layout = go.Layout(
        title = 'Portfolio optitmisation',
        yaxis = dict(title='Annualised Return (%)'),
        xaxis = dict(title= 'Annualised Volatility (%)'),
        showlegend = True,
        legend = dict(
            x = 0.75, y = 0, traceorder = 'normal',
            bgcolor='#e2e2e2',
            bordercolor='black',
            borderwidth=2
        ),
        width=800,
        height=600
    )
    fig = go.Figure(data=data, layout=layout)
    div = opy.plot(fig, auto_open=False, output_type='div')
    return div


def trace_by_time(stocks, weights, years = 1):
    weights = adjust_weights(weights)
    weights = np.array(weights)
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days = 365 * years)
    mean_returns, cov_matrix = get_data(stocks, start=start_date, end=end_date)

    returns, std = portfolio_performance(weights, mean_returns, cov_matrix) 
    returns, std = round(returns*100, 2), round(std*100, 2)

    return ef_graph(mean_returns, cov_matrix, returns, std, 0.05)


# stocks = ['EZTC3.SA', 'WEGE3.SA', 'TEND3.SA', 'EGIE3.SA', 'ITSA3.SA', 'FLRY3.SA', 'MGLU3.SA', 'B3SA3.SA', 'ENBR3.SA', 'ABEV3.SA', 'COKE', 'GOOGL', 'AMZN']
# weights = [1.48, 1.63, 1.71, 2.13, 2.09, 2.03, 1.91, 1.86, 1.76, 2, 0.96, 5.77, 5.77]

# stocks = ['WIZS3.SA', 'ITSA4.SA', 'PSSA3.SA', 'ITUB4.SA', 'B3SA3.SA', 'XP', 'T', 'BRK-B', 'MCD', 'FPE', 'JNK', 'VOO', 'GOOGL', 'VYM']
# weights = [1.88, 2.26, 2.63, 3.01, 3.01, 1.29, 1.5, 1.61, 1.72, 1.72, 1.72, 1.93, 2.15, 2.15]

# trace_by_time(stocks, weights, 5)

