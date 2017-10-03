"""
Call from command line, point towards a folder
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
        with open(fname, 'rb') as f:
            records = pickle.load(f)
            all_records.extend(records)

    df = pd.DataFrame(all_records)
    df.to_csv(output_file, sep='\t')

if __name__ == '__main__':
    agg()
