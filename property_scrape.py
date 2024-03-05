from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth


PATH = "C:/chromedriver-win64/chromedriver.exe"

def get_homes_in_area(state,city):
    url="https://www.trulia.com/"+state+"/"+city+"/APARTMENT,CONDO,COOP,MULTI-FAMILY,SINGLE-FAMILY_HOME,TOWNHOUSE_type/"
    headers= {
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
         "Accept-Language":"en-US,en;q=0.9",
         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
         "Accept-Encoding":"gzip, deflate, br",
         "upgrade-insecure-requests":"1"
         }
    
    options = Options()
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver=webdriver.Chrome(service=Service(PATH))

    stealth(driver,
       user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.105 Safari/537.36',
       languages=["en-US", "en"],
       vendor="Google Inc.",
       platform="Win32",
       webgl_vendor="Intel Inc.",
       renderer="Intel Iris OpenGL Engine",
       fix_hairline=True,
       )
    
    driver.get(url)
    html = driver.find_element("tag name",'html')
    total_height = int(driver.execute_script("return document.body.scrollHeight"))

    #Implement smooth scroll to account for dynamically loaded properties
    for i in range(1, total_height, 10):
        driver.execute_script(f"window.scrollTo(0, {i});")
    html_content = driver.page_source

    # Parse the html content once all loaded
    soup = BeautifulSoup(html_content, "html.parser")
    html = soup.prettify("utf-8")

    #Find number of pages for iterating
    paginationList=soup.find_all("li",{"data-testid":"pagination-page-link"})
    limit=int(paginationList[-1].get_text())
    print("Pages:",limit)
    
    properties = {}

    for i in range(2,limit+1):
        #Process Properties
        for property in soup.findAll("div", attrs={"data-testid": "home-card-sale"}):
            validProperty=True
            try:
                link = property.find("a",attrs={"data-testid":"property-card-link"})
                price = property.find("div",attrs={"data-testid": "property-price"}).get_text()
                beds = property.find("div",attrs={"data-testid": "property-beds"}).get_text()
                baths = property.find("div",attrs={"data-testid": "property-baths"}).get_text()
                footage = property.find("div",attrs={"data-testid": "property-floorSpace"}).get_text()
                images=",".join([image["src"] for image in property.find("div",attrs={"data-testid":"property-card-carousel-container"}).find_all("img")])
            except Exception as e:
                validProperty=False
                print(e)     
            finally:
                if validProperty:
                    properties[link.div["title"]]=[link["href"],beds,baths,footage,price,images]
        #Stop if processed final page
        if i==(limit+1):
            break
        #Get next page data
        driver.get(url+str(i)+"_p/")
        html = driver.find_element("tag name",'html')
        total_height = int(driver.execute_script("return document.body.scrollHeight"))

        for j in range(1, total_height, 10):
            driver.execute_script(f"window.scrollTo(0, {j});")
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
    #see number found
    print(len(properties))
    with open(f'{state}_{city}_houses.tsv',mode="w") as f:
        f.write("Property\tLink\tPrice\tBeds\tBaths\tSquare Feet\tImage Links\n")
        for property in properties:
            f.write("\t".join([property]+properties[property])+"\n")
    return


if __name__ == "__main__":
    try:
        state=input("Enter an abbreviated state in the US (ex: Minnestoa -> MN): ")
        city=input("Enter a city in "+state+": ")
        get_homes_in_area(state,city)
    except Exception as e:
        print(e,"An exception occurred")
    finally:
        print("Done")
