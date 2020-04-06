# -*- coding: utf-8 -*-

from sh import tail
import os
from time import sleep
import mysql.connector
import subprocess
import shlex
import socket
import sh
import time
import unittest
import logging
import datetime
import sys
import subprocess
import smtplib
from appium import webdriver
import boto3
	
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

sys.path.append('../setup/py_modules')
from mysql_insert import MysqlDataInsert
from log_adb_info  import AdbDdata
from alerts_globo import SendAlert

class SimpleAndroidTests(unittest.TestCase):
    def setUp(self):
	self.udid = sys.argv[1]
        self.device_id = self.udid
#	self.capture_cap = sys.argv[3]

        desired_caps = {}
        desired_caps['platformName'] = 'iOS'
	desired_caps['automationName'] = 'XCUITest'	
        desired_caps['udid'] = self.device_id
	desired_caps['deviceName'] = self.device_id
	desired_caps['bundleId'] = "com.globo.hydra"
	desired_caps['newCommandTimeout'] =600
#	if self.capture_cap =="1":
#		desired_caps['headspin.capture'] = True
#	else:
#		desired_caps['headspin.capture'] = False
	desired_caps['no-reset'] = True

	self.os= "iOS"
	self.status = "Fail_Launch"
	self.home_pg_load_time= 0
	self.app_launch_time = 0 
	self.series_load_time = 0 
	self.video_laod_time = 0
	self.buffer_in_video= False
	self.movie_check=False
	self.progress_check=False
	self.session_id = None
	self.kpi_dic= {}
	self.pass_count = 0
        self.fail_count = 0
	self.kpi_count=4
	
	self.alerts = SendAlert()
	
	#Start the log cature
#        self.timestamp =  str(int(round(time.time() * 1000)))
#        self.path=os.getcwd()+ "/logs/"+str(self.timestamp)
#        print self.path
#        os.mkdir(self.path)
#
#        self.process =subprocess.Popen("exec "+"idevicesyslog -u " + self.device_id + " > " +self.path+"/"+ str(self.timestamp)+'_'+self.device_id + ".log", shell=True)
#
	appium_input= sys.argv[2]
        if appium_input.isdigit():
        	self.url= ('http://127.0.0.1:' + appium_input + '/wd/hub')
        else:
        	self.url= appium_input
        print self.url

        self.driver = webdriver.Remote(self.url, desired_caps)
		
	self.start_app= int(round(time.time() * 1000))

    def tearDown(self):

#	print "Pass count is %s" %self.pass_count
#        if self.pass_count!=self.kpi_count:
#                self.fail_count = self.kpi_count - self.pass_count
#        else:
#                self.fail_count = 0
#        print "Fail count is %s " %self.fail_count
#	if self.capture_cap =="1":
#                self.session_id = self.driver.session_id
#                print self.session_id
#        else:
#                self.session_id = None

#	screenshot_name = str(self.timestamp)+"_"+self.device_id+".png"
#	self.driver.save_screenshot(self.path+"/" +screenshot_name)
#	
#	if self.status!="Pass":
#		print self.driver.page_source.encode('utf-8')
#	screenshot_path = self.path+"/"+screenshot_name
#	
#	log_file_name = str(self.timestamp)+"_"+self.device_id+".log"
#	log_path = self.path+"/"+ log_file_name
#
#
#	s3 = boto3.resource('s3')
#        s3.meta.client.upload_file(screenshot_path, 'grafana-images.headspin.io','globo/'+screenshot_name)
#        s3.meta.client.upload_file(log_path, 'grafana-images.headspin.io','globo/'+log_file_name)
#        print "Pushed to AWS"
#	
#	log_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+log_file_name
#        png_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+screenshot_name
#	
#	self.threshold= 5000
#	if not all( i< self.threshold for i in list(self.kpi_dic.values())) or self.status!= "Pass"  :
#                        slack_messge= []
#			message_to_be_send=""
#                        if not all( i< self.threshold for i in list(self.kpi_dic.values()) ):
#
#                                for key,value in self.kpi_dic.items():
#                                        if value>self.threshold:
#                                                slack_messge.append('{} : {}'.format(key,value))
#                                for text in slack_messge:
#                                        message_to_be_send =  message_to_be_send+text+"\n"
#        	                print message_to_be_send
#
#                        message_to_be_send = self.os+"\n"+self.udid+"\n"+message_to_be_send+"\n" +"Device_log url:"+log_url+"\n"+"Device screenshot url:"+png_url
#
#                        #slack alert
#                        self.alerts.slack_alert(message_to_be_send)
#
#                        #Mail ALert
#                        self.alerts.email_alert(message_to_be_send)

       #Insert to app table
#        insert = MysqlDataInsert()
#        insert.globo_kpi_metrics(self.driver, self.app_launch_time, self.home_pg_load_time, self.series_load_time, self.video_laod_time, self.buffer_in_video, self.pass_count,self.fail_count,self.status,self.timestamp,self.session_id)
	
#        print self.process.pid
#        self.process.kill()


	#end the session
        self.driver.quit()

    def videoplay_check(self, sec):
        self.driver.implicitly_wait(5)
        t_end = time.time() + sec
        while time.time() < t_end:
            try:
                screen_size = self.driver.get_window_size()
                width = screen_size['width']
                height = screen_size['height']
                tap_x = width*0.5
                tap_y=height*0.23
                self.driver.tap([(tap_x,tap_y)])
                seek_bar = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeOther' and name CONTAINS 'seekbar'")
                sleep(5)
            except:
                spinner = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeImage' and name CONTAINS 'spinner'")
                print "Video Interrupted"
                self.video_play()

    def video_play(self):
        self.driver.implicitly_wait(1)
        t_end = time.time() + 10
        while time.time() < t_end:
            try:
                spinner = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeImage' and name CONTAINS 'spinner'")
                print "Spinner!!"
            except:
                break


 


    def test_globo(self):
	#App Launch
	self.driver.implicitly_wait(50)

	#Check if the app lauunch is completed
	home_button = self.driver.find_element_by_name("Agora")

	launched_app = int(round(time.time() * 1000))

        #calcualting launch time
        self.app_launch_time = launched_app - self.start_app
        print ("App Launch Time is %s ms" %self.app_launch_time)
	d = {'globo_launch_time': self.app_launch_time}
#        self.kpi_dic.update(d)
	
#	self.pass_count = self.pass_count + 1
	
	sleep(5)
		


	#********new test********
	category_btn = self.driver.find_element_by_name("Categorias")
	category_btn.click()
	
	cinema_tab = self.driver.find_element_by_name("Cinema")
	cinema_tab.click()
	
	movie_title=self.driver.find_element_by_name("Harry Potter E A Pedra Filosofal")
	movie_title_value=movie_title.get_attribute('value')
	movie_title.click()
	assista_btn = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and label CONTAINS 'Continue'")
	sleep(2)
	print"found"
        location = assista_btn.location
        size=assista_btn.size
        self.x_tap = location['x']+int(size['width']/2)
        self.y_tap= location['y']+int(size['height']/2)
        print self.x_tap,self.y_tap
	sleep(5)
        self.driver.tap([(self.x_tap,self.y_tap)])
	print"clicked"

	#tap
	video_player= self.driver.find_element_by_name("Container")
	print" video "
	#video_player=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeOther' and name CONTAINS 'Container'")
	screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        tap_x = width/2
        tap_y=height/4
	sleep(5)
        self.driver.tap([(tap_x,tap_y)])
        print"Tap done"
		

	video_start = int(round(time.time() * 1000))
        t_end_ad = time.time() + 60
        cmd = shlex.split("idevicesyslog -u  %s" %self.device_id)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for line in iter(process.stdout.readline, b''):
                if "FigStreamPlayer" in line:
                        video_end = int(round(time.time() * 1000))
                        print "VideoPlayed"
                        break
                if time.time() > t_end_ad:
                        break
        process.kill()
	self.video_laod_time = video_end- video_start
        print "Video load time ", self.video_laod_time
#        d = {'globo_video_load_time': self.video_laod_time}
#        self.kpi_dic.update(d)

#        self.pass_count = self.pass_count + 1


	#***watch video for a minute***
	self.videoplay_check(60)
	self.driver.implicitly_wait(50)
	
	#pause_btn=self.driver.find_element_by_name("PlayPauseButton")
	

	back_btn = self.driver.find_element_by_name("Voltar")
	back_btn.click()

	sleep(1)
	#checking conditions
	progress_bar = self.driver.find_element_by_name("Progresso").get_attribute('value')

	progress = progress_bar.split('%')[0]
	print progress_bar
	
	self.driver.close_app()
	sleep(10)
	self.driver.launch_app()


	home_btn=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Início'")
	home_btn.click()
	print"on home page"

	search_btn=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Busca'")
        search_btn.click()
	search_bar=self.driver.find_element_by_class_name("XCUIElementTypeSearchField")
	#type-XCUIElementTypeSearchField , name-O que você quer assistir?
	search_bar.click()
	search_bar.send_keys("Harry Potter E A Pedra Filosofal")
	#movie=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeStaticText' and name CONTAINS 'Harry Potter E A Pedra Filosofal'")
	movie=self.driver.find_element_by_name("Harry Potter E A Pedra Filosofal")
	movie_value=movie.get_attribute('value')
	movie.click()

	if(movie_title_value==movie_value):
	    print "Title found"
	    self.movie_check=True
	    #self.pass_count = self.pass_count + 1		
	else:
	    print"Title not found"
	
	

	progress_bar_chk=self.driver.find_element_by_name("Progresso").get_attribute('value')
	print progress_bar_chk
	progress_chk=progress_bar_chk.split('%')[0]
		
	if(int(progress)==int(progress_chk)):
	    print"Progress bar value same"
	    self.progress_check=True
	   # self.pass_count = self.pass_count + 1 	
	else:
	    print"value not same"



	

	
	
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
	

