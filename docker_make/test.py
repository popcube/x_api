import json
from selenium import webdriver

def handler(event, context):
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    driver = webdriver.Chrome(options=options, executable_path="/opt/chromedriver")
    driver.get("https://example.com")

    print(driver.title)

    return {
        'statusCode': 200,
        'body': json.dumps("done.")
    }
