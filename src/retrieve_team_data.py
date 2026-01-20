import pandas as pd
import time
import io
import random
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib3.exceptions import ReadTimeoutError
from selenium.common.exceptions import WebDriverException, TimeoutException

def init_driver():
    options = Options()
    # options.add_argument("--headless=new") # Uncomment to hide browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager'
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(20) 
    return driver

driver = init_driver()

teams = ['nwe','buf','mia','nyj','jax','htx','clt','oti','pit','rav','cin','cle','den',
         'sdg','kan','rai','phi','dal','was','nyg','car','tam',
         'atl','nor','chi','gnb','det','min','sea','ram','sfo','crd']

link = "https://www.pro-football-reference.com/teams/"

print("Starting robust scraper...")

for team in teams:
    print(f'--- Processing {team} ---')
    team_data = []
    
    years = list(range(1960, 2025))
    i = 0
    
    while i < len(years):
        year = years[i]
        
        try:
            time.sleep(random.uniform(2.0, 3.5))
            
            driver.get(f"{link}{team}/{year}.htm")

            if "Page Not Found" in driver.title:
                i += 1
                continue

            html = driver.page_source.replace('', '')
            
            try:
                dfs = pd.read_html(io.StringIO(html), attrs={'id': 'team_stats'}, header=[0, 1], flavor='html5lib')
            except ValueError:
                print(f"  [Skip] {year} (No table)")
                i += 1
                continue

            if not dfs:
                i += 1
                continue

            df = dfs[0]
            
            new_cols = []
            for col in df.columns:
                if "Unnamed" in str(col[0]): 
                    new_cols.append(col[1])
                else:
                    new_cols.append(f"{col[0]}_{col[1]}")
            df.columns = new_cols

            label_col = df.columns[0]
            row = df[df[label_col].astype(str).str.contains("Team Stats", na=False)]
            
            if not row.empty:
                data = row.iloc[0].to_dict()
                data['season'] = year
                data['team'] = team
                team_data.append(data)
                print(f"  [OK] {year}")
            else:
                print(f"  [Warn] {year} (Row missing)")
            
            i += 1

        except (WebDriverException, ReadTimeoutError, TimeoutException) as e:
            print(f"!! DRIVER CRASHED on {team} {year}. Restarting... !!")
            print(f"Error: {e}")
            
            try:
                driver.quit()
            except:
                pass
            
            time.sleep(5)
            driver = init_driver()
            print("!! Driver restarted. Retrying year... !!")

    if team_data:
        pd.DataFrame(team_data).to_csv(f'output/tables/team_stats/{team}_team_data.csv', index=False)
        print(f"Saved {team}")

driver.quit()