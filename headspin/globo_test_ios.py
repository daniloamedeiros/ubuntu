# -*- coding: utf-8 -*-

from sh import tail
import os
from time import sleep
import mysql.connector
import subprocess
import socket
import sh
import shlex
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
from alerts_globo import SendAlert
from log_adb_info import AdbDdata
from mysql_insert import MysqlDataInsert

class SimpleAndroidTests(unittest.TestCase):
    def setUp(self):
        self.udid = sys.argv[1]
        self.device_id = self.udid
        self.capture_cap = sys.argv[3]
        desired_caps = {}
        desired_caps['platformName'] = 'iOS'
        desired_caps['automationName'] = 'XCUITest'
        desired_caps['udid'] = self.device_id
        desired_caps['deviceName'] = self.device_id
        desired_caps['bundleId'] = "com.globo.hydra"
        desired_caps['newCommandTimeout'] = 600
        if self.capture_cap == "1":
            desired_caps['headspin:capture'] = True
        else:
            desired_caps['headspin:capture'] = False
        desired_caps['no-reset'] = True
        self.os = "iOS"
        self.status = "Fail_Launch"
        self.home_pg_load_time = 0
        self.app_launch_time = 0
        self.series_load_time = 0
        self.video_laod_time = 0
        self.buffer_in_video = False
        self.test_name = "Globo_Play_Video"
        self.session_id = None
        self.kpi_dic = {}
        self.pass_count = 0
        self.fail_count = 0
        self.alerts = SendAlert()
        # Start the log cature
        self.timestamp = str(int(round(time.time() * 1000)))
        self.path = os.getcwd() + "/logs/"+str(self.timestamp)
        print self.path
        os.mkdir(self.path)
        self.process = subprocess.Popen("exec "+"idevicesyslog -u " + self.device_id + " > " +
                                        self.path+"/" + str(self.timestamp)+'_'+self.device_id + ".log", shell=True)
        appium_input = sys.argv[2]
        if appium_input.isdigit():
            self.url = ('http://127.0.0.1:' + appium_input + '/wd/hub')
        else:
            self.url = appium_input
        print self.url

        self.driver = webdriver.Remote(self.url, desired_caps)
        self.start_app = int(round(time.time() * 1000))

    def tearDown(self):

        print "Pass count is %s" % self.pass_count
        if self.pass_count != 5:
            self.fail_count = 5 - self.pass_count
        else:
            self.fail_count = 0
        print "Fail count is %s " % self.fail_count
        if self.capture_cap == "1":
            self.session_id = self.driver.session_id
            print self.session_id
        else:
            self.session_id = None

        screenshot_name = str(self.timestamp)+"_"+self.device_id+".png"
        self.driver.save_screenshot(self.path+"/" + screenshot_name)

        if self.status != "Pass":
            print self.driver.page_source.encode('utf-8')
        screenshot_path = self.path+"/"+screenshot_name

        log_file_name = str(self.timestamp)+"_"+self.device_id+".log"
        log_path = self.path+"/" + log_file_name

        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(
            screenshot_path, 'grafana-images.headspin.io', 'globo/'+screenshot_name)
        s3.meta.client.upload_file(
            log_path, 'grafana-images.headspin.io', 'globo/'+log_file_name)
        print "Pushed to AWS"

        log_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+log_file_name
        png_url = "https://s3-us-west-2.amazonaws.com/grafana-images.headspin.io/globo/"+screenshot_name

        self.threshold = 5000
        if not all(i < self.threshold for i in list(self.kpi_dic.values())) or self.status != "Pass":
            slack_messge = []
            message_to_be_send = ""
            if not all(i < self.threshold for i in list(self.kpi_dic.values())):

                for key, value in self.kpi_dic.items():
                    if value > self.threshold:
                        slack_messge.append('{} : {}'.format(key, value))
                for text in slack_messge:
                    message_to_be_send = message_to_be_send+text+"\n"
                print message_to_be_send

            message_to_be_send = self.os+"\n"+self.udid+"\n"+message_to_be_send + \
                "\n" + "Device_log url:"+log_url+"\n"+"Device screenshot url:"+png_url

            # slack alert
            self.alerts.slack_alert(message_to_be_send)

            # Mail ALert
            self.alerts.email_alert(message_to_be_send)

       # Insert to app table
        insert = MysqlDataInsert()
        insert.globo_kpi_metrics(self.driver, self.app_launch_time, self.home_pg_load_time, self.series_load_time, self.video_laod_time,
                                 self.buffer_in_video, self.pass_count, self.fail_count, self.status, self.timestamp, self.session_id, self.test_name)

        print self.process.pid
        self.process.kill()

        # end the session
        self.driver.quit()

    def test_globo(self):
        # App Launch
        self.driver.implicitly_wait(50)

        # Check if the app lauunch is completed
        home_button = self.driver.find_element_by_name("Agora")

        launched_app = int(round(time.time() * 1000))

        # calcualting launch time
        self.app_launch_time = launched_app - self.start_app
        print ("App Launch Time is %s ms" % self.app_launch_time)
        d = {'globo_launch_time': self.app_launch_time}
        self.kpi_dic.update(d)

        self.pass_count = self.pass_count + 1

        sleep(5)

        # login
        self.status = "Fail_login"
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        tap_x = width*0.924
        tap_y = height*0.057

        # profile_button tap
        self.driver.tap([(tap_x, tap_y)])

        # logout

        try:
            self.driver.implicitly_wait(5)
            logout_button = self.driver.find_element_by_name("Sair")
            logout_button.click()
            confirm_button = self.driver.find_element_by_name("Sim")
            confirm_button.click()
            self.driver.find_element_by_class_name(
                "XCUIElementTypeNavigationBar")
            sleep(2)
            self.driver.tap([(tap_x, tap_y)])

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

        self.driver.tap([(close_x_tap, close_y_tap)])

        start_login = int(round(time.time() * 1000))
        home_button = self.driver.find_element_by_name("Agora")
        self.driver.find_element_by_class_name("XCUIElementTypeImage")
        end_login = int(round(time.time() * 1000))

        self.home_pg_load_time = end_login - start_login
        print("Home page loading time is %s ms" % self.home_pg_load_time)

        d = {'globo_post_login_home_load_time': self.home_pg_load_time}
        self.kpi_dic.update(d)

        self.pass_count = self.pass_count + 1

        sleep(2)

        # series view time

        categories_tab = self.driver.find_element_by_name("Categorias")
        categories_tab.click()
	sleep(3)
        series_tab = self.driver.find_element_by_name("Séries")
	try:
        	series_tab.click()
	except:
		location = series_tab.location
		size = series_tab.size
		self.x_tap = location['x']+int(size['width']/2)
	        self.y_tap= location['y']+int(size['height']/2)
	        self.driver.tap([(self.x_tap,self.y_tap)])

        sleep(5)

        first_poster_tab = self.driver.find_elements_by_class_name("XCUIElementTypeStaticText")[0]
        location = first_poster_tab.location
	size = first_poster_tab.size
	self.x_tap = location['x']+int(size['width']/2)
	self.y_tap= location['y']+int(size['height']/2)
        self.driver.tap([(self.x_tap,self.y_tap)])

        series_load_start = int(round(time.time() * 1000))
        self.driver.find_element_by_name("Episódios")
        series_load_end = int(round(time.time() * 1000))

        self.series_load_time = series_load_end - series_load_start
        d = {'globo_series_page_load_time': self.series_load_time}
        self.kpi_dic.update(d)
        print "Series load time", self.series_load_time
        self.pass_count = self.pass_count + 1

        sleep(2)

        # video playback
        self.status = "Fail_video_play"
        self.driver.implicitly_wait(10)
        try:
            continue_button = self.driver.find_element_by_name(
                "titleHighlightViewCellFirstButton")
        except:
            pass
        sleep(4)
        try:
            continue_button.click()
        except:
            con_x = width*0.296
            con_y = height*0.607
            self.driver.tap([(con_x, con_y)])
        video_start = int(round(time.time() * 1000))
        t_end_ad = time.time() + 60
        cmd = shlex.split("idevicesyslog -u  %s" % self.device_id)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for line in iter(process.stdout.readline, b''):
            if "FigStreamPlayer" in line:
                video_end = int(round(time.time() * 1000))
                print "VideoPlayed"
                break
            if time.time() > t_end_ad:
                break
        process.kill()
	
	self.video_laod_time = video_end - video_start

	self.driver.implicitly_wait(5)
        try:
                oops_button = self.driver.find_element_by_name("OK")
                oops_button.click()
                sleep(2)
                self.driver.tap([(con_x,con_y)])

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
		self.video_laod_time = video_play - video_second
        except:
                pass
        print "Video load time ", self.video_laod_time
        d = {'globo_video_load_time': self.video_laod_time}
        self.kpi_dic.update(d)

        self.pass_count = self.pass_count + 1
        self.buffer_in_video = False
        sleep(5)


        t_end = time.time() + 60
        self.driver.implicitly_wait(1)
        while time.time() < t_end:
            try:
                spinner = self.driver.find_element_by_name("spinner")
                self.buffer_in_video = True
                break
            except:
                pass

        if self.buffer_in_video:
            self.status = "Video_interrupted"
        else:
            self.status = "Pass"
            self.pass_count += 1


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
