from selenium import webdriver
from selenium.webdriver.common.by import By


class ChromeControl(object):
    def __init__(self, driver_path):
        self.options = webdriver.ChromeOptions()
        prefs = {
            "profile.default_content_setting_values.notifications": 1,
        }
        self.options.add_experimental_option('prefs', prefs)
        self.options.add_experimental_option('excludeSwitches', ['disable-popup-blocking', 'enable-logging'])
        self.options.add_argument('start-maximized')
        self.driver = webdriver.Chrome(driver_path, options=self.options)
        self.driver.implicitly_wait(5)

    def button_click(self, element):
        self.driver.find_element(By.XPATH, element).click()

    def get_text(self, element):
        return self.driver.find_element(By.XPATH, element).text

    def find_element(self, element):
        return self.driver.find_element(By.XPATH, element)

    def find_elements(self, element):
        return self.driver.find_elements(By.XPATH, element)
