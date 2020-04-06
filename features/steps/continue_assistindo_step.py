import logging
from time import sleep
from behave import given, when, then
from selenium.common.exceptions import NoSuchElementException
from pages.homePage import Locator


@given('that I am logged into the app')
def step_impl(context):
    pass


@when('I scroll down')
def step_impl(context):
    sleep(10)
    loc = Locator(context)
    loc.pesquisar_trilho_continue_assistindo_home()


@then('I see the trail of continue watching')
def step_impl(context):
    pass


# ------------------------------------ Scenario 2 ----------------------------------------

@when('I click on categories')
def step_impl(context):
    loc = Locator(context)
    loc.click_menu_categorias()

@when('I click on the cinema category')
def step_impl(context):
    loc = Locator(context)
    loc.click_categoria_cinema()

@when('click on the first title')
def step_impl(context):
    loc = Locator(context)
    loc.click_primeiro_item_categoria_cinema()

@when('check the video running time and click watch')
def step_impl(context):
    loc = Locator(context)
    if loc.assert_botao_assistir_ou_continuar == 'Assista':
        loc.click_botao_assistir_ou_continuar()

    else:

        context.temp_inicio_video = float(loc.assert_tempo_video())
        print(">>>>>>>>>>>Tempo de inicio do vídeo>>>>>>>>>>>>>",context.temp_inicio_video)
        loc.click_botao_assistir_ou_continuar()

@when('I wait two minutes of playing the video')
def step_impl(context):
    sleep(120)

@then('I validate that the progression of the film has changed in relation to the start time')
def step_impl(context):
    loc = Locator(context)
    loc.click_menu_categorias()
    loc.click_categoria_cinema()
    loc.click_primeiro_item_categoria_cinema()
    temp_final_video = float(loc.assert_tempo_video())
    inicio_video = context.temp_inicio_video
    print('Tempo inicial >>>>>>',inicio_video)
    print('Tempo final >>>>>>', temp_final_video)

    if temp_final_video > inicio_video:
        print("Continue assistindo funcionou")
    else:
        raise Exception("\nContinue assistindo NÃO está funcionando corretamente")


    #-------------------------- Scenario 3 -----------------------------

@when('I click on the series category')
def step_impl(context):
    loc = Locator(context)
    loc.click_categoria_serie()

@then('I validate that the series progression has changed in relation to the start time')
def step_impl(context):
    loc = Locator(context)
    loc.click_menu_categorias()
    loc.click_categoria_serie()
    loc.click_primeiro_item_categoria_cinema()
    temp_final_video = float(loc.assert_tempo_video())
    inicio_video = context.temp_inicio_video
    print('Tempo inicial >>>>>>',inicio_video)
    print('Tempo final >>>>>>', temp_final_video)

    if temp_final_video > inicio_video:
        print("Continue assistindo funcionou")
    else:
        raise Exception("\nContinue assistindo NÃO está funcionando corretamente")


    #---------------------------------Scenario 4 -------------------------------------

@when(u'I check the video running time and click on watch the first episode')
def step_impl(context):
    loc = Locator(context)
    if loc.assert_botao_assistir_ou_continuar == 'Assista':
        context.driver.swipe(525, 1200, 525, 600)
        loc.click_primeiro_episodio_serie()

    else:

        context.temp_inicio_video = float(loc.assert_tempo_video())
        print(">>>>>>>>>>>Tempo de inicio do vídeo>>>>>>>>>>>>>", context.temp_inicio_video)
        context.driver.swipe(525, 1200, 525, 600)
        loc.click_primeiro_episodio_serie()


