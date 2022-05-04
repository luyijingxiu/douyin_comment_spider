#!/usr/bin/env/ python
# -*- coding:utf-8 -*-

import os
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, 'config.json'), encoding='UTF-8') as fp:
    CONFIG = json.load(fp)

tik_tok_prefix_url = 'https://www.douyin.com'

video_regex = r"^https://www.douyin.com/video/(.*)\?.*$"

file_save_path = file_path + r'/spider/'

# http://chromedriver.storage.googleapis.com/index.html
chrome_driver_path = file_path + '/chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
browser = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
browser.maximize_window()


def start():
    try:
        for tik_tok_id in CONFIG['tik_tok_id_list']:
            req_url = f"{tik_tok_prefix_url}/user/{tik_tok_id}"
            browser.get(req_url)
            browser.implicitly_wait(10)
            handle_page_lazy_loading()
            save_userinfo()
            save_works()
    finally:
        browser.close()
        browser.quit()


def handle_page_lazy_loading(max_scroll_cnt: int = -1):
    # window_height = [browser.execute_script('return document.body.scrollHeight;')]
    i = 0
    while max_scroll_cnt == -1 or i < max_scroll_cnt:
        browser.execute_script('scroll(0,document.body.scrollHeight)')
        time.sleep(3)
        # half_height = int(window_height[-1]) / 2
        # browser.execute_script('scroll(0,{0})'.format(half_height))
        # browser.execute_script('scroll(0,100000)')
        # time.sleep(3)
        # check_height = browser.execute_script('return document.body.scrollHeight;')
        # if check_height == window_height[-1]:
        #     break
        # else:
        #     window_height.append(check_height)
        i = i + 1
        print(f'第{i}次翻页加载')


def save_userinfo():
    username = browser.find_element(By.XPATH,
                                    '//*[@id="root"]/div/div[2]/div/div/div[2]/div[1]/div[2]/h1/span/span/span/span/span').text
    filepath = f"{file_save_path}/user/{username}"
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    os.chdir(filepath)
    file_name = '主页信息.txt'
    with open(file_name, 'a+', encoding='UTF-8') as file:
        file.write(browser.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div/div[2]/div[1]').text)
        file.close()


def save_works():
    ul = browser.find_element(By.XPATH, "//*[@id='root']/div/div[2]/div/div/div[4]/div[1]/div[2]/ul")
    lis = ul.find_elements_by_xpath('li')
    li_len = len(lis)
    i = 0
    while i < li_len:
        try:
            forward_element = lis[i].find_element(By.XPATH,
                                                  '//*[@id="root"]/div/div[2]/div/div/div[4]/div[1]/div[2]/ul/li[3]/a')
            browser.execute_script("arguments[0].scrollIntoView();", forward_element)
            forward_element.click()
        except:
            browser.find_element(By.XPATH, '//*[@id="login-pannel"]/div[2]').click()
            continue
        browser.switch_to.window(browser.window_handles[1])
        title = browser.find_element(By.XPATH,
                                     "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[1]/div/h1/span[2]").text
        print(f'title: {title}')
        favorite_num = browser.find_element(By.XPATH,
                                            "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[1]/div/span").text
        comment_num = browser.find_element(By.XPATH,
                                           "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[2]/span").text
        collect_num = browser.find_element(By.XPATH,
                                           "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[3]/span").text
        release_time = browser.find_element(By.XPATH,
                                            "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[2]/span").text
        file_name = '抖音作品.txt'
        with open(file_name, 'a+', encoding='UTF-8') as file:
            print('----- 第' + str(i + 1) + '个抖音作品 -----')
            file.write('----- 第' + str(i + 1) + '个抖音作品 -----\n')
            file.write('标题: ' + title + '\n')
            file.write('获赞: ' + str(favorite_num) + '\n')
            file.write('评论: ' + str(comment_num) + '\n')
            file.write('收藏: ' + str(collect_num) + '\n')
            file.write(release_time + '\n')
            file.write('链接: ' + browser.current_url + '\n\n')
            file.close()
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        i = i + 1
        if i % 10 == 0:
            time.sleep(3)


def login():
    print("开始登录")
    WebDriverWait(browser, 24 * 60 * 3600).until(lambda driver: find_element_by_xpath_silent('//*[@id="qdblhsHs"]') is not None or find_element_by_xpath_silent('//*[@id="Qf6c6FMM"]') is not None)

    login_btn_case1 = find_element_by_xpath_silent('//*[@id="qdblhsHs"]')
    login_btn_case2 = find_element_by_xpath_silent('//*[@id="Qf6c6FMM"]')

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

    icon_obj_1 = find_element_by_xpath_silent('//*[@id="douyin-header"]/header/div[2]/div[2]/div/div/div/ul[1]/li[5]')
    icon_obj_2 = find_element_by_xpath_silent(
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


def begin_search(keyword: str):
    req_url = f"{tik_tok_prefix_url}/search/{keyword}"

    browser.get(req_url)
    time.sleep(2)
    login()
    # search_input = browser.find_element(By.XPATH,'//*[@id="douyin-header"]/div/header/div/div/div[1]/div/div[2]/div/form/input[1]')
    # search_input.send_keys(keyword)
    #
    # search_btn = browser.find_element(By.XPATH, '//*[@id="douyin-header"]/div/header/div/div/div[1]/div/div[2]/div/button')
    # search_btn.click()
    handle_page_lazy_loading(10)
    video_parent = browser.find_element(By.XPATH, '//*[@id="dark"]/div[2]/div/div[3]/div[1]/ul')
    list = video_parent.find_elements_by_xpath('li')
    li_len = len(list)
    print(f"视频总数：{li_len}")
    i = 1

    video_ur_list = []
    while i <= li_len:
        video = browser.find_element(By.XPATH, f'//*[@id="dark"]/div[2]/div/div[3]/div[1]/ul/li[{i}]')
        browser.execute_script("arguments[0].scrollIntoView();", video)

        time.sleep(2)

        # hover_div = video.find_element(By.XPATH, 'div/div/div[3]/div/div/div[1]/div[1]/div/div[3]/div[2]')
        # webdriver.ActionChains(browser).move_to_element(hover_div).perform()

        video_info_div = video.find_element(By.XPATH,
                                            'div/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div[1]/xg-controls/xg-inner-controls/xg-right-grid/xg-icon[1]/a')
        print(video_info_div.get_attribute("href"))
        video_ur_list.append(video_info_div.get_attribute("href"))
        i = i + 1

    file_path = f"{file_save_path}/search/{keyword}"
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    file_name = 'video_url_list.json'

    with open(f"{file_path}/{file_name}", 'w', encoding='UTF-8') as file:
        file.write(json.dumps(video_ur_list, indent=3, ensure_ascii=False))
        file.close()
    browser.close()


def save_searched_video_list_data(keyword: str):
    req_url = f"{tik_tok_prefix_url}/search/{keyword}"
    browser.get(req_url)
    time.sleep(3)
    login()
    with open(f"{file_save_path}/search/{keyword}/video_url_list.json", 'r', encoding='UTF-8') as file:
        video_list_json = file.read()
        video_list = json.loads(video_list_json)
        print(video_list)
    for video_url in video_list:
        video_id = get_video_id_from_url(video_url)
        save_single_work(video_id)


def save_single_work(video_id: str):
    print(f"开始存储视频:{video_id}")
    req_url = f"{tik_tok_prefix_url}/video/{video_id}"
    browser.get(req_url)
    browser.implicitly_wait(10)

    # 切换窗口
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])

    save_video_meta_data(video_id)
    save_comments_1(video_id)
    browser.close()


def save_video_meta_data(video_id: str):
    req_url = f"{tik_tok_prefix_url}/video/{video_id}"
    video_meta_data = {}
    video_meta_data["id"] = video_id
    video_meta_data["url"] = req_url

    title = browser.find_element(By.XPATH,
                                 "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[1]/div/h1/span[2]").text
    print(f'标题: {title}')
    video_meta_data["title"] = title

    favorite_num = browser.find_element(By.XPATH,
                                        "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[1]/span").text
    print(f"获赞: {favorite_num}")
    video_meta_data["favorite_num"] = favorite_num

    comment_num = browser.find_element(By.XPATH,
                                       "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[2]/span").text
    print(f"评论: {comment_num}")
    video_meta_data["comment_num"] = comment_num

    collect_num = browser.find_element(By.XPATH,
                                       "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[3]/span").text
    print(f"收藏: {collect_num}")
    video_meta_data["collect_num"] = collect_num

    release_time = browser.find_element(By.XPATH,
                                        "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[2]/span").text
    release_time = release_time[5:]
    print(f"发布时间: {release_time}")
    video_meta_data["release_time"] = release_time

    author_info = {}
    video_meta_data["author_info"] = author_info
    author_name = browser.find_element(By.XPATH,
                                       "//*[@id='root']/div/div[2]/div/div/div[2]/div/div[1]/div[2]/a/div/span/span/span/span/span").text
    print(f"作者: {author_name}")
    author_info["name"] = author_name

    author_main_page = browser.find_element(By.XPATH,
                                            "//*[@id='root']/div/div[2]/div/div/div[2]/div/div[1]/div[2]/a").get_attribute(
        "href")
    print(f"作者主页: {author_main_page}")
    author_info["main_page"] = author_main_page

    author_follower_num = browser.find_element(By.XPATH,
                                               "//*[@id='root']/div/div[2]/div/div/div[2]/div/div[1]/div[2]/p/span[2]").text
    print(f"作者粉丝: {author_follower_num}")
    author_info["follower_num"] = author_follower_num

    author_praise_num = browser.find_element(By.XPATH,
                                             "//*[@id='root']/div/div[2]/div/div/div[2]/div/div[1]/div[2]/p/span[4]").text
    print(f"作者获赞: {author_praise_num}")
    author_info["praise_num"] = author_praise_num

    file_path = f"{file_save_path}/work/{video_id}"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = 'metadata.json'

    with open(f"{file_path}/{file_name}", 'w', encoding='UTF-8') as file:
        file.write(json.dumps(video_meta_data, indent=3, ensure_ascii=False))
        file.close()
    return video_meta_data


def save_comments_1(video_id: str):
    comment_list = []

    i = 0

    while True:
        # browser.execute_script("arguments[0].scrollIntoView();", list[i])
        # user_name = list[i].find_elements_by_xpath("div/div[2]/div[1]/div[1]/div/a/span/span/span/span/span")[0].text
        comment_obj = find_element_by_xpath_silent(f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{i + 1}]')
        if comment_obj is None or comment_obj.text == "加载中":
            browser.execute_script('scroll(0,document.body.scrollHeight)')
            print(f"检测到评论暂未刷新，开始往下翻页，当前以加载{i + 1}条评论")
            time.sleep(3)

            search_btn = browser.find_element(By.XPATH,
                                              '//*[@id="douyin-header"]/header/div[2]/div[1]/div/div[2]/div/form')
            if search_btn.text == "结束":
                print(f"检测评论框输入了结束，结束评论获取")
                break
        else:
            comment_info = get_comment_info(i)

            i = i + 1
            comment_list.append(comment_info)

    file_path = f"{file_save_path}/work/{video_id}"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = 'comment_list.json'
    with open(f"{file_path}/{file_name}", 'w', encoding='UTF-8') as file:
        file.write(json.dumps(comment_list, indent=3, ensure_ascii=False))
        file.close()


def save_comments(video_id: str):
    comment_list = []
    handle_page_lazy_loading()

    comment_divs = browser.find_element(By.XPATH, "//*[@id='root']/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]")

    browser.execute_script("arguments[0].scrollIntoView();", comment_divs)
    list = comment_divs.find_elements_by_xpath('div')
    li_len = len(list)
    print(f"评论总数：{li_len}")
    i = 0

    while i < li_len - 2:
        # browser.execute_script("arguments[0].scrollIntoView();", list[i])
        # user_name = list[i].find_elements_by_xpath("div/div[2]/div[1]/div[1]/div/a/span/span/span/span/span")[0].text

        comment_info = get_comment_info(i)
        i = i + 1
        comment_list.append(comment_info)

    file_path = f"{file_save_path}/work/{video_id}"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = 'comment_list.json'
    with open(f"{file_path}/{file_name}", 'w', encoding='UTF-8') as file:
        file.write(json.dumps(comment_list, indent=3, ensure_ascii=False))
        file.close()


def get_comment_info(index):
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


def get_video_id_from_url(video_url: str):
    matcher = re.match(video_regex, video_url)
    return matcher.group(1)


def find_element_by_xpath_silent(xpath):
    try:
        element = browser.find_element(By.XPATH, xpath)
        return element
    except Exception as e:
        print(
            f'selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: "method":"xpath","selector":"{xpath}"')
        return None


if __name__ == '__main__':
    # save_single_work("7064526918795709730")
    # begin_search("屋顶光伏")
    save_searched_video_list_data("屋顶光伏")
