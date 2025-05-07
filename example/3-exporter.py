#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time        : 2025/3/11 20:50 
@Author      : SiYuan 
@Email       : 863909694@qq.com 
@File        : wxManager-3-exporter.py
@Description : 
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

import time
from multiprocessing import freeze_support

from exporter.config import FileType
from exporter import HtmlExporter, TxtExporter, AiTxtExporter, DocxExporter, MarkdownExporter, ExcelExporter
from wxManager import DatabaseConnection, MessageType


def export():
    st = time.time()

    db_dir = 'wxid_cyy7k443xxcv22/Msg'  # 解析后的数据库路径
    db_version = 3  # 数据库版本，这里使用3，因为我们解析的是微信3.x版本

    wxid = 'wxid_b74e9m6nr74b21'  # 从上一步的联系人列表中选择的一个wxid
    output_dir = './data/'  # 输出文件夹

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    conn = DatabaseConnection(db_dir, db_version)  # 创建数据库连接
    database = conn.get_interface()  # 获取数据库接口

    contact = database.get_contact_by_username(wxid)  # 查找某个联系人
    if not contact:
        print(f"未找到联系人: {wxid}")
        return
    
    print(f"开始导出联系人: {contact.nickname} ({contact.wxid})")
    
    exporter = HtmlExporter(
        database,
        contact,
        output_dir=output_dir,
        type_=FileType.HTML,
        message_types=None,  # 要导出的消息类型，默认全导出
        time_range=['2020-01-01 00:00:00', '2035-03-12 00:00:00'],  # 要导出的日期范围，默认全导出
        group_members=None  # 指定导出群聊里某个或者几个群成员的聊天记录
    )

    exporter.start()
    et = time.time()
    print(f'导出完成，耗时：{et - st:.2f}s')


def batch_export(max_contacts=None):
    """
    批量导出HTML
    :param max_contacts: 最多导出的联系人数量，None表示导出所有
    :return:
    """
    st = time.time()

    db_dir = 'wxid_cyy7k443xxcv22/Msg'  # 解析后的数据库路径
    db_version = 3  # 数据库版本，这里使用3，因为我们解析的是微信3.x版本
    output_dir = './data/'  # 输出文件夹

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    conn = DatabaseConnection(db_dir, db_version)  # 创建数据库连接
    database = conn.get_interface()  # 获取数据库接口

    contacts = database.get_contacts()  # 获取所有联系人
    
    # 如果设置了最大联系人数量，则只取前N个联系人
    if max_contacts is not None and max_contacts > 0:
        contacts = contacts[:max_contacts]
        print(f"已设置最大导出联系人数量: {max_contacts}")
    
    total_contacts = len(contacts)
    print(f"找到总共 {total_contacts} 个联系人，开始批量导出...")
    
    success_count = 0
    skip_count = 0
    
    for i, contact in enumerate(contacts):
        try:
            print(f"[{i+1}/{total_contacts}] 正在导出联系人: {contact.nickname} ({contact.wxid})")
            exporter = HtmlExporter(
                database,
                contact,
                output_dir=output_dir,
                type_=FileType.HTML,
                message_types=None,  # 要导出所有消息类型
                time_range=['2020-01-01 00:00:00', '2035-03-12 00:00:00'],  # 要导出的日期范围，默认全导出
                group_members=None  # 指定导出群聊里某个或者几个群成员的聊天记录
            )

            exporter.start()
            success_count += 1
            print(f"成功导出 {contact.nickname} 的聊天记录")
        except Exception as e:
            print(f"导出 {contact.nickname} 的聊天记录时出错: {str(e)}")
            skip_count += 1
            continue
            
    et = time.time()
    print(f'批量导出完成，成功：{success_count}，跳过：{skip_count}，总耗时：{et - st:.2f}s')


def batch_export_by_fmt():
    """
    批量导出多种格式
    :return:
    """
    st = time.time()

    db_dir = 'wxid_cyy7k443xxcv22/Msg'  # 解析后的数据库路径
    db_version = 3  # 数据库版本，这里使用3，因为我们解析的是微信3.x版本

    wxid = 'wxid_b74e9m6nr74b21'  # 从上一步的联系人列表中选择的一个wxid
    output_dir = './data/'  # 输出文件夹

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    conn = DatabaseConnection(db_dir, db_version)  # 创建数据库连接
    database = conn.get_interface()  # 获取数据库接口

    contact = database.get_contact_by_username(wxid)  # 查找某个联系人
    if not contact:
        print(f"未找到联系人: {wxid}")
        return
    
    print(f"开始导出联系人: {contact.nickname} ({contact.wxid})")
    
    exporters = {
        FileType.HTML: HtmlExporter,
        FileType.TXT: TxtExporter,
        FileType.AI_TXT: AiTxtExporter,
        FileType.MARKDOWN: MarkdownExporter,
        FileType.XLSX: ExcelExporter,
        FileType.DOCX: DocxExporter
    }
    for file_type, exporter in exporters.items():
        print(f"导出格式: {file_type}")
        execute = exporter(
            database,
            contact,
            output_dir=output_dir,
            type_=file_type,
            message_types=None,  # 要导出的消息类型，默认全导出
            time_range=['2020-01-01 00:00:00', '2035-03-12 00:00:00'],  # 要导出的日期范围，默认全导出
            group_members=None  # 指定导出群聊里某个或者几个群成员的聊天记录
        )

        execute.start()
    et = time.time()
    print(f'多格式导出完成，耗时：{et - st:.2f}s')


if __name__ == '__main__':
    freeze_support()
    # export()  # 导出单个联系人
    batch_export(max_contacts=5)  # 批量导出前5个联系人，用于测试
    # batch_export_by_fmt()  # 导出单个联系人的多种格式
