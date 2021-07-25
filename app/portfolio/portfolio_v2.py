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

from app import config, stocks

quandl.ApiConfig.api_key = config['QUANDL_API_TOKEN']

def get_portfolio(tickers, budget, risk_factor):
    wiki = WikipediaDataProvider(
        token=quandl.ApiConfig.api_key,
        tickers=tickers,
        end=stocks.get_date(is_datetime=True)
    )
    wiki.run()
    n = len(tickers) # number of assets/stocks
    mu = wiki.get_period_return_mean_vector() # expected return for each assets/stocks (vector of length 'n')
    sigma = wiki.get_period_return_covariance_matrix() # covariances between assets/stocks (matrix of size 'n' X 'n')
    _budget = budget # number of assets/stocks to be selected out of 'n'
    q = risk_factor # set risk factor
    num_layers = 1

    gammas = ParameterVector('gamma', num_layers)
    betas = ParameterVector('beta', num_layers)
    gammas_dict = {parameter: np.random.random() for parameter in gammas}
    betas_dict = {parameter: np.random.random() for parameter in betas}
    param_dict = gammas_dict | betas_dict
    print(param_dict)

    # Create new QAOA Circuit
    portfolio_circuit = qaoa_circuit(mu, sigma, q, gammas, betas, num_layers)
    # Bind Parameters
    portfolio_bounded_circuit = portfolio_circuit.bind_parameters(param_dict)
    # Measure Qubits to Classical Bits
    portfolio_bounded_circuit.measure(range(n), range(n))
    # Get Backend
    backend = Aer.get_backend('qasm_simulator')
    # Create Job
    portfolio_job = execute(portfolio_bounded_circuit, backend, shots=1000000)
    portfolio_result = portfolio_job.result()

    # Remove results that don't meet budget
    portfolio_budgeted_result_counts = remove_nonbudget_states(portfolio_result.get_counts(), _budget)
    print(mu)
    print(sigma)
    print(portfolio_result.get_counts())
    print(portfolio_budgeted_result_counts)


def qaoa_circuit(mu: np.ndarray, sigma: np.ndarray, q: int, gammas, betas, reps: int=1):
    num_assets = len(mu)

    qaoa_circuit = QuantumCircuit(num_assets, num_assets)

    # Apply initial layer of Hadamard gates to all qubits
    qaoa_circuit.h(range(num_assets))

    # Outer loop to create each layer
    for rep in range(reps):
        # Apply RZ rotational gates from cost layer
        for i in range(num_assets):
            qaoa_circuit.rz((mu[i] + q * np.sum(sigma[i])) * gammas[rep], i)

        # Apply RZZ rotational gates for entangled qubit rotations from cost layer
        for i in range(num_assets):
            for j in range(num_assets):
                if i != j:
                    qaoa_circuit.rzz(q * .5 * sigma[i, j] * gammas[rep], i, j)

        # Apply single qubit X rotations with angle 2 * beta_i to all qubits
        qaoa_circuit.rx(2 * betas[rep], range(num_assets))

    return qaoa_circuit

def remove_nonbudget_states(states_counts: dict, budget: int):
    for i in range(len(states_counts.keys()) - 1, -1, -1):
        cnt = 0
        key = list(states_counts.keys())[i]
        for c in key:
            if c == '1':
                cnt += 1
        
        if cnt != budget:
            states_counts.pop(key)

    return states_counts