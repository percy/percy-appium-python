import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from percy import  percy_screenshot
from percy.lib.ignore_region import IgnoreRegion

USER_NAME = "pradumkumar_USRpXW"
ACCESS_KEY = "3oYGPpwSxJpxpWKpzYEg"


def run_session(capability):
    driver = webdriver.Remote('https://hub-cloud.browserstack.com/wd/hub', capability)
    usernamexpath = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.widget.EditText[1]";
    passxpath = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.view.ViewGroup/android.widget.EditText[2]";
    username = driver.find_element(by=AppiumBy.XPATH, value=usernamexpath)
    password = driver.find_element(by=AppiumBy.XPATH, value=passxpath)
                
    #username = driver.find_element_by_xpath(usernamexpath)
    #password = driver.find_element_by_xpath(passxpath)
    username.send_keys("kasdhjksdhfsdf")
    password.send_keys("slkdfksjdfhkdj")
    login = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Login")
    login.click()
    ignore_region_xpaths = [usernamexpath]
    ignore_region_ids = ["Login"]
    ignore_region_appium_elements = [password]

    options = {
        "ignore_regions_xpaths": ignore_region_xpaths,
        "ignore_region_accessibility_ids": ignore_region_ids,
        "ignore_region_appium_elements": ignore_region_appium_elements
    }
    ignore_region = IgnoreRegion(1116, 126,108,972)
    custom_ignore_regions = [ignore_region]
    percy_screenshot(driver, 'screenshot 1',
     ignore_regions_xpaths = ignore_region_xpaths, 
     ignore_region_accessibility_ids= ignore_region_ids,
     custom_ignore_regions= custom_ignore_regions
    )
    

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
        "deviceName": "Google Pixel 4",
        "app": 'bs://361abd112d63e1d96c4a34f538a7b390594c3956',
        "appium:percyOptions": {
            # enabled is default True. This can be used to disable visual testing for certain capabilities
            "enabled": True,
            'ignoreErrors': False,
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