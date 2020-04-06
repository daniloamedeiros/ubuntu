# -*- coding: utf-8 -*-

from sh import tail
import os
from time import sleep
import mysql.connector
import subprocess
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
	self.session_id = None
	self.kpi_dic= {}
	self.pass_count = 0
        self.fail_count = 0

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
#        if self.pass_count!=5:
#                self.fail_count = 5 - self.pass_count
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
		
	#login
	self.status="Fail_login"
	screen_size = self.driver.get_window_size()
	width = screen_size['width']
        height = screen_size['height']
	tap_x = width*0.92
	tap_y = height*0.064
	
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

        close_x_tap = width*0.061
        close_y_tap = height*0.064

        self.driver.tap([(close_x_tap,close_y_tap)])
	
	start_login = int(round(time.time() * 1000))
	home_button = self.driver.find_element_by_name("Agora")
        self.driver.find_element_by_class_name("XCUIElementTypeImage")
	end_login = int(round(time.time() * 1000))

	self.home_pg_load_time =end_login - start_login
	print("Home page loading time is %s ms" %self.home_pg_load_time)

#	d = {'globo_post_login_home_load_time': self.home_pg_load_time}
#        self.kpi_dic.update(d)
#
#	self.pass_count = self.pass_count + 1
#
#	sleep(2)
		
	#series view time

#	categories_tab = self.driver.find_element_by_name("Categorias")
#	categories_tab.click()	
#
#	series_tab = self.driver.find_element_by_name("Séries")
#	series_tab.click()
#
#	sleep(5)
#
#        first_poster_tab = self.driver.find_element_by_class_name("XCUIElementTypeStaticText")
#        first_poster_tab.click()
#	
#	series_load_start= int(round(time.time() * 1000))
#	self.driver.find_element_by_name("Episódios")	
#	series_load_end = int(round(time.time() * 1000))
#		
#	self.series_load_time = series_load_end- series_load_start
#	d = {'globo_series_page_load_time': self.series_load_time}
#        self.kpi_dic.update(d)
#        print "Series load time",self.series_load_time
#	self.pass_count = self.pass_count + 1
#
#	sleep(2)

	#video playback
#	self.status= "Fail_video_play"
#	self.driver.implicitly_wait(10)
#	try:
#		continue_button = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Continue'")
#	except:
#		continue_button = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Assista'")
#	sleep(4)
#	try:
#		continue_button.click()
#	except:
#		con_x = width*0.309
#        	con_y = height*0.618
#		self.driver.tap([(con_x,con_y)])
#	video_start = int(round(time.time() * 1000))
#
#        self.driver.implicitly_wait(1)
#        t_end= time.time() +60
#        while time.time() < t_end:
#                try:
#                        spinner = self.driver.find_element_by_name("spinner")
#                except:
#                        break
#	video_end = int(round(time.time() * 1000))
#	t_end= time.time() +10
#        while time.time() < t_end:
#                try:
#                        spinner = self.driver.find_element_by_name("spinner")
#                except:
#			video_end = int(round(time.time() * 1000))
#                        break
#
#        self.video_laod_time = video_end- video_start
#        print "Video load time ", self.video_laod_time
#	d = {'globo_video_load_time': self.video_laod_time}
#        self.kpi_dic.update(d)
#	
#        self.pass_count = self.pass_count + 1
#	self.buffer_in_video= False
#	sleep(5)
#	t_end= time.time() +60
#        while time.time() < t_end:
#                try:
#                        spinner = self.driver.find_element_by_name("spinner")
#                        self.buffer_in_video= True
#                        break
#                except:
#                        pass
#
#        if self.buffer_in_video:
#                self.status= "Video_interrupted"
#        else:
#                self.status = "Pass"
#		self.pass_count +=1
	


	#######new test
	category_btn = self.driver.find_element_by_name("Categorias")
	category_btn.click()
	
	cinema_tab = self.driver.find_element_by_name("Cinema")
	cinema_tab.click()
	
	movie_title=self.driver.find_element_by_name("Harry Potter E A Pedra Filosofal")
	movie_title.click()
	assista_btn = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Continue'")
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
		


	#seekbar moved to half the movie length
	pause_btn=self.driver.find_element_by_name("PlayPauseButton")
        #pause_btn = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'PlayPauseButton'")
	pause_btn.click()
	sleep(5)
	
        seek_bar = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeOther' and name CONTAINS 'seekbar'")
	location = seek_bar.location
	size=seek_bar.size
	self.x_tap = location['x']+int(size['width']*0.66)
	self.y_tap= location['y']+int(size['height']/2)	
	print self.x_tap,self.y_tap
	self.driver.tap([(self.x_tap,self.y_tap)])
	sleep(2)

	elapsed_time=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeStaticText' and name CONTAINS 'elapsedTime'").get_attribute('value')
	total_time=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeStaticText' and name CONTAINS 'totalDuration'").get_attribute('value')
	hr,min,sec=elapsed_time.split(':')
	time_elapsed=(int(hr)*60)+int(min)+(int(sec)/60)
	print time_elapsed
	hour,minute,second=total_time.split(':')
	time_total=(int(hour)*60)+int(minute)+(int(second)/60)
	print time_total

	remaining_time=time_total-time_elapsed-1
	print remaining_time

	pause_btn.click()
	sleep(1)
	#scrubber=self.driver.find_element_by_name("scrubber")#type-XCUIElementTypeOther

	back_btn = self.driver.find_element_by_name("Voltar")
	back_btn.click()

	
	#checking conditions
	progress_bar = self.driver.find_element_by_name("Progresso").get_attribute('value')

	progress = progress_bar.split('%')[0]
	#print progress
	if int(progress) >= 50:
		print"Progress bar moved"
	else :
		print"error"
	continue_btn = self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Continue'")
	print"continue button found"

	time_btn=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeStaticText' and name CONTAINS 'restantes'").get_attribute('value')
	print time_btn
	if "h" in time_btn:
		hr_time=time_btn.split("h")[0]
		min_time=time_btn.split("min")[0].split("h")[1]
		time_remain=(int(hr_time)*60)+int(min_time)
	else :
		min_time=time_btn.split("min")[0]
		time_remain=int(min_time)

	if remaining_time == time_remain:
		print"time verified"
	else :
		print"error"
	

	
	#self.driver.close_app()
	#sleep(10)
	#self.driver.launch_app()


	home_btn=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Início'")
	home_btn.click()
	print"on home page"

	search_btn=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeButton' and name CONTAINS 'Busca'")
        search_btn.click()
	search_bar=self.driver.find_element_by_class_name("XCUIElementTypeSearchField")
	#type-XCUIElementTypeSearchField , name-O que você quer assistir?
	search_bar.click()
	search_bar.send_keys("Harry Potter E A Pedra Filosofal")
	movie=self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeStaticText' and name CONTAINS 'Harry Potter E A Pedra Filosofal'")
	movie.click()
	
	


	#swipe down
	#screen_size = self.driver.get_window_size()
        #width = screen_size['width']
        #height = screen_size['height']
     	#swipe_start_x = width/2
	#swipe_start_y = height*0.25
	#swipe_end_x = width/2
	#swipe_end_y = height*0.75
	#sleep(2)
	#self.driver.swipe(swipe_start_x, swipe_start_y, swipe_end_x, swipe_end_y)	
	#sleep(2)
	#self.driver.swipe(swipe_end_x, swipe_end_y, swipe_start_x, swipe_start_y)
	#sleep(2)
	#print"swiped"
	#self.driver.implicitly_wait(10)

	#btn=self.driver.find_element_by_name("Continue assistindo")
	#print"element found"
	#checking for movie name and progress bar
#	movie_name = self.driver.find_element_by_name("")
#	movie_progressbar = self.driver.find_element_by_name("Progresso").get_attribute('value')




	#####download test###
        #category_btn = self.driver.find_element_by_name("Categorias")
	#category_btn.click()

	#novelas_btn = self.driver.find_element_by_name("Novelas")
	#novelas_btn.click()

	#series_title = self.driver.find_element_by_name("A Dona do Pedaço")
	#series_title.click()

	
	#self.driver.find_element_by_ios_predicate("type == 'XCUIElementTypeStaticText' and name CONTAINS 'TRECHOS'")
	#print "page loaded"
	
	#tap
	#screen_size = self.driver.get_window_size()
        #width = screen_size['width']
        #height = screen_size['height']
        #tap_x = width/2
        #tap_y=height*0.33
        #sleep(5)
        #self.driver.tap([(tap_x,tap_y)])
        #print"Tap done"

	# play full series
##	video_player= self.driver.find_element_by_name("Container")
##	print"started playing"
##	sleep(2100)
	#elt to identify video fully played
##	print"end"
	sleep(2)

	#screen_size = self.driver.get_window_size()
        #width = screen_size['width']
        #height = screen_size['height']
        #tap_x = width*0.16
        #tap_y=height*0.72
        #sleep(5)
        #self.driver.tap([(tap_x,tap_y)])
        #print"Tapped download btn"
	
	#elt to check whether download started
	#sleep(600)

	


	#download_btn = self.driver.find_element_by_name("Downloads")
	#download_btn.click()
	
	#series_title = self.driver.find_element_by_name("A Dona do Pedaç")
	#series_title.click()
	
	#self.driver.find_element_by_name("videoCellTitleLabel")
	#print"series added to download list"

	

	
	
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
	

