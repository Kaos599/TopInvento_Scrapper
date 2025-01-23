# Advanced Google News Scraper

![Python Version](https://img.shields.io/badge/python-3.x-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

This repository contains a set of Python scripts designed to scrape Google News for articles related to specific keywords. The scripts extract detailed information from the articles, including titles, snippets, publication dates, sources, and full content. The extracted data is saved in CSV files for further analysis.

## Project Structure


### Files

- **`main.py`**: A simple script to scrape Google News for articles related to specific keywords and save the results in a CSV file.
- **`main2.py`**: An advanced version of the scraper with robust error handling, logging, and detailed metadata extraction.
- **`main3.py`**: An extended version of the scraper with additional features and improvements.
- **`scraper.log`**: A log file that records the scraping process, including any errors or warnings encountered.
- **`advanced_ip_news_data.csv`**, **`advanced_ip_news_data_v2.csv`**, **`advanced_ip_news_data_v3.csv`**, **`ip_news_data.csv`**: CSV files containing the scraped news data.

## Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`

You can install the required packages using pip:

```sh
pip install requests beautifulsoup4
```
## Usage
Running the Simple Scraper (main.py)
This script scrapes Google News for articles related to specific keywords and saves the results in a CSV file.

```sh
python main.py
```
Running the Advanced Scraper (main2.py)
This script provides more robust error handling, logging, and detailed metadata extraction.


```sh
python main2.py
```
Running the Extended Scraper (main3.py)
This script includes additional features and improvements over the advanced scraper.

```sh
python main3.py
```
Configuration
Keywords
The keywords to search for are defined in the KEYWORDS_LIST variable in each script. You can modify this list to include the keywords you are interested in.

## Output CSV Filename
The output CSV filename is defined in the OUTPUT_CSV_FILENAME variable in each script. You can change this to your desired filename.

## User Agents
The USER_AGENT_LIST variable contains a list of user agents to use for the requests. This helps to avoid being blocked by Google. You can add or modify the user agents in this list.

## Request Delays
The REQUEST_DELAY_MIN and REQUEST_DELAY_MAX variables define the minimum and maximum delay between requests. This helps to avoid being blocked by Google. You can adjust these values as needed.

## Logging
The advanced and extended scrapers log the scraping process to the scraper.log file. This includes information about the articles being scraped, any errors encountered, and warnings about potential issues.

## Example Output
Here is an example of the JSON output from the simple scraper (main.py):

```json
[
  {
    "link": "https://finance.yahoo.com/news/inventhelp-inventor-develops-highly-portable-151500318.html",
    "title": "InventHelp Inventor Develops Highly Portable, Durable, and Reusable Floor Product (IPL-705)",
    "snippet": "\"I wanted to create a portable, durable, and reusable floor that could be easily installed in primarily outdoor spaces for various different...",
    "date": "1 hour ago",
    "source": "Yahoo Finance"
  },
  ...
]
```

