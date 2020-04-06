from time import sleep
from behave import then, when
from selenium.common.exceptions import NoSuchElementException

from pages.homePage import Locator


@when('clico no menu download')
def step_impl(context):
    loc = Locator(context)
    loc.click_menu_download()


@when('verifico que todos os downloads foram apagados')
def step_impl(context):
    loc = Locator(context)
    while True:
        try:
            loc.assert_lista_download_vazio()
            break
        except NoSuchElementException:

            loc.click_selecionar_itens_downlaod()
            loc.click_primeiro_item_lista_download()
            loc.click_apagar_download()



@when('realizo o download')
def step_impl(context):
    loc = Locator(context)
    loc.click_menu_categorias()
    loc.click_categoria_novela()
    loc.click_primeiro_item_categoria_novela()
    loc.click_icone_download_lista_capitulo()
    sleep(10)
    loc.click_navegar_voltar()
    loc.click_menu_download()
    loc.click_primeiro_item_lista_download()


@then('verifico se o donwload foi realizado com sucesso')
def step_impl(context):
    loc = Locator(context)
    while True:
        try:

            loc.assert_download_concluido()
            print(">>>>>>>>>>>>> Download realizado com sucesso!!!!")
            break

        except NoSuchElementException:
            print("\n> Download em andamento ...")

