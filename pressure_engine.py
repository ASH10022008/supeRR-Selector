import pandas as pd
import numpy as np


def _aggregate_player_metrics(df, player_id_column, player_name_column):
    player_columns = [player_id_column, player_name_column]
    normal = df.loc[~df['is_high_pressure']]
    pressure = df.loc[df['is_high_pressure']]

    normal_stats = normal.groupby(player_columns, as_index=False).agg(
        balls_normal=('runs', 'size'),
        runs_normal=('runs', 'sum')
    )
    pressure_aggregations = {
        'balls_pressure': ('runs', 'size'),
        'runs_pressure': ('runs', 'sum'),
        'avg_stakes': ('stakes_weight', 'mean'),
        'avg_recency': ('recency_weight', 'mean')
    }
    if 'match_id' in pressure.columns:
        pressure_aggregations['matches_pressure'] = ('match_id', 'nunique')
    if 'is_wicket' in pressure.columns:
        pressure_aggregations['wickets_pressure'] = ('is_wicket', 'sum')

    pressure_stats = pressure.groupby(player_columns, as_index=False).agg(**pressure_aggregations)
    stats = normal_stats.merge(pressure_stats, on=player_columns, how='inner')
    if 'matches_pressure' not in stats.columns:
        stats['matches_pressure'] = 1
    if 'wickets_pressure' not in stats.columns:
        stats['wickets_pressure'] = 0

    stats = stats.loc[
        (stats['balls_normal'] >= 30) & (stats['balls_pressure'] >= 20)
    ].copy()
    return stats


def compute_pressure_and_rankings(processed_csv="data/processed_ball_by_ball.csv"):
    print("Loading processed delivery data...")
    df = pd.read_csv(processed_csv)
    
    # Check if player name columns exist, otherwise assign fallback/merged names
    if 'striker_name' not in df.columns:
        if 'striker' in df.columns:
            df['striker_name'] = df['striker']
        else:
            df['striker_name'] = "Player " + df['striker_id'].astype(str)
            
    if 'bowler_name' not in df.columns:
        if 'bowler' in df.columns:
            df['bowler_name'] = df['bowler']
        else:
            df['bowler_name'] = "Player " + df['bowler_id'].astype(str)

    # Parse dates (format: dd/mm/yyyy)
    if 'date' in df.columns:
        df['date_parsed'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
        max_date = df['date_parsed'].max()
        # Calculate years ago from the latest dataset date for exponential decay
        df['years_ago'] = (max_date - df['date_parsed']).dt.days / 365.25
        # Recency weight: half-life decay (matches from current year close to 1.0, older decay smoothly)
        df['recency_weight'] = np.exp(-0.35 * df['years_ago'].fillna(df['years_ago'].median()))
    else:
        df['recency_weight'] = 1.0

    # Map Match Stakes/Types to Multipliers
    if 'match_type' in df.columns:
        stakes_mapping = {
            'final': 2.5,
            'qualifier': 1.8,
            'semi': 1.9,
            'eliminator': 1.7,
            'super4': 1.5,
            'others': 1.0,
            'league':1.2
        }
        df['match_type_clean'] = df['match_type'].astype(str).str.lower().str.strip()
        df['stakes_weight'] = df['match_type_clean'].map(stakes_mapping).fillna(1.0)
    else:
        df['stakes_weight'] = 1.0

    print("Applying quantitative pressure definitions...")
    is_death_overs = df['phase'] == 'Death'
    is_collapse = (df['cum_wickets'] >= 5) & (df['overid'] <= 15)
    df['is_high_pressure'] = is_death_overs | is_collapse
    
    print("Calculating Batting Performance Metrics...")
    batters = _aggregate_player_metrics(df, 'striker_id', 'striker_name')
    pressure_deliveries = df.loc[df['is_high_pressure']]
    league_avg_pressure_sr = (
        pressure_deliveries['runs'].sum() / len(pressure_deliveries) * 100
        if not pressure_deliveries.empty else 0
    )
    batters['sr_normal'] = batters['runs_normal'] / batters['balls_normal'] * 100
    batters['sr_pressure'] = batters['runs_pressure'] / batters['balls_pressure'] * 100
    batters['league_avg_pressure_sr'] = league_avg_pressure_sr
    batters['clutch_impact'] = (
        batters['sr_pressure'] - league_avg_pressure_sr
        + 0.2 * (batters['sr_pressure'] - batters['sr_normal'])
    )
    batters['clutch_score'] = (
        batters['clutch_impact']
        * np.log1p(batters['balls_pressure'])
        * np.log1p(batters['matches_pressure'])
        * batters['avg_stakes']
        * batters['avg_recency']
    )
    df_batters = batters.rename(columns={
        'striker_id': 'player_id',
        'striker_name': 'player_name'
    })[
        ['player_id', 'player_name', 'balls_pressure', 'sr_normal',
         'sr_pressure', 'league_avg_pressure_sr', 'clutch_impact', 'clutch_score']
    ].round(2).sort_values(
        by='clutch_score', ascending=False
    ).reset_index(drop=True)

    print("Calculating Bowling Performance Metrics...")
    bowlers = _aggregate_player_metrics(df, 'bowler_id', 'bowler_name')
    league_avg_pressure_econ = (
        pressure_deliveries['runs'].sum() / len(pressure_deliveries) * 6
        if not pressure_deliveries.empty else 0
    )
    bowlers['econ_normal'] = bowlers['runs_normal'] / bowlers['balls_normal'] * 6
    bowlers['econ_pressure'] = bowlers['runs_pressure'] / bowlers['balls_pressure'] * 6
    bowlers['league_avg_pressure_econ'] = league_avg_pressure_econ
    bowlers['clutch_impact'] = (
        15 * (league_avg_pressure_econ - bowlers['econ_pressure'])
        + 3 * (bowlers['econ_normal'] - bowlers['econ_pressure'])
        + (bowlers['wickets_pressure'] / bowlers['balls_pressure'] * 36) * 10
    )
    bowlers['clutch_score'] = (
        bowlers['clutch_impact']
        * np.log1p(bowlers['balls_pressure'])
        * np.log1p(bowlers['matches_pressure'])
        * bowlers['avg_stakes']
        * bowlers['avg_recency']
    )
    df_bowlers = bowlers.rename(columns={
        'bowler_id': 'player_id',
        'bowler_name': 'player_name'
    })[
        ['player_id', 'player_name', 'balls_pressure', 'econ_normal',
         'econ_pressure', 'league_avg_pressure_econ', 'wickets_pressure',
         'clutch_impact', 'clutch_score']
    ].round(2).sort_values(
        by='clutch_score', ascending=False
    ).reset_index(drop=True)
    
    return df_batters, df_bowlers

if __name__ == "__main__":
    top_batters, top_bowlers = compute_pressure_and_rankings()
    print("\n--- TOP 10 BATTERS UNDER PRESSURE ---")
    print(top_batters.head(10).to_string(index=False))
    print("\n--- TOP 10 BOWLERS UNDER PRESSURE ---")
    print(top_bowlers.head(10).to_string(index=False))