#coding=utf-8
#encoding=utf-8
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


class Globo_1hour_video(unittest.TestCase):
    #check if the necessary folders are present, if not create
    def check_dir(self,dir_path):
        if not os.path.isdir(dir_path):
            print "Creating the log dir"
            os.mkdir(dir_path)
    def adb_dump_data(self, udid,reference, step, adb_dump_dir):
        #save the sys dump of the phone
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
        #Before test function
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
        desired_caps['newCommandTimeout'] =1200
        if self.capture_cap =="1":
            desired_caps['headspin:capture.video'] = True
        else:
            desired_caps['headspin:capture.video'] = False
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
        self.home_pg_load_time= 0
        self.cinema_load_time= 0
        self.video_load_time= 0
        self.alerts_during_video_play=False
        self.buffer_count = 0
        self.alert_count = 0
        self.test_name = "Globo_1hour_video"
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
        #After function
        self.adb_activities.after_test(self.udid, self.reference, self.driver, self.status)
        if self.capture_cap =="1":
            self.session_id = self.driver.session_id
            print self.session_id
        else:
            self.session_id = None
        #Insert to app table
        insert = MysqlDataInsert()
        insert.globo_1hour_video_metrics(self.driver, self.app_launch_time, self.home_pg_load_time, self.cinema_load_time, self.video_load_time, self.alerts_during_video_play,self.buffer_count,self.alert_count, self.pass_count,self.fail_count,self.status,self.reference,self.session_id,self.test_name)
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
        if not all( i< self.threshold for i in list(self.kpi_dic.values())) or self.status!= "Pass":
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
            #Mail Alert
            self.alerts.email_alert(message_to_be_send)
        self.driver.quit()
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
        sleep(5)
        #library tab view time
        self.status="Fail_login"
        user_icon = self.driver.find_element_by_id("com.globo.globotv:id/menu_profile_custom_view_profile")
        user_icon.click()
        sleep(5)
        #Log out
        try:
            self.driver.implicitly_wait(5)
            logout =  self.driver.find_element_by_android_uiautomator('new UiSelector().text("Sair")')	
            logout.click()
            sleep(2)
            #Confirm log out
            yes_btn = self.driver.find_element_by_id('android:id/button1')
            yes_btn.click()
            sleep(5)
            #Click on te account button
            self.driver.implicitly_wait(10)
            user_icon = self.driver.find_element_by_id("com.globo.globotv:id/menu_profile_custom_view_profile")
            user_icon.click()
            sleep(5)
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
        home_page = self.driver.find_element_by_id("com.globo.globotv:id/custom_view_premium_highlights_image_view_background")
        home_page_load_end = int(round(time.time() * 1000))
        self.home_pg_load_time = home_page_load_end- home_page_load_start
        d = {'globo_post_login_home_load_time': self.home_pg_load_time}
        self.kpi_dic.update(d)
        self.pass_count +=1
        print "Home page loading time ", self.home_pg_load_time
        sleep(5)
        self.driver.implicitly_wait(60)
        categories_tab = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Categorias")')
        categories_tab.click()
        sleep(5)
        cinema = self.driver.find_elements_by_id('com.globo.globotv:id/view_holder_categories_image_view_cover')[2]
        cinema.click()
        sleep(5)
        first_poster = self.driver.find_elements_by_id('com.globo.globotv:id/custom_view_title_image_view_poster')[0]
        first_poster.click()
        cinema_load_start= int(round(time.time() * 1000))
        title = self.driver.find_element_by_id('com.globo.globotv:id/activity_title_text_view_title')
        cinema_load_end = int(round(time.time() * 1000))
        self.cinema_load_time = cinema_load_end- cinema_load_start
        self.pass_count +=1
        d = {'globo_cinema_page_load_time': self.cinema_load_time}
        self.kpi_dic.update(d)
        print "Cinema load time",self.cinema_load_time
        self.status= "Fail_video_play_start"
        continue_btn = self.driver.find_element_by_id('com.globo.globotv:id/activity_title_button_one')
        continue_btn.click()
        video_start = int(round(time.time() * 1000))
        self.driver.implicitly_wait(1)
        try:
            self.driver.find_element_by_id("android:id/button1").click()
            sleep(2)
            play_button = self.driver.find_element_by_id("com.globo.globotv:id/activity_title_button_one")
            play_button.click()
            video_second = int(round(time.time() * 1000))
            self.driver.implicitly_wait(1)
            t_end = time.time()+10
            while time.time() < t_end:
                try:
                    spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
                    print "Spinner!!"
                except:
                    video_play = int(round(time.time() * 1000))
                    print "Not displayed"
                    break
            self.video_load_time = video_play - video_second
        except:
            t_end = time.time() + 10
            while time.time() < t_end:
                try:
                    spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
                    print "Spinner!!"
                except:
                    video_end = int(round(time.time() * 1000))
                    print "Not displayed"
                    break
            self.video_load_time = video_end- video_start
        self.driver.implicitly_wait(5)
        
        print ("Video load time ",self.video_load_time)
        self.pass_count +=1
        d = {'globo_video_load_time': self.video_load_time}
        self.kpi_dic.update(d)
        buffer_flag=False
        sleep(5)
        t_end= time.time()+3600
        while time.time() < t_end:
            self.driver.implicitly_wait(1)
            try:
                spinner = self.driver.find_element_by_id('com.globo.globotv:id/progress_bar')
                if buffer_flag==False:
                    buffer_flag=True
                    self.buffer_count+=1
            except:
                buffer_flag=False
                pass
            self.driver.implicitly_wait(0.5)
            try:
                flag=0
                try:
                    alert = self.driver.find_element_by_android_uiautomator('new UiSelector().textContains("OK")')
                    flag=1
                except:
                    pass
                if flag==0:
                    try:
                        alert = self.driver.find_element_by_android_uiautomator('new UiSelector().textContains("Ok")')
                        flag=2
                    except expression as identifier:
                        pass
                if flag==0:
                    try:
                        alert = self.driver.find_element_by_android_uiautomator('new UiSelector().textContains("ATUALIZAR")')
                        flag=3
                    except:
                        pass
                alert.click()
                self.alerts_during_video_play = True
                self.alert_count+=1
                try:
                    self.driver.find_element_by_id("android:id/button1").click()
                except:
                    pass
                try:
                    continue_btn = self.driver.find_element_by_id('com.globo.globotv:id/activity_title_button_one')
                    continue_btn.click()
                    sleep(3)
                except:
                    pass
            except:
                pass
        if self.alerts_during_video_play:
            self.status= "Fail_video_interrupted_by_alerts"
        else:
            self.status = "Pass"
            self.pass_count +=1

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Globo_1hour_video)
    unittest.TextTestRunner(verbosity=2).run(suite)
