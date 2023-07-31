//Feature: The promotions service backend
//    As an Store Owner
//    I need a RESTful promotions service
//    So that I can keep track of all the promotions in the store

//Background:
 //   Given the following promotions
 //       | id         | name       | start_date | end_date   | whole_store| message              | promotion_changes_price|
 //       | 1          | 20% Off    | 2023-01-01 | 2023-01-05 | True       | promo_test_1         | True                   |
 //       | 2          | 30% Off    | 2023-03-01 | 2023-04-05 | False      | promo_test_2         | True                   |
 //       | 3          | Summer Sale| 2023-06-12 | 2023-06-15 | True       | Buy One Get One Free | True                   |


//Scenario: The server is running
//    When I visit the "home page"
//    Then I should see "Promotions Service" in the title
//    And  I should not see "404 Not Found"
