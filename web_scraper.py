import json
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

# List of URLs for scraping
l = ["https://ru.wikipedia.org/wiki/%D0%9F%D0%B5%D1%80%D1%81%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9_%D0%BA%D0%BE%D0%BC%D0%BF%D1%8C%D1%8E%D1%82%D0%B5%D1%80", 
     "https://ru.wikipedia.org/wiki/Linux"]

def scrap_web_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        user_agent = UserAgent().random
        context = browser.new_context(user_agent=user_agent)
        
        page = context.new_page()

        page.goto(url)

        page.wait_for_selector("p")

        data = [p.text_content() for p in page.query_selector_all("p")]

        browser.close()

        return {"url": url, "data": data}

def save_scraped_data(scraped_data, filename="scraped_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)


def links_scraped_data_with_playwright(links):
    data = {"links": [], "data": []}

    can_scrape = False
    all_data = []
    print(links)
    for link in l[:2]:
        if link in data["links"]:
            continue
        
        ignore = ["https://instagram.com", "https://facebook.com", "https://youtube.com", "https://x.com"]

        if link in ignore:
            continue
        else:
            scraped_data = scrap_web_with_playwright(link)
            all_data.append(scraped_data)
            try:
                data["links"].append(link)
                data["data"].append(scraped_data)
            except:
                continue

        
        
        
    save_scraped_data(data)


def search_with_playwright(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
    
        context = browser.new_context(user_agent=UserAgent().random)
        
        page = context.new_page()

        page.goto(f"https://www.bing.com/search?q={query}")
        page.reload()
        page.wait_for_selector("h2", timeout=5000)

        links = []
        for a_tag in page.query_selector_all("a"):
            href = a_tag.get_attribute("href")
            # print(href)
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
    # Example search query
    query = "Trump won the election"
    search_with_playwright(query)

    # Loading the search result file and printing links
    with open("search_results.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    print(data)

    # Scrape the links from the search results and save to a file
    links_scraped_data_with_playwright(data['links'])
