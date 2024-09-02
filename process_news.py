"""
This code is an RPA automation made with the Robocorp framework to get information
from web articles, in this case molded to work for https://www.latimes.com/
We require the following data:
• Title
• Date
• Author
• Image file
• Image description
• Article URL

With this data, we create an Excel file with this information.

This is done with the use of up-to-date Python programming, OOP, no automation, 
no API, and uploaded with GitHub integration to the Robocloud platform.

Ideas to expand: A new workitem value can be added, which can control the 
time frame of the articles retrieved. This would require a loop that keeps True
as long as the date of the article (can be seen in the search before clicking
on the article) meets the criteria of the timeframe

Made by Apolo Uzcátegui, Colombian developer.
"""


"""
Robocorp + RPA libraries used
"""

from robocorp.tasks import task
from robocorp import workitems
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.Tables import Table
from RPA.Browser.Selenium import Selenium
import re
import logging
from datetime import datetime


class Article:
    def __init__(self, title, date, author, img, img_desc, money_mention, link):
        self.title = title
        self.date = date
        self.author = author
        self.img = img
        self.img_desc = img_desc
        self.money_mention = money_mention
        self.link = link


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # You can set it to INFO, WARNING, ERROR, etc.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("output/Process_news.log"),  # Log to a file
        logging.StreamHandler()  # Also output to the console
    ]
)

logger = logging.getLogger(__name__)


"""
Category options:
1 - California
2 - World and nation
3 - Food
4 - Business
"""
categories = {
    "1": "input[name='f0'][value='00000163-01e2-d9e5-adef-33e2984a0000']",
    "2": "input[name='f0'][value='00000168-8694-d5d8-a76d-efddaf000000']",
    "3": "input[name='f0'][value='00000168-8683-d2cb-a969-de8b247e0000']",
    "4": "input[name='f0'][value='00000168-865c-d5d8-a76d-efddd6550000']",
}

"""
Sorting options
1 - California
2 - World and nation
3 - Food
4 - Business
"""
sorts = {
    "1": "Relevance",
    "2": "Newest",
    "3": "Oldest"
}


@task
def process_news():
    """
    We get the workitems from the initialization.
    News are searched in the latimes site.
    We open the specific article.
    The data from the specific article is taken.
    The output file in excel is created.
    """
    logger.info("News Process started.")
    browser.configure(
        slowmo=500,
    )
    logger.info("Browser slowmo set to 500.")

    search_parameters = get_workitem()

    search_news(search_parameters)
    open_article()
    article = get_article_data()
    create_output_file(article)

    logger.info("Process Finished.")

def get_workitem():
    """
    We get the data from the workitem that sets the parameters.
    This is made with a "for" in case we need to expand to more workitems.
    """
    logger.info("The 'get_workitem' process started.")

    for item in workitems.inputs:
        search_parameters = item.payload

    return search_parameters


def search_news(search_parameters):
    """
    We set the variables needed to crawl through the site.
    Then, the variables of the search parameters are separated.
    The clicks and fills to get to the articles are executed.
    The clicks necessary to configure the search are done.
    """
    logger.info("The 'get_workitem' process finished successfully.")
    logger.info("The 'search_news' process started.")

    # Search related variables
    news_portal = "https://www.latimes.com/"
    search_tab = ".xs-5\:h-6"
    search_text = "[name=q]"
    search_button = ".h-6\.25"
    order_by = "select.select-input[name='s']"
    article_type = (
        'input[name="f1"][value="8fd31d5a-5e1c-3306-9f27-6edc9b08423e"]')

    # Article related variables
    phrase = search_parameters["phrase"]
    category = categories[search_parameters["category"]]
    time = sorts[search_parameters["time"]]

    # Steps to open the page
    browser.goto(news_portal)
    page = browser.page()
    page.wait_for_timeout(2000)

    # Steps to make the phrase search
    page.click(search_tab)
    page.fill(search_text, phrase)
    page.click(search_button)
    page.wait_for_timeout(2000)
    reload_page()

    # Steps to change the filters
    page.click(category)
    page.click(article_type)
    page.select_option(order_by, time)
    page.wait_for_timeout(500)
    reload_page()


def reload_page():
    """
    Does a page reload, can be used to avoid modals or timeouts
    """
    page = browser.page()
    browser.page().reload()
    logger.info("Browser page reloaded.")


def open_article():
    """
    Opens the first article from a search
    """
    logger.info("The 'search_news' process finished successfully.")
    logger.info("The 'open_article' process started.")

    page = browser.page()

    first_article = "li:nth-child(1) h3.promo-title a"

    page.click(first_article)
    page.wait_for_timeout(500)


def get_article_data():
    """
    Gets the information needed from the article.
    Returns an object of the article class.
    """
    logger.info("The 'open_article' process finished successfully.")
    logger.info("The 'get_article_data' process started.")

    page = browser.page()

    # Function to get the text from article
    text_from_article = get_article_text()

    # Fetching the specific data necessary for the article
    title = page.locator(".headline").inner_text()
    date = page.locator(".published-date-day").inner_text()
    author = page.locator(".authors .author-name .link").inner_text()
    img = page.locator(
        ".page-lead-media .figure img[src]").get_attribute("src")
    img_desc = page.locator(
        ".page-lead-media .figure .image").get_attribute("alt")
    money_mention = find_money_mentions(text_from_article)
    link = page.url

    article = Article(title, date, author, img, img_desc, money_mention, link)

    page.wait_for_timeout(5000)

    return article


def get_article_text():
    """
    Analyzes the text div from the DOM by joining all "p" elements.
    """
    page = browser.page()

    paragraphs = page.locator('div[data-element="story-body"] p')
    paragraph_count = paragraphs.count()
    article_text = []

    for i in range(paragraph_count):
        text = paragraphs.nth(i).text_content()
        article_text.append(text)

    full_article = "\n\n".join(article_text)

    return full_article


def find_money_mentions(text):
    """
    Define a regex pattern to match money formats required.
    After, if any mentions exist, return True, or else False.
    """
    pattern = r'(\$\d{1,3}(,\d{3})*(\.\d{2})?)|(\d+\s+(dollars|USD))'
    matches = re.findall(pattern, text)

    money_mentions = [match[0] if match[0] else match[3] for match in matches]

    print(money_mentions)

    if not money_mentions:
        money_mention = False
    else:
        money_mention = True

    return money_mention


def create_output_file(article):
    """
    A file in the output is created with the article data.
    """
    logger.info("The 'get_article_data' process finished successfully.")
    logger.info("The 'create_output_file' process started.")

    header = ["Title", "Date", "Author", "Image filename",
              "Image description", "Money mention", "Link"]
    data = [article.title, article.date, article.author, article.img,
            article.img_desc, article.money_mention, article.link]

    excel = Files()
    excel.create_workbook("output/output.xlsx")
    excel.append_rows_to_worksheet([header, data], header=True)

    excel.save_workbook()
    excel.close_workbook()

    logger.info("Workbook for output/output.xlsx created/updated.")
    logger.info("The 'create_output_file' process finished successfully.")
