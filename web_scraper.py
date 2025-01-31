import json
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import urllib.request

# List of URLs for scraping
l = ["https://ru.wikipedia.org/wiki/%D0%9F%D0%B5%D1%80%D1%81%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D0%BA%D0%BE%D0%BC%D0%BF%D1%8C%D1%8E%D1%82%D0%B5%D1%80", 
     "https://ru.wikipedia.org/wiki/Linux"]

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
            img_links.append(image_tag['src']) 
        return {"url": url, "data": data, "img_links": img_links}
    except:
        return {"url": url, "data": "Failed to retrieve data", "img_links": "Failed to retrieve data"}
    
def scrape_images(url):
    headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers)
    soup = bs(response.text, "html.parser")
     
    

    

def save_scraped_data(scraped_data, filename="scraped_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)


def scrape_data_from_links(links):
    data = {"links": [], "data": []}

    all_data = []
    counter = 0

    img_links = {"links": []}

    for link in links[1:4]:
        if link in data["links"]:
            continue
        scraped_data = scrape_web_pages(link)
        all_data.append(scraped_data)
        try:
          data["links"].append(link)
          data["data"].append(scraped_data)
          img_links["links"].extend(scrape_images(link))
        except:
            continue
        
        
    save_scraped_data(img_links, filename="scraped_images.json")  
    save_scraped_data(data)


def download_images(img_links):
    counter = 0
    for link in img_links:
        if "https" in link:
            counter += 1
            try:
                urllib.request.urlretrieve(link, f"img/{counter}.jpg")
            except:
                continue
        if counter >= 3:
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
              link = href
              links.append(link)

        data = {"links": links}
        with open("search_results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        browser.close()

    # print(links)
    return links

if __name__ == "__main__":
    query = "Trump won the election"
    search_with_playwright(query)

    with open("search_results.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    scrape_data_from_links(data['links'])

    with open("scraped_data.json", "r", encoding="utf-8") as file:
        scraped_data = json.load(file)
    print(scraped_data)

    for data in scraped_data["data"]:
        download_images(data["img_links"])

    