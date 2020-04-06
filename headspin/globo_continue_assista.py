
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
from appium.webdriver.common.touch_action import TouchAction
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
	if self.capture_cap =="1":
		desired_caps['headspin.capture'] = True	
        else:
                desired_caps['headspin.capture'] = False
        desired_caps['no-reset'] = True


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
	self.initial_video_play= 0 
	self.sub_video_play = 0
	self.title_check = False
	self.progress_check = False
	self.test_name = "Continue_Assistindo"
	self.kpi_count = 6
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
        insert.globo_continuar_metrics(self.driver, self.app_launch_time,self.home_pg_load_time, self.initial_video_play, self.title_check,self.progress_check,self.sub_video_play, self.pass_count,self.fail_count,self.status,self.reference,self.session_id,self.test_name)


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
		screen_size = self.driver.get_window_size()
		width = screen_size['width']
		height = screen_size['height']
		tap_x = width*0.5
		tap_y=height*0.23
		self.driver.tap([(tap_x,tap_y)])
		player_control = self.driver.find_element_by_id("com.globo.globotv:id/media_control")
		sleep(5)	
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
		print "Spinner!!"
            except:
		break		

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

        #library tab view time
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

	self.driver.implicitly_wait(10)
	try:
        	entrar = self.driver.find_element_by_id('com.globo.globotv:id/activity_profile_text_view_get_int')
        	entrar.click()
	except:
		user_icon = self.driver.find_element_by_id("com.globo.globotv:id/menu_profile_custom_view_profile")
	        user_icon.click()
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
	button = self.driver.find_element_by_android_uiautomator('new UiSelector().text("ENTRAR")')
	location = button.location
	size = button.size
	self.x_tap = location['x']+int(size['width']/2)
	self.y_tap= location['y']+int(size['height']/2)
        sleep(2)
	self.driver.tap([(self.x_tap,self.y_tap)])


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

	self.driver.implicitly_wait(50)
        home_page = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Agora")')
        home_page_load_end = int(round(time.time() * 1000))
        self.home_pg_load_time = home_page_load_end- home_page_load_start
        d = {'globo_post_login_home_load_time': self.home_pg_load_time}
        self.kpi_dic.update(d)
        self.pass_count +=1
        print "Home page loading time ", self.home_pg_load_time	
	
	
	sleep(4)
	#Choose a title from home page

	categories_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Categorias")')
        categories_tab.click()
        sleep(2)

	
        series = self.driver.find_elements_by_id('com.globo.globotv:id/view_holder_categories_image_view_cover')[1]
        series.click()
        sleep(2)

	
	screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        swipe_start_x = width/2
        swipe_start_y = height*0.7
        swipe_end_x = width/2
        swipe_end_y = height*0.3
        self.driver.implicitly_wait(5)
        self.driver.swipe(swipe_start_x, swipe_start_y, swipe_end_x, swipe_end_y,1000)
        while True:
                try:
                        title_button = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_title_image_view_poster")
                        break
                except:
                        self.driver.swipe(swipe_start_x, swipe_start_y, swipe_end_x, swipe_end_y,1000)
                        continue
        
        actions = TouchAction(self.driver)
        actions.tap(title_button).perform()
	self.driver.implicitly_wait(50)
        title_name = self.driver.find_element_by_id("com.globo.globotv:id/activity_title_text_view_title")

	#title_encode = title_name.text.decode('iso-8859-1')
	#get_title_name = title_encode.encode('utf-8')
        get_title_name = title_name.text
	print get_title_name
	Details_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().text("Detalhes")')
	Details_tab.click()
        Spec_headline1 = self.driver.find_element_by_id('com.globo.globotv:id/fragment_title_details_text_view_specifications').text
#        Spec_genres1 = self.driver.find_element_by_id('com.globo.globotv:id/fragment_title_details_text_view_subset').text
        Spec_country1 = self.driver.find_element_by_id('com.globo.globotv:id/fragment_title_details_text_view_country').text 
	sleep(2)
	play_button = self.driver.find_element_by_id("com.globo.globotv:id/activity_title_button_one")
	play_button.click()
	self.status="Fail_video_Play"	
	video_start = int(round(time.time() * 1000))
	self.driver.implicitly_wait(1)
	t_end = time.time() +60
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
			video_end = int(round(time.time() * 1000))
			print "Not displayed"
			break
	self.initial_video_play = video_end- video_start	
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
                        	video_play = int(round(time.time() * 1000))
                        	print "Not displayed"
                        	break
		self.initial_video_play =  video_play -video_second
        except:
                pass
	
	print "Initial Video load time ", self.initial_video_play
	self.pass_count +=1
	d = {'globo_initial_play': self.initial_video_play}

        self.kpi_dic.update(d)
	#Watch the Video for 1 minute	
	self.videoplay_check(80)
	self.driver.implicitly_wait(50)
	
	navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Navigate up")')
	navigate_up.click()

	self.status ="Fail_get_progress"
	get_title_progress = self.driver.find_element_by_id("com.globo.globotv:id/activity_title_progress").text
	print get_title_progress

	sleep(2)
	navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Navigate up")')
        navigate_up.click()


	#closing and relaunching app
	self.driver.close_app()
        sleep(10)
        self.driver.launch_app()

	#App relaunched
	
	#Searching for the same title
	search_button = self.driver.find_element_by_id("com.globo.globotv:id/menu_bottom_navigation_view_item_search")
	search_button.click()

	search_bar = self.driver.find_element_by_id("com.globo.globotv:id/search_src_text")
	search_bar.click()
	search_bar.send_keys(get_title_name)
	self.driver.press_keycode(66)
        i=0
        while i<len(self.driver.find_elements_by_id("com.globo.globotv:id/view_holder_custom_view_rails_custom_view_title")):
                title_select = self.driver.find_elements_by_id("com.globo.globotv:id/view_holder_custom_view_rails_custom_view_title")[i]
                title_select.click()

                self.status="Fail_title_check"
                self.title_check =False
                search_title = self.driver.find_element_by_id("com.globo.globotv:id/activity_title_text_view_title")
                search_title_name = search_title.text
                print search_title_name
                Details_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().text("Detalhes")')
                Details_tab.click()
                Spec_headline2 = self.driver.find_element_by_id('com.globo.globotv:id/fragment_title_details_text_view_specifications').text
                #Spec_genres2 = self.driver.find_element_by_id('com.globo.globotv:id/fragment_title_details_text_view_subset').text
                Spec_country2 = self.driver.find_element_by_id('com.globo.globotv:id/fragment_title_details_text_view_country').text 
                
                if (search_title_name==get_title_name) and (Spec_headline1==Spec_headline2)  and (Spec_country1==Spec_country2) :
                        print "Title found"	
                        self.title_check = True
                        self.pass_count = self.pass_count+1
                        break
                else:
                        i+=1
                        navigate_up = self.driver.find_element_by_android_uiautomator('new UiSelector().descriptionContains("Navigate up")')
                        navigate_up.click()

	sleep(2)
	self.status="Fail_progress_check"
	self.progress_check = False
	search_title_progress = self.driver.find_element_by_id("com.globo.globotv:id/activity_title_progress")
	search_title_progress = search_title_progress.text
	print search_title_progress
	if search_title_progress ==get_title_progress:
		print "Progress time verified"
		self.progress_check = True
		self.pass_count = self.pass_count+1

	
	continue_button = self.driver.find_element_by_id("com.globo.globotv:id/activity_title_button_one")
	continue_button.click()		

	sub_start = int(round(time.time() * 1000))
	self.driver.implicitly_wait(1)
        t_end = time.time() +60
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
			sub_end = int(round(time.time() * 1000))
                        print "Not displayed"
                        break
	
	print " Video Resumed "	
	self.sub_video_play = sub_end - sub_start
        print "subsequent video load time ", self.sub_video_play
        self.pass_count +=1
	sleep(10)
	if self.progress_check ==False:
		self.status ="Fail_progress_check"
	elif self.title_check ==False:
		self.status="Fail_title_check"
	else:
		self.status = "Pass"



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)





