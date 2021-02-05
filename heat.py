import re
import requests
from bs4 import BeautifulSoup as b
import concurrent.futures

# ui functionality:
#   user should be able to add filters based on heat, ingredients, awards, 
#   chile pepper and brand. User should be able to filter down from any one
#   one of those things: eg, out of those with extreme heat, i want the ones
#   that mention garlic, and from those I want ones that won awards. The filters
#   can maybe be provided narrowing order or somehow utilize set() after compiling?
#   First item in the filter can be category search (this is only filter the
#   site will let you narrow down by). This includes: award winning, heat level,
#   chile pepper, or brand. And then if you click on a sauce you can further 
#   narrow with the other given filters. Using the set() method will probably 
#   be the best option here. So, use first filter and then with the other filters
#   you can narrow down with set. But you'll likely just have to scrape all the
#   sauces first.

#   output should give a list of all titles/brands matching those requirements along
#   with each of their respective urls, and or description. You can maybe later 
#   add an option to add them to the cart or to do a search for them on amazon
#   or something. 
#
#   set() may not work as well as just using an AND condition while scraping
#   pages based on first filter. One other thing you can do is just scrape all
#   pages and then use filters and set() afterwards. Initially it will take longer
#   but then you won't need to send anymore requests for that. 

#   You can use threadpoolexecutor to fetch contents of sauces. 

def page_search():
    '''
    Collects URLs of sauces for each page of results based on the first
    filter given by user
    '''

    base_url =  "https://heathotsauce.com"
    filters = str(input()).split(', ')

    # Initialize first page

    page = 1
    collections_url = base_url + '/collections/' + filters[0].replace(' ', '-') + str(page)
    html = requests.get(collections_url).text
    soup = b(html, "html.parser")
    total_sauce_list = []

    # Loop through pages until end

    while not soup.find(text=re.compile("*.o products found.*")):

        collections_url = base_url + '/collections/' + filters[0].replace(' ', '-') + str(page)
        page += 1
        sauces = soup.find_all(class_=re.compile("three columns.*"))
        sauce_list = [sauce.a.attrs['href'] for sauce in sauces]
        total_sauce_list.extend(sauce_list)

    return total_sauce_list, filters, base_url# Fed to executor and sauce_filter_search()


def sauce_filter_search(sauce_url, filters, base_url):
    '''
    Returns relevant info as results when sauce page meets filter criteria
    '''

    html = requests.get(base_url + sauce_url)
    soup = b(html, "html.parser")
    result = []
    if soup.find(text=re.compile(r'*.{filters}.*', re.I)): # TODO syntax poss incor.
        title = soup.title.get_text()
        #description = soup.meta.find(name='description').attrs['content'].get_text()
        # add title, url, price, descrption to results dict or list
        return result

def main():
    results = []
    total_sauce_list, filters, base_url = page_search()
    with concurrent.futures.ThreadPoolExecutor as executor:
        for result in executor.map(sauce_filter_search, total_sauce_list): # TODO incomplete
            results.append(result)
    return results
if __name__ == "__main__":
    results = main()
    print(results)
