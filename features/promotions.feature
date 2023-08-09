Feature: The promotion service back-end
 As a eCommerce Manager
 I need a RESTful catalog service
 So that I can keep track of all my promotions

Background:
 Given the following promotions
        | name       | start_date | end_date | message | whole_store | promotion_changes_price | has_been_extended |
        | promo1 | 2023-08-01 | 2023-12-10 | message one | True | True | False |



Scenario: The server is running
    When I visit the "home page"
    Then I should see "Welcome to the Promotions Service"
    And I should not see "404 Not Found"


Scenario: Query promotions
    When I visit the "home page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "promo1" in the results
    And I should not see "leo" in the results

Scenario: List all Promotions
    When I visit the "home Page"
    And I press the "List" button
    Then I should see the message "Success"
    And the promotions table should be populated

Scenario: Cancel a promotion
    When I visit the "home page"
    And I set the "ID" to an existing id
    And I press the "Cancel" button
    Then I should see the message "Promotion canceled!"

Scenario: Delete a promotion
    When I visit the "home page"
    And I set the "ID" to an existing id
    And I press the "Delete" button
    Then I should see the message "Promotion has been Deleted!"
