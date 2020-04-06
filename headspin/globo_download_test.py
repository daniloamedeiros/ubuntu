
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
import requests
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

from appium import webdriver
sys.path.append('../setup/py_modules')
from mysql_insert import MysqlDataInsert
from log_adb_info  import AdbDdata
from alerts_globo import SendAlert


class SimpleAndroidTests(unittest.TestCase):
	
#check if the necessary folders are present, if not create
    def check_dir(self,dir_path):
            if not os.path.isdir(dir_path):
                    print "Creating the log dir"
                    os.mkdir(dir_path)

    def adb_dump_data(self, udid,reference, step, adb_dump_dir):

	
        #save teh sys dump of the phone
        self.adb_activities.get_dumpsys(udid, reference, step, adb_dump_dir )

        #Get the cpu info
        cpu_usage = self.adb_activities.get_cpuinfo(udid)

        #Get mem info
        mem_usage= self.adb_activities.get_mem_info(udid, self.package)

        #Device temp
        temperature= self.adb_activities.get_device_temp(udid)

        print step, cpu_usage,mem_usage, temperature
        return [step, cpu_usage,mem_usage,temperature]

    def setUp(self):

	self.reference= str(int(round(time.time() * 1000)))
	self.package = "com.globo.globotv"

	#device id as 1st argument
        self.udid = sys.argv[1]
	self.os = 'Android'
	
	#logs folder	
	self.logs_dir = os.getcwd()+ "/logs"
	print self.logs_dir
	self.check_dir(self.logs_dir) 
	self.logs_dir= self.logs_dir + "/"+ self.reference
	os.mkdir(self.logs_dir )


	#adb_dump folder
        self.adb_dump_dir= os.getcwd()+ "/adb_dump"
        self.check_dir(self.adb_dump_dir)
        self.adb_dump_dir= self.adb_dump_dir+ "/"+ self.reference
        os.mkdir(self.adb_dump_dir)

	self.adb_activities= AdbDdata()
	self.alerts = SendAlert()
	self.array_of_data_list= []
	adb_data= self.adb_dump_data(self.udid, self.reference, "Before_Test", self.adb_dump_dir)	
	self.array_of_data_list.append(adb_data)

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
#	desired_caps['headspin:controlLock']= True
        desired_caps['automationName'] = "uiautomator2"
	desired_caps['newCommandTimeout'] =600
	if self.capture_cap =="1":
		desired_caps['headspin:capture.video'] = True
	        desired_caps['headspin:capture.network'] = False
#                desired_caps['headspin.capture'] = True
        else:
                desired_caps['headspin.capture'] = False
        desired_caps['no-reset'] = True

	#appium input as 2nd argument	
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
	self.video_laod_time= 0
	self.download_start_time = 0
	self.dowload_check = False
	self.kpi_count =4
	self.pass_count = 0
        self.fail_count = 0

    def tearDown(self):
		
	#incrementing kpi count
	print "Pass count is %s" %self.pass_count
        if self.pass_count!=self.kpi_count:
                self.fail_count = self.kpi_count - self.pass_count
        else:
                self.fail_count = 0
        print "Fail count is %s " %self.fail_count

	#After function
	self.adb_activities.after_test(self.udid, self.reference, self.driver, self.status)
	if self.capture_cap =="1":
		self.session_id = self.driver.session_id
        	print self.session_id
        else:
                self.session_id = None
        #Insert to app table
        insert = MysqlDataInsert()
#        insert.globo_kpi_metrics(self.driver, self.app_launch_time, self.home_pg_load_time, self.series_load_time, self.video_laod_time, self.buffer_in_video, self.pass_count,self.fail_count,self.status,self.reference,self.session_id)


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
	
	#data_list is [step,cpuinfo, meminfo, temp]
	adb_data= self.adb_dump_data(self.udid, self.reference, "After_Test", self.adb_dump_dir)
	self.array_of_data_list.append(adb_data)

	#data_list is [step,cpuinfo, meminfo, temp]
	for data_list in self.array_of_data_list:
                insert.globo_device_details(self.driver, data_list, self.status, self.reference)
        self.driver.quit()

    def test_login(self):


        self.driver.implicitly_wait(60)
        #Launching app
	home_page_image  = self.driver.find_element_by_id('com.globo.globotv:id/custom_view_premium_highlights_image_view_background')
        launched_app = int(round(time.time() * 1000))
	
	#calcualting launch time
        self.app_launch_time = launched_app - self.start_app
        print ("App Launch Time is %s ms" %self.app_launch_time)
	d = {'globo_launch_time': self.app_launch_time}
        self.kpi_dic.update(d)
	#incrementing pass count
	self.pass_count +=1

	
	categories_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().text("Categorias")')
	categories_tab.click()


	novelas = self.driver.find_element_by_android_uiautomator('new UiSelector().text("Novelas")')
	novelas.click()

	first_poster = self.driver.find_elements_by_id('com.globo.globotv:id/custom_view_title_image_view_poster')[0]
	first_poster.click()
	
	thumb = self.driver.find_element_by_id("com.globo.globotv:id/thumb")

	title = self.driver.find_element_by_id("com.globo.globotv:id/title")
	
	thumb = self.driver.find_element_by_id("com.globo.globotv:id/thumb")
        thumb.click()

	self.status= "Fail_video_play"

	self.driver.implicitly_wait(1)
        t_end= time.time() +60
	video_start = int(round(time.time() * 1000))
        while time.time() < t_end:
                try:
                        spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
                        print "Spinner!!"
                except:
                        print "Not displayed"
                        break
		
	self.driver.implicitly_wait(1)
	t_end= time.time() +60
	while time.time() < t_end:
		try:
	                spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
			print "Spinner!!"
		except:
			print "Not displayed"
			break
		
	video_end = int(round(time.time() * 1000))

	self.video_laod_time = video_end- video_start
	print "Video load time ", self.video_laod_time
	self.pass_count +=1
	d = {'globo_video_load_time': self.video_laod_time}

        self.kpi_dic.update(d)
		
	sleep(5)	
		
	self.status="Fail_Download"
	donwload_button = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_download_status_content_root")
	donwload_button.click()

	start_download = int(round(time.time() * 1000))
	download_progress = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_download_status_status_progress_bar")
	end_download = int(round(time.time() * 1000))

	self.download_start_time = end_download - start_download
	print " Download start time ",self.download_start_time
	self.pass_count +=1
	d = {'globo_download_start_time': self.download_start_time}

        self.kpi_dic.update(d)

	sleep(5)

	navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Navigate up")')
	navigate_up.click()

	sleep(3)
	self.status = "Fail_Download_Verify"

	download_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().text("Downloads")')
	download_tab.click()

	download_title = self.driver.find_element_by_id("com.globo.globotv:id/view_holder_download_text_view_title")
	download_title.click()

	title_name = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_video_text_view_title")
	print "Title found on download list"
	self.dowload_check = True
	self.pass_count +=1

	sleep(2)	
	progress = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_download_status_status_progress_bar")
	progress.click()
		
	accept_button = self.driver.find_element_by_id("android:id/button1")
	accept_button.click()
	
	sleep(2)
	self.status = "Pass"
	
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)





