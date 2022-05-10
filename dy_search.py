import json
import os
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import spider_util

file_path = os.path.dirname(__file__)
tik_tok_prefix_url = 'https://www.douyin.com'
file_save_path = file_path + r'/spider/'


def begin_search(browser: WebDriver, keyword: str, expect_search_result_num: int):
    req_url = f"{tik_tok_prefix_url}/search/{keyword}"

    browser.get(req_url)
    time.sleep(2)
    spider_util.dy_login(browser)

    i = 1

    video_ur_list = []
    while i <= expect_search_result_num:
        video = browser.find_element(By.XPATH, f'//*[@id="dark"]/div[2]/div/div[3]/div[1]/ul/li[{i}]')
        browser.execute_script("arguments[0].scrollIntoView();", video)

        WebDriverWait(browser, 30).until(lambda driver: driver.find_element(By.XPATH,
                                                                            f'//*[@id="dark"]/div[2]/div/div[3]/div[1]/ul/li[{i}]/div/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div[1]/xg-controls/xg-inner-controls/xg-right-grid/xg-icon[1]/a')
                                         )
        video_info_div = browser.find_element(By.XPATH,
                                              f'//*[@id="dark"]/div[2]/div/div[3]/div[1]/ul/li[{i}]/div/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div[1]/xg-controls/xg-inner-controls/xg-right-grid/xg-icon[1]/a')
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


def save_searched_video_list_data(browser: WebDriver, keyword: str):
    req_url = f"{tik_tok_prefix_url}/search/{keyword}"
    browser.get(req_url)
    time.sleep(3)
    spider_util.dy_login(browser)
    with open(f"{file_save_path}/search/{keyword}/video_url_list.json", 'r', encoding='UTF-8') as file:
        video_list_json = file.read()
        video_list = json.loads(video_list_json)
        print(video_list)
    for video_url in video_list:
        video_id = spider_util.get_video_id_from_url(video_url)
        video_file_path = f"{file_save_path}/work/{video_id}"
        if os.path.exists(video_file_path):
            print(f"视频:{video_id}已处理")
        else:
            save_single_work(browser, video_id)


def save_single_work(browser: WebDriver, video_id: str):
    print(f"开始存储视频:{video_id}")
    req_url = f"{tik_tok_prefix_url}/video/{video_id}"
    browser.get(req_url)
    browser.implicitly_wait(10)

    # 切换窗口
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])

    video_meta = save_video_meta_data(browser, video_id)
    comment_num_str = video_meta["comment_num"]
    comment_num = spider_util.str_to_int(comment_num_str)
    if comment_num > 100:
        save_comments_manually(browser, video_id)
    else:
        save_comments_automatically(browser, video_id)
    browser.close()


def save_video_meta_data(browser: WebDriver, video_id: str):
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


def save_comments_manually(browser: WebDriver, video_id: str):
    """
    存储评论，需要手动参与
    一般适用于评论很多的视频，因为自动化往下滚动加载会导致视频
    1. 通过在搜索框输入结束表示评论加载完毕
    2. 评价加载不动的时候要多动一动，抖音就会认为不是爬虫，然后就能加载动了
    :param browser:
    :param video_id:
    :return:
    """
    comment_list = []

    i = 0

    search_btn = browser.find_element(By.XPATH,
                                      '//*[@id="douyin-header"]/header/div[2]/div[1]/div/div[2]/div/form')

    while True:
        # browser.execute_script("arguments[0].scrollIntoView();", list[i])
        # user_name = list[i].find_elements_by_xpath("div/div[2]/div[1]/div[1]/div/a/span/span/span/span/span")[0].text
        comment_obj = spider_util.find_element_by_xpath_silent(browser,
            f'//*[@id="root"]/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]/div[{i + 1}]')
        if comment_obj is None or comment_obj.text == "加载中":
            browser.execute_script('scroll(0,document.body.scrollHeight)')
            print(f"检测到评论暂未刷新，开始往下翻页，当前已加载{i + 1}条评论")
            time.sleep(3)

            if search_btn.text == "结束":
                print(f"检测评论框输入了结束，结束评论获取")
                break
        else:
            comment_info = spider_util.get_comment_info(browser, i)

            i = i + 1
            comment_list.append(comment_info)

    file_path = f"{file_save_path}/work/{video_id}"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = 'comment_list.json'
    with open(f"{file_path}/{file_name}", 'w', encoding='UTF-8') as file:
        file.write(json.dumps(comment_list, indent=3, ensure_ascii=False))
        file.close()


def save_comments_automatically(browser: WebDriver, video_id: str):
    """
    自动化地存储评论
    1. 通过在搜索框输入结束表示评论加载完毕
    2. 评价加载不动的时候要多动一动，抖音就会认为不是爬虫，然后就能加载动了
    :param browser:
    :param video_id:
    :return:
    """
    comment_list = []
    spider_util.handle_page_lazy_loading(browser, 3)

    comment_divs = browser.find_element(By.XPATH, "//*[@id='root']/div/div[2]/div/div/div[1]/div[3]/div/div/div[4]")

    browser.execute_script("arguments[0].scrollIntoView();", comment_divs)
    list = comment_divs.find_elements_by_xpath('div')
    li_len = len(list)
    print(f"评论总数：{li_len}")
    i = 0

    while i < li_len - 2:
        # browser.execute_script("arguments[0].scrollIntoView();", list[i])
        # user_name = list[i].find_elements_by_xpath("div/div[2]/div[1]/div[1]/div/a/span/span/span/span/span")[0].text

        comment_info = spider_util.get_comment_info(browser, i)
        i = i + 1
        comment_list.append(comment_info)

    file_path = f"{file_save_path}/work/{video_id}"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = 'comment_list.json'
    with open(f"{file_path}/{file_name}", 'w', encoding='UTF-8') as file:
        file.write(json.dumps(comment_list, indent=3, ensure_ascii=False))
        file.close()



