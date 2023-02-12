"""
Main program for qPCR analysis application
"""

__author__ = 'Maitreya Venkataswamy'

from backend import load_data, compute
from frontend import make_barplot

df = compute(load_data('qPCR analysis template.xlsx'))

for p in df.target.unique():
    make_barplot(df, p)

import matplotlib.pyplot as plt
plt.show()


