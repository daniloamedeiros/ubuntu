# coding=utf-8
# encoding=utf-8
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
import subprocess
import boto3
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from appium.webdriver.common.touch_action import TouchAction
from appium import webdriver
sys.path.append('../setup/py_modules')
from mysql_insert import MysqlDataInsert
from log_adb_info  import AdbDdata
from alerts_globo import SendAlert
from random import seed
from random import randint
import shlex

class Globo_Download_Content_iOS(unittest.TestCase):

    def setUp(self):

        self.reference= str(int(round(time.time() * 1000)))
        self.package = "com.globo.hydra"
        #device id as 1st argument
        self.device_id = sys.argv[1]
        self.os= "iOS"       
        
	self.adb_activities= AdbDdata()
        self.alerts = SendAlert()
       
	 #Before test function
        #self.adb_activities.before_test(self.device_id)
        self.capture_cap = sys.argv[3]
      
	  #desired caps for the app
        desired_caps = {}
        desired_caps['platformName'] = self.os
        desired_caps['automationName'] = 'XCUITest'	
        desired_caps['udid'] = self.device_id
        desired_caps['deviceName'] = self.device_id
        desired_caps['bundleId'] = self.package
        desired_caps['newCommandTimeout'] =600
        desired_caps['no-reset'] = True
	if self.capture_cap == "1":
            desired_caps['headspin:capture'] = True
        else:
            desired_caps['headspin:capture'] = False       
 
        self.status = "Fail_Launch"
        self.path=os.getcwd()+ "/logs/"+str(self.reference)
        print self.path
       	os.mkdir(self.path)	
	self.process =subprocess.Popen("exec "+"idevicesyslog -u " + self.device_id + " > " +self.path+"/"+ str(self.reference)+'_'+self.device_id + ".log", shell=True) 
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
	
	#Insert to app table
        insert = MysqlDataInsert()
        insert.globo_download_content(self.driver, self.app_launch_time,self.home_pg_load_time, self.video_load_time, self.title_check,self.download_time, self.pass_count,self.fail_count,self.status,self.reference,self.session_id,self.test_name)

	screenshot_name = str(self.reference)+"_"+self.device_id+".png"
        self.driver.save_screenshot(self.path+"/" + screenshot_name)

        screenshot_path = self.path+"/"+screenshot_name

        log_file_name = str(self.reference)+"_"+self.device_id+".log"
        log_path = self.path+"/" + log_file_name

        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(screenshot_path, 'grafana-images.headspin.io', 'globo/'+screenshot_name)
        s3.meta.client.upload_file(log_path, 'grafana-images.headspin.io', 'globo/'+log_file_name)
        print "Pushed to AWS"

        log_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+log_file_name
        png_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+screenshot_name	
 
        
        self.threshold= 5000
        if not all( i< self.threshold for i in list(self.kpi_dic.values())) or self.status!= "Pass":
            slack_messge= []
            message_to_be_send=""
            if not all( i< self.threshold for i in list(self.kpi_dic.values())):
                for key,value in self.kpi_dic.items():
                    if value>self.threshold:
                        slack_messge.append('{} : {}'.format(key,value))
                for text in slack_messge:
                    message_to_be_send =  message_to_be_send+text+"\n"
                print message_to_be_send
            message_to_be_send = self.os+"\n"+self.device_id+"\n"+message_to_be_send+"\n" +"Device_log url:"+log_url+"\n"+"Device screenshot url:"+png_url
            #slack alert
            self.alerts.slack_alert(message_to_be_send)
            #Mail Alert
            self.alerts.email_alert(message_to_be_send)
        
        self.driver.quit()

    def videoplay_check(self, sec):
        self.driver.implicitly_wait(5)
        t_end = time.time() + sec
        while time.time() < t_end:
            try:
		sleep(5)
		self.driver.tap([(105,181)])
                player_control = self.driver.find_element_by_accessibility_id("PlayPauseButton")
            except:
                spinner = self.driver.find_element_by_name("spinner")
                print "Video Interrupted"
                self.video_play()

    def video_play(self):
        self.driver.implicitly_wait(30)
        t_end = time.time() + 10
        cmd = shlex.split("idevicesyslog -u  %s" % self.device_id)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for line in iter(process.stdout.readline, b''):
            if "FigStreamPlayer" in line:
                print "VideoPlayed"
                video_end = int(round(time.time() * 1000))
                break
            if time.time() > t_end_ad:
                break
        process.kill()
    
    def delete_download(self):
        self.driver.implicitly_wait(6)
        try:
            downloads_tab = self.driver.find_element_by_name("Downloads")
            downloads_tab.click()
            sleep(5)
            edit_button = self.driver.find_element_by_accessibility_id("Editar")
            edit_button.click()
            check_box = self.driver.find_element_by_class_name("XCUIElementTypeCell").find_element_by_class_name("XCUIElementTypeButton")
            check_box.click()
            conf_del = self.driver.find_element_by_accessibility_id("Apagar")
            conf_del.click()
        except:
            pass

    def test_login(self):
        self.driver.implicitly_wait(60)
        
	#Launching app
        agora_tab = self.driver.find_element_by_name("Agora")
        launched_app = int(round(time.time() * 1000))
   
        #calcualting launch time
        self.app_launch_time = launched_app - self.start_app
        print ("App Launch Time is %s ms" %self.app_launch_time)
        d = {'globo_launch_time': self.app_launch_time}
        self.kpi_dic.update(d)
        #incrementing pass count
        self.pass_count +=1
   	sleep(3)

        self.delete_download()
        self.driver.implicitly_wait(60)
        home_tab = self.driver.find_element_by_name("Início")
        home_tab.click()

        #login
        self.status="Fail_login"
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        tap_x = width*0.924
        tap_y = height*0.057
        #profile_button tap
        self.driver.tap([(tap_x,tap_y)])

        #logout
        try:
            self.driver.implicitly_wait(5)
            logout_button = self.driver.find_element_by_name("Sair")
            logout_button.click()
            confirm_button = self.driver.find_element_by_name("Sim")
            confirm_button.click()
            self.driver.find_element_by_class_name("XCUIElementTypeNavigationBar")
            sleep(2)
            self.driver.tap([(tap_x,tap_y)])
        except:
            pass

        self.driver.implicitly_wait(30)
        entrar = self.driver.find_element_by_name("Entrar")	
        entrar.click()

        email_id = self.driver.find_element_by_name("e-mail")
        email_id.click()
        email_id.set_value('laurent_headspin')

        password = self.driver.find_element_by_name("senha")
        password.click()
        password.set_value('Globo@321')

        login_button = self.driver.find_element_by_name("ENTRAR")
        login_button.click()


        self.status = "Fail_page_load_post_login"

        self.driver.find_element_by_name("Sair")
        sleep(2)
        close_x_tap = width*0.934
        close_y_tap = height*0.0587

        self.driver.tap([(close_x_tap,close_y_tap)])
        
        start_login = int(round(time.time() * 1000))
        home_button = self.driver.find_element_by_name("Agora")
        self.driver.find_element_by_class_name("XCUIElementTypeImage")
        end_login = int(round(time.time() * 1000))

        self.home_pg_load_time =end_login - start_login
        print("Home page loading time is %s ms" %self.home_pg_load_time)

        d = {'globo_post_login_home_load_time': self.home_pg_load_time}
        self.kpi_dic.update(d)

        self.pass_count = self.pass_count + 1
        sleep(5)

        categories = self.driver.find_element_by_name("Categorias") 
        categories.click()
        sleep(4)
        novelas = self.driver.find_element_by_name("Novelas")
        novelas.click()
        sleep(4)
        
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        
	swipe_start_x = width/2
        swipe_start_y = height*0.6
        swipe_end_x = width/2
        swipe_end_y = height*0.2

        sleep(4)
        seed(time.time())
	for i in range (0,randint(0,4)):
	    self.driver.swipe(swipe_start_x,swipe_start_y,swipe_end_x,swipe_end_y,1000)
	seed(time.time()**2)

	selector = "type == 'XCUIElementTypeStaticText' AND visible == 1"
   	title_buttons = self.driver.find_elements_by_ios_predicate(selector)
  	title_button = title_buttons[randint(0,5)]
	sleep(5)

	location = title_button.location
	size = title_button.size
	self.x_tap = location['x']+int(size['width']/2)
        self.y_tap= location['y']+int(size['height']/2)
	self.driver.tap([(self.x_tap,self.y_tap)])
            
	sleep(5)
	title_name = self.driver.find_element_by_accessibility_id("titleHighlightViewCellTitleName")
	get_title_name = title_name.text.lower().encode('utf-8')
	title_name =str(get_title_name)
            
        self.driver.implicitly_wait(10) 
	try:
	    thumb_button = self.driver.find_elements_by_class_name("XCUIElementTypeCollectionView")[0].find_elements_by_class_name("XCUIElementTypeButton")[0]
	    thumb_button.click()
	    sleep(2)
	except:
	    pass            

	self.status= "Fail_video_play"
            
	try:
	    continue_button = self.driver.find_element_by_name("titleHighlightViewCellFirstButton")
	except:
	    pass	
	sleep(4)
	try:
	    continue_button.click()
	except:
	    con_x = width*0.296
	    con_y = height*0.607
	    self.driver.tap([(con_x,con_y)])

        video_start = int(round(time.time() * 1000))
	t_end_ad = time.time() + 60
	cmd = shlex.split("idevicesyslog -u  %s" %self.device_id)
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

	for line in iter(process.stdout.readline, b''):
		if "FigStreamPlayer" in line:
			print "VideoPlayed"
                        video_end = int(round(time.time() * 1000))
	                break
                if time.time() > t_end_ad:
                        break
	process.kill()

	self.video_load_time = video_end - video_start

        self.driver.implicitly_wait(5)
        try:
                oops_button = self.driver.find_element_by_name("OK")
                oops_button.click()
                sleep(2)
                self.driver.tap([(con_x, con_y)])

                video_second = int(round(time.time() * 1000))
                t_end_ad = time.time() + 60
                cmd = shlex.split("idevicesyslog -u  %s" % self.device_id)
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

                for line in iter(process.stdout.readline, b''):
                        if "FigStreamPlayer" in line:
                                print "VideoPlayed"
                                video_play = int(round(time.time() * 1000))
                                break 
                        if time.time() > t_end_ad:
                                break
                process.kill()
                self.video_load_time = video_play - video_second
        except:
                pass

	print "Video load time ", self.video_load_time
	d = {'globo_video_load_time': self.video_load_time}
	self.kpi_dic.update(d)
        sleep(5)
	self.pass_count = self.pass_count + 1
	
	#Watch the Video for 1 minute	
	self.videoplay_check(30)
	self.driver.implicitly_wait(10)
	
	screen_size = self.driver.get_window_size()
	width = screen_size['width']
	height = screen_size['height']
	swipe_start_x = width/2
	swipe_start_y = height*0.7
	swipe_end_x = width/2
	swipe_end_y = height*0.3
	
	try:
		potential_download_buttons = self.driver.find_elements_by_accessibility_id("")
		flag=0
		for j in potential_download_buttons:
			if j.size['height']>=22 and j.size['height']<=28:
				download_button = j
                        	flag=1
                        	break
            		if flag==1:
				break
		sleep(5)

	        download_button.click()	
	except:
		tap_x = width*0.21
		tap_y = height*0.708
		self.driver.tap([(tap_x,tap_y)])

        start_download = int(round(time.time() * 1000))
            

        t_end = time.time() +50
        self.driver.implicitly_wait(3)
	self.status = "Fail_Download"
        downloads_tab = self.driver.find_element_by_accessibility_id("Downloads")
        downloads_tab.click()
        try:
            dont_cancel_download = self.driver.find_element_by_accessibility_id("Não")
            dont_cancel_download.click()
            downloads_tab = self.driver.find_element_by_accessibility_id("Downloads")
            downloads_tab.click()   
        except:
            pass
	sleep(5)

	self.driver.implicitly_wait(50)
        download_title_name = self.driver.find_elements_by_class_name("XCUIElementTypeCell")[0].find_elements_by_class_name("XCUIElementTypeStaticText")[2].get_attribute("name")
        download_title = download_title_name.lower().encode("utf-8")
	download_title_name = str(download_title)
        print download_title_name
        if download_title_name == title_name:
                print "Title Added to list"
                self.title_check = True
                self.pass_count = self.pass_count+1
    
        self.driver.implicitly_wait(5)
	t_end = time.time() + 1200
        while time.time() < t_end:
            try:
                download_bar = self.driver.find_element_by_accessibility_id("1 download em andamento")
            except:
                end_download = int(round(time.time() * 1000))
                break	


        sleep(4)
	self.download_time = end_download -start_download
        print "Download time:  ",self.download_time
        self.pass_count = self.pass_count+1
        d = {'Download_time': self.download_time}
        self.kpi_dic.update(d)

        self.driver.implicitly_wait(50)
        self.delete_download()
        sleep(5)
        
        if self.title_check ==False:
            self.status="Fail_title_check"
        else:
            self.status = "Pass"

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Globo_Download_Content_iOS)
    unittest.TextTestRunner(verbosity=2).run(suite)





