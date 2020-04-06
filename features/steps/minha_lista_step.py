from time import sleep
from behave import given, when, then
from selenium.common.exceptions import NoSuchElementException
from pages.homePage import Locator



@given(u'I am logged in to the application')
def step_impl(context):
    pass


@when(u'I\'m on my list')
def step_impl(context):
    loc = Locator(context)
    loc.click_menu_perfil()
    loc.click_minha_lista()


@when(u'clean all content')
def step_impl(context):
    loc = Locator(context)
    while True:
        try:
            loc.click_minha_lista()
            loc.assert_minha_lista_vazia()

            break
        except NoSuchElementException:
            loc.click_primeiro_item_minha_lista()
            loc.click_adicionar_remover_item_minha_lista()
            sleep(10)
            loc.click_menu_inicio()
            loc.click_menu_perfil()
            loc.click_minha_lista()

@when(u'I click on add content to my list')
def step_impl(context):
    loc = Locator(context)
    context.driver.back()
    context.driver.back()
    loc.click_menu_categorias()
    loc.click_categoria_novela()
    loc.click_primeiro_item_categoria_novela()
    loc.click_adicionar_remover_item_minha_lista()
    sleep(5)

@when(u'I verify that the content has been added')
def step_impl(context):
    loc = Locator(context)
    loc.click_menu_inicio()
    loc.click_menu_perfil()
    loc.click_minha_lista()
    sleep(5)
    loc.click_primeiro_item_minha_lista()
    sleep(5)


@when(u'close and reopen the app')
def step_impl(context):
    context.driver.close_app()
    sleep(5)
    context.driver.launch_app()

@when(u'I click on my list')
def step_impl(context):
    sleep(5)
    loc = Locator(context)
    loc.click_menu_perfil()
    loc.click_minha_lista()


@then(u'I verify that the content has been added')
def step_impl(context):
    loc = Locator(context)
    loc.click_primeiro_item_minha_lista()
    loc.assert_item_adicionado_minha_lista()

@then('I check the track on my list')
def step_impl(context):
    context.driver.back()
    loc = Locator(context)
    previous_title = None
    repeat_count = 0
    while True:
        try:
            loc.trilho_minha_lista()
            print(loc.trilho_minha_lista())
            break
        except NoSuchElementException:
            loc.swipe_up()
            loc.exibe_nome_do_trilho()
            print(">>>>>>>>>> ", loc.exibe_nome_do_trilho())
            if loc.exibe_nome_do_trilho() == previous_title:
                repeat_count += 1
            if repeat_count == 3:
                raise Exception("Trilho do Continue assistindo não disponivel")
            previous_title = loc.exibe_nome_do_trilho()