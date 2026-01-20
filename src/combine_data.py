import pandas as pd
import os

directory = 'output/tables/team_GS'

df = pd.DataFrame()

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    
    team_df = pd.read_csv(file_path)

    team_df['team'] = filename[:3]

    df = pd.concat([df, team_df], ignore_index=True)

df.to_csv('output/tables/ALL_GS_data.csv')