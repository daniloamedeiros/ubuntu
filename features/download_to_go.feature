@d2g
Feature: Download to go
  Scenario: Validar funcinamento do download to go

    Given that I am logged into the app
    When clico no menu download
    And verifico que todos os downloads foram apagados
    And realizo o download
    Then verifico se o donwload foi realizado com sucesso


