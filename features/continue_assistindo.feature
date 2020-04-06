@continue_assistindo
Feature: Continue assistindo
@trilho_ca
  Scenario: Validar trilho disponivel na home
    Given that I am logged into the app
    When I scroll down
    Then I see the trail of continue watching

@ca_filme
  Scenario: Assistir um filme da categoria cinema
    Given that I am logged into the app
    When I click on categories
    And I click on the cinema category
    And click on the first title
    And check the video running time and click watch
    And I wait two minutes of playing the video
    And close and reopen the app
    Then I validate that the progression of the film has changed in relation to the start time

  @ca_serie_titulo
  Scenario: Verificar que ao assistir uma série através do titulo, a opção de continue assistindo
  está disponível com a timeline (barra de progressão)

    Given that I am logged into the app
    When I click on categories
    And I click on the series category
    And click on the first title
    And check the video running time and click watch
    And I wait two minutes of playing the video
    And close and reopen the app
    Then I validate that the series progression has changed in relation to the start time

    @ca_serie_episodio
  Scenario: Verificar que ao assistir uma série através dos episódios, a opção de continue
  assistindo está disponível, com a timeline (barra de progressão)

    Given that I am logged into the app
    When I click on categories
    And I click on the series category
    And click on the first title
    And I check the video running time and click on watch the first episode
    And I wait two minutes of playing the video
    And close and reopen the app
    Then I validate that the series progression has changed in relation to the start time
