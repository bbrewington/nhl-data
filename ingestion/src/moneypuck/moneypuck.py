"""MoneyPuck data fetching functionality."""

import pandas as pd
from .config.settings import MONEYPUCK_RAW_DIR

def get_moneypuck_data(season=None, save=True):
    """
    Fetch MoneyPuck data for a specific season
    
    Args:
        season (str, optional): Season in format '20232024'. Defaults to current season.
        save (bool, optional): Whether to save the data. Defaults to True.
    
    Returns:
        pandas.DataFrame: The fetched data
    """
    base_url = "https://moneypuck.com/moneypuck/playerData/seasons"
    
    if not season:
        # Logic to determine current season
        import datetime
        current_year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        if month >= 9:  # NHL season typically starts in October
            season = f"{current_year}{current_year+1}"
        else:
            season = f"{current_year-1}{current_year}"
    
    url = f"{base_url}/{season}/{season}_skaters.csv"
    
    # Fetch data
    df = pd.read_csv(url)
    
    # Save if requested
    if save:
        output_path = MONEYPUCK_RAW_DIR / f"moneypuck_skaters_{season}.csv"
        MONEYPUCK_RAW_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved data to {output_path}")
    
    return df
