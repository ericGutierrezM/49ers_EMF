import pandas as pd

real = pd.read_csv('output/tables/team_GS/sfo_GS.csv')
synthetic = pd.read_csv('output/sfo_synthetic.csv')

real = real[real['year']<1988]
synthetic = synthetic[synthetic['year']<1988]

diff = real['GS_mean'] - synthetic['0']

print(f'ATE: {round(diff.sum()/len(diff),2)}')