import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

TREATED_TEAM = 'sfo'
TREATMENT_YEAR = 1988
START_YEAR = 1960
END_YEAR = 2024
OUTPUT_DIR = Path('output/figs')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

real_df = pd.read_csv(f'output/tables/team_GS/{TREATED_TEAM}_GS.csv')
synth_df = pd.read_csv(f'output/{TREATED_TEAM}_synthetic.csv')
years = list(range(START_YEAR, END_YEAR + 1))

with plt.style.context('seaborn-v0_8-whitegrid'):
    
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)

    ax.plot(years, real_df['GS_mean'], 
            color='#1f77b4',
            linewidth=2.5, 
            label='Actual 49ers')

    ax.plot(years, synth_df['0'], 
            color='#d62728', 
            linestyle='--', 
            linewidth=2, 
            alpha=0.9,
            label='Synthetic Control (Counterfactual)')

    ax.axvline(TREATMENT_YEAR, color='black', linestyle='-', linewidth=1.5, alpha=0.8)
    
    ax.axvspan(TREATMENT_YEAR, END_YEAR, color="#FB7B7BFF", alpha=0.1, label='Substation Exposure')

    ax.annotate('49ers move near substation (1988)', 
                xy=(TREATMENT_YEAR, ax.get_ylim()[1] - 0.5),
                xytext=(TREATMENT_YEAR - 12, ax.get_ylim()[1] - 0.5),
                arrowprops=dict(arrowstyle='->', color='black'),
                fontsize=11, fontweight='bold', ha='center')

    ax.set_title(f'Synthetic Control Method: Impact of Substation on 49ers Health\n({START_YEAR}-{END_YEAR})', 
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_ylabel('Average Games Started (GS) per Player', fontsize=12)
    ax.set_xlabel('Year', fontsize=12)
    
    ax.legend(loc='lower left', frameon=True, framealpha=0.9, fontsize=11)

    ax.set_xlim(START_YEAR, END_YEAR)
    ax.tick_params(axis='both', which='major', labelsize=11)
    
    plt.tight_layout()

    output_path = OUTPUT_DIR / f'scm_{TREATED_TEAM}.png'
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")