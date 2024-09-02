from robocorp.tasks import task
from robocorp import workitems
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Browser.Selenium import Selenium

class search_config:
    def __init__(self, phrase, category, time):
        self.phrase = phrase
        self.category = category
        self.time = time

    @classmethod
    def get_data(cls, search_parameters):
        search_phrase = search_parameters[""]
        category = work_item.get("category")
        months_back = int(work_item.get("months_back", 0))
        return cls(search_phrase, category, months_back)
    
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
    browser.configure(
        slowmo=500,
    )

    search_parameters = get_workitem()
    message = search_parameters["time"]

    search_news(search_parameters)
    open_article()
    title, date, author, link =  get_article_data()
    print(title)
    print(date)
    print(author)
    print(link)

def get_workitem():
    """
    We get the data from the workitem that sets the parameters.
    This is made with a "for" in case we need to expand to more workitems.
    """
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

    news_portal = "https://www.latimes.com/"
    search_tab = ".xs-5\:h-6"
    search_text = "[name=q]"
    search_button = ".h-6\.25"
    order_by = "select.select-input[name='s']"

    #nth-child(1) li:nth-child(1) .checkbox-input-element:nth-child(1)
    phrase = search_parameters["phrase"]
    category = categories[search_parameters["category"]]
    time = sorts[search_parameters["time"]]
    article_type = ('input[name="f1"][value="8fd31d5a-5e1c-3306-9f27-6edc9b08423e"]')

    browser.goto(news_portal)
    page = browser.page()
    page.wait_for_timeout(2000) 

    page.click(search_tab)
    page.fill(search_text, phrase)
    page.click(search_button)
    page.wait_for_timeout(2000) 
    reload_page()

    page.click(category)
    page.click(article_type)
    page.select_option(order_by, time)
    page.wait_for_timeout(500)
    reload_page()

def reload_page():
    page = browser.page()
    browser.page().reload()

def open_article():
    page = browser.page()

    first_article = "li:nth-child(1) h3.promo-title a"

    page.click(first_article)
    page.wait_for_timeout(500) 

def get_article_data():
    page = browser.page()
    title = page.locator(".headline").inner_text()
    date = page.locator(".published-date-day").inner_text()
    author = page.locator(".authors .author-name .link").inner_text()
    img = page.locator(".page-lead-media .figure img[src]").get_attribute("src")
    img_desc =page.locator(".page-lead-media .figure .image").get_attribute("alt")
    link = page.url
    print(img)
    print(img_desc)
    page.wait_for_timeout(10000) 

    return title, date, author, link