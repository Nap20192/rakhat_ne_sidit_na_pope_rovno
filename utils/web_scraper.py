import json

import os
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import urllib.request
from urllib.parse import urljoin
from PIL import Image
import io

from models import Prompt

def scrape_web_pages(url):
    headers = {"User-Agent": UserAgent().random}
    try:
        response = requests.get(url, headers=headers)
        soup = bs(response.text, "html.parser")
        all_p = soup.find_all("p")
        data = [p.text for p in all_p]
        img_tags = soup.find_all('img')
        img_links = []
        for image_tag in img_tags:
            src = image_tag.get('src')
            if src:
                absolute_src = urljoin(url, src)
                img_links.append(absolute_src)
        return {"url": url, "data": data, "img_links": img_links}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"url": url, "data": "Failed to retrieve data", "img_links": "Failed to retrieve data"}


def scrape_images(url):
    headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers)
    soup = bs(response.text, "html.parser")
    img_tags = soup.find_all('img')
    img_links = []
    for img in img_tags:
        src = img.get('src')
        if src:
            absolute_src = urljoin(url, src)
            if "https" in absolute_src:
                img_links.append(absolute_src)
    return img_links


def save_scraped_data(scraped_data, filename="./scraped_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)


def scrape_data_from_links(links):
    data = {"links": [], "data": []}
    all_data = []
    counter = 3
    img_links = {"links": []}

    for link in links[:counter]:
        if link in data["links"]:
            continue
        scraped_data = scrape_web_pages(link)
        all_data.append(scraped_data)
        try:
            data["links"].append(link)
            data["data"].append(scraped_data)
            image_links = scrape_images(link)
            if not image_links:
                counter += 1
            img_links["links"].extend(image_links)
            print(f"Scraped data from {link}")
        except Exception as e:
            print(f"Failed to scrape data from {link}: {e}")
            continue
    save_scraped_data(data)


def download_images(img_links, min_size_kb=10):
    counter = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    for link in img_links:
        if "https" not in link or "svg" in link:
            continue
        try:
            req = urllib.request.Request(link, headers=headers)
            with urllib.request.urlopen(req) as response:
                img_data = response.read()

            file_size_kb = len(img_data) / 1024
            if file_size_kb < min_size_kb:
                print(f"Skipping {link} (File size: {file_size_kb:.2f} KB - Out of range)")
                continue
            else:
                with urllib.request.urlopen(req) as response:
                    with open(f"./img/{counter}.jpg", 'wb') as f:
                        f.write(response.read())
                counter += 1
        except Exception as e:
            print(f"Failed to download image from {link}: {e}")
            continue
        if counter >= 4:
            break

def search_with_playwright(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=UserAgent().random)
        page = context.new_page()
        page.goto(f"https://www.bing.com/search?q={query}")
        page.reload()
        page.wait_for_selector("li.b_algo h2", timeout=10000)

        links = []
        for a_tag in page.query_selector_all("a"):
            href = a_tag.get_attribute("href")
            print(href)
            if href and "https" in href:
                links.append(href)

        data = {"links": links}
        with open("./search_results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        browser.close()
    return links

def search_images_with_playwright(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=UserAgent().random)
        page = context.new_page()
        page.goto(f"https://www.bing.com/images/search?q={query}")
        page.reload()
        page.wait_for_selector("img.mimg", timeout=10000)

        images = []
        for img_tag in page.query_selector_all("img.mimg"):
            src = img_tag.get_attribute("src")
            if src and "https" in src:
                images.append(src)

        data = {"images": images}
        with open("./images_results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        browser.close()
    return images

def clean_image_directory():
    directory = "./img"
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory {directory}")
        return

    deleted_count = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print(f"Cleaned image directory. Removed {deleted_count} files")



"""
MAIN FUNCTION
"""

def unified_scraping_flow(search_query:Prompt):
    clean_image_directory()
    # Step 1: Perform web search and get links
    print(f"Searching for: {search_query.get_prompt()}")
    search_results = search_with_playwright(search_query.get_prompt())
    # Step 2: Scrape content from found links
    print("\nScraping content from top results...")
    scrape_data_from_links(search_results)

    # Step 3: Load scraped data to get image links
    try:
        with open("./scraped_data.json", "r", encoding="utf-8") as f:
            scraped_data = json.load(f)
            all_image_links = []
            for entry in scraped_data["data"]:
                if isinstance(entry.get("img_links"), list):
                    all_image_links.extend(entry["img_links"])
    except Exception as e:
        print(f"Error loading scraped data: {e}")
        return

    # Step 4: Download images
    print("\nDownloading images...")
    download_images(all_image_links)

    print("\nScraping workflow completed successfully!")
    print(f"Total pages scraped: {len(scraped_data['data'])}")
    print(f"Total images found: {len(all_image_links)}")




if __name__ == "__main__":
    prompt =Prompt("banana fruit")
    unified_scraping_flow(prompt)

