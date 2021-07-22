# Run in async
import asyncio
# Get backend
from qiskit import Aer
# Variational Quantum Eigensolvers
from qiskit.algorithms import VQE, QAOA
# Classical optimizers
from qiskit.algorithms.optimizers import COBYLA, ADAM
from qiskit_optimization.algorithms import MinimumEigenOptimizer

from qiskit.circuit.library import TwoLocal
from qiskit.utils import QuantumInstance
from qiskit_finance.applications.optimization import PortfolioOptimization
# Load stock data
from qiskit_finance.data_providers import *
# For running on real device
from qiskit.providers.ibmq import IBMQ

import numpy as np
import pandas as pd
import datetime

import quandl