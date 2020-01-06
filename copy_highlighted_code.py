#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import argparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def create_driver():
    # creates a chrome driver
    capability = DesiredCapabilities.CHROME
    capability["pageLoadStrategy"] = "none"

    options = Options()
    # options.add_argument("--headless")

    driver = webdriver.Chrome(desired_capabilities=capability, options=options)

    wait = WebDriverWait(driver, 5)

    # accesses the website
    driver.get(url)

    return driver, wait


def switch_to_frame(driver, wait):
    try:
        wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="subsection"]/div[2]/div/center/iframe')))
        time.sleep(1)
    except:
        print("{}cannot load the page".format(err_msg))
        exit(1)

    # switches to the frame that contains text area of code, languages and submission button
    driver.switch_to.frame(1)


def input_code(driver, wait):
    # receives code
    stop_word = "#/"
    code = ''
    print("code: (input #/ to indicate the end of the code, and input ### to exit)")
    for line in iter(input, stop_word):
        code += f"{line}\n"

    if code == "###":
        return False

    # inputs to the text area
    try:
        print("inputting code")

        wait.until(ec.presence_of_element_located((By.ID, 'code')))
    except:
        print("{}cannot find the text area for inputting code".format(err_msg))
        exit(2)
    else:
        text_area_code = driver.find_element_by_id("code")
        text_area_code.send_keys(code)
        print("done")

    return True


def get_supported_languages(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")

    option_list = list(soup.find("select", id="class").children)

    supported_language_list = []
    for option in option_list:
        try:
            option_string = option.string
            if option_string != "\n":
                # split string like "C, C++" -> ["C", "C++"]
                split_list = option.string.split(", ")
                if len(split_list) == 1:
                    supported_language_list.append(option.string)
                else:
                    supported_language_list.extend(split_list)
        except:
            pass

    return supported_language_list


def select_language(driver, language):
    if language.lower() in ["c", "c++"]:
        language = ""

    if not language:
        language_display = "C, C++"
    else:
        # retrieves the list of su[ported language
        supported_language_list = get_supported_languages(driver)
        supported_language_list_lower = [supported_language.lower() for supported_language in supported_language_list]

        if language.lower() in supported_language_list_lower:
            language_display = supported_language_list[supported_language_list_lower.index(language.lower())]
        else:
            print("{}input language not supported, C / C++ highlighted style will be used".format(err_msg))
            print(f"supported languages: {supported_language_list}")
            language_display = "C, C++"

    print(f"selecting language: {language_display}")

    # selects a language
    option = driver.find_element_by_id("class")
    option.click()
    option.send_keys(language)

    print("done")


def submit(driver):
    print("submitting")

    input_submit = driver.find_element_by_tag_name("input")
    input_submit.click()

    print("done")


def select_n_copy(driver, wait):
    print("copying")

    # switches to the new window
    driver.switch_to.window(driver.window_handles[1])

    # locates highlighted code
    try:
        wait.until(ec.presence_of_element_located((By.TAG_NAME, 'ol')))
    except:
        print("{}cannot locate highlighted code".format(err_msg))
        exit(3)
    else:
        # selects all and copies
        driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL, 'a')
        time.sleep(1)
        driver.find_element_by_tag_name("body").send_keys(Keys.CONTROL, 'c')

        print("done")


def clean_code(driver, wait):
    print("cleaning code")

    try:
        wait.until(ec.presence_of_element_located((By.ID, 'code')))
    except:
        print("{}cannot find the text area for inputting code".format(err_msg))
        exit(2)
    else:
        text_area_code = driver.find_element_by_id("code")
        text_area_code.send_keys(Keys.CONTROL, 'a')
        text_area_code.send_keys(Keys.BACK_SPACE)

        print("done")


def copy_highlighted_code(language):
    # generates a headless driver
    driver, wait = create_driver()

    # switches to the frame
    switch_to_frame(driver, wait)

    while True:
        # inputs code to be highlighted
        continue_input = input_code(driver, wait)
        if not continue_input:
            break

        # selects a language
        select_language(driver, language)

        # clicks "show highlighted" to submit
        submit(driver)

        # selects and copies
        select_n_copy(driver, wait)

        # switches to the main page
        driver.switch_to.window(driver.window_handles[0])

        # switches the frame
        switch_to_frame(driver, wait)

        # cleans code in the text area
        clean_code(driver, wait)

        print()


if __name__ == '__main__':
    url = "http://www.planetb.ca/syntax-highlight-word"

    err_msg = "copy-highlighted_code.py: error: "

    parser = argparse.ArgumentParser(description="copy_highlighted_code.py - a tool for copying highlighted code from "
                                                 "http://www.planetb.ca/syntax-highlight-word")
    parser.add_argument("--language", "-l", action="store", default="", help="language (full name) of the code, "
                                                                             "c / c++ by default")
    args = parser.parse_args()

    copy_highlighted_code(args.language)
