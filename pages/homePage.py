import logging
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class Locator():


    def __init__(self, context):
        self.driver = context.driver
        self.context = context

        self.MENU_CATEGORIA =                     (By.ID, "com.globo.globotv:id/menu_bottom_navigation_view_item_categories")
        self.watching_title =                     (By.ID, 'new UiSelector().textContains("Continue assistindo")')
        self.POSTER =                             (By.ID, "com.globo.globotv:id/custom_view_continue_watching_image_view_poster")
        self.MENU_PERFIL =                        (By.ID, "com.globo.globotv:id/custom_view_profile_image_view_picture")
        self.MINHA_LISTA =                        (By.ID, 'new UiSelector().textContains("Minha lista")')
        self.ASSERT_MINHA_LISTA_VAZIA =           (By.ID, "com.globo.globotv:id/custom_view_empty_state_text_view_message")

        self.ASSERT_ITEM_ADICIONADO_MINHA_LISTA = (By.ID, "com.globo.globotv:id/fragment_title_button_two")
        self.ASSERT_DOWNLOAD_CONCLUIDO =          (By.ID, "com.globo.globotv:id/custom_view_download_status_image_view_icon")
        self.PRIMEIRO_ITEM_MINHA_LISTA =          (By.ID, "com.globo.globotv:id/custom_view_title_image_view_poster")
        self.ADICIONA_REMOVER_ITEM_MINHA_LISTA =  (By.ID, "com.globo.globotv:id/fragment_title_button_two")

        self.NAVEGAR_VOLTAR =                     (By.XPATH, "//android.widget.ImageButton[@content-desc='Navegar para cima']")
        self.BANNER_DESTAQUE =                    (By.ID, "com.globo.globotv:id/custom_view_premium_highlights_image_view_background")
        self.TRILHO_CONTINUE_ASSISTINDO =         (By.ID, 'new UiSelector().textContains("Continue assistindo")')
        self.TRILHO_MINHA_LISTA =                 (By.ID, 'new UiSelector().textContains("Minha lista")')
        self.MENU_DOWNLOAD =                      (By.ID, "com.globo.globotv:id/menu_bottom_navigation_view_item_downloads")
        self.MENU_INICIO =                        (By.ID, "com.globo.globotv:id/menu_bottom_navigation_view_item_home")
        self.ASSERT_LISTA_DOWNLOAD_VAZIA =        (By.ID, "com.globo.globotv:id/custom_view_empty_state_image_view_icon")
        self.ASSERT_DOWNLOAD_EM_ANDAMENTO =       (By.ID, 'com.globo.globotv:id/view_holder_download_title_text_view_downloading')
        self.SELECIONAR_ITENS_DOWNLOAD =          (By.ID, "com.globo.globotv:id/menu_downloads_item_edit")
        self.PRIMEIRO_ITEM_LISTA_DOWNLOAD =       (By.ID, "com.globo.globotv:id/view_holder_download_title_content_root")
        self.APAGAR_DOWNLOAD =                    (By.ID, "com.globo.globotv:id/snackbar_action")
        self.PRIMEIRO_ITEM_CATEGORIA_NOVELA =     (By.ID, "com.globo.globotv:id/custom_view_title_image_view_poster")
        self.PRIMEIRO_ITEM_CATEGORIA_CINEMA =     (By.ID, "com.globo.globotv:id/custom_view_title_image_view_poster")
        self.BTN_ASSISTIR_OU_CONTINUAR =          (By.ID, "com.globo.globotv:id/fragment_title_button_one")
        self.PRIMEIRO_EPISODIO_SERIE  =           (By.ID, "com.globo.globotv:id/custom_view_video_image_view_cover")
        self.CATEGORIA_NOVELA =                   (By.ID, 'new UiSelector().textContains("Novelas")')
        self.CATEGORIA_CINEMA =                   (By.ID, 'new UiSelector().textContains("Cinema")')
        self.CATEGORIA_SERIE =                    (By.ID, 'new UiSelector().textContains("Séries")')
        self.ICONE_DOWNLOAD_LISTA_CAPITULO =      (By.ID, "custom_view_video_custom_view_download_status")
        self.NOME_DO_TRILHO =                     (By.ID, 'new UiSelector().className("android.widget.TextView")')
        self.ASSERT_TEMPO_VIDEO =                 (By.ID, "com.globo.globotv:id/fragment_title_progress")

    def pesquisar_trilho_continue_assistindo_home(self):
        previous_title = None
        repeat_count = 0
        while True:
            try:
                self.trilho_continue_assistindo()
                break
            except NoSuchElementException:
                self.swipe_up()
                self.exibe_nome_do_trilho()
                # print(">>>>>>>>>> ", loc.exibe_nome_do_trilho())
                if self.exibe_nome_do_trilho() == previous_title:
                    repeat_count += 1

                if repeat_count == 3:
                    logging.info("O elemento: ")
                    logging.info(str(self.pesquisar_trilho_continue_assistindo_home))
                    logging.info("Não está disponível")
                    raise Exception()

                previous_title = self.exibe_nome_do_trilho()

    def assert_item_adicionado_minha_lista(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        item_adicionado_minha_lista = self.driver.find_element_by_id(self.ASSERT_ITEM_ADICIONADO_MINHA_LISTA[1])
        if item_adicionado_minha_lista.text == "Adicionado":
            print(">>>>>>>>>", item_adicionado_minha_lista.text )
        else:
            raise Exception("O minha lista nao foi salvo ao reiniciar o APP")

    def exibe_nome_do_trilho(self):
        nome_do_trilho = self.driver.find_element_by_android_uiautomator(self.NOME_DO_TRILHO[1])
        return nome_do_trilho.text

    def click_botao_assistir_ou_continuar(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        botao_assistir_ou_continuar = self.driver.find_element_by_id(self.BTN_ASSISTIR_OU_CONTINUAR[1])
        return botao_assistir_ou_continuar.click()

    def click_primeiro_episodio_serie(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        primeiro_episodio_serie = self.driver.find_element_by_id(self.PRIMEIRO_EPISODIO_SERIE[1])
        return primeiro_episodio_serie.click()

    def assert_botao_assistir_ou_continuar(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        botao_assistir_ou_continuar = self.driver.find_element_by_id(self.BTN_ASSISTIR_OU_CONTINUAR[1])
        return botao_assistir_ou_continuar.text

    def click_primeiro_item_lista_download(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        primeiro_item_lista_download = self.driver.find_element_by_id(self.PRIMEIRO_ITEM_LISTA_DOWNLOAD[1])
        return primeiro_item_lista_download.click()

    def click_icone_download_lista_capitulo(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        icone_download_lista_capitulo = self.driver.find_element_by_id(self.ICONE_DOWNLOAD_LISTA_CAPITULO[1])
        return icone_download_lista_capitulo.click()

    def click_primeiro_item_categoria_novela(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        primeiro_item_categoria_novela = self.driver.find_element_by_id(self.PRIMEIRO_ITEM_CATEGORIA_NOVELA[1])
        return primeiro_item_categoria_novela.click()

    def click_primeiro_item_categoria_cinema(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        primeiro_item_categoria_cinema = self.driver.find_element_by_id(self.PRIMEIRO_ITEM_CATEGORIA_CINEMA[1])
        return primeiro_item_categoria_cinema.click()

    def click_categoria_novela(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        categoria_novela = self.driver.find_element_by_android_uiautomator(self.CATEGORIA_NOVELA[1])
        return categoria_novela.click()

    def click_categoria_cinema(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        categoria_cinema = self.driver.find_element_by_android_uiautomator(self.CATEGORIA_CINEMA[1])
        return categoria_cinema.click()

    def click_categoria_serie(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        categoria_serie = self.driver.find_element_by_android_uiautomator(self.CATEGORIA_SERIE[1])
        return categoria_serie.click()

    def click_apagar_download(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        apagar_download = self.driver.find_element_by_id(self.APAGAR_DOWNLOAD[1])
        return apagar_download.click()

    def click_selecionar_itens_downlaod(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        selecionar_itens_download = self.driver.find_element_by_id(self.SELECIONAR_ITENS_DOWNLOAD[1])
        return selecionar_itens_download.click()

    def click_banner_destaque(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        banner_destaque = self.driver.find_element_by_id(self.BANNER_DESTAQUE[1])
        return banner_destaque.click()

    def click_adicionar_remover_item_minha_lista(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        adicionar_remover_item_minha_lista = self.driver.find_element_by_id(self.ADICIONA_REMOVER_ITEM_MINHA_LISTA[1])
        return adicionar_remover_item_minha_lista.click()

    def click_primeiro_item_minha_lista(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        click_primeiro_item_minha_lista = self.driver.find_element_by_id(self.PRIMEIRO_ITEM_MINHA_LISTA[1])
        return click_primeiro_item_minha_lista.click()

    def click_menu_download(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        click_menu_download = self.driver.find_element_by_id(self.MENU_DOWNLOAD[1])
        return click_menu_download.click()

    def click_menu_inicio(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        menu_inicio = self.driver.find_element_by_id(self.MENU_INICIO[1])
        return menu_inicio.click()

    def click_menu_categorias(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        menu_categorias = self.driver.find_element_by_id(self.MENU_CATEGORIA[1])
        return menu_categorias.click()

    def assistir_titulo(self):
        assistir_titulo = self.driver.find_element_by_android_uiautomator(self.watching_title[1])
        return assistir_titulo

    def trilho_continue_assistindo(self):
        continue_assistindo = self.driver.find_element_by_android_uiautomator(self.TRILHO_CONTINUE_ASSISTINDO[1])
        return continue_assistindo

    def trilho_minha_lista(self):
        minha_lista = self.driver.find_element_by_android_uiautomator(self.TRILHO_MINHA_LISTA[1])
        print("trilho Minha Lista")
        return minha_lista

    def poster(self):
        poster = self.driver.find_element_by_id(self.POSTER[1]).click()
        return poster

    def click_menu_perfil(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        menu_perfil = self.driver.find_element_by_id(self.MENU_PERFIL[1])
        return menu_perfil.click()

    def click_minha_lista(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        minha_lista = self.driver.find_element_by_android_uiautomator(self.MINHA_LISTA[1]).click()
        return minha_lista

    def assert_minha_lista_vazia(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        assert_minha_lista_vazia = self.driver.find_element_by_id(self.ASSERT_MINHA_LISTA_VAZIA[1])
        return assert_minha_lista_vazia

    def assert_download_em_andamento(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        download_em_andamento = self.driver.find_element_by_id(self.ASSERT_DOWNLOAD_EM_ANDAMENTO[1])
        return download_em_andamento

    def assert_tempo_video(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        tempo_video = (self.driver.find_element_by_id(self.ASSERT_TEMPO_VIDEO[1]))
        return tempo_video.text

    def assert_lista_download_vazio(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        assert_lista_download_vazio = self.driver.find_element_by_id(self.ASSERT_LISTA_DOWNLOAD_VAZIA[1])
        return assert_lista_download_vazio

    def assert_download_concluido(self):
        sleep(2)
        assert_download_concluido = self.driver.find_element_by_id(self.ASSERT_DOWNLOAD_CONCLUIDO[1])
        return assert_download_concluido

    def click_navegar_voltar(self):
        sleep(2)
        self.driver.implicitly_wait(30)
        navegar_voltar = self.driver.find_element_by_xpath(self.NAVEGAR_VOLTAR[1])
        return navegar_voltar.click()

    def swipe_up(self):
        screen = self.driver.get_window_size()
        w = screen['width']
        h = screen['height']
        move_x = w / 2
        move_y = h * 0.7
        move_end_x = w / 2
        move_end_y = h * 0.3
        self.driver.swipe(move_x, move_y, move_end_x, move_end_y)


