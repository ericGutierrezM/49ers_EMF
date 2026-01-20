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

# --- 1. SETUP FUNCTION (Auto-Restart Capability) ---
def init_driver():
    options = Options()
    # options.add_argument("--headless=new") # Uncomment to run invisibly
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false") # Block images for speed
    options.page_load_strategy = 'eager' 
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(20) # Kill if page load > 20s
    return driver

# Initialize Driver
driver = init_driver()

link = "https://www.pro-football-reference.com/teams/"

teams = ['nwe','buf','mia','nyj','jax','htx','clt','oti','pit','rav','cin', 
         'cle','den','sdg','kan','rai','phi','dal','was','nyg','car','tam',
         'atl','nor','chi','gnb','det','min','sea','ram','sfo','crd']

print("Starting robust GS scraper...")

for team in teams:
    print(f'--- Processing {team} ---')
    
    team_years_data = []

    years = list(range(1960, 2025))
    i = 0
    
    while i < len(years):
        year = years[i]
        
        try:
            time.sleep(random.uniform(2.0, 3.5))
            
            driver.get(f"{link}{team}/{year}_roster.htm")

            if "Page Not Found" in driver.title:
                team_years_data.append({'year': year, 'GS_mean': np.nan})
                i += 1
                continue

            html = driver.page_source.replace('', '')
            
            try:
                dfs = pd.read_html(io.StringIO(html), attrs={'id': 'starters'}, flavor='html5lib')
            except ValueError:
                print(f"  [Skip] {year} (Table not found)")
                team_years_data.append({'year': year, 'GS_mean': np.nan})
                i += 1
                continue

            if not dfs:
                team_years_data.append({'year': year, 'GS_mean': np.nan})
                i += 1
                continue

            df = dfs[0]
            
            if 'GS' not in df.columns:
                print(f"  [Warn] {year} ('GS' column missing)")
                team_years_data.append({'year': year, 'GS_mean': np.nan})
                i += 1
                continue

            df['GS'] = pd.to_numeric(df['GS'], errors='coerce')
            
            df_clean = df.dropna(subset=['GS'])
            
            if not df_clean.empty:
                mean_gs = df_clean['GS'].mean()
                team_years_data.append({'year': year, 'GS_mean': mean_gs})
                print(f"  [OK] {year}: {mean_gs:.2f}")
            else:
                team_years_data.append({'year': year, 'GS_mean': np.nan})

            i += 1

        except (WebDriverException, ReadTimeoutError, TimeoutException) as e:
            print(f"!! CRASH on {team} {year}. Restarting Driver... !!")
            try:
                driver.quit()
            except:
                pass
            time.sleep(5)
            driver = init_driver()
            print("!! Restarted. Retrying... !!")

    avg_GS = pd.DataFrame(team_years_data)
    
    avg_GS['moving_avg'] = avg_GS['GS_mean'].rolling(window=4, min_periods=1).mean()


    output_path = f'output/tables/team_GS/{team}_GS.csv'
    avg_GS.to_csv(output_path, index=False)
    print(f"Saved {output_path}")

driver.quit()