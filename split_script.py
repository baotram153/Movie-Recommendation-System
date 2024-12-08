import pandas as pd

def split_csv(csv_file, output_prefix, chunk_size=1000000):
  """
  Splits a large CSV file into smaller chunks.

  Args:
    csv_file: Path to the input CSV file.
    output_prefix: Prefix for the output chunk file names (e.g., 'ratings_chunk_').
    chunk_size: Number of rows per chunk.
  """

  chunk_number = 1
  for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
    chunk.to_csv(f'{output_prefix}{chunk_number}.csv', index=False)
    chunk_number += 1

file_path = "dataset/ml-32m/ratings.csv"
# Example usage:
split_csv(file_path, 'ratings_chunk_', chunk_size=10000000) 