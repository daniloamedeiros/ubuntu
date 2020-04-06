### 3 arguments
# 1 -> device id
# 2 -> appium url
# 3 -> 1/0 (1 to turn tether ON. 0 to turn tether OFF) 


import os

from time import sleep
import time
import unittest
import datetime
import sys
from appium import webdriver

import urllib3
urllib3.disable_warnings()

class TetherIos(unittest.TestCase):

	def setUp(self):

		self.udid= sys.argv[1]	
		self.appium_url= sys.argv[2]

		#To switch off expect the 3rd argument to be 1 else 0
		self.switch_to = sys.argv[3]

		desired_caps = {}
	        desired_caps['platformName'] = 'iOS'
	        desired_caps['udid'] = self.udid
		desired_caps['deviceName'] = self.udid
		desired_caps['automationName'] = 'XCUITest'
		desired_caps['bundleId'] = 'io.headspin.tether'
		desired_caps['newCommandTimeout'] =600

	
		self.driver = webdriver.Remote(self.appium_url, desired_caps)

	def tearDown(self):
        	self.driver.quit()


	def test_tether(self):

		switch = self.driver.find_element_by_class_name('XCUIElementTypeSwitch')
		switch_state = switch.get_attribute('value')
		
		#Switch on tether
		if self.switch_to=="1" and switch_state != "1":
			switch.click()

		#Switch off tether
		if self.switch_to=="0" and switch_state !="0":
			switch.click()

		switch = self.driver.find_element_by_class_name('XCUIElementTypeSwitch')
		switch_state = switch.get_attribute('value')

		if switch_state == "1":
			print "Tether turned ON"

		else:
			print "Tether turned OFF"

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TetherIos)
    unittest.TextTestRunner(verbosity=2).run(suite)
