import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import json

def scrap_web(url):
    headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers)
    
    if response.headers.get('Content-Type') == 'application/json':
        data = response.json()
        with open("scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    else:
        soup = bs(response.text, "html.parser")
        with open("scraped_data.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        return soup

def search_web(query):
    url = f"https://www.google.com/search?q={query}"
    headers = { 
    "User-Agent": UserAgent().random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Cookie": "AEC=AZ6Zc-WSqCeKLiU4vLaRV1I-ZZzZwMNQhH2m7gSeczF1DDANViYhave1Gg; NID=521=KPwzCIDoDbpiRHDt5VAf1zjDmOdL15OLpvkLEpFlIypheDCgo8_zJJfgBwjDH4RE3EjY3JyIY7k-6GPkTQjQ1c5XS9XZqs66PCMvp0tT-ZtraVveY3jr-XaEmxhk3zO07tL4xZv6OOdotloqtjZAijcboX0_O-pQBmHXYMK4nfzuYIfBbIlp06JwFvEGbQ9kH20LXSN098jeAaq0Tp6L9LrRF0HuZulKwwU2Dq_XBBwl5K-slZYnGLyswDaNEatEsCcUmBryb5doaufLimvZV3paeu3m4_HXudoTg8Ewxmx0a-9rbXiL0tspAdnrS77ITwHiupHlkAbt-PPSGsxuJqawA5aG1O8Skqyr-HBUttX25u70-WUQLsJdx92KUkrgz3sIFwcm36SarUVt-K2VZ6sJR9oOHsX0P9emdmjUKiBzktId-romkkpy6L_HACNQEr62jbyfgcfBoOscy2uZliXev7EwbfRfWI-AxdOZ6ckBZ40I-u-zQmypPR9TYMGiEpof694pbSHUo2tBirt6IwXEcP0Qo0k78zXB8pxUPKmMw_hKzVE3QaigIyp0e10-nnpJS_8g7UwkoiOphWI87JVc6tQJCXfps19CiLt1f1416TF5_FILpL3I_lqrd8d-pCwA6BsZearssLmGNMYaAiWF8MDnhtMfLdz3TxtXpnc4NBpPqtJDjfDNE6d_AKt-YGKYbOgZfr0OYh9wpp03mqCfG-hqhF-5vh7AV20jXwzOvVS6q8jSekl9ev8IwhyP49fkWuJc09K2wbD-8vMIOOHHAwOwYNRUPps_xUWQfYfycjrkcvGEg4xfXtY1g4YLqnBRSiRRDnuizw; SID=g.a000sAgAb8XvJ2xF60ut2P6w6Wj4PbiwBhonTcVNG8OpZFFfritZ6VatuACezsqmHANiz1QSYgACgYKAaQSARQSFQHGX2MizGOHFypmCIShqWCfF23hwhoVAUF8yKpPWO2KEqNRsLhLlkYgWuDb0076; __Secure-1PSID=g.a000sAgAb8XvJ2xF60ut2P6w6Wj4PbiwBhonTcVNG8OpZFFfritZILRSWmBR98bJdOjQMiVP9gACgYKAZ0SARQSFQHGX2MiegUNjZjGJJvPKnFGZSOZIxoVAUF8yKogqdo1ptXICgffez5XJtjV0076; __Secure-3PSID=g.a000sAgAb8XvJ2xF60ut2P6w6Wj4PbiwBhonTcVNG8OpZFFfritZDu4p31LKsa-NBkr4MLnQHQACgYKAfMSARQSFQHGX2MizqbELKj3BjNz1bDLvJj0uRoVAUF8yKpI38OFAsf9fxr-maKjSeQ80076; HSID=A8WLJ0EHudtbEqfud; SSID=AfK4wpAErXh4XPbvu; APISID=_3pf1Tz_HE0txOXz/AKKd8jLlLYuCHwaBm; SAPISID=S9fQdr12xA5qOxBN/AzWRhMYr1H13vsDw4; __Secure-1PAPISID=S9fQdr12xA5qOxBN/AzWRhMYr1H13vsDw4; __Secure-3PAPISID=S9fQdr12xA5qOxBN/AzWRhMYr1H13vsDw4; SIDCC=AKEyXzX-2un5NDwd2UU2SOlyfxtqQaLeUkUFfYH7DuOAXHAdmvfrBtEhHhg4u5IhOw0SRr4WDX7A; __Secure-1PSIDCC=AKEyXzU38k3NQM6jqw32eSpV9uLAZdgDl-lPPeoHBJTF7iVvqcimgfjnYixlc3ngJwJKGg5fshs; __Secure-3PSIDCC=AKEyXzXgHL51dIpEdZAoGAWWJ8-jL0lZfBKxv5viKox0Tzqs2lwlahd06_GQQNc8RpH_3kxQFU0; SEARCH_SAMESITE=CgQIjp0B; __Secure-1PSIDTS=sidts-CjEBmiPuTV-5Ph697pBGyYUtB1nFyFGSRkAJYNNeiuAa7FBPJmnLK3iwLM55Jlhku_IZEAA; __Secure-3PSIDTS=sidts-CjEBmiPuTV-5Ph697pBGyYUtB1nFyFGSRkAJYNNeiuAa7FBPJmnLK3iwLM55Jlhku_IZEAA; __Secure-ENID=24.SE=OrGbFkxZ9ef3FToA8tsfnx4UWvx9rGhpjbeb1kCs_kozI3RnUAcNKYsTNDuTQU-s1Sw3G5sSUJtjsetjDkAoohR28aKVhB2cg260t2s5rJRi_1RUQx28AoTaNNBIW4Zu60EK-WndIQLn-qKG6DfN7UUG8-e1yQy7q-W5xLWRScsj36HklzrGZaVRdbkhkq29aoEhWw2od9r8Uq8cnl6ibEtz-wf_4IJV66I; OTZ=7910683_36_32__32_; DV=A-xG86v-91JQ0LiuPDVHP2WBLsDnSBnWSxWyBWS9uAAAALDvYO7I265HigAAABBCjJMXcI0dSAAAAHUuNXbOwPihFAAAAA",
    "Connection": "keep-alive",
    "Host": "www.google.com",
}
    

    response = requests.get(url, headers=headers)
    response.encoding = 'UTF-8'
    soup = bs(response.text, "html.parser")
    with open("sd.html", "w", encoding="UTF-8") as f:
        f.write(soup.prettify())
    
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/url?q=" in href: 
            link = href.split("/url?q=")[1].split("&")[0]  
            links.append(link)
    
    data = {"links": links}
    with open("search_results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(soup)
    print(links)
    return links

if __name__ == "__main__":
    url = "https://dev.to/spara_50/rag-with-web-search-2c3e"
    web = search_web("apple")
    data = scrap_web(url)
