import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "admission.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def prepare_data():
    df = pd.read_csv(RAW_DATA_PATH)
    
    df.columns = df.columns.str.strip()
    if "Serial No." in df.columns:
        df = df.drop(columns=["Serial No."])
    
    X = df.drop(columns=["Chance of Admit"])
    y = df["Chance of Admit"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    X_train.to_csv(PROCESSED_DIR / "X_train.csv", index=False)
    X_test.to_csv(PROCESSED_DIR / "X_test.csv", index=False)
    y_train.to_csv(PROCESSED_DIR / "y_train.csv", index=False)
    y_test.to_csv(PROCESSED_DIR / "y_test.csv", index=False)
    
    print(f"Data prepared: {len(X_train)} train, {len(X_test)} test samples")

if __name__ == "__main__":
    prepare_data()

