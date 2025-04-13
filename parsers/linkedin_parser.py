from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import LINKEDIN_PASSWORD, YOUR_EMAIL
import logging
import time
import traceback
import random
import pickle
from typing import List, Dict
from database import get_user_settings
from config import SessionLocal

logger = logging.getLogger(__name__)

def save_cookies(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def human_like_delay(min=1, max=3):
    time.sleep(random.uniform(min, max))

def human_like_type(element, text):
    for char in text:
        element.send_keys(char)
    time.sleep(random.uniform(0.1, 0.3))

def parse_linkedin(user_id: int) -> List[Dict]:
    db = SessionLocal()
    try:
        settings = get_user_settings(db, user_id)
        if not settings:
            return []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-single-click-autofill")
        options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
        options.add_argument("--disable-translate")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3]
        });
        """
        })

        return login_and_search(driver, settings)

    except Exception as e:
        logger.error(f"LinkedIn parsing error: {e}")
        logger.debug(traceback.format_exc())
        return []
    finally:
        db.close()
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Driver quit failed: {e}")

def login_and_search(driver, settings):
    try:

        try:
            driver.get("https://www.linkedin.com")
            load_cookies(driver, "linkedin_cookies.pkl")
            driver.refresh()
            human_like_delay(2, 4)

            if "feed" in driver.current_url:
                logger.info("Logged in via cookies")
            else:
                raise Exception("Cookies not valid")
        except:
            logger.info("Logging in normally")
            driver.get("https://www.linkedin.com/login")
            human_like_delay(2, 5)

            username = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password = driver.find_element(By.ID, "password")

            human_like_type(username, YOUR_EMAIL)
            human_like_delay(1, 2)
            human_like_type(password, LINKEDIN_PASSWORD)
            human_like_delay(1, 2)

            submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit.click()
            human_like_delay(3, 6)

            save_cookies(driver, "linkedin_cookies.pkl")

        search_url = (
            f"https://www.linkedin.com/jobs/search/?keywords={'%20'.join(settings.keywords)}"
            f"&location={'%20'.join(settings.locations)}"
        )
        driver.get(search_url)
        human_like_delay(3, 6)

        # Wait for results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list"))
        )

        # Scroll to load more results
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Parse results
            vacancies = []
            jobs = driver.find_elements(By.CSS_SELECTOR, ".jobs-search__results-list li")

            for job in jobs[:15]:  # Limit to 15 results
                try:
                    title = job.find_element(By.CSS_SELECTOR, "h3").text.strip()
                    company = job.find_element(By.CSS_SELECTOR, "h4").text.strip()
                    url = job.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                    vacancies.append({
                        "title": title if title else 'Not specified',
                        "company": company if company else 'Not specified',
                        "salary": "Not specified",  # LinkedIn often doesn't show salary
                        "url": url,
                        "source": "LinkedIn"
                    })
                except Exception as e:
                    logger.warning(f"Error parsing LinkedIn job: {e}")

            return vacancies

    except Exception as e:
        logger.error(f"Error during LinkedIn search: {e}")
        return []
