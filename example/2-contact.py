#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2025/3/11 20:46 
@Author      : SiYuan 
@Email       : 863909694@qq.com 
@File        : wxManager-2-contact.py 
@Description : 
"""
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

import time

from wxManager import DatabaseConnection

# 根据上一步的结果设置
db_dir = 'wxid_cyy7k443xxcv22/Msg'  # 第一步解析后的数据库路径
db_version = 3  # 数据库版本，4 or 3，这里使用3，因为我们在上一步解析的是微信3.x版本

conn = DatabaseConnection(db_dir, db_version)  # 创建数据库连接
database = conn.get_interface()  # 获取数据库接口

st = time.time()
cnt = 0
contacts = database.get_contacts()
for contact in contacts:
    print(contact)
    contact.small_head_img_blog = database.get_avatar_buffer(contact.wxid)
    cnt += 1
    if contact.is_chatroom:
        print('*' * 80)
        print(contact)
        chatroom_members = database.get_chatroom_members(contact.wxid)
        print(contact.wxid, '群成员个数：', len(chatroom_members))
        for wxid, chatroom_member in chatroom_members.items():
            chatroom_member.small_head_img_blog = database.get_avatar_buffer(wxid)
            print(chatroom_member)
            cnt += 1

et = time.time()

print(f'联系人个数：{cnt} 耗时：{et - st:.2f}s')
