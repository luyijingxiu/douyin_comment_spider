import re
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

video_regex = r"^https://www.douyin.com/video/(.*)\?.*$"


def dy_login(browser: WebDriver):
    print("开始登录")
    WebDriverWait(browser, 24 * 60 * 3600).until(lambda driver: find_element_by_xpath_silent(browser,
                                                                                             '//*[@id="qdblhsHs"]') is not None or find_element_by_xpath_silent(
        browser, '//*[@id="Qf6c6FMM"]') is not None)

    login_btn_case1 = find_element_by_xpath_silent(browser, '//*[@id="qdblhsHs"]')
    login_btn_case2 = find_element_by_xpath_silent(browser, '//*[@id="Qf6c6FMM"]')

    if login_btn_case1 is not None:
        try:
            print("登录机制1")
            login_btn_case1.click()
        except Exception as e:
            print(e)
    elif login_btn_case2 is not None:
        try:
            print("登录机制2")
            login_btn_case2.click()
        except Exception as e:
            print(e)
    else:
        print("暂不支持的登录机制")
        raise Exception("登录失败")

    icon_obj_1 = find_element_by_xpath_silent(browser,
                                              '//*[@id="douyin-header"]/header/div[2]/div[2]/div/div/div/ul[1]/li[5]')
    icon_obj_2 = find_element_by_xpath_silent(browser,
                                              '//*[@id="douyin-header"]/div/header/div/div/div[2]/div/div/div/ul[1]/li[5]/a')
    if icon_obj_1 is not None:
        print(f'find //*[@id="douyin-header"]/header/div[2]/div[2]/div/div/div/ul[1]/li[5], {icon_obj_1.text}')
    if icon_obj_2 is not None:
        print(f'find //*[@id="douyin-header"]/div/header/div/div/div[2]/div/div/div/ul[1]/li[5]/a, {icon_obj_2.text}')

    WebDriverWait(browser, 24 * 60 * 3600).until(lambda driver: driver.find_element(By.XPATH,
                                                                                    '//*[@id="douyin-header"]/header/div[2]/div[2]/div/div/div/ul[1]/li[5]')
                                                                and (driver.find_element(By.XPATH,
                                                                                         '//*[@id="douyin-header"]/header/div[2]/div[2]/div/div/div/ul[1]/li[5]').text == ""))

    print("登录成功")

def str_to_int(num_str:str):
    if num_str is None:
        return 0
    elif num_str.endswith("W") or num_str.endswith("w"):
        prefix=num_str[0:-1]
        return float(prefix)*1000
    else:
        return float(num_str)

def get_video_id_from_url(video_url: str):
    matcher = re.match(video_regex, video_url)
    return matcher.group(1)


def find_element_by_xpath_silent(browser: WebDriver, xpath):
    try:
        element = browser.find_element(By.XPATH, xpath)
        return element
    except Exception as e:
        print(
            f'selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: "method":"xpath","selector":"{xpath}"')
        return None


def scroll_to_bottom(browser: WebDriver, max_scroll_cnt):
    """
    滚动到页面底部
    :param browser: driver
    :param max_scroll_cnt: 最大滚动次数
    :return:
    """
    if max_scroll_cnt <= 0:
        print("最大滚动次数不能小于等于0")
        return
    for i in range(max_scroll_cnt):
        browser.execute_script('scroll(0,document.body.scrollHeight)')
        time.sleep(3)
        i = i + 1
        print(f'第{i}次翻页加载')


def handle_page_lazy_loading(browser: WebDriver, refresh_interval:int):
    window_height = [browser.execute_script('return document.body.scrollHeight;')]
    while True:
        browser.execute_script('scroll(0,100000)')
        time.sleep(refresh_interval)
        half_height = int(window_height[-1]) / 2
        browser.execute_script('scroll(0,{0})'.format(half_height))
        browser.execute_script('scroll(0,100000)')
        time.sleep(refresh_interval)
        check_height = browser.execute_script('return document.body.scrollHeight;')
        if check_height == window_height[-1]:
            break
        else:
            window_height.append(check_height)


def get_comment_info(browser: WebDriver, index):
    comment_info = {}
    user_name = browser.find_element(By.XPATH,
                                     f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{index + 1}]/div/div[2]/div[1]/div[1]/div/a/span/span/span/span/span').text
    print(f'用户名: {user_name}')
    comment_info["user_name"] = user_name
    #
    main_page = browser.find_element(By.XPATH,
                                     f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{index + 1}]/div/div[1]/a').get_attribute(
        "href")
    print(f'主页: {main_page}')
    comment_info["main_page"] = main_page

    comment_time = browser.find_element(By.XPATH,
                                        f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{index + 1}]/div/div[2]/div[1]/div[1]/p').text
    print(f'评论时间: {comment_time}')
    comment_info["comment_time"] = comment_time

    comment_text = browser.find_element(By.XPATH,
                                        f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{index + 1}]/div/div[2]/p').text
    print(f'评论内容: {comment_text}')
    comment_info["comment_text"] = comment_text

    # try:
    #     sub_comment_num = browser.find_element(By.XPATH,f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{i+1}]/div/div[2]/div[2]/button').text
    # except:
    #     sub_comment_num = 0
    #
    # print(f'二级评论数: {sub_comment_num}')
    # comment_info["sub_comment_num"] = sub_comment_num

    praise_num = browser.find_element(By.XPATH,
                                      f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{index + 1}]/div/div[2]/div[2]/div/p').text
    print(f'点赞数: {praise_num}\n\n')
    comment_info["praise_num"] = praise_num

    return comment_info
