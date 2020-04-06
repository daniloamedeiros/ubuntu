from time import sleep
from appium import webdriver
import requests
import json
import datetime
import mysql.connector


def post_to_kibana(url, data):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r)


def before_all(context):
    context.device = context.config.userdata['device']
    context.url = context.config.userdata['url']
    # context.test_id = datetime.datetime.now().strftime('%d%m%Y%H%M%S%f')


def before_step(context, step):
    sleep(2)


def before_feature(context, feature):
    context.test_id = datetime.datetime.now().strftime('%d%m%Y%H%M%S%f')
    context.nomefeature = feature.name
    context.horafeature = datetime.datetime.now().strftime('%d/%m/%Y_%H:%M:%S')
    context.nomefeature = feature.name


def before_scenario(context, scenario):
    udid = context.device
    url = context.url

    context.nomescenario = scenario.name
    context.scenariotags = scenario.tags

    desired_caps = {}
    desired_caps['platformName'] = "Android"
    desired_caps['udid'] = udid
    desired_caps['deviceName'] = udid
    desired_caps['appPackage'] = "com.globo.globotv"
    desired_caps['appActivity'] = "com.globo.globotv.splash.SplashActivity"
    desired_caps['noReset'] = True
    desired_caps['automationName'] = "uiautomator2"
    desired_caps['newCommandTimeout'] = 900
    desired_caps['no-reset'] = True
    driver = webdriver.Remote(url, desired_caps)
    context.driver = driver
    return context.driver


def after_step(context, step, feature=None):
    if step.status.value == 2:
        Step_status = "passed"
    else:
        Step_status = "failed"

    # relatorio_step = {
    #     "test_id": context.test_id,
    #     "type": "step",
    #     "feature": context.feature.name,
    #     "scenario": context.nomescenario,
    #     "step": step.name,
    #     "status": Step_status,
    #     "tags_feature": context.feature.tags,
    #     "tags_scenarios": context.scenario.tags,
    #     "datetime": context.horafeature,
    #     "platforma": "Android",
    #     "device": context.device,
    #     "origin": "Tsuru"
    # }
    # print(">>>>>>>>>>")
    # pprint(relatorio_step)

    # post_to_kibana(url = "http://tcp.logstash.video.globoi.com:80", data = relatorio_step)
    test_id = context.test_id
    tipo  = "step"
    feature  = context.feature.name
    scenario  = context.nomescenario
    step  = step.name
    _status  = Step_status
    tags_feature  = str(context.feature.tags[0])
    tags_scenarios  = str(context.scenario.tags[0])
    _datetime  = context.horafeature
    platforma  = "Android"
    device  = context.device
    origin  = "local"


    db_connection = mysql.connector.connect(host="gplay.cnn3lwvpaphc.sa-east-1.rds.amazonaws.com", user="admin", passwd="Aa123123", database="gplay")
    cursor = db_connection.cursor()
    sql = "INSERT INTO relatorio (test_id, tipo, feature, scenario, step, _status, tags_feature, tags_scenarios,_datetime, platforma, device, origin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (test_id, tipo, feature, scenario, step, _status, tags_feature, tags_scenarios,_datetime, platforma, device, origin)
    cursor.execute(sql, values)
    current_date = datetime.date.today()
    formatted_date = current_date.strftime('%d/%m/%Y')

    print(formatted_date)
    print("\n")
    print(cursor.rowcount, "record inserted.")
    print("\n")

    sql = ("SELECT test_id, tipo origin,feature FROM relatorio")
    cursor.execute(sql)

    for (test_id, tipo,feature) in cursor:
        print(test_id, tipo,feature)
    print("\n")


    cursor.close()
    db_connection.commit()
    db_connection.close()

def after_scenario(context, scenario):
    context.scenariostatus = scenario.status

    # if scenario.status.value == 2:
    #     scenario_status = "passed"
    # else:
    #     scenario_status = "failed"

    # relatorio_scenario = {
    #     "client": "tsuru-robo-tester-globoplay",
    #     "owner": "qualidade-performance",
    #     "test_id": context.test_id,
    #     "type": "scenario",
    #     "feature": context.feature.name,
    #     "scenario": scenario.name,
    #     "status": scenario_status,
    #     "datetime": context.horafeature,
    #     "platforma": "Android",
    #     "device": context.device,
    #     "origin": "Tsuru"
    # }
    #
    # print(">>>>>>>>>>")
    # pprint(relatorio_scenario)
    # post_to_kibana(url="http://tcp.logstash.video.globoi.com:80", data=relatorio_scenario)

    context.driver.quit()


def after_feature(context, feature):
    pass
    # if feature.status.value == 2:
    #     feature_status = "passed"
    # else:
    #     feature_status = "failed"

    # relatorio_feature = {
    #     "client": "tsuru-robo-tester-globoplay",
    #     "owner": "qualidade-performance",
    #     "test_id": context.test_id,
    #     "type": "Feature",
    #     "feature": context.feature.name,
    #     "status": feature_status,
    #     "datetime": context.horafeature,
    #     "platforma": "Android",
    #     "device": context.device,
    #     "origin": "Tsuru"
    # }
    # print(">>>>>>>>>>")
    # pprint(relatorio_feature)
    # post_to_kibana(url = "http://tcp.logstash.video.globoi.com:80", data = relatorio_feature)