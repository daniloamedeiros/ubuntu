import unittest

import driver
import self
from selenium import webdriver


class MyTestCase(unittest.TestCase):
    def test_something(self):
        udid = "ZY3235B66B"
        url = "http://127.0.0.1:4723/wd/hub"

        desired_caps = {}
        desired_caps['platformName'] = "Android"
        desired_caps['udid'] = udid
        desired_caps['deviceName'] = udid
        desired_caps['appPackage'] = "com.globo.globotv"
        desired_caps['appActivity'] = "com.globo.globotv.splash.SplashActivity"
        desired_caps['noReset'] = True
        desired_caps['automationName'] = "uiautomator2"
        desired_caps['newCommandTimeout'] = 900
        desired_caps['no-reset'] = True
        driver = webdriver.Remote(url, desired_caps)
        driver = driver
        return driver



    (">>>>>>>>>>>>>> ", driver.get_settings)


if __name__ == '__main__':
    unittest.main()
