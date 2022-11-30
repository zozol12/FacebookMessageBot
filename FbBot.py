import sys
from time import sleep

from selenium import webdriver
import logging

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from driver_init import DriverInitializer

logger = logging.getLogger(__name__)
format = logging.Formatter("[%(asctime)s] [%(name)s | %(levelname)s] %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)

class FbBot:
    """Facebook Bot that is using normal account"""
    driver: webdriver.Chrome
    username: str = None
    password: str = None
    cookies: list = None
    blocked: bool = False
    tries: int = 0

    driver_working: bool = True

    def __init__(self, login: str = None, password: str = None, cookies: list = None,
                 driver_ini: DriverInitializer = DriverInitializer(None, True, None)):
        """Creates instance of FbBot, you can either specify only login and password or only cookies OR both.
        You can use FbBot.from_credentials(login, pass) or FbBot.from_cookies(cookies)
        to create instance with better flexibility."""
        logger.setLevel(logging.DEBUG)
        logger.info("Initializing new instance of FbBot.")
        self.username = login
        self.password = password
        self.driver = driver_ini.init()
        self.driver.implicitly_wait(2)
        if cookies is not None:
            self.set_cookies(cookies)

        self.driver_working = False

    @classmethod
    def from_credentials(cls, login: str, password: str,
                         proxy: str = None, headless: bool = True, browser_profile=None):
        """Create FacebookBot using credentials"""
        driver_ini = DriverInitializer(proxy, headless, browser_profile)
        return cls(login=login, password=password, driver_ini=driver_ini)

    @classmethod
    def from_cookies(cls, cookies: list, proxy: str = None, headless: bool = True, browser_profile=None):
        """Create FacebookBot using cookies (exported as json using for example c3c FbState Utility)"""
        driver_ini = DriverInitializer(proxy, headless, browser_profile)
        return cls(cookies=cookies, driver_ini=driver_ini)

    def login(self):
        """Login using available methods (login/pass or cookies)
        Returns logged in state (True if login was successful or False if it wasn't)"""
        if self.username and self.password is not None:
            try:
                self.driver.get("https://facebook.com/login.php")
                self.__accept_cookies(self.driver)
                email = self.driver.find_element(By.NAME, "email")
                email.send_keys(self.username)
                passw = self.driver.find_element(By.NAME, "pass")
                passw.send_keys(self.password)
                loginbtn = self.driver.find_element(By.ID, "loginbutton")
                loginbtn.click()
                self.driver.refresh()
            except NoSuchElementException as ex:
                logger.info("FbBot is already logged in")
                pass
            if self.is_logged_in():
                return True
        if self.cookies is not None:
            self.set_cookies(self.cookies)
            if self.is_logged_in():
                return True
        return False

    def set_cookies(self, cookies: list):
        """Sets cookies"""
        self.cookies = cookies
        # Parse and add cookies
        for cookie in cookies:
            # Fbstate.json Integration
            if 'key' in cookie:
                cookie['name'] = cookie['key']
            # sameSite is redundant
            if 'sameSite' in cookie:
                cookie.pop("sameSite")
            # if cookie["key"] == "c_user":
            #     self.uid = cookie["value"]
            self.driver.add_cookie(cookie)

    def send_message(self, uid, message):
        """Send Message to user with provided UID"""
        self.driver_working = True
        if not self.is_logged_in:
            self.driver_working = False
            raise Exception("The bot is not logged in. You need to use login function before sending message!")
        try:
            self.driver.get(f"https://www.facebook.com/messages/t/{uid}/")
            blocked_list = self.driver.find_elements(By.XPATH,
                                                     '//span[contains(text(), "You can\'t message this account.") or '
                                                     'contains(text(), "Nie możesz wysyłać wiadomości do tego konta.")]')
            if len(blocked_list) > 0:
                logger.exception(f"Couldn't message user <{uid}>. This account is not eligible to message this user.")
                return False

            text = self.driver.find_element(By.XPATH, "//div[@aria-label='Message' or @aria-label='Wiadomość']/p")
            text.send_keys(message)
            # \n works as an enter
            text.send_keys("\n")
            sleep(1)
            self.tries = 0
            self.driver_working = False
            logger.info(f"Message to user <{uid}> was successfully sent.")
            return True
        except Exception as ex:
            self.driver_working = False
            # if account fails to send a message 5 times for unknown reason, FbBot state is set as blocked
            if self.__is_blocked():
                raise Exception("Couldn't send message, because sending messages function is blocked")
            self.tries += 1
            if self.tries == 5:
                self.blocked = True
            raise Exception(f"Couldn't send message! Reason: {ex}")

    def is_logged_in(self):
        """Check if bot is logged in to fb"""
        try:
            if "login" in self.driver.current_url:
                return False
        except Exception as ex:
            raise Exception(f"Error at Checking logged in state. Reason: {ex}")
        return True

    # TODO
    # def get_uids_from_group(self, gid: str, users: int = 10000) -> list[str]:
    #     """Scrape UIDs from facebook group (max 10.000 users - facebook limitation) and it needs some time.
    #
    #     Parameters:
    #         gid (str) - Facebook Group ID.
    #         users (int) - Amount of users to collect.
    #     """

    def __is_blocked(self):
        self.driver.get("https://www.facebook.com/messages/t/")
        sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//span[text()='You’re Temporarily Blocked']")
            logger.exception('Account is blocked for sending messages!')
            self.blocked = True
            return True
        except:
            return False

    @staticmethod
    def __accept_cookies(driver):
        """Accept cookies if theres popup"""
        try:
            button = driver.find_element(By.XPATH, "//button[.='Only allow essential cookies']")
            button.click()
        except NoSuchElementException:
            pass
        except Exception as ex:
            raise Exception(f"Error at accepting cookies. Reason: {ex}")
