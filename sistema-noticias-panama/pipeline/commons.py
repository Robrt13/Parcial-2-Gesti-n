from . import pd

def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path.split('/')[-1]}")