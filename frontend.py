"""
Functions and components for application frontend
"""

__author__ = 'Maitreya Venkataswamy'

import seaborn as sns
sns.set()
import matplotlib.pyplot as plt


# TODO: refactor this
def make_barplot(df, primer):
    fig = plt.figure()
    ax = fig.gca()

    sns.barplot(
        data=df.query('target == @primer'),
        x='cell_line',
        y='rq',
        hue='time',
        #palette='cubehelix',
        ax=ax
    )
    
    ax.set_title(primer)
    ax.set_xlabel('Cell Line')
    ax.set_ylabel('Relative Quantification')
    ax.legend(title='Time')

    return fig