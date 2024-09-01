import hashlib
import os
import logging
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

# Set up logging for file errors
logging.basicConfig(filename='file_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set up logging for long filenames
long_filename_logger = logging.getLogger('long_filenames')
long_filename_logger.setLevel(logging.INFO)
handler = logging.FileHandler('long_filenames.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
long_filename_logger.addHandler(handler)

def generate_filename_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.endswith('/'):
        path += 'index.html'
    elif '.' not in os.path.basename(path):
        path += '/index.html'
    
    hash_object = hashlib.md5(url.encode('utf-8'))
    filename = hash_object.hexdigest()
    
    ext = os.path.splitext(path)[1] or '.html'
    
    return filename + ext

def save_page(url, content):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.endswith('/'):
        path += 'index.html'
    elif '.' not in os.path.basename(path):
        path += '/index.html'
    filename = os.path.join('saved_pages', 'ELTIS_site', path.lstrip('/'))
    
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as file:
            file.write(content)
        return filename
    except OSError as e:
        if e.winerror == 206:  # File name or extension is too long
            long_filename_logger.info(f"Long filename encountered: {filename}")
            short_filename = os.path.join('saved_pages', 'ELTIS_site', generate_filename_from_url(url))
            try:
                os.makedirs(os.path.dirname(short_filename), exist_ok=True)
                with open(short_filename, 'wb') as file:
                    file.write(content)
                return short_filename
            except OSError as e:
                logging.error(f"Failed to save file '{short_filename}': {e}")
                return None
        else:
            logging.error(f"Failed to save file '{filename}': {e}")
            return None

def fetch_and_save_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        filename = save_page(url, response.content)
        if filename:
            print(f"Saved {url} to {filename}")
        else:
            print(f"Failed to save {url}")
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")

from bs4 import ParserRejectedMarkup

def crawl_website(start_url):
    visited_urls = set()
    urls_to_visit = [start_url]
    
    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue
        
        visited_urls.add(current_url)
        print(f"Visiting: {current_url}")
        
        fetch_and_save_page(current_url)
        
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    full_url = urljoin(current_url, href)
                    parsed_url = urlparse(full_url)
                    
                    if parsed_url.netloc == urlparse(start_url).netloc:
                        if full_url not in visited_urls and full_url not in urls_to_visit:
                            urls_to_visit.append(full_url)
            
            except ParserRejectedMarkup as e:
                logging.error(f"Failed to parse {current_url}: {e}")
                print(f"Failed to parse {current_url}: {e}")
            
            except Exception as e:
                logging.error(f"Error while processing {current_url}: {e}")
                print(f"Error while processing {current_url}: {e}")
        
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {current_url}: {e}")
            print(f"Failed to fetch {current_url}: {e}")

# Start crawling from the initial URL
start_url = "https://www.eltis.com/"  # Replace with your start URL
crawl_website(start_url)