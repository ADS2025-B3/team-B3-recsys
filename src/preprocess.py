import pandas as pd
from sklearn.model_selection import train_test_split
import os

# Configuration
RANDOM_STATE = 42
TEST_SIZE = 0.2
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'u.data')
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')

def process_data():
    print("Cargando MovieLens 100k dataset...")
    
    # Define the columns
    columns = ['user_id', 'movie_id', 'rating', 'timestamp']
    
    
    df = pd.read_csv(RAW_DATA_PATH, sep='\t', names=columns)
    
    print(f"Dataset cargado. Filas: {df.shape[0]}")
    
    # Simple preprocess
    # Convert timestamp tolegible date 
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Split Train/Test
    print("Dividiendo en Train y Test...")
    train, test = train_test_split(df, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    
    train.to_csv(os.path.join(PROCESSED_DIR, 'train.csv'), index=False)
    test.to_csv(os.path.join(PROCESSED_DIR, 'test.csv'), index=False)
    
    print(f"Ready! Files storaged in {PROCESSED_DIR}")

if __name__ == '__main__':
    process_data()