from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import sys
import time

account = "pj_sekai"
url = "https://twitter.com/" + account
# user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'

options = Options()
options.add_argument('--headless')
options.add_argument("--window-size=1920,1080")
# options.add_argument('user_agent=user_agent')
driver = webdriver.Chrome(options=options)
driver.get(url)


actions = ActionChains(driver)
html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html, "html.parser")
before_mouseover = soup.select('div[id="layers"]')
print(before_mouseover)

mouseover_ele = driver.find_element(
    By.XPATH, f'//a[@href="/{account}/followers"]')
print()
print()
print(mouseover_ele.get_attribute("outerHTML"))
print(mouseover_ele.is_displayed())
print()
actions.move_to_element(mouseover_ele).perform()
time.sleep(1)
mouseover_ele = driver.find_element(
    By.XPATH, f'//a[@href="/{account}/followers"]')
print(mouseover_ele.get_attribute("outerHTML"))
# sys.exit(0)
html = driver.page_source.encode('utf-8')
soup = BeautifulSoup(html, "html.parser")
after_mouseover = soup.select('div[id="layers"]')

print(before_mouseover == after_mouseover)

print(soup.select('div[role="tooltip"]')[0].text)

# time.sleep(100)
