import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from interval import every
from send_status import send_telegram

USER = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
TIMER = int(os.getenv('TIMER'))

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# chrome_options.headless = True
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('disable-gpu')

service = Service(ChromeDriverManager().install())


def init_driver():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver


def login(driver):
    driver.get("https://ircc-tracker-suivi.apps.cic.gc.ca/en/login")
    username = driver.find_element(By.ID, 'uci')
    username.send_keys(USER)

    password_input = driver.find_element(By.ID, 'password')
    password_input.send_keys(PASSWORD)

    driver.find_element(By.ID, 'sign-in-btn').click()


def get_updated_date(driver):
    meta_data_elements_locator = (By.CSS_SELECTOR, ".meta-data span:nth-child(2)")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(meta_data_elements_locator))

    updated_date_element = driver.find_element(*meta_data_elements_locator)
    date_text = updated_date_element.text.strip()
    return datetime.strptime(date_text, "%b %d, %Y")


def check_profile():
    driver = None
    try:
        driver = init_driver()
        login(driver)

        # Find and click on the last row in the table
        last_row_locator = (By.CSS_SELECTOR, "table tr:last-child")
        last_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located(last_row_locator))
        last_row.click()

        # Find and click on the first column in the last row
        first_column_locator = (By.CSS_SELECTOR, "table tr:last-child td:first-child a")
        first_column_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located(first_column_locator))
        first_column_link.click()

        # Wait for the relevant elements to be present on the page
        meta_data_elements_locator = (By.CSS_SELECTOR, ".meta-data span:nth-child(2)")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(meta_data_elements_locator))

        updated_date = get_updated_date(driver)

        four_days_ago = datetime.now() - timedelta(days=2)
        if updated_date >= four_days_ago:
            driver.get_screenshot_as_file("screenshot.png")
            print('\033[32m' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ' Current status: Update!' + '\033[0m')
            send_telegram('Ghost update! Check profile ASAP')
        else:
            print('\33[33m' + datetime.now().strftime(
                '%d-%m-%Y %H:%M:%S') + ' Current status: Nothing new, try again later.' + '\33[0m')

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()


check_profile()

every(TIMER, check_profile)

