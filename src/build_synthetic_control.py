### Imports ###
import pandas as pd
import numpy as np
from scipy.optimize import minimize

### Setup ###
TREATMENT_YEAR = 1988
TREATED_TEAM = 'sfo'

data = pd.read_csv('output/tables/ALL_team_data.csv')
y = pd.read_csv('output/tables/ALL_GS_data.csv')

### Filter and Group data ###
data = data[data['season'] < TREATMENT_YEAR]

FEATURES = ['PF','Yds','Tot Yds & TO_Ply','Tot Yds & TO_Y/P','Tot Yds & TO_TO','FL','1stD',
            'Passing_Cmp','Passing_Att','Passing_Yds','Passing_TD','Passing_Int','Passing_NY/A',
            'Passing_1stD','Rushing_Att','Rushing_Yds','Rushing_TD','Rushing_Y/A','Rushing_1stD',
            'Penalties_Pen','Penalties_Yds','Penalties_1stPy']

grouped_data = data.groupby(['team'])[FEATURES].mean()
grouped_y = y.groupby(['team'])['GS_mean'].mean()

grouped_data = grouped_data.join(grouped_y).T

X_treated = grouped_data[TREATED_TEAM]
X_donors = grouped_data.drop([TREATED_TEAM], axis=1)

y_treated = y.pivot(index='year', columns='team', values='GS_mean')[TREATED_TEAM]
y_donors = y.pivot(index='year', columns='team', values='GS_mean').drop([TREATED_TEAM], axis=1)

y_donors = y_donors.dropna(axis=1)

teams_to_drop = [x for x in X_donors.columns if(x not in y_donors.columns) ]

X_donors = X_donors.drop(teams_to_drop, axis=1)

### Get optimal weights ###

def loss_w(W, X_donors, X_treated):
    X_synth = X_donors @ W
    error_w = X_synth - X_treated
    mse = (error_w**2).mean()

    return mse

n_donors = len(X_donors.columns)
w_start = [1/n_donors for _ in X_donors.columns]
bounds = [(0, 1) for _ in range(n_donors)]

cons = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

res = minimize(
    fun=loss_w,                
    x0=w_start,                
    args=(X_donors, X_treated),
    method='SLSQP',            
    bounds=bounds,             
    constraints=cons           
)

W_optimal = res.x

y_synthetic = y_donors @ W_optimal

y_synthetic.to_csv(f'output/{TREATED_TEAM}_synthetic.csv')