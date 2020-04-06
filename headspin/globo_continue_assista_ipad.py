# coding=utf-8
# encoding=utf-8

from time import sleep
import os
import mysql.connector
import socket
import shlex
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
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from appium.webdriver.common.touch_action import TouchAction
from appium import webdriver
sys.path.append('../setup/py_modules')
import boto3
from mysql_insert import MysqlDataInsert
from log_adb_info import AdbDdata
from alerts_globo import SendAlert

class Globo_Continue_Assista_iOS(unittest.TestCase):
    # check if the necessary folders are present, if not create
    def check_dir(self, dir_path):
        while True:
            try:
                os.mkdir(dir_path)
            except:
                break

    def adb_dump_data(self, udid, reference, step, adb_dump_dir):
        # save the sys dump of the phone
        self.adb_activities.get_dumpsys(udid, reference, step, adb_dump_dir)
        # Get the cpu info
        cpu_usage = self.adb_activities.get_cpuinfo(udid)
        # Get mem info
        mem_usage = self.adb_activities.get_mem_info(udid, self.package)
        # Device temp
        temperature = self.adb_activities.get_device_temp(udid)
        print step, cpu_usage, mem_usage, temperature
        return [step, cpu_usage, mem_usage, temperature]

    def setUp(self):
        self.reference = str(int(time.time() * 1000))
        self.package = "com.globo.hydra"
        # device id as 1st argument
        self.device_id = sys.argv[1]
        self.os = "iOS"

        self.adb_activities = AdbDdata()
        self.alerts = SendAlert()
        self.array_of_data_list = []
        # Before test function
        # self.adb_activities.before_test(self.device_id)
        self.capture_cap = sys.argv[3]
        # desired caps for the app
        desired_caps = {}
        desired_caps['platformName'] = self.os
        desired_caps['automationName'] = 'XCUITest'
        desired_caps['udid'] = self.device_id
        desired_caps['deviceName'] = self.device_id
        desired_caps['bundleId'] = self.package
        desired_caps['newCommandTimeout'] = 600
        desired_caps['no-reset'] = True

        if self.capture_cap == "1":
            desired_caps['headspin:capture'] = True
        else:
            desired_caps['headspin:capture'] = False
        self.status = "Fail_Launch"
        self.path = os.getcwd() + "/logs/"+str(self.reference)
        print self.path
        self.check_dir(self.path)
        self.process = subprocess.Popen("exec "+"idevicesyslog -u " + self.device_id + " > " +
                                        self.path+"/" + str(self.reference)+'_'+self.device_id + ".log", shell=True)
        appium_input = sys.argv[2]
        if appium_input.isdigit():
            self.url = ('http://127.0.0.1:' + appium_input + '/wd/hub')
        else:
            self.url = appium_input

        # launching app
        self.driver = webdriver.Remote(self.url, desired_caps)
        self.start_app = int(round(time.time() * 1000))

        # initialising variables
        self.status = "Fail_launch"
        self.app_launch_time = 0

        self.status_dic = {}
        self.kpi_dic = {}

        self.app_launch_time = 0
        self.home_pg_load_time = 0
        self.initial_video_play = 0
        self.sub_video_play = 0
        self.title_check = False
        self.progress_check = False
        self.test_name = "Continue_Assistindo"
        self.kpi_count = 6
        self.pass_count = 0
        self.fail_count = 0

    def tearDown(self):
        # incrementing kpi count
        print "Pass count is %s" % self.pass_count
        if self.pass_count != self.kpi_count:
            self.fail_count = self.kpi_count - self.pass_count
        else:
            self.fail_count = 0
        print "Fail count is %s " % self.fail_count

        if self.capture_cap == "1":
            self.session_id = self.driver.session_id
            print self.session_id
        else:
            self.session_id = None
        # Insert to app table
        insert = MysqlDataInsert()
        insert.globo_continuar_metrics(self.driver, self.app_launch_time, self.home_pg_load_time, self.initial_video_play, self.title_check,
                                       self.progress_check, self.sub_video_play, self.pass_count, self.fail_count, self.status, self.reference, self.session_id, self.test_name)

        screenshot_name = str(self.reference)+"_"+self.device_id+".png"
        self.driver.save_screenshot(self.path+"/" + screenshot_name)

        screenshot_path = self.path+"/"+screenshot_name

        log_file_name = str(self.reference)+"_"+self.device_id+".log"
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
            message_to_be_send = self.os+"\n"+self.device_id+"\n"+message_to_be_send + \
                "\n" + "Device_log url:"+log_url+"\n"+"Device screenshot url:"+png_url
            # slack alert
            self.alerts.slack_alert(message_to_be_send)
            # Mail ALert
            self.alerts.email_alert(message_to_be_send)
        self.driver.quit()

    def videoplay_check(self, sec):
        self.driver.implicitly_wait(5)
        t_end = time.time() + sec
        while time.time() < t_end:
            try:
                self.driver.find_element_by_accessibility_id(
                    'Container').click()
                player_control = self.driver.find_element_by_accessibility_id(
                    "PlayPauseButton")
                sleep(5)
            except:
                try:
                    spinner = self.driver.find_element_by_accessibility_id('Conexão da rede em andamento')
                except:
                    continue
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
            if time.time() > t_end:
                break
        process.kill()

    def test_login(self):
        # App Launch
        self.driver.implicitly_wait(50)
        # Check if the app lauunch is completed
        home_button = self.driver.find_element_by_name("Agora")
        launched_app = int(round(time.time() * 1000))
        # calculating launch time
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
        tap_x = width*0.956
        tap_y = height*0.042
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
        except:
            pass
        self.driver.implicitly_wait(30)
        sleep(3)
        # tap on profile button
        self.driver.tap([(tap_x, tap_y)])
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
        close_x_tap = width*0.813
        close_y_tap = height*0.220
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

        # Starting Continue_Assista
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
            self.y_tap = location['y']+int(size['height']/2)
            self.driver.tap([(self.x_tap, self.y_tap)])
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        swipe_start_x = width/2
        swipe_start_y = height*0.7
        swipe_end_x = width/2
        swipe_end_y = height*0.3
        self.driver.implicitly_wait(5)
        #self.driver.swipe(swipe_start_x, swipe_start_y, swipe_end_x, swipe_end_y,1000)
        while True:
            try:
                title_button = self.driver.find_elements_by_class_name("XCUIElementTypeCell")[
                    0].find_elements_by_class_name("XCUIElementTypeStaticText")[0]
                break
            except:
                self.driver.swipe(swipe_start_x, swipe_start_y,
                                  swipe_end_x, swipe_end_y, 1000)
                continue
        self.driver.implicitly_wait(10)
        title_button.click()
        try:
            title_name = self.driver.find_element_by_accessibility_id("titleHighlightViewCellTitleName")
        except:
            location = title_button.location
            size = series_tab.size
            self.x_tap = location['x']+int(size['width']/2)
            self.y_tap = location['y']+int(size['height']/2)
            self.driver.tap([(self.x_tap, self.y_tap)],1000)
            sleep(3)
            title_name = self.driver.find_element_by_accessibility_id("titleHighlightViewCellTitleName")
        get_title_name = title_name.text.encode('utf-8')
        print get_title_name
        sleep(3)
        Details_tab = self.driver.find_element_by_accessibility_id(
            "tabViewCell1")
        if (Details_tab.text != "Detalhes"):
            Details_tab = self.driver.find_element_by_accessibility_id(
                "tabViewCell2")
        try:
            Details_tab.click()
        except:
            location = Details_tab.location
            size = Details_tab.size
            self.x_tap = location['x']+int(size['width']/2)
            self.y_tap = location['y']+int(size['height']/2)
            self.driver.tap([(self.x_tap, self.y_tap)])

        spec1 = self.driver.find_elements_by_class_name("XCUIElementTypeCell")[
            1].find_elements_by_class_name("XCUIElementTypeStaticText")[3].text

        sleep(2)
        play_button = self.driver.find_element_by_accessibility_id(
            "titleHighlightViewCellFirstButton")
        play_button.click()
        self.status = "Fail_video_Play"
        video_start = int(round(time.time() * 1000))

        t_end_ad = time.time() + 60
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
        self.initial_video_play = video_end - video_start

        self.driver.implicitly_wait(5)
        try:
            oops_button = self.driver.find_element_by_name("OK")
            oops_button.click()
            sleep(2)
            return
        except:
            pass
        print "Initial Video load time ", self.initial_video_play

        self.pass_count += 1
        d = {'globo_initial_play': self.initial_video_play}
        self.kpi_dic.update(d)

        # Watch the Video for 1 minute
        self.videoplay_check(80)
        self.driver.implicitly_wait(50)
        navigate_up = self.driver.find_element_by_accessibility_id("Voltar")
        navigate_up.click()
        self.status = "Fail_get_progress"
        sleep(5)
        get_title_progress = self.driver.find_element_by_name("Progresso").text
        print get_title_progress
        sleep(2)
#        navigate_up = self.driver.find_element_by_accessibility_id("Voltar")
#        navigate_up.click()
        sleep(5)
        # closing and relaunching app
        self.driver.close_app()
        sleep(10)
        self.driver.launch_app()

        # App relaunched
        home_tab = self.driver.find_element_by_name("Início")
        # Searching for the same title
        search_button = self.driver.find_element_by_name("Busca")
        search_button.click()

        search_bar = self.driver.find_element_by_accessibility_id(
            "O que você quer assistir?")
        search_bar.click()
        search_bar.send_keys(get_title_name.decode('utf-8'))
        # self.driver.press_keycode(66)
        self.driver.implicitly_wait(3)
        i = 0
        while i < len(self.driver.find_element_by_name("searchViewCollectionView").find_element_by_name("titleCollectionViewCollectionView").find_elements_by_class_name("XCUIElementTypeCell")):
            title_select = self.driver.find_element_by_name("searchViewCollectionView").find_element_by_name(
                "titleCollectionViewCollectionView").find_elements_by_class_name("XCUIElementTypeCell")[i]
            title_select.click()
            self.status = "Fail_title_check"
            self.title_check = False
            try:
                search_title = self.driver.find_element_by_accessibility_id(
                    "titleHighlightViewCellTitleName")
            except:
                navigate_up = self.driver.find_element_by_accessibility_id(
                    "Voltar")
                navigate_up.click()
                continue
            search_title_name = search_title.text.encode('utf-8')
            print search_title_name
            sleep(3)
            Details_tab = self.driver.find_element_by_accessibility_id(
                "tabViewCell1")
            if (Details_tab.text != "Detalhes"):
                Details_tab = self.driver.find_element_by_accessibility_id(
                    "tabViewCell2")
            try:
                Details_tab.click()
            except:
                location = Details_tab.location
                size = Details_tab.size
                self.x_tap = location['x']+int(size['width']/2)
                self.y_tap = location['y']+int(size['height']/2)
                self.driver.tap([(self.x_tap, self.y_tap)])
            spec2 = self.driver.find_elements_by_class_name("XCUIElementTypeCell")[
                1].find_elements_by_class_name("XCUIElementTypeStaticText")[3].text
            if (search_title_name == get_title_name) and (spec1 == spec2):
                print "Title found"
                self.title_check = True
                self.pass_count = self.pass_count+1
                break
            else:
                i += 1
                navigate_up = self.driver.find_element_by_accessibility_id(
                    "Voltar")
                navigate_up.click()
                sleep(20)
        sleep(2)
        self.status = "Fail_progress_check"
        self.progress_check = False
        search_title_progress = self.driver.find_element_by_name(
            "Progresso").text
        print search_title_progress
        if search_title_progress == get_title_progress:
            print "Progress time verified"
            self.progress_check = True
            self.pass_count = self.pass_count+1

        continue_button = self.driver.find_element_by_accessibility_id(
            "titleHighlightViewCellFirstButton")
        continue_button.click()

        video_start = int(round(time.time() * 1000))
        t_end_ad = time.time() + 60
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
        self.sub_video_play = video_end - video_start
        print "subsequent video load time ", self.sub_video_play
        self.pass_count += 1
        sleep(10)
        if self.progress_check == False:
            self.status = "Fail_progress_check"
        elif self.title_check == False:
            self.status = "Fail_title_check"
        else:
            self.status = "Pass"


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Globo_Continue_Assista_iOS)
    unittest.TextTestRunner(verbosity=2).run(suite)
