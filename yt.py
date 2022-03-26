import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def yt(text):
    text=text.lower()
    co=Options()
    co.add_experimental_option("detach",True)

    driver = webdriver.Chrome(r"C:\chromedriver.exe",options=co)
    driver.implicitly_wait(1)
    driver.maximize_window()
    indx = text.split().index('youtube')
    ind = text.split()[indx + 1:]
    driver.get("http://www.youtube.com/results?search_query="+'+'.join(ind))
    #print("http://www.youtube.com/results?search_query="+'+'.join(ind))

yt("play youtube dil galti kar baitha h")


#https://www.youtube.com/results?search_query=dil+galti+kar+betha+hai