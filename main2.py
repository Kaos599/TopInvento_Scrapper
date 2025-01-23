import requests
from bs4 import BeautifulSoup
import csv
import json
import logging
import time
import random
import re


logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


KEYWORDS_LIST = ["intellectual property", "patent lawyer", "ip enforcement", "inventor", "patent holder"]
NUM_ARTICLES_TO_SCRAPE = 25  
OUTPUT_CSV_FILENAME = "advanced_ip_news_data.csv"
USER_AGENT_LIST = [ 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/1460.1.57',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
]
REQUEST_DELAY_MIN = 1 
REQUEST_DELAY_MAX = 3 


GOOGLE_NEWS_ITEM_SELECTOR = "div.SoaBEf" 
GOOGLE_NEWS_ITEM_SELECTOR_FALLBACK = "div.Gx5Zad" 
GOOGLE_TITLE_SELECTOR = "div.MBeuO" 
GOOGLE_TITLE_SELECTOR_FALLBACK = "div.BNeawe.vvjwJb.AP7Wnd" 
GOOGLE_SNIPPET_SELECTOR = ".GI74Re" 
GOOGLE_SNIPPET_SELECTOR_FALLBACK = ".BNeawe.s3v9rd.AP7Wnd" 
GOOGLE_DATE_SELECTOR = ".LfVVr" 
GOOGLE_DATE_SELECTOR_FALLBACK = ".NUnG9d > span" 
GOOGLE_SOURCE_SELECTOR = ".NUnG9d span" 
GOOGLE_SOURCE_SELECTOR_FALLBACK = ".BNeawe.UPmit.AP7Wnd" 

ARTICLE_CONTENT_SELECTORS = [ 
    'article',                  
    'div.article-body',         
    'div.entry-content',
    'div.post-content',
    'div.story-content',
    'div.article__content',
    'div[itemprop="articleBody"]', 
    'div.content',              
    'div#article-content',      
    'div#content'
]
ARTICLE_AUTHOR_SELECTORS = [ 
    'span[itemprop="author"]', 
    'meta[name="author"]',     
    'meta[property="article:author"]', 
    'p.author',                
    'span.author',
    'div.author',
    'a[rel="author"]'          
]
ARTICLE_PUBLISH_DATE_SELECTORS = [ 
    'time[itemprop="datePublished"]', 
    'meta[itemprop="datePublished"]', 
    'meta[name="date"]',        
    'meta[property="article:published_time"]', 
    'time.entry-date',          
    'span.post-date',
    'div.datePublished',
    'span.date'
]
ARTICLE_IMAGE_SELECTOR = 'img[src]' 


def get_random_user_agent():
    return random.choice(USER_AGENT_LIST)

def get_random_delay():
    return random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)

def extract_article_content(article_url):
    """Attempts to extract full article content from a given URL."""
    try:
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(article_url, headers=headers, timeout=15) 
        response.raise_for_status()
        article_soup = BeautifulSoup(response.content, 'html.parser')

        for selector in ARTICLE_CONTENT_SELECTORS:
            content_container = article_soup.select_one(selector)
            if content_container:
                
                paragraphs = content_container.find_all('p') 
                if not paragraphs: 
                    article_text = content_container.text.strip()
                else:
                    article_text = "\n\n".join([p.text.strip() for p in paragraphs]) 
                return article_text.strip() 

        logging.warning(f"Article content selectors failed for URL: {article_url}")
        return "Article content extraction failed. Selectors may need adjustment." 

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching article content from {article_url}: {e}")
        return f"Error fetching article content: {e}"
    except Exception as e:
        logging.error(f"Error processing article content from {article_url}: {e}")
        return f"Error processing article content: {e}"

def extract_metadata(article_soup):
    """Extracts author, publish date, images, etc. from article soup."""
    metadata = {
        'author': 'Unknown',
        'publish_date': 'Unknown',
        'image_urls': [],
        'categories': [], 
        'keywords': []   
    }

    
    for selector in ARTICLE_AUTHOR_SELECTORS:
        author_element = article_soup.select_one(selector)
        if author_element:
            metadata['author'] = author_element.get_text(strip=True) or metadata['author'] 
            break 

    
    for selector in ARTICLE_PUBLISH_DATE_SELECTORS:
        date_element = article_soup.select_one(selector)
        if date_element:
            date_text = date_element.get('content') or date_element.get_text(strip=True) 
            if date_text:
                metadata['publish_date'] = date_text
                break

    
    image_elements = article_soup.select(ARTICLE_IMAGE_SELECTOR)
    metadata['image_urls'] = [img['src'] for img in image_elements if img.get('src')] 

    return metadata


def google_news_scraper(keywords, num_articles_limit=None):
    """
    Scrapes Google News results, extracts full content and metadata.
    Implements robust selectors, error handling, and logging.
    """
    results = []
    articles_scraped_count = 0
    search_query = " OR ".join([f'"{keyword}"' for keyword in keywords]) + " news"
    print(f"Search Query: {search_query}")
    logging.info(f"Starting scraper for keywords: {keywords}. Target articles: {num_articles_limit if num_articles_limit else 'Unlimited'}")

    page = 0
    while True: 
        start = page * 10
        search_url = f"https://www.google.com/search?q={search_query}&gl=us&tbm=nws&start={start}"
        headers = {'User-Agent': get_random_user_agent()}

        try:
            print(f"Fetching search page {page+1}...")
            response = requests.get(search_url, headers=headers, timeout=10) 
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            
            news_items = soup.select(GOOGLE_NEWS_ITEM_SELECTOR)
            if not news_items:
                news_items = soup.select(GOOGLE_NEWS_ITEM_SELECTOR_FALLBACK)
                if not news_items:
                    logging.warning(f"No news items found on page {page+1} using primary or fallback selectors. Google Search structure might have changed significantly.")
                    print(f"Warning: No news items found on page {page+1}. Search structure might have changed.")
                    break 


            for item in news_items:
                if num_articles_limit and articles_scraped_count >= num_articles_limit:
                    print(f"Reached article limit of {num_articles_limit}. Stopping scraping.")
                    logging.info(f"Scraping stopped: Reached article limit of {num_articles_limit}.")
                    return results 

                try: 
                    link_element = item.find('a')
                    if not link_element or not link_element.get('href'): 
                        logging.warning("News item missing link. Skipping.")
                        continue

                    link = link_element['href']
                    if not link.startswith("http"): 
                        link = "https://www.google.com" + link 

                    
                    title_element = item.select_one(GOOGLE_TITLE_SELECTOR)
                    if not title_element:
                        title_element = item.select_one(GOOGLE_TITLE_SELECTOR_FALLBACK)
                    title_text = title_element.get_text(strip=True) if title_element else "Title Not Found"

                    
                    snippet_element = item.select_one(GOOGLE_SNIPPET_SELECTOR)
                    if not snippet_element:
                        snippet_element = item.select_one(GOOGLE_SNIPPET_SELECTOR_FALLBACK)
                    snippet_text = snippet_element.get_text(strip=True) if snippet_element else "Snippet Not Found"

                    
                    date_element = item.select_one(GOOGLE_DATE_SELECTOR)
                    if not date_element:
                        date_element = item.select_one(GOOGLE_DATE_SELECTOR_FALLBACK)
                    date_text = date_element.get_text(strip=True) if date_element else "Date Not Found"

                    
                    source_element = item.select_one(GOOGLE_SOURCE_SELECTOR)
                    if not source_element:
                        source_element = item.select_one(GOOGLE_SOURCE_SELECTOR_FALLBACK)
                    source_text = source_element.get_text(strip=True) if source_element else "Source Not Found"


                    print(f"Scraping article: {title_text[:50]}...") 
                    logging.info(f"Extracting data for article: {title_text}")

                    article_content = extract_article_content(link) 
                    article_soup_for_metadata = BeautifulSoup(requests.get(link, headers={'User-Agent': get_random_user_agent()}, timeout=10).content, 'html.parser') 
                    metadata = extract_metadata(article_soup_for_metadata) 

                    results.append({
                        'search_title': title_text, 
                        'search_snippet': snippet_text,
                        'search_date': date_text,
                        'search_source': source_text,
                        'search_link': link,
                        'article_title': metadata.get('article_title', 'Title from Search'), 
                        'article_author': metadata.get('author', 'Unknown'),
                        'article_publish_date': metadata.get('publish_date', 'Unknown'),
                        'article_content': article_content,
                        'article_image_urls': metadata.get('image_urls', []),
                        'article_categories': metadata.get('categories', []), 
                        'article_keywords': metadata.get('keywords', [])     
                    })
                    articles_scraped_count += 1

                except Exception as e: 
                    logging.error(f"Error processing news item: {e}", exc_info=True) 
                    print(f"Warning: Error processing a news item. Skipping. Error: {e}")
                    continue 

            page += 1
            if len(news_items) < 10: 
                print("Reached end of Google News results.")
                logging.info("Reached end of Google News results.")
                break 

            time.sleep(get_random_delay()) 

        except requests.exceptions.RequestException as e: 
            logging.error(f"Error fetching search page {page+1}: {e}")
            print(f"Error fetching search page {page+1}: {e}")
            break 
        except Exception as e: 
            logging.error(f"Unexpected error processing search page {page+1}: {e}", exc_info=True)
            print(f"Unexpected error processing search page {page+1}: {e}")
            break

    print("Scraping complete.")
    logging.info("Scraping completed.")
    return results


if __name__ == "__main__":
    print("Starting Advanced Google News Scraper...")
    news_data = google_news_scraper(KEYWORDS_LIST, NUM_ARTICLES_TO_SCRAPE)

    if news_data:
        csv_filename = OUTPUT_CSV_FILENAME
        fieldnames = ['search_title', 'search_snippet', 'search_date', 'search_source', 'search_link',
                      'article_title', 'article_author', 'article_publish_date', 'article_content',
                      'article_image_urls', 'article_categories', 'article_keywords']

        with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(news_data)
        print(f"Data saved to {csv_filename}")
        logging.info(f"Data saved to {csv_filename}")

    else:
        print("No news articles found or an error occurred during scraping.")
        logging.warning("No news articles found or errors during scraping.")