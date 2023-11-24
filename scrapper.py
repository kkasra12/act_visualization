import os
import pickle
import re
import time
from bs4 import BeautifulSoup

from regex import B
import requests


class CacheList:
    def __init__(self, path) -> None:
        self.path = path
        self.load()
        # TODO: if path is None, dont save the cache at all

    def __contains__(self, item):
        return item in self.cache

    def __iter__(self):
        return iter(self.cache)

    def __len__(self):
        return len(self.cache)

    def __getitem__(self, index):
        return self.cache[index]

    def __setitem__(self, index, value):
        self.cache[index] = value
        self.save()

    def append(self, item):
        self.cache.append(item)
        self.save()

    def pop(self, index=0):
        self.cache.pop(index)
        self.save()

    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.cache, f)

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                self.cache = pickle.load(f)
        else:
            self.cache = []


class Scrapper:
    def __init__(self, cache_file="cach.pkl", start_url=None, request_delay=0.5):
        """
        Scrapper function to scrap the web page

        first list in the cache is unvisited links and second list is the content of the links

        in this function:
         - if the visited_links is empty we will add the links in the start_url
         - else we will start scrapping the links in the unvisited_links
         - if the unvisited_links has only one None value we will stop scrapping


        :param cache_file: str, path to the cache file
        """
        if start_url is None:
            self.start_url = "https://artificialintelligenceact.com"
        else:
            self.start_url = start_url
        self.matching_regex = "^https://artificialintelligenceact.com/title-[ivx]+/.+$"
        self.last_request_time = 0
        self.start_time = time.time()
        self.request_delay = request_delay
        self.cache = CacheList(cache_file)
        if len(self.cache) == 0:
            self.cache.append(self.first_page_links)
            self.cache.append([])
        self.unvisited_links = self.cache[0]
        self.unvisited_links.append(None) 
        # stop criteria: if the unvisited_links has only one None value we will stop scrapping
        self.content = self.cache[1]


    @property
    def first_page_links(self):
        """
        scrap the self.start_url and return the links in the first page that matchs the self.matching_regex
        :return: list of links in the first page
        """
        first_page = self.request(self.start_url)
        links = first_page.find_all("a", href=re.compile(self.matching_regex))
        return [link["href"] for link in links]

    def request(self, url):
        """
        :param url: str, url to request
        :return: str, html of the url
        """
        time.sleep(max(0, self.last_request_time + self.request_delay - time.time()))
        self.last_request_time = time.time()
        return BeautifulSoup(requests.get(url).content, "html.parser")

    def scrap(self):
        """
        scrap the web page
        :return: None
        """
        while self.unvisited_links[0] is not None:
            url = self.unvisited_links.pop(0)
            new_content = self.scrap_page(url)
            self.content.append(new_content)
            self.cache.save()
            print(f"page {url} scrapped, {len(self.unvisited_links)} remaining, elapsed time: {time.time() - self.start_time}")

    def scrap_page(self, url):
        """
        scrap the page in the url
        we only consider a `<div>` with `class="container main-content"` and we should ignore the other parts of the page.
        to be more precise we only consider the <p> tags in the main-content div
        :param url: str, url to scrap
        """
        page_content = self.request(url)
        main_content = page_content.find("div", class_="container main-content")
        if main_content is None:
            return ""
        else:
            paragraphs = main_content.find_all("p")
            return [p.text for p in paragraphs]
        
    
        