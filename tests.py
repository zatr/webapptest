from selenium import webdriver
import unittest
import worker
from settings import target_url, assert_text
import time


class TestSubmitAnalystItems(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.target_url = target_url
        self.assert_text = assert_text
        self.driver.get(self.target_url)
        self.assert_title()
        worker.analyst_login(self.driver)

    def tearDown(self):
        time.sleep(3)
        self.driver.quit()

    def assert_title(self):
        try:
            self.assertIn(self.assert_text, self.driver.title)
        except:
            print 'Page title assertion failed. Check settings.'
            self.tearDown()
            self.skipTest(TestSubmitAnalystItems)
    
    def test_create_default_all_requests(self):
        worker.create_default_menu_new_item(self.driver, 'all requests')

    def test_create_default_problem(self):
        worker.create_default_menu_new_item(self.driver, 'Problem')

    def test_create_default_change(self):
        worker.create_default_menu_new_item(self.driver, 'Change')

    def test_create_default_task(self):
        worker.create_default_menu_new_item(self.driver, 'Task')

    def test_create_default_all_items(self):
        worker.create_default_menu_new_item(self.driver, 'all')

    def test_create_empty_change(self):
        worker.create_empty_menu_new_item(self.driver, 'Change')

    def test_create_new_change_click_cab_group(self):
        worker.create_new_change_click_cab_group(self.driver)

    def test_create_new_request_status(self):
        worker.create_new_request_status(self.driver, automatic_closure=True)
