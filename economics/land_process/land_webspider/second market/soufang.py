# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class Soufang(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://land.fang.com/landfinancing/0_0_0_0_0_0_____0______1.html"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_soufang(self):
        driver = self.driver
        driver.get(self.base_url + "/landfinancing/0_0_0_0_0_0_____0______1.html")
        driver.find_element_by_id("region_1111111").click()
        driver.find_element_by_id("iItemTypeLandUse_203").click()
        driver.find_element_by_id("province_110000").click()
        driver.find_element_by_id("iTransferFormFinancingForm_101").click()
        driver.find_element_by_id("iTransferFormFinancingForm_103").click()
        driver.find_element_by_id("iTransferFormFinancingForm_102").click()
        driver.find_element_by_css_selector("body").click()
        driver.find_element_by_id("order_amount").click()
        driver.find_element_by_id("iTransferFormFinancingForm_101").click()
        driver.find_element_by_id("order_amount").click()
        driver.find_element_by_id("order_amount").click()
        driver.find_element_by_id("pagego").click()
        driver.find_element_by_id("pagego").clear()
        driver.find_element_by_id("pagego").send_keys("2")
        driver.find_element_by_link_text("Go").click()
        # ERROR: Caught exception [unknown command []]
        # ERROR: Caught exception [unknown command []]
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
