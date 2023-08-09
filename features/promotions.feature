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

Scenario: Create a Promotion
    When I visit the "home page"
    And I set the "Name" to "promo2"
    And I set the "Message" to "new promotion"
    And I set the "Start Date" to "08-10-2023"
    And I set the "End Date" to "08-20-2027"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "Message" field should be empty
    And the "Start Date" field should be empty
    And the "end date" field should be empty
    When I paste the "id" field
    And I set the "Name" to "promo2"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "promo2" in the results
    And I should see "new promotion" in the results
    And I should see "Fri, 20 Aug 2027 00:00:00 GMT" in the results
    And I should see "Thu, 10 Aug 2023 00:00:00 GMT" in the results

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
