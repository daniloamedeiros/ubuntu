
from time import sleep
import os
import mysql.connector
import socket
import sh
import time
import unittest
import logging
import datetime
import sys
import ConfigParser
import random
from random import seed
from random import randint
from appium import webdriver
sys.path.append('../setup/py_modules')
from mysql_insert import MysqlDataInsert
from log_adb_info  import AdbDdata
from alerts_globo import SendAlert


class Globo_Download_Content_Test(unittest.TestCase):
	
	def setUp(self):
		self.reference= str(int(round(time.time() * 1000)))
		self.package = "com.globo.globotv"
		#device id as 1st argument
		self.udid = sys.argv[1]
		self.os = 'Android'
	
		self.adb_activities= AdbDdata()
	        self.alerts = SendAlert()

        	#Befre test function
	        self.adb_activities.before_test(self.udid)

		self.capture_cap = sys.argv[3]
		#desired caps for the app
		desired_caps = {}
		desired_caps['platformName'] = self.os
		desired_caps['udid'] = self.udid
		desired_caps['deviceName'] = self.udid
		desired_caps['appPackage'] = self.package
		desired_caps['appActivity'] = "com.globo.globotv.splash.SplashActivity"
		desired_caps['noReset'] = True
		desired_caps['automationName'] = "uiautomator2"
		desired_caps['newCommandTimeout'] =600
		desired_caps['no-reset'] = True
		if self.capture_cap == "1":
            		desired_caps['headspin:capture'] = True
        	else:
            		desired_caps['headspin:capture'] = False
		appium_input= sys.argv[2]
		if appium_input.isdigit():
			self.url= ('http://127.0.0.1:' + appium_input + '/wd/hub')
		else:
			self.url= appium_input
		#launching app
		self.driver = webdriver.Remote(self.url, desired_caps)
		self.start_app = int(round(time.time() * 1000))
		#initialising variables
		self.status = "Fail_launch"
		self.app_launch_time= 0
		self.status_dic = {}
		self.kpi_dic= {}
		self.app_launch_time= 0
		self.home_pg_load_time = 0
		self.video_load_time = 0
		self.download_time = 0 
		self.title_check = False
		self.test_name = "Globo_Download_Content"
		self.kpi_count = 5
		self.pass_count = 0
		self.fail_count = 0

		self.title_name = ""
	
	def tearDown(self):		
		#incrementing kpi count
		print "Pass count is %s" %self.pass_count
		if self.pass_count!=self.kpi_count:
			self.fail_count = self.kpi_count - self.pass_count
		else:
			self.fail_count = 0
		print "Fail count is %s " %self.fail_count
	
		if self.capture_cap =="1":
                	self.session_id = self.driver.session_id
                	print self.session_id
        	else:
                	self.session_id = None	

		self.adb_activities.after_test(self.udid, self.reference, self.driver, self.status)
	
		insert = MysqlDataInsert()
	        insert.globo_download_content(self.driver, self.app_launch_time,self.home_pg_load_time, self.video_load_time, self.title_check,self.download_time, self.pass_count,self.fail_count,self.status,self.reference,self.session_id,self.test_name)
	

		path=os.getcwd()+ "/logs/"

	        if self.status=="Pass":
        	        screenshot_name = str(self.reference)+'_'+ self.udid +".png"
                	log_file_name = str(self.reference)+'_'+self.udid + ".log"
        	else:
                	log_file_name = str(self.reference)+'_'+self.udid + "_error.log"
                	screenshot_name = str(self.reference)+'_'+ self.udid +"_error.png"


	        screenshot_path = path+"/"+screenshot_name

        	log_path = path+"/"+ log_file_name

        	log_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+log_file_name
        	png_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+screenshot_name

		self.threshold= 5000
	        if not all( i< self.threshold for i in list(self.kpi_dic.values())) or self.status!= "Pass"  :
                        slack_messge= []
                        message_to_be_send=""
                        if not all( i< self.threshold for i in list(self.kpi_dic.values()) ):

                                for key,value in self.kpi_dic.items():
                                        if value>self.threshold:
                                                slack_messge.append('{} : {}'.format(key,value))
                                for text in slack_messge:
                                        message_to_be_send =  message_to_be_send+text+"\n"
                                print message_to_be_send

                        message_to_be_send = self.os+"\n"+self.udid+"\n"+message_to_be_send+"\n" +"Device_log url:"+log_url+"\n"+"Device screenshot url:"+png_url

                        #slack alert
                        self.alerts.slack_alert(message_to_be_send)

                        #Mail ALert
                        self.alerts.email_alert(message_to_be_send)
		self.driver.quit()
	
	
	def videoplay_check(self, sec):
		self.driver.implicitly_wait(5)
		t_end = time.time() + sec
		while time.time() < t_end:
			try:
				sleep(5)
				screen_size = self.driver.get_window_size()
				width = screen_size['width']
				height = screen_size['height']
				tap_x = width*0.4
				tap_y=height*0.23
				self.driver.tap([(tap_x,tap_y)])
				player_control = self.driver.find_element_by_id("com.globo.globotv:id/media_control")
			except:
				spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
				print "Video Interrupted"
				self.video_play()		
	
	def video_play(self):
		self.driver.implicitly_wait(1)
		t_end = time.time() + 10
		while time.time() < t_end:
			try:
				spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
			except:
				break		
	
	def delete_download(self):
		self.driver.implicitly_wait(6)
		try:
			downloads_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Downloads")')
			downloads_tab.click()

			sleep(5)
			edit_button = self.driver.find_element_by_id("com.globo.globotv:id/menu_downloads_item_edit")
			edit_button.click()

			
			check_box = self.driver.find_elements_by_id("com.globo.globotv:id/view_holder_download_title_check_box_selected")
			for box in check_box:
				box.click()
				sleep(1)
	
			conf_del = self.driver.find_element_by_id("com.globo.globotv:id/snackbar_action")
			conf_del.click()
		except:
			pass
	
	#Select a random novela and check if it's downloadable. Else, searches and selects another random Novela
	def search_random_novela(self):
		screen_size = self.driver.get_window_size()
		width = screen_size['width']
		height = screen_size['height']
		swipe_start_x = width/2
		swipe_start_y = height*0.6
		swipe_end_x = width/2
		swipe_end_y = height*0.2
		while True:
			sleep(4)
			categories = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Categorias")')
			categories.click()
			
			novelas = self.driver.find_element_by_android_uiautomator('new UiSelector().text("Novelas")')
			novelas.click()
			sleep(3)

			random.seed(time.time())
			n=0
			#Random number of swipes on novela screen
			while n<random.randint(0,6):
				self.driver.swipe(swipe_start_x,swipe_start_y,swipe_end_x,swipe_end_y,1000)
				n+=1
			random.seed(time.time())
			#Picks random novela from those currently on screen
			title_button = self.driver.find_elements_by_id("com.globo.globotv:id/view_holder_custom_view_grid_custom_view_title")[random.randint(0,5)]
			title_button.click()
			
			sleep(2)

			self.title_name = self.driver.find_element_by_id("com.globo.globotv:id/title").text
			self.title_name = self.title_name.lower()

			print self.title_name
			thumb_button = self.driver.find_element_by_id("com.globo.globotv:id/thumb")
			sleep(2)
			thumb_button.click()
			self.driver.implicitly_wait(2)
			try:
				self.driver.find_element_by_id("com.globo.globotv:id/activity_video_custom_view_download")
				break
			except:
				sleep(5)
				back_btn = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Navigate up")')
		                back_btn.click()	
				sleep(3)
				back_btn = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Navigate up")')
		                back_btn.click()
				continue

	def video_metrics_control(self):
		#Starting video and monitoring it's metrics
		self.status="Fail_video_Play"	
		video_start = int(round(time.time() * 1000))
		self.driver.implicitly_wait(1)
		t_end = time.time() +60
		while time.time() < t_end:
			try:
				spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
			except:
				print "Not displayed"
				break
			
		self.driver.implicitly_wait(1)
		t_end = time.time() +60
		while time.time() < t_end:
			try:
				spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
			except:
				video_end = int(round(time.time() * 1000))
				break
		self.video_load_time = video_end- video_start	
		self.driver.implicitly_wait(5)
	        try:
        	        self.driver.find_element_by_id("android:id/button1").click()
			sleep(2)
                	play_button.click()
                	video_second = int(round(time.time() * 1000))
                	self.driver.implicitly_wait(1)
                	t_end = time.time() +60
                	while time.time() < t_end:
                        	try:
                                	spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
                        	except:
                                	break

                	t_end= time.time() +60
                	while time.time() < t_end:
                        	try:
                                	spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
                        	except:
                                	video_play = int(round(time.time() * 1000))
                                	break
			self.video_load_time = video_play - video_second
 	        except: 
      			pass
	
		print "Video load time ", self.video_load_time
		d = {'globo_video_load_time': self.video_load_time}
		self.kpi_dic.update(d)
		sleep(4)	
		#Watch the Video for 1 minute	
		self.videoplay_check(30)
		self.driver.implicitly_wait(50)
	
	def test_login(self):
		self.driver.implicitly_wait(60)
		#Launching app
		agora_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Agora")')
		launched_app = int(round(time.time() * 1000))
		
		#calcualting launch time
		self.app_launch_time = launched_app - self.start_app
		print ("App Launch Time is %s ms" %self.app_launch_time)
		d = {'globo_launch_time': self.app_launch_time}
		self.kpi_dic.update(d)
		#incrementing pass count
		self.pass_count +=1
		sleep(2)

		self.delete_download()
		self.driver.implicitly_wait(60)
		
		home_tab = self.driver.find_element_by_id("com.globo.globotv:id/menu_bottom_navigation_view_item_home")
		home_tab.click()
		self.status="Fail_login"
		user_icon = self.driver.find_element_by_id("com.globo.globotv:id/menu_profile_custom_view_profile")
		user_icon.click()
		
		#Log out
		try:
			self.driver.implicitly_wait(5)
			logout =  self.driver.find_element_by_android_uiautomator('new UiSelector().text("Sair")')
			logout.click()
			#Confirm log out
			yes_btn = self.driver.find_element_by_id('android:id/button1')
			yes_btn.click()
			#Click on te account button
			self.driver.implicitly_wait(10)
			user_icon = self.driver.find_element_by_id("com.globo.globotv:id/menu_profile_custom_view_profile")
			user_icon.click()
		except:
			pass
		self.driver.implicitly_wait(60)
		entrar = self.driver.find_element_by_id('com.globo.globotv:id/activity_profile_text_view_get_int')
		entrar.click()
		self.driver.implicitly_wait(10)
		try:
			none_of_the_above = self.driver.find_element_by_id("com.google.android.gms:id/cancel")
			none_of_the_above.click()
		except:
			pass
		sleep(5)
		self.driver.implicitly_wait(60)
		email_id_tf = self.driver.find_element_by_class_name('android.widget.EditText')
		email_id_tf.set_value('laurent_headspin')
		#password
		password_tf = self.driver.find_elements_by_class_name('android.widget.EditText')[1]
		password_tf.set_value('Globo@321')
		
		sleep(5)
		buttons= self.driver.find_elements_by_class_name("android.widget.Button")
		for button in buttons:
			entrar = button.text
			if entrar =="ENTRAR":
				button.click()
				break
		
		self.status = "Fail_page_load_post_login"
		back_btn = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Navigate up")')
		back_btn.click()
		home_page_load_start = int(round(time.time() * 1000))
		self.driver.implicitly_wait(0.5)
		t_end = time.time()+60
		while time.time() < t_end:
			try:
				self.driver.find_element_by_class_name('android.widget.ProgressBar')
			except:
				break
		
		self.driver.implicitly_wait(60)
		home_page = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_premium_highlights_image_view_background")
		home_page_load_end = int(round(time.time() * 1000))
		self.home_pg_load_time = home_page_load_end- home_page_load_start
		d = {'globo_post_login_home_load_time': self.home_pg_load_time}
		self.kpi_dic.update(d)
		sleep(2)
		self.pass_count +=1
		print "Home page loading time ", self.home_pg_load_time	
		while True:
			self.search_random_novela()
			self.video_metrics_control()
			#*********Download content**********# 
			download_button = self.driver.find_element_by_id("com.globo.globotv:id/activity_video_custom_view_download")
			download_button.click()
			self.driver.implicitly_wait(15)
			try:
				start_download = int(round(time.time() * 1000))
				download_progress = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_download_status_status_progress_bar")
				break
			except:
				download_limit = self.driver.find_element_by_class_name("android.widget.Button")
				download_limit.click()
				navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Navigate up")')
				navigate_up.click()
				navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Navigate up")')
				navigate_up.click()
				continue
		sleep(2)
		#video play pass count increment
		self.pass_count= self.pass_count+1
		self.driver.implicitly_wait(60)
		navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Navigate up")')
		navigate_up.click()
		
		navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Navigate up")')
		navigate_up.click()
		
		downloads_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Downloads")')
		downloads_tab.click()
		sleep(2)
	
		download_title = self.driver.find_elements_by_id("com.globo.globotv:id/view_holder_download_text_view_title")
		
		screen_size = self.driver.get_window_size()
	        width = screen_size['width']
        	height = screen_size['height']

        	swipe_start_x = width/2
        	swipe_start_y = height*0.7
        	swipe_end_x = width/2
        	swipe_end_y = height*0.3
	
		self.driver.implicitly_wait(10)	
	
		for i in range(0,5):	
			try:
				options_menu = self.driver.find_element_by_id("com.globo.globotv:id/view_holder_download_title_text_view_downloading")
				break
			except:
				sleep(2)	
				self.driver.swipe(swipe_start_x,swipe_start_y,swipe_end_x,swipe_end_y)

		download_title = self.driver.find_elements_by_id("com.globo.globotv:id/view_holder_download_text_view_title")

		for title in download_title:
			download_title_name = title.text.lower()
			print download_title_name
			if download_title_name ==self.title_name:
				print "Title Added to list"
	                        self.title_check = True
        	                self.pass_count = self.pass_count+1
				break	
	
		options_menu = self.driver.find_element_by_id("com.globo.globotv:id/view_holder_download_title_text_view_downloading")
		options_menu.click()
			
		
		sleep(4)
		self.driver.implicitly_wait(5)
		
		#Waits for download to finish
		self.status="Fail_Download"
		t_end = time.time() + 1200
	        while time.time() < t_end:
			try:
				self.driver.find_element_by_id("com.globo.globotv:id/custom_view_download_status_status_progress_bar")
				continue
			except:
				self.driver.implicitly_wait(5)
				try:
					ok_entendi = self.driver.find_element_by_id("android:id/button1")
				except:
					self.driver.find_element_by_id("com.globo.globotv:id/custom_view_download_status_image_view_icon")	
				end_download = int(round(time.time() * 1000))
				self.download_time = end_download - start_download - 10000
				print "Download time:  ",self.download_time
				self.pass_count = self.pass_count+1
				d = {'globo_download_time': self.download_time}
				self.kpi_dic.update(d)
				break
		
		self.driver.implicitly_wait(50)
		self.delete_download()
		sleep(5)
		
		if self.title_check ==False:
			self.status="Fail_title_check"
		else:
			self.status = "Pass"

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(Globo_Download_Content_Test)
	unittest.TextTestRunner(verbosity=2).run(suite)





