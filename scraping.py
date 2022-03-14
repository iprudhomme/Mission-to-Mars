# Import Splinter and BeautifulSoup
from signal import pthread_kill
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    hemispheres = mars_hemispheres(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres" : hemispheres
    }

    browser.quit()
    return data 

# Setup Splinter
#executable_path = {'executable_path': ChromeDriverManager().install()}
#browser = Browser('chrome', **executable_path, headless=False)

def mars_news(browser):
    # Visit the Mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #Convert the browswer html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for erro handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None 

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None 

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

## Mars Facts
def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
        
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    return df.to_html()

def mars_hemispheres(browser):
    # Visit the Mars Hemisphere site
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Retrieve the image urls and titles for each hemisphere.
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        #Use the div tag to return the 4 titles and the anchor tags to the full image pages. 
        hemispheres = img_soup.find_all('div', class_='description')

        #Loop through the hemispheres
        for hemisphere in hemispheres:
            hemispheres_dict = {}
            #assign the title from each description
            title = hemisphere.h3.text
            #use the title for the browsers' find by text option, to find the anchor tag to click
            browser.links.find_by_partial_text(title).click() 
            #use the find by text to find the Sample anchor and grab the href from it.
            img_url = browser.find_by_text("Sample")["href"]
            #save the retrieved image url and the tile to the hemispheres_dict
            hemispheres_dict['image_url'] = img_url    
            hemispheres_dict['title'] = title
            #append the hemispheres_dict to the final list.
            hemisphere_image_urls.append(hemispheres_dict)
            browser.back()
    except BaseException:
        return None

    #Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls


if __name__ == "__main__":
   print(scrape_all())