# Process portfolio while running
from multiprocessing import Process
# Get backend
from qiskit import Aer, execute, QuantumCircuit, ClassicalRegister, transpile
# Variational Quantum Eigensolvers
from qiskit.algorithms import VQE, QAOA
# Classical optimizers
from qiskit.algorithms.optimizers import COBYLA, SLSQP, ADAM
from qiskit_optimization.algorithms import MinimumEigenOptimizer

from qiskit.circuit import Parameter, ParameterVector

from qiskit_finance.applications.optimization import PortfolioOptimization

from qiskit.circuit.library import TwoLocal
from qiskit.utils import QuantumInstance
from qiskit_optimization import QuadraticProgram
# Load stock data
from qiskit_finance.data_providers import *
# For running on real device
from qiskit.providers.ibmq import IBMQ

import numpy as np
import pandas as pd
import datetime
from qiskit_optimization.algorithms.minimum_eigen_optimizer import MinimumEigenOptimizationResult

import quandl

from app import config, mongodb, stocks

quandl.ApiConfig.api_key = config['QUANDL_API_TOKEN']
    
def generate_portfolio(user_id):
    tickers, budget = get_user_portfolio_settings(user_id)

    num_assets = len(tickers)
    data = WikipediaDataProvider(
        token=quandl.ApiConfig.api_key,
        tickers=tickers,
        end=stocks.get_date(is_datetime=True)
    )
    data.run()

    mu = data.get_period_return_mean_vector()
    sigma = data.get_period_return_covariance_matrix()

    q = .5
    penalty = num_assets

    portfolio = PortfolioOptimization(expected_returns=mu, covariances=sigma, risk_factor=q, budget=budget)
    qp = portfolio.to_quadratic_program()

    backend = Aer.get_backend('statevector_simulator')

    adam = ADAM()
    adam.set_options(maxiter=250)
    quantum_instance = QuantumInstance(backend=backend)
    qaoa_mes = QAOA(optimizer=adam, reps=3, quantum_instance=quantum_instance)
    qaoa = MinimumEigenOptimizer(qaoa_mes)
    result = qaoa.solve(qp)
    add_portfolio(user_id, result)

def get_user_portfolio_settings(user_id):
    portfolio_settings = mongodb.get_portfolio_settings(user_id)
    return portfolio_settings['stocks'], portfolio_settings['optimize_count']

def add_portfolio(user_id, result):
    which_stocks = get_user_portfolio_settings(user_id)[0]
    possible_stocks = list(which_stocks)
    for i in range(len(which_stocks) - 1, -1, -1):
        if result.x[i] == 0:
            which_stocks.pop(i)
    portfolio_json = {
        'date': stocks.get_date(),
        'status': 'complete',
        'chosen_stocks': which_stocks,
        'possible_stocks': possible_stocks,
        'optimal_value': list(result.x),
        'optimal_function_value': result.fval
    }
    mongodb.add_optimized_portfolio(user_id, opt_portfolio=portfolio_json)
    # print(portfolio_json)

def create_add_portfolio(user_id):
    possible_stocks = get_user_portfolio_settings(user_id)[0]
    portfolio_json = {
        'date': stocks.get_date(),
        'status': 'pending',
        'possible_stocks': possible_stocks,
    }
    mongodb.add_optimized_portfolio(user_id, pending_portfolio=portfolio_json)
    p = Process(target=generate_portfolio, args=(user_id,))
    p.start()


# print(f'selected: {new_port.x}, value: {new_port.fval}')