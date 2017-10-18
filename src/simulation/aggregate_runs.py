"""
Call from command line, point towards a folder

python aggregate_runs.py -i /mnt/md0/network_sampling_data/stats -o /mnt/md0/network_sampling_data/dfs/output.tsv

python aggregate_runs.py -i /home/geb97/network-sampling/sim_output/stats -o /mnt/md0/network_sampling_data/outfile.tsv

python aggregate_runs.py -i /Users/g/Documents/network-sampling/stats -o /Users/g/Documents/network-sampling/dfs/output.tsv

import pickle
import pandas as pd
all_records = []

with open('/mnt/md0/network_sampling_data/stats/pokec_graph.p', 'rb') as f:
    records = pickle.load(f)
    all_records.extend(records)

df = pd.DataFrame(all_records)
df.to_csv('/mnt/md0/network_sampling_data/dfs/pokec_graph.tsv', sep='\t')
"""
import click
import glob
import pickle
import pandas as pd

@click.command()
@click.option('--input-path', '-i')
@click.option('--output_file', '-o')
def agg(input_path: str, output_file: str):
    all_records = []

    flist = glob.glob(input_path + '/*.p')
    for idx, fname in enumerate(flist):
        click.echo('Parsing file {}'.format(fname))
        with open(fname, 'rb') as f:
            records = pickle.load(f)
            for record in records:
                record['graph_idx'] = idx
            all_records.extend(records)

    df = pd.DataFrame(all_records)
    df.to_csv(output_file, sep='\t')

if __name__ == '__main__':
    agg()
