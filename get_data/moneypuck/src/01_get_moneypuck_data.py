import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin
from zipfile import ZipFile

import pandas as pd
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("../data/moneypuck")


def get_url(url, output_dir, output_filename):
    filepath = os.path.join(output_dir, output_filename)

    try:
        print(f"Downloading {url} to {filepath}")
        response = requests.get(url)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"Successfully downloaded {output_filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")


def fetch_hockey_stats_table(
    url="https://moneypuck.com/data.htm",
    css_selector="#page-content-wrapper > div:nth-child(1) > table",
):
    """
    Fetch the hockey stats table from the specified URL using a CSS selector
    and parse it into a pandas DataFrame

    Args:
        url (str): The URL to fetch from
        css_selector (str): CSS selector to find the table

    Returns:
        pd.DataFrame: DataFrame containing the parsed table data
    """
    # Send HTTP request to fetch the webpage
    try:
        headers = {
            "User-Agent": "python-requests/2.32.3/BrentBrewington/https://github.com/bbrewington"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table using the CSS selector
    table = soup.select_one(css_selector)

    if not table:
        print(f"No table found with selector: {css_selector}")
        return None

    # Initialize lists to store our data
    data = []

    # Process each row except the header row
    for row in table.find_all("tr")[1:]:  # Skip header row
        # Extract cells
        cells = row.find_all("td")

        if len(cells) < 5:  # Ensure the row has enough cells
            continue

        # Extract year from the first cell
        year = cells[0].text.strip()

        # Define categories based on the table structure
        categories = ["skaters", "goalies", "lines", "teams"]

        # Extract CSV links for each category
        urls = {}
        for i, category in enumerate(categories):
            # Add 1 to index because the first cell is the year
            link_tag = cells[i + 1].find("a")
            if link_tag and "href" in link_tag.attrs:
                # Get the href attribute (CSV URL)
                relative_url = link_tag["href"]
                # Make it an absolute URL
                absolute_url = urljoin(url, relative_url)
                urls[category] = absolute_url
            else:
                urls[category] = None

        # Add all information to our data list
        row_data = {
            "Season": year,
            "Skaters_URL": urls.get("skaters"),
            "Goalies_URL": urls.get("goalies"),
            "Lines_URL": urls.get("lines"),
            "Teams_URL": urls.get("teams"),
        }

        data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Clean up Season column (remove extra spaces and HTML formatting)
    df["Season"] = df["Season"].apply(lambda x: re.sub(r"\s+", "", x))

    return df


def download_season_level(df, category=None, output_subdir=Path("season_level")):
    """
    Download CSV files from the URLs in the DataFrame

    Args:
        df (pd.DataFrame): DataFrame containing CSV URLs
        category (str, optional): Category to download ('Skaters', 'Goalies', 'Lines', 'Teams')
                                If None, download all categories
        output_dir (Path): Subdirectory to save downloaded files
    """
    import os

    # Create output directory if it doesn't exist
    output_dir = DATA_DIR / output_subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define which columns to process
    if category:
        columns = [f"{category}_URL"]
    else:
        columns = [col for col in df.columns if col.endswith("_URL")]

    # Download each CSV
    for _, row in df.iterrows():
        season = row["Season"]

        for playoff_type in ["regular", "playoffs"]:
            for col in columns:
                url = row[col]
                if pd.isna(url) or not url:
                    continue
                if playoff_type == "playoffs":
                    url = url.replace("/regular/", "/playoffs/")

                # Create filename from URL
                category = col.replace("_URL", "")
                output_filename = f"{category}_{season}_{playoff_type}.csv"
                get_url(url=url, output_dir=output_dir, output_filename=output_filename)


if __name__ == "__main__":
    # Fetch and parse the table
    df = fetch_hockey_stats_table()

    if df is not None:
        # Display the DataFrame
        print("\nDataFrame of Hockey Stats URLs:")
        print(df.head())

        # Save the DataFrame to a CSV file
        df.to_csv("config/hockey_stats_links.csv", index=False)
        print("\nSaved DataFrame to config/hockey_stats_links.csv")

        # Optional: Uncomment to download the CSV files
        for category in ["Skaters", "Goalies", "Lines", "Teams"]:
            print(f"\nDownloading all {category.lower()} CSV files...")
            download_season_level(df, category=category)

    with open("config/dir_file_url_config.json", "r") as f:
        dir_file_url_config = [
            (x["dest_subdir"], x["dest_filename"], x["url"]) for x in json.load(f)
        ]

    for dir_file_url in dir_file_url_config:
        output_subdir, filename, url = dir_file_url
        output_dir = Path(f"{DATA_DIR}/{output_subdir}")
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True, exist_ok=True)
        get_url(url, output_dir, filename)
        if filename[-4:] == ".zip":
            print(f"Unzipping {filename}")
            with ZipFile(output_dir / filename, "r") as zip_ref:
                zip_ref.extractall(output_dir)
