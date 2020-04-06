@minhalista
Feature: Minha Lista

  Scenario: Validar se o minha lista está funcionando corretamente
        Given I am logged in to the application
        When I'm on my list
        And clean all content
        And I click on add content to my list
        And I verify that the content has been added
        And close and reopen the app
        And I click on my list
        Then I verify that the content has been added
        And I check the track on my list

