import pandas as pd
import matplotlib.pyplot as plt

# Load the results CSV file
df = pd.read_csv('/Users/ayetirishith/Desktop/AIML PROJECT/outputs/results.csv')

# Convert non-numeric 'cost' values like 'FAIL' to NaN
df['numeric_cost'] = pd.to_numeric(df['cost'], errors='coerce')

# Group by map and algorithm to get mean and std dev for cost, nodes, and time
summary = df.groupby(['map', 'algo']).agg({
    'numeric_cost': ['mean', 'std'],
    'nodes': ['mean', 'std'],
    'time_s': ['mean', 'std']
}).reset_index()

# Rename columns for readability
summary.columns = ['map', 'algo', 'cost_mean', 'cost_std', 'nodes_mean', 'nodes_std', 'time_mean', 'time_std']

# Save summary table as CSV (optional)
summary.to_csv('outputs/summary_stats.csv', index=False)

# Create bar plots per map
for m in df['map'].unique():
    d = df[df['map'] == m]
    
    # Plot path cost
    plt.figure()
    plt.bar(d['algo'], d['numeric_cost'])
    plt.title(f'Path Cost Comparison: {m}')
    plt.ylabel('Cost')
    plt.xlabel('Algorithm')
    plt.tight_layout()
    plt.savefig(f'outputs/plot_cost_{m}.png')
    plt.close()
    
    # Plot nodes expanded
    plt.figure()
    plt.bar(d['algo'], d['nodes'])
    plt.title(f'Nodes Expanded: {m}')
    plt.ylabel('Nodes')
    plt.xlabel('Algorithm')
    plt.tight_layout()
    plt.savefig(f'outputs/plot_nodes_{m}.png')
    plt.close()
    
    # Plot runtime
    plt.figure()
    plt.bar(d['algo'], d['time_s'])
    plt.title(f'Execution Time: {m}')
    plt.ylabel('Time (s)')
    plt.xlabel('Algorithm')
    plt.tight_layout()
    plt.savefig(f'outputs/plot_time_{m}.png')
    plt.close()

