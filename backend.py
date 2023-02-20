"""
Functions for data manipulation
"""

__author__ = 'Maitreya Venkataswamy'

import pandas as pd
import numpy as np

COLUMN_TYPES = {
    'Well Position': str,
    'Sample': str,
    'Target': str,
    'Cq': float
}
NA_VALUES = ['Undetermined']


# # TODO: Refactor this
# primer_avg = {
#     'primer 1': 19,
#     'primer 2': 14,
#     'primer 3': 21,
#     'primer 4': 16,
#     'primer 5': 8,
#     'primer 6': 5,
#     'primer control': None
# }

def load_data(filename):
    df = pd.read_excel(
        filename,
        header=20,
        usecols=['Well Position', 'Sample', 'Target', 'Cq'],
        dtype=COLUMN_TYPES,
        na_values=NA_VALUES
    )

    df.columns = map(
        lambda s: s.lower().replace(' ', '_'),
        df.columns
    )

    return df


# TODO: Refactor this
def compute(df, primer_avg):
    control_primer = df.target.mode().iloc[0]

    df['cell_line'] = df['sample'].str.rpartition(' ')[0]
    df['time'] = df['sample'].str.rpartition(' ')[2]
    assert df.time.str.fullmatch(r'^D\d+$').all()

    def cq_control_column(dfn):
        assert len(dfn) == 2
        idx_control = dfn.query('target == @control_primer').index[0]
        assert(dfn.loc[idx_control].target == control_primer)
        dfn['cq_control'] = dfn.loc[idx_control].cq
        return dfn

    df = df.groupby('well_position', group_keys=False).apply(cq_control_column)

    df['delta_ct'] = df['cq'] - df['cq_control']

    df['primer_avg'] = df.target.map(primer_avg)

    df['rq'] = 2.0 ** (-1.0 * (df.delta_ct - df.primer_avg))

    return df