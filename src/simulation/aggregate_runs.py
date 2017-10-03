"""
Call from command line, point towards a folder

python aggregate_runs.py -i /mnt/md0/network_sampling_data/sim_output_dd -o outfile.tsv
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
    for fname in flist:
        click.echo('Parsing file {}'.format(fname))
        with open(fname, 'rb') as f:
            records = pickle.load(f)
            all_records.extend(records)


    df = pd.DataFrame(all_records)
    df.to_csv(output_file, sep='\t')

if __name__ == '__main__':
    agg()