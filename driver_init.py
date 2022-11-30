from seleniumwire import webdriver

from selenium.webdriver.chrome.options import Options as ChromeOptions

from webdriver_manager.chrome import ChromeDriverManager
import logging

logger = logging.getLogger(__name__)


class DriverInitializer:
    driver: webdriver.Chrome

    def __init__(self, proxy=None, headless=True, profile=None):
        self.proxy = proxy
        self.headless = headless
        self.profile = profile

    def set_properties(self, browser_option):
        """adds capabilities to the driver"""
        if self.headless:
            browser_option.add_argument('--headless')
        if self.profile:
            logger.info("Loading Profile from {}".format(self.profile))
            browser_option.add_argument("user-DATA-dir={}".format(self.profile))
        browser_option.add_argument('--no-sandbox')
        browser_option.add_argument("--disable-dev-shm-usage")
        browser_option.add_argument('--ignore-certificate-errors')
        browser_option.add_argument('--disable-gpu')
        browser_option.add_argument('--log-level=3')
        browser_option.add_argument('--disable-notifications')
        browser_option.add_argument('--disable-popup-blocking')
        return browser_option

    def init(self):
        """returns driver instance"""
        logger.setLevel(logging.INFO)
        # if browser is suppose to be chrome
        browser_option = ChromeOptions()
        # automatically installs chromedriver and initialize it and returns the instance
        if self.proxy is not None:
            options = {
                'https': 'https://{}'.format(self.proxy.replace(" ", "")),
                'http': 'http://{}'.format(self.proxy.replace(" ", "")),
                'no_proxy': 'localhost, 127.0.0.1'
            }
            logger.info("Using: {}".format(self.proxy))
            self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                           options=self.set_properties(browser_option), seleniumwire_options=options)

        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                       options=self.set_properties(browser_option))
        return self.driver
