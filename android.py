import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from percy import percy_screenshot

USER_NAME = "testend_SpcUGB"
ACCESS_KEY = "oy8oSqWgG9ZAnsU9hYWc"


def run_session(capability):
    options = UiAutomator2Options().load_capabilities(capability)
    driver = webdriver.Remote('https://hub-dev-app-percy.bsstag.com/wd/hub', options=options)
    percy_screenshot(driver, 'screenshot 1')

    # search_element = WebDriverWait(driver, 30).until(
    #     EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia"))
    # )
    # search_element.click()
    # search_input = WebDriverWait(driver, 30).until(
    #     EC.element_to_be_clickable(
    #         (AppiumBy.ID, "org.wikipedia.alpha:id/search_src_text")
    #     )
    # )
    # search_input.send_keys("BrowserStack")
    # time.sleep(2)
    # driver.hide_keyboard()
    # percy_screenshot(driver, 'screenshot 2')

    driver.quit()


if __name__ == '__main__':
    pixel_4 = {
      "platformVersion" : "11.0",
      "deviceName" : "Google Pixel 4",
        "app": 'bs://4c583aff6ca089dce5e3b2aae09803bcd45878c7',
        "appium:percyOptions": {
            # enabled is default True. This can be used to disable visual testing for certain capabilities
            "enabled": True
        },
        'bstack:options' : {
            "projectName" : "My Project",
            "buildName" : "test percy_screnshot",
            "sessionName" : "BStack first_test",

            # Set your access credentials
            "userName" : USER_NAME,
            "accessKey" : ACCESS_KEY
        },
        "platformName": "android",
    }

    capabilities_list = [pixel_4]
    print(list(map(run_session, capabilities_list)))