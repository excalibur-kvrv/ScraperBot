from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from random import randint
from csv import writer
from time import sleep
import socket
import shutil
import socks
import os


class ScraperBot:
    def __init__(self, timer_range=(30, 60)):
        # @param (timer_range) : this specifies a range for randint to choose from to set a crawl delay

        self.start_url = input("Enter url")
        self.headers = { "User-Agent": "Modzilla/5.0" }
        self.timer = timer_range

    def check_file_exists_and_return_contents(self, url):
        # @param (url): this is used to check whether a file has been cached, if not it'll fetch the file and cache for processing
        # @returns: a tuple containing two values:-
        #           1. is_present (a boolean for if the file is cached or not)
        #           2. contents (a str containing the contents of the passed in url) 
        # 
        # This code checks whether a scraped page has been cached, if not it will cache it.
        
        print("fetching " + url)
        if url == self.start_url:
            index_path = os.path.join(os.getcwd(), "scraped_pages", "index.html")
            if os.path.exists(index_path):
                with open(index_path) as file:
                    contents = "".join(file.readlines())
                return True, contents
            else:
                os.makedirs(os.path.split(index_path)[0])
                req = Request(url, headers=self.headers)
                contents = urlopen(req).read()
                with open(index_path, "w") as file:
                    file.write(contents.decode("utf-8"))
                return False, contents
        else:
            parsed_url = urlparse(url)
            scraped_pages_path = os.path.join(os.getcwd(), "scraped_pages", parsed_url.path[1:])
            _, tail = os.path.split(scraped_pages_path)
            if os.path.exists(scraped_pages_path):
                try:
                    page_location = os.path.join(scraped_pages_path, f"{tail}{parsed_url.query.split('=')[1]}.html")
                except:
                    page_location = os.path.join(scraped_pages_path, f"{parsed_url.path[1: len(parsed_url.path) - 1]}1.html")

                if os.path.exists(page_location):
                    with open(page_location) as file:
                        contents = "".join(file.readlines())
                    return True, contents
                else:
                    req = Request(url, headers=self.headers)
                    contents = urlopen(req).read()
                    with open(page_location, "w") as file:
                        file.write(contents.decode("utf-8"))
                    return False, contents
            else:
                os.makedirs(scraped_pages_path)
                return self.check_file_exists_and_return_contents(url)

    def fetch_internal_urls_content(self):
        # This code will fetch all the internal url's and process them using the process_downloaded_pages()
        # method to get the required data

        _, contents = self.check_file_exists_and_return_contents(self.start_url)
        soup = BeautifulSoup(contents, "html.parser")
        a_tags = soup.find_all("a", class_="c-landing-module__image-component")
        for tag in a_tags:
            page_url = urljoin(self.start_url, tag.attrs["href"])
            
            try:
                is_present, contents = self.check_file_exists_and_return_contents(page_url)
                self.process_downloaded_pages(contents, page_url)
            except Exception as err:
                print("error occurred while fetching " + page_url)
                print(err)
                continue

            page_soup = BeautifulSoup(contents, "html.parser")
            
            try:
                page_total = int(page_soup.find(class_="o-pagination__li o-pagination__number--next").get_text())
            except Exception as err:
                continue

            # if page_total is less than 2 then there is no more page numbers to scroll 
            if page_total >= 2:
                for i in range(2, page_total + 1):
                    if page_url.endswith("/"):
                        page_url = page_url[: len(page_url) - 1] 
                    is_present, contents = self.check_file_exists_and_return_contents(f"{page_url}?page={i}")
                    self.process_downloaded_pages(contents, page_url)
                    # if the data is not present in cache then a timer will trigger to add a crawl delay as specified 
                    # by the class attribute timer
                    if not is_present:
                        sleep(randint(*self.timer))
            # if page is present in cache, send the page contents directly, else trigger a crawl delay
            # as specified by class attribute timer
            if not is_present:
                sleep(randint(*self.timer))

    def process_downloaded_pages(self, content, url):
        # @param (content): takes in the content to be processed
        # @param (url): takes in the url of the page to be parsed
        # 
        # This method generates a data.csv file that contains the following information in the respective order :- 
        # (product_title (str), product_decription (str), 
        # product_price (str), product_colors (list), product_img_url (str), product_sizes (list))

        print("processing", url)
        soup = BeautifulSoup(content, "html.parser")
        product_details = soup.find_all("div", class_="dom-product-tile c-product-tile c-product-tile--regular c-product-tile js-product-tile")
        with open("data.csv", "a") as file:
            csv_writer = writer(file)
            for product in product_details:
                try:
                    product_title = product.find("h3", class_="c-product-tile__h3 c-product-tile__h3--regular").get_text().strip()
                    product_price = product.find("span", class_="c-product-meta__current-price").get_text().strip()
                    product_colors = [a_tag.attrs["aria-label"].strip() for a_tag in product.find_all("a", class_="o-list-swatches__a")]
                    product_img_url = "http:" + product.find("img", class_="c-product-tile__img").attrs["src"]
                    product_info_url = product.find("a", class_="c-product-tile__image-link js-product-tile__image-link").attrs["href"]
                    product_desc, product_sizes = self.fetch_product_sizes_description(urljoin(url, product_info_url))
                    csv_writer.writerow([product_title, product_desc, product_price, product_colors, product_img_url, product_sizes])
                except Exception as err:
                    print(err)
                    continue

    def fetch_product_sizes_description(self, url):
        # @param (url): takes the url of the product page
        # @returns: a tuple of product description (str) and the product sizes (list)
        # 
        # This method is used to fetch product description and sizes from the product page

        is_present, contents = self.check_file_exists_and_return_contents(url)
        if not is_present:
            sleep(randint(*self.timer))
        soup = BeautifulSoup(contents, "html.parser")
        sizes = soup.find_all("li", class_="c-radio-styled__small")
        product_sizes = []
        for size in sizes:
            product_sizes.append(size.get_text().strip())
        
        description = soup.find("div", class_="c-text-truncate__text u-break-word").find("p").get_text().strip()
        return description, product_sizes

    def start(self, keep=True, proxy=False):
        # @param (keep): if keep is set to False it will delete the cached pages stored in the scraped_pages/ directory after
        #                processing all the pages
        #        (proxy): if proxy is set to True it will connect to the tor network and change your ip
        # This method is used to start the bot
        print(f"Your ip is {urlopen('http://icanhazip.com').read().decode('utf-8')}")

        if proxy:
            print(f"Connecting to tor network")
            socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
            socket.socket = socks.socksocket
            print(f"Your proxy ip is {urlopen('http://icanhazip.com').read().decode('utf-8')}")

        print("Starting bot")
        self.fetch_internal_urls_content()
        print("Completed fetching and processing of pages")
        if not keep:
            shutil.rmtree(os.path.join(os.getcwd(), "scraped_pages"))

if __name__ == "__main__":
    # timer_range specifies the crawl delay range for ranint to choose a random time to sleep,
    # the robots.txt file specifies a crawl delay of 60 for bots, so choose an appropriate range.
    bot = ScraperBot(timer_range=(60, 80))

    # if keep is set to False it will delete the cached pages after processing is complete.
    bot.start(keep=True, proxy=True)
