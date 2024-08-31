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

@task
def process_news():
    browser.configure(
        slowmo=500,
    )

    search_parameters = get_workitem()
    message = search_parameters["time"]
    print(message)

    search_news(search_parameters)

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
    The clicks and fills to get to the articles are executed.
    """

    news_portal = "https://www.latimes.com/"
    search_tab = ".xs-5\:h-6"
    search_text = "[name=q]"
    search_button = ".h-6\.25"

    phrase = search_parameters["phrase"]
    category = ('input[name="f1"][value="8fd31d5a-5e1c-3306-9f27-6edc9b08423e"]')#search_parameters["category"]
    #time = #search_parameters["phrase"]

    browser.goto(news_portal)
    page = browser.page()
    page.wait_for_timeout(2000) 

    page.click(search_tab)
    page.fill(search_text, phrase)
    page.click(search_button)
    page.wait_for_timeout(2000) 

    reload_page()

    page.click(category)
    #page.wait_for_timeout(500) 
    
    browser.page().reload()
    page.wait_for_timeout(500)
    first_article = "li:nth-child(1) .promo-title"
    #first_li_element = page.locator(first_li_xpath)
    print(first_article)
    #first_li_element.wait_for(state="visible")
    page.click(first_article)
    page.wait_for_timeout(10000) 

def reload_page():
    page = browser.page()
    browser.page().reload()