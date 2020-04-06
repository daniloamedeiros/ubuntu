from behave import *
from selenium.common.exceptions import NoSuchElementException
# import pdb

def skip_splash(context):
    context.driver.implicitly_wait(10)
    # click em avançar splash
    btn_splash = context.driver.find_elements_by_class_name(
        "android.widget.ImageView")
    for x in range(0, 2):
        btn_splash[8].click()

    modal_access_device = context.driver.find_element_by_id(
        "com.android.packageinstaller:id/permission_allow_button")
    if modal_access_device.is_displayed():
        modal_access_device.click()
    else:
        pass
    # botão já possuo login
    btn_login_spalsh = context.driver.find_element_by_id(
        "com.globo.globotv:id/fragment_tutorial_step_three_button_already_have_login")
    btn_login_spalsh.click()

@given('that the app was launched')
def app_launched(context):
    context.driver.implicitly_wait(10)
    user_icon = context.driver.find_element_by_id("com.globo.globotv:id/custom_view_profile_image_view_picture")
    user_icon.click()
    context.driver.implicitly_wait(2)
    try:
        context.driver.find_element_by_android_uiautomator('new UiSelector().text("Seja assinante")')
        context.driver.back()
    except NoSuchElementException:
        btn_sair = context.driver.find_element_by_android_uiautomator('new UiSelector().text("Sair")')
        btn_sair.click()
        context.driver.implicitly_wait(1)
        btn_logout = context.driver.find_element_by_id('android:id/button1')
        btn_logout.click()

@when('the login screen loads')
def load_globoid_screen(context):
    # click icone menu
    user_icon = context.driver.find_element_by_id(
        "com.globo.globotv:id/custom_view_profile_image_view_picture")
    user_icon.click()
    context.driver.implicitly_wait(2)
    # click no ENTRAR
    entrar = context.driver.find_element_by_id(
        'com.globo.globotv:id/activity_profile_text_view_get_int')
    entrar.click()
    # tempo de carregamento GloboID
    context.driver.implicitly_wait(10)

@when('I log in application')
def input_log_in_globoID(context):
    context.driver.implicitly_wait(5)
    # login no GloboID
    email = context.driver.find_element_by_class_name(
        'android.widget.EditText')
    email.set_text('globoplay.test2@gmail.com')

    # password
    context.driver.implicitly_wait(3)
    password = context.driver.find_elements_by_class_name(
        'android.widget.EditText')[1]
    password.set_text('gplay2019')

    # botao globoid
    context.driver.implicitly_wait(3)
    context.driver.find_element_by_xpath('//*[@text="ENTRAR"]').click()

    # verifica o carregamento da tela do perfil logado
    try:
        context.driver.implicitly_wait(3)
        context.driver.find_element_by_android_uiautomator('new UiSelector().text("ASSINANTE")')
    except NoSuchElementException:
        raise Exception("Ocorreu um erro ao efetuar o login")

@Then('I click exit and confirm exit')
def exit_app(context):

    # clicar em sair e confirmar saida
    btn_sair = context.driver.find_element_by_android_uiautomator(
        'new UiSelector().text("Sair")')
    btn_sair.click()
    context.driver.implicitly_wait(1)
    btn_logout = context.driver.find_element_by_id('android:id/button2')
    btn_logout.click()