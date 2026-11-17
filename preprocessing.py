import pandas as pd
import numpy as np

def load_and_preprocess_data(data_dir="data/"):
    print("Loading datasets...")
    matches = pd.read_csv(f"{data_dir}/matches.csv")
    ball_by_ball = pd.read_csv(f"{data_dir}/ball_by_ball.csv")
    competitions = pd.read_csv(f"{data_dir}/competitions.csv")
    
    # Merge matches with competitions to get format and season info
    match_comp = pd.merge(matches, competitions, on="comp_id", how="inner")
    
    # Merge ball-by-ball with match info
    df = pd.merge(ball_by_ball, match_comp, on="match_id", how="inner")
    
    print("Deriving match-state and phase features...")
    # Calculate over number and phase
    # overid is usually 1-indexed (1 to 20 in T20s)
    df['phase'] = np.select(
        [
            df['overid'] <= 6,
            (df['overid'] > 6) & (df['overid'] <= 15),
            df['overid'] > 15
        ],
        ['Powerplay', 'Middle', 'Death'],
        default='Middle'
    )
    
    # Sort chronologically to compute cumulative match states correctly
    df = df.sort_values(by=['match_id', 'innings', 'overid', 'over_ball_num'])
    
    # Cumulative runs and wickets per innings in a match
    df['cum_runs'] = df.groupby(['match_id', 'innings'])['runs'].cumsum()
    df['cum_wickets'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum()
    
    # Balls remaining in innings (assuming standard 120 balls max for T20)
    df['balls_bowled'] = (df['overid'] - 1) * 6 + df['over_ball_num']
    df['balls_remaining'] = np.maximum(0, 120 - df['balls_bowled'])
    
    return df

if __name__ == "__main__":
    df = load_and_preprocess_data()
    print(f"Successfully processed {len(df):,} delivery records.")
    df.to_csv("data/processed_ball_by_ball.csv", index=False)