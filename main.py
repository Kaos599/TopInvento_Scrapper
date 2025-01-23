import requests
from bs4 import BeautifulSoup
import csv
import json 

def get_ip_news_data(keywords, num_results_per_page=20): 
    """
    Scrapes Google News results for given keywords based on the tutorial's method.

    Args:
        keywords (list): A list of keywords to search for.
        num_results_per_page (int): Number of results per page (adjust if needed, max ~100).

    Returns:
        list: A list of dictionaries, where each dictionary contains news data.
    """
    news_results = []
    search_query = " OR ".join([f'"{keyword}"' for keyword in keywords])
    search_url = f"https://www.google.com/search?q={search_query}&gl=us&tbm=nws&num={num_results_per_page}" 

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, "html.parser")

        for el in soup.select("div.SoaBEf"): 
            try: 
                news_item = {
                    "link": el.find("a")["href"],
                    "title": el.select_one("div.MBeuO").get_text(),
                    "snippet": el.select_one(".GI74Re").get_text(),
                    "date": el.select_one(".LfVVr").get_text(),
                    "source": el.select_one(".NUnG9d span").get_text()
                }
                news_results.append(news_item)
            except AttributeError:
                print("Warning: Could not extract all elements from a news item. Skipping.")
                continue 

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return [] 

    return news_results

if __name__ == "__main__":
    keywords_list = ["intellectual property", "patent lawyer", "ip enforcement", "inventor", "patent holder"]
    news_data = get_ip_news_data(keywords_list, num_results_per_page=20) 

    if news_data:
        csv_filename = "ip_news_data.csv"
        fieldnames = ["link", "title", "snippet", "date", "source"]

        with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file: 
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(news_data)
        print(f"Data saved to {csv_filename}")

        
        print(json.dumps(news_data, indent=2))

    else:
        print("No news articles found or an error occurred.")