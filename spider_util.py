import datetime
import random
import re
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree


video_regex = r"^https://www.douyin.com/video/(.*)(\?.*)?$"
login_btn_case1_xpath='//*[@id="_7hLtYmO"]'
login_btn_case2_xpath='//*[@id="tcTjz3nj"]'

def dy_login(browser: WebDriver):
    print("开始登录")
    WebDriverWait(browser, 24 * 60 * 3600).until(lambda driver: find_element_silent(browser,
                                                                                             login_btn_case1_xpath) is not None or find_element_silent(
        browser, login_btn_case2_xpath) is not None)

    login_btn_case1 = find_element_silent(browser, login_btn_case1_xpath)
    login_btn_case2 = find_element_silent(browser, login_btn_case2_xpath)

    if login_btn_case1 is not None:
        try:
            print("登录机制1")
            execute_silent(lambda:login_btn_case1.click())
            WebDriverWait(browser, 24 * 60 * 3600).until(
                lambda driver: find_element_silent(driver, login_btn_case1_xpath) is None)
        except Exception as e:
            print(e)
    elif login_btn_case2 is not None:
        try:
            print("登录机制2")
            execute_silent(lambda: login_btn_case2.click())
            WebDriverWait(browser, 24 * 60 * 3600).until(
                lambda driver: find_element_silent(browser, login_btn_case2_xpath) is None)
        except Exception as e:
            print(e)
    else:
        print("暂不支持的登录机制")
        raise Exception("登录失败")

    print("登录成功")

def execute_silent(method):
    try:
        method()
    except Exception as e:
        print(e)

def execute_function_silent(method):
    try:
        return method()
    except Exception as e:
        print(e)
        return None

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

def fake_human_scroll(browser:WebDriver, max_scroll):
    """
    上下滑动假装认为操作
    :param browser:
    :return:
    """
    for i in range(0, random.randint(1,10)):
        browser.execute_script(f'scrollBy(0,{-random.randint(1,max_scroll)})')
        time.sleep(random.random()/2)
        browser.execute_script(f'scrollBy(0,{random.randint(1,max_scroll)})')
        time.sleep(random.random()/2)


def find_element_silent(browser: WebDriver, name, by=By.XPATH):
    try:
        element = browser.find_element(by, name)
        return element
    except Exception as e:
        print(e)
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

def get_lxml_etree(browser):
    html_str = browser.execute_script("return document.documentElement.innerHTML")
    html = etree.HTML(html_str)
    return html

def get_comment_info_by_lxml(root, index):

    # root:      //*[@id="douyin-right-container"]/div[2]/div/div[1]/div[5]/div/div/div[3]/div[10]
    # time:   	//*[@id="douyin-right-container"]/div[2]/div/div[1]/div[5]/div/div/div[3]/div[10]/div/div[2]/div/div[2]/span
    # praise: 	//*[@id="douyin-right-container"]/div[2]/div/div[1]/div[5]/div/div/div[3]/div[10]/div/div[2]/div/div[3]/div/div[1]/p[1]/span
    # main_page: //*[@id="douyin-right-container"]/div[2]/div/div[1]/div[5]/div/div/div[3]/div[10]/div/div[2]/div/div[1]/div[1]/div/a
    # name:   	//*[@id="douyin-right-container"]/div[2]/div/div[1]/div[5]/div/div/div[3]/div[10]/div/div[2]/div/div[1]/div[1]/div/a/span/span/span/span/span/span
    # comment:	//*[@id="douyin-right-container"]/div[2]/div/div[1]/div[5]/div/div/div[3]/div[10]/div/div[2]/div/p

    comment_text_relative_xpath = "div/div[2]/div/p/span/span/span/span/span/span/span"
    user_name_relative_xpath = "div/div[2]/div/div[1]/div[1]/div/a/span/span/span/span/span/span"
    main_page_relative_xpath = "div/div[2]/div/div[1]/div[1]/div/a/@href"
    praise_relative_xpath = "div/div[2]/div/div[3]/div/div[1]/p[1]/span"
    comment_time_and_location_relative_xpath = "div/div[2]/div/div[2]/span"

    comment_info = {}

    comment_obj_list = root.xpath(f'//*[@id="douyin-right-container"]/div[2]/div/div[1]/div[5]/div/div/div[3]/div[{index}]')
    if comment_obj_list is None or len(comment_obj_list) == 0:
        print(f"索引为{index}的div未发现评论")
        return None

    comment_obj = comment_obj_list[0]

    # 存储爬取时候的时间，因为评论时间都是相对时间，比如1天前，9个月前等
    comment_info["data_snapshot_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    user_name_list = comment_obj.xpath(user_name_relative_xpath)
    if user_name_list is not None and len(user_name_list) != 0:
        user_name = user_name_list[0].text
        print(f'用户名: {user_name}')
        comment_info["user_name"] = user_name

    main_page_list = comment_obj.xpath(main_page_relative_xpath)
    if main_page_list is not None and len(main_page_list) != 0:
        main_page = main_page_list[0]
        if main_page.startswith("//"):
            main_page=main_page[2:]
        print(f'主页: {main_page}')
        comment_info["main_page"] = main_page

    comment_time_list = comment_obj.xpath(comment_time_and_location_relative_xpath)
    if comment_time_list is not None and len(comment_time_list) != 0:
        comment_time = comment_time_list[0].text
        print(f'评论时间: {comment_time}')
        comment_info["comment_time_and_location"] = comment_time

    comment_text_list = comment_obj.xpath(comment_text_relative_xpath)
    if comment_text_list is not None and len(comment_text_list) != 0:
        comment_text = comment_text_list[0].text
        print(f'评论内容: {comment_text}')
        comment_info["comment_text"] = comment_text

    praise_num_list = comment_obj.xpath(praise_relative_xpath)
    if praise_num_list is not None and len(praise_num_list) != 0:
        praise_num = praise_num_list[0].text
        print(f'点赞数: {praise_num}')
        comment_info["praise_num"] = praise_num

    return comment_info

def get_comment_info_by_selenium(browser: WebDriver, index):
    comment_info = {}
    user_name = browser.find_element(By.XPATH,
                                     f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{index + 1}]/div/div[2]/div[1]/div[2]/div[1]/div/a/span/span/span/span/span').text
    print(f'用户名: {user_name}')
    comment_info["user_name"] = user_name
    #
    main_page = browser.find_element(By.XPATH,
                                     f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{index + 1}]/div/div[2]/div[1]/div[2]/div[1]/div/a').get_attribute(
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


