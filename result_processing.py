import json
import os

import pandas as pd

def dy_work_json_to_excel(work_info_json_path, result_path):
    work_dir_list = os.listdir(work_info_json_path)
    for work_id in work_dir_list:
        print(f"处理作品： {work_id}")
        comment_list_file_path = f"{work_info_json_path}/{work_id}/comment_list.json"
        meta_data_file_path = f"{work_info_json_path}/{work_id}/metadata.json"

        comment_list = []
        metadata = {}

        with open(comment_list_file_path, "r", encoding='UTF-8') as cfile:
            comment_list_json_str = cfile.read()
            origin_commit_list = json.loads(comment_list_json_str)

        with open(meta_data_file_path, "r", encoding='UTF-8') as mfile:
            meta_data_json_str = mfile.read()
            origin_metadata = json.loads(meta_data_json_str)
            author_info = origin_metadata["author_info"]
            metadata["作品id"] = origin_metadata["id"]
            metadata["作品链接"] = origin_metadata["url"]
            metadata["作品标题"] = origin_metadata["title"]
            metadata["作品点赞数"] = origin_metadata["favorite_num"]
            metadata["作品评论数"] = origin_metadata["comment_num"]
            metadata["作品发布时间"] = origin_metadata["release_time"]
            metadata["作者名字"] = author_info["name"]
            metadata["作者主页"] = author_info["main_page"]
            metadata["作者粉丝数"] = author_info["follower_num"]
            metadata["作者获赞数"] = author_info["praise_num"]

            del origin_metadata["author_info"]

        for origin_comment_info in origin_commit_list:
            comment_info = {}
            for key in metadata:
                comment_info[key] = metadata[key]
            comment_info["评论用户名"] = origin_comment_info.get("user_name")
            comment_info["评论用户主页"] = origin_comment_info.get("main_page")
            comment_info["评论时间"] = origin_comment_info.get("comment_time")
            comment_info["评论内容"] = origin_comment_info.get("comment_text")
            comment_info["评论被赞数"] = origin_comment_info.get("praise_num")
            comment_list.append(comment_info)

        save_comment_info_to_excel(result_path, comment_list, work_id)

def save_comment_info_to_excel(result_path, comment_list, work_id,):
    if len(comment_list)==0:
        print(f"作品：{work_id}无评论，跳过")
        return
    result={}
    for key in comment_list[0]:
        result[key]=[]

    for comment_info in comment_list:
        for key in result:
            result[key].append(comment_info.get(key,""))

    df = pd.DataFrame(result)
    with pd.ExcelWriter(result_path, mode='a', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=work_id)
        print(f"作品：{work_id}存储成功")


if __name__ == '__main__':
    dy_work_json_to_excel(os.path.dirname(__file__) + r'/spider/work', os.path.dirname(__file__) + r'/spider/result/work.xlsx')
