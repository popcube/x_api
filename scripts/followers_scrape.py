from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import sys
import time
import os

account = "pj_sekai"
url = "https://twitter.com/" + account
# user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'


def lambda_handler(event, context):

    options = Options()
    # options.binary_location = "/opt/chromes-for-selenium/headless-chromium"
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--single-process")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--homedir=/tmp")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    # options.add_argument('user_agent=user_agent')
    driver = webdriver.Chrome(
        # "/opt/chromes-for-selenium/chromedriver",
        options=options
    )
    driver.implicitly_wait(30)
    driver.maximize_window()
    driver.get(url)
    print(1)

    actions = ActionChains(driver)
    print(2)
    html = driver.page_source.encode('utf-8')
    print(3)
    soup = BeautifulSoup(html, "html.parser")
    print(4)
    before_mouseover = soup.select('div[id="layers"]')
    print(5)
    print(before_mouseover)

    mouseover_ele = driver.find_element(
        By.XPATH, f'//a[@href="/{account}/followers"]')
    print()
    print("##### mouseover_ele #####")
    print(mouseover_ele.get_attribute("outerHTML"))
    print("##### is displayed? #####")
    print(mouseover_ele.is_displayed())
    print(mouseover_ele.rect)
    print(mouseover_ele.is_selected())
    print(mouseover_ele.is_enabled())
    print()
    hover = actions.move_to_element(mouseover_ele)
    hover.perform()
    while True:
        try:
            driver.find_element(By.XPATH, f'//div[@role="tooltip"]')
            break
        except:
            continue

    driver.save_screenshot("./ss.png")

    # mouseover_ele = driver.find_element(
    #     By.XPATH, f'//a[@href="/{account}/followers"]')
    # print(mouseover_ele.get_attribute("outerHTML"))
    # sys.exit(0)
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    after_mouseover = soup.select('div[id="layers"]')

    print()
    print("###### whether layer div is updated #####")
    print(not (before_mouseover == after_mouseover))

    print(soup.select('div[role="tooltip"]')[0].text)

    # time.sleep(100)


lambda_handler("", "")
