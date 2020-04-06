import self
from pages.homePage import Locator as locator
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver


class Implement(WebDriver):

    def __init__(self, context):
        self.driver = context.driver
        self.context = context



    def login(driver):
        driver.implicitly_wait(10)
        user_icon = driver.find_element_by_id("com.globo.globotv:id/menu_profile_custom_view_profile")
        user_icon.click()
        try:
            driver.implicitly_wait(10)
            entrar = driver.find_element_by_id('com.globo.globotv:id/activity_profile_text_view_get_int')
            entrar.click()
            driver.implicitly_wait(60)

            # login no GloboID
            email = driver.find_element_by_class_name('android.widget.EditText')
            email.set_value('laurent_headspin')
            driver.implicitly_wait(1)
            # password
            password = driver.find_elements_by_class_name('android.widget.EditText')[1]
            password.set_value('Globo@321')
            driver.implicitly_wait(1)
            # #botao globoid
            buttons = driver.find_elements_by_class_name("android.widget.Button")
            for button in buttons:
                entrar = button.text
                if entrar == "ENTRAR":
                    button.click()
                    driver.implicitly_wait(50)
                    btn_voltar_home = driver.find_element_by_class_name("android.widget.ImageButton")
                    btn_voltar_home.click()
                    break

            # logout = driver.find_element_by_android_uiautomator('new UiSelector().text("Sair")')
            # logout.click()
            # btn = driver.find_element_by_id('android:id/button1')
            # btn.click()


        except NoSuchElementException:
            pass

            # import pdb; pdb.set_trace()


    def logout(driver):
        driver.implicitly_wait(10)

        user_icon = driver.find_element_by_id("com.globo.globotv:id/menu_profile_custom_view_profile")
        user_icon.click()
        try:
            logout = driver.find_element_by_android_uiautomator('new UiSelector().text("Sair")')
            logout.click()
            btn = driver.find_element_by_id('android:id/button1')
            btn.click()
        except NoSuchElementException:
            pass

        btn_back = driver.find_element_by_class_name('android.widget.ImageButton')
        btn_back.click()

    def swipe_up(driver):
        screen = self.driver.get_window_size()
        w = screen['width']
        h = screen['height']
        move_x = w / 2
        move_y = h * 0.7
        move_end_x = w / 2
        move_end_y = h * 0.3
        driver.swipe(move_x, move_y, move_end_x, move_end_y)


        def pesquisar_trilho(self):

            self.driver.implicitly_wait(10)
            previous_title = None
            repeat_count = 0
            while True:
                try:
                    locator.assistir_titulo()
                    locator.poster()

                    break
                except NoSuchElementException:
                    self.swipe_up(self.driver)
                    item = self.driver.find_element_by_android_uiautomator("com.globo.globotv:id/custom_view_rails_thumb_horizontal_text_view_title")
                    print(">>>>>>>>>> ", item.text)
                    if item.text == previous_title:
                        repeat_count += 1

                    if repeat_count == 3:
                        raise Exception("Trilho do Continue assistindo não disponivel")
                    previous_title = item.text

