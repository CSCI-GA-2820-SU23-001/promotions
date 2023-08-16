"""
Promotions Steps

Steps file for promotions.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import os
import requests
from behave import given, when, then
from compare import expect

import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
ID = None

ID_PREFIX = 'promotion_'


@given('the following promotions')
def step_impl(context):
    """ Delete all Promotions and load new ones """

    # List all of the promotions and delete them one by one
    rest_endpoint = f"{context.base_url}/api/promotions"
    print(f'step_impl {rest_endpoint}')
    #rest_endpoint = "http://localhost:8080/api/promotions"
    context.resp = requests.get(rest_endpoint)
    assert(context.resp.status_code == HTTP_200_OK)
    for promo in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{promo['id']}")
        assert(context.resp.status_code == HTTP_204_NO_CONTENT)

    # load the database with new promotions
    for row in context.table:
        payload = {
            "name": row['name'],
            "start_date": row['start_date'],
            "end_date": row['end_date'],
            "whole_store": row['whole_store'] in ['True', 'true', '1'],
            "message": row['message'],
            "promotion_changes_price": row['promotion_changes_price'] in ['True', 'true', '1'],
            "has_been_extended": row['promotion_changes_price'] in ['True', 'true', '1'],
            "original_end_date": row['end_date'],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        context.resp_id = context.resp.json()['id']
        assert(context.resp.status_code == HTTP_201_CREATED)


@given(u'the server is started')
def step_impl(context):
  context.base_url = os.getenv(
    'BASE_URL',
    'http://localhost:8080'
    )
  #context.base_url = 'http://localhost:8080'
  print(f'Server started: {context.base_url}')
  context.resp = requests.get(context.base_url + '/')
  assert context.resp.status_code == 200

@when(u'I visit the "home page"')
def step_impl(context):
 #context.base_url = 'http://localhost:8080'
 print(f'visit home page: {context.base_url}')
 context.driver.get(context.base_url)
 context.resp = requests.get(context.base_url + '/')
 assert context.resp.status_code == 200

def step_impl(context):
 raise NotImplementedError('STEP: When I visit the "home page"')

@then('I should see "{message}"')
def step_impl(context, message):
 assert message in str(context.resp.text)

def step_impl(context, message):
 assert message not in str(context.resp.text)

@then('I should not see "{message}"')
def step_impl(context, message):
 assert message not in str(context.resp.text)
def step_impl(context):
 raise NotImplementedError('STEP: Then I not should see "404 Not Found"')


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element(By.ID, button_id).click()

@when(u'I set the "ID" to an existing id')
def step_impl(context):
    context.driver.find_element(By.ID, "promotion_id").send_keys(context.resp_id)

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    assert(found)

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    assert(found)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element(By.ID, 'search_results')
    assert(name not in element.text)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)

@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element(By.ID, element_id))
    assert(element.first_selected_option.text == text)

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    assert(element.get_attribute('value') == u'')

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    assert(found)

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)



##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)
@then('the promotions table should be populated')
def step_impl(context):
    search_table_promotions = context.driver.find_elements(By.XPATH, '//*[@id="search_results"]/table/tbody/*')
    expect(len(search_table_promotions) > 0).to_be(True)

