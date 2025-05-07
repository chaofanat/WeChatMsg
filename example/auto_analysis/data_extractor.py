#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import math
import colorsys
import datetime
from typing import Tuple, List, Dict, Any

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

from wxManager import DatabaseConnection, Me
from wxManager.decrypt import decrypt_v3, decrypt_v4, get_info_v3, get_info_v4


def decrypt_database(version_type="3.x"):
    """
    根据微信版本类型解密数据库
    
    Args:
        version_type: 微信版本类型，可选值 "3.x" 或 "4.0"
        
    Returns:
        解密后的数据库路径和数据库版本
    """
    print(f"开始解密微信{version_type}版本的数据库...")
    
    try:
        if version_type == "3.x":
            # 加载版本列表
            version_list_path = os.path.join(root_dir, 'wxManager/decrypt/version_list.json')
            with open(version_list_path, "r", encoding="utf-8") as f:
                version_list = json.loads(f.read())
                
            # 获取微信信息
            wx_info_list = get_info_v3(version_list)
            if not wx_info_list:
                print("未找到微信信息，请确保微信已登录")
                return None, None
                
            wx_info = wx_info_list[0]  # 使用第一个微信账号
            print(f"找到微信账号: {wx_info.nick_name} ({wx_info.wxid})")
            
            # 初始化Me对象
            me = Me()
            me.wx_dir = wx_info.wx_dir
            me.wxid = wx_info.wxid
            me.name = wx_info.nick_name
            
            # 设置输出目录
            output_dir = wx_info.wxid
            key = wx_info.key
            
            if not key:
                print('错误: 未找到密钥，请重启微信后再试')
                return None, None
                
            # 解密数据库
            decrypt_v3.decrypt_db_files(key, src_dir=wx_info.wx_dir, dest_dir=output_dir)
            
            # 保存账号信息
            info_data = me.to_json()
            info_path = os.path.join(output_dir, 'Msg', 'info.json')
            os.makedirs(os.path.dirname(info_path), exist_ok=True)
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(info_data, f, ensure_ascii=False, indent=4)
                
            print(f"数据库解密成功，在{os.path.join(output_dir, 'Msg')}路径下")
            return os.path.join(output_dir, 'Msg'), 3
            
        elif version_type == "4.0":
            # 获取微信信息
            wx_info_list = get_info_v4()
            if not wx_info_list:
                print("未找到微信信息，请确保微信已登录")
                return None, None
                
            wx_info = wx_info_list[0]  # 使用第一个微信账号
            print(f"找到微信账号: {wx_info.nick_name} ({wx_info.wxid})")
            
            # 初始化Me对象
            me = Me()
            me.wx_dir = wx_info.wx_dir
            me.wxid = wx_info.wxid
            me.name = wx_info.nick_name
            
            # 设置输出目录
            output_dir = wx_info.wxid
            key = wx_info.key
            
            if not key:
                print('错误: 未找到密钥，请重启微信后再试')
                return None, None
                
            # 解密数据库
            decrypt_v4.decrypt_db_files(key, src_dir=wx_info.wx_dir, dest_dir=output_dir)
            
            # 保存账号信息
            info_data = me.to_json()
            info_path = os.path.join(output_dir, 'db_storage', 'info.json')
            os.makedirs(os.path.dirname(info_path), exist_ok=True)
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(info_data, f, ensure_ascii=False, indent=4)
                
            print(f"数据库解密成功，在{os.path.join(output_dir, 'db_storage')}路径下")
            return os.path.join(output_dir, 'db_storage'), 4
        
        else:
            print(f"不支持的微信版本类型: {version_type}")
            return None, None
            
    except Exception as e:
        print(f"解密数据库时出错: {str(e)}")
        return None, None


def get_chat_data(db_dir, db_version=3, time_range=(datetime.datetime(2010, 1, 1), datetime.datetime.now())):
    """
    从微信数据库获取聊天数据并生成统计
    
    Args:
        db_dir: 数据库目录
        db_version: 数据库版本
        time_range: 时间范围
        
    Returns:
        聊天数据列表
    """
    try:
        # 创建数据库连接
        conn = DatabaseConnection(db_dir, db_version)
        database = conn.get_interface()
        
        # 获取联系人列表
        contacts = database.get_contacts()
        
        # 计算每个联系人的消息统计
        chat_data = []
        try:
            my_id = database.me.wxid  # 尝试通过me属性获取
        except:
            my_id = None  # 如果获取失败，则设置为None
        
        print(f"开始处理联系人数据，共 {len(contacts)} 个联系人...")
        
        # 进度计数
        count = 0
        for contact in contacts:
            count += 1
            if count % 50 == 0:
                print(f"已处理 {count}/{len(contacts)} 个联系人...")
                
            # 跳过自己
            if contact.wxid == my_id:
                continue
                
            # 获取聊天记录
            messages = database.get_messages(contact.wxid, time_range)
            
            if not messages:
                contact_data = {
                    'wxid': contact.wxid,
                    'nickname': contact.nickname or contact.remark or contact.wxid,
                    'total_count': 0,
                    'my_count': 0,
                    'other_count': 0,
                    'is_chatroom': 1 if contact.wxid.endswith('@chatroom') else 0,
                    'send_ratio': 0,
                    'interaction_score': 0
                }
                chat_data.append(contact_data)
                continue
                
            # 计算消息统计
            total_count = len(messages)
            my_count = sum(1 for msg in messages if msg.is_sender)
            other_count = total_count - my_count
            
            # 计算发送比例
            send_ratio = my_count / total_count if total_count > 0 else 0
            
            # 创建联系人数据
            contact_data = {
                'wxid': contact.wxid,
                'nickname': contact.nickname or contact.remark or contact.wxid,
                'total_count': total_count,
                'my_count': my_count,
                'other_count': other_count,
                'is_chatroom': 1 if contact.wxid.endswith('@chatroom') else 0,
                'send_ratio': send_ratio
            }
            
            # 计算互动指数
            interaction_score = calculate_interaction_score(contact_data)
            contact_data['interaction_score'] = interaction_score
            
            chat_data.append(contact_data)
        
        print(f"数据处理完成，共 {len(chat_data)} 个联系人")
        return chat_data
        
    except Exception as e:
        print(f"从数据库获取聊天数据时出错: {str(e)}")
        return None


def calculate_interaction_score(row):
    """
    计算社交互动指数，衡量社交关系的远近
    
    算法说明:
    1. 消息总量权重: 消息越多，关系越近
    2. 双向互动率: 发送/接收比例越接近1:1，关系越平衡
    3. 单向通信差异: 区分我发送和对方发送的单向情况
    4. 群聊调整: 对群聊关系进行适当调整
    """
    total_msgs = row['total_count']
    my_msgs = row['my_count']
    other_msgs = row['other_count']
    is_group = row['is_chatroom']
    
    # 基础分 - 消息总量的对数，避免大群聊过度主导
    base_score = math.log(total_msgs + 1) * 10
    
    # 互动平衡度 (0-1) - 值越接近1表示互动越平衡
    if total_msgs > 0:
        if my_msgs == 0 and other_msgs > 0:
            # 只有对方发送消息（如公众号、服务号）
            # 根据消息数量给予一定权重，但低于双向通信
            balance = 0.15 + min(0.15, 0.05 * math.log(other_msgs + 1))
        elif other_msgs == 0 and my_msgs > 0:
            # 只有我发送消息，表示我比较关注但对方不太响应
            balance = 0.25 + min(0.15, 0.05 * math.log(my_msgs + 1))
        elif my_msgs > 0 and other_msgs > 0:
            # 双向通信，计算平衡度
            ratio = min(my_msgs, other_msgs) / max(my_msgs, other_msgs)
            balance = 0.5 + ratio * 0.5  # 将范围调整为0.5-1.0
        else:
            # 无消息交互（理论上不会出现这种情况）
            balance = 0
    else:
        balance = 0
    
    # 群聊调整
    if is_group:
        # 群聊中发言比例低，关系可能较远
        group_factor = 0.7  # 群聊关系权重
        
        # 在群里发言比例
        speak_ratio = my_msgs / total_msgs if total_msgs > 0 else 0
        
        # 根据在群里的发言比例调整关系近度
        if speak_ratio > 0.1:  # 积极参与群聊
            group_factor = 0.9
        elif speak_ratio > 0.05:  # 中等参与
            group_factor = 0.8
    else:
        # 一对一聊天
        group_factor = 1.0
    
    # 最终分数计算
    final_score = base_score * balance * group_factor
    
    # 限制分数在0-100之间
    return min(100, max(0, final_score))


def generate_echarts_data(data, time_range):
    """
    生成ECharts图表所需的数据
    """
    # 生成图例数据
    legendData = ["我", "好友", "群聊", "服务号/订阅号"]
    
    # 节点分类
    categoriesData = [{"name": "我"}, {"name": "好友"}, {"name": "群聊"}, {"name": "服务号/订阅号"}]
    
    # 节点数据
    nodesData = []
    
    # 连接数据
    linksData = []
    
    # 节点详情数据
    nodeDetails = [{
        'id': item['wxid'],
        'name': item['nickname'],
        'total_msgs': item['total_count'],
        'sent_msgs': item['my_count'],
        'received_msgs': item['other_count'],
        'is_group': bool(item['is_chatroom']),
        'send_ratio': item['send_ratio'],
        'interaction_score': item['interaction_score']
    } for item in data]
    
    # 创建中心节点（我）
    me_node = {
        "id": "me",
        "name": "我",
        "symbolSize": 50,
        "category": 0,
        "value": 100,
        "x": 0,
        "y": 0,
        "fixed": True,
        "itemStyle": {"color": "#FF4500"}
    }
    nodesData.append(me_node)
    
    # 根据互动指数计算节点颜色
    max_score = max(item['interaction_score'] for item in data) if data else 50
    
    for item in data:
        wxid = item['wxid']
        name = item['nickname']
        is_group = item['is_chatroom']
        interaction_score = item['interaction_score']
        
        # 决定节点类别
        category = 0  # 默认为0（我）
        if wxid.startswith('gh_'):
            category = 3  # 服务号/订阅号
        elif wxid.endswith('@chatroom'):
            category = 2  # 群聊
        else:
            category = 1  # 好友
            
        # 计算节点大小（基于消息总量）
        if is_group:
            # 群聊节点适当放大
            symbol_size = 35 + min(15, math.log(item['total_count'] + 1) * 2)
        else:
            symbol_size = 15 + min(25, math.log(item['total_count'] + 1) * 3)
            
        # 计算节点颜色（基于互动指数）
        # 使用从蓝色到紫色到红色的渐变
        normalized_score = interaction_score / max_score
        
        # 颜色计算 - 使用HSL色彩空间
        # 从240度(蓝色)到300度(紫色)到360/0度(红色)
        if normalized_score <= 0.5:
            # 蓝到紫 (240到300度)
            hue = 240 + normalized_score * 2 * 60
        else:
            # 紫到红 (300到360度)
            hue = 300 + (normalized_score - 0.5) * 2 * 60
            
        # 确保色相在0-360范围内
        hue = hue % 360
        
        # 转换HSL到RGB
        rgb = colorsys.hls_to_rgb(hue/360, 0.5, 1.0)
        
        # 转换为RGB字符串
        color = f"rgb({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)})"
            
        # 创建节点
        node = {
            "id": wxid,
            "name": name,
            "symbolSize": symbol_size,
            "category": category,
            "value": interaction_score,
            "itemStyle": {"color": color}
        }
        nodesData.append(node)
        
        # 创建到中心节点的连接
        link = {
            "source": "me",
            "target": wxid,
            "value": interaction_score,
            "lineStyle": {
                "width": interaction_score / 10,  # 连线宽度
                "opacity": interaction_score / 100  # 连线透明度
            }
        }
        linksData.append(link)
    
    # 将datetime对象转换为字符串以便JSON序列化
    formatted_time_range = []
    if time_range:
        for dt in time_range:
            if isinstance(dt, datetime.datetime):
                formatted_time_range.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                formatted_time_range.append(str(dt))
    
    return {
        "legendData": legendData,
        "nodesData": nodesData, 
        "linksData": linksData,
        "categoriesData": categoriesData,
        "nodeDetails": nodeDetails,
        "time_range": formatted_time_range
    }


def extract_and_generate_json(db_dir, db_version, 
                             time_range=(datetime.datetime(2010, 1, 1), datetime.datetime.now()),
                             max_contacts=1000,
                             output_file='chat_data.json'):
    """
    从数据库提取数据并生成JSON文件
    
    Args:
        db_dir: 数据库目录
        db_version: 数据库版本
        time_range: 时间范围
        max_contacts: 最大联系人数量
        output_file: 输出文件路径
        
    Returns:
        是否成功
    """
    # 获取聊天数据
    print(f"正在从数据库{db_dir}获取聊天数据...")
    data = get_chat_data(db_dir, db_version, time_range)
    
    if data:
        # 筛选活跃联系人（至少有0条消息）
        active_contacts = [contact for contact in data if contact['total_count'] >= 0]
        
        # 按互动指数排序
        sorted_contacts = sorted(active_contacts, key=lambda x: x['interaction_score'], reverse=True)
        
        # 限制联系人数量（避免图表过于拥挤）
        if len(sorted_contacts) > max_contacts:
            print(f"发现{len(sorted_contacts)}个联系人，限制为最活跃的{max_contacts}个")
            sorted_contacts = sorted_contacts[:max_contacts]
        
        # 生成ECharts数据
        echarts_data = generate_echarts_data(sorted_contacts, time_range)
        
        # 输出JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(echarts_data, f, ensure_ascii=False, indent=2)
        print(f"JSON数据已保存到: {os.path.abspath(output_file)}")
        print(f"共生成{len(sorted_contacts)}个联系人的社交关系数据")
        return True
    else:
        print("获取数据失败，请检查数据库路径是否正确")
        return False


if __name__ == "__main__":
    # 测试代码
    # 解密数据库
    db_dir, db_version = decrypt_database("3.x")
    
    if db_dir and db_version:
        # 提取数据并生成JSON
        time_range = (datetime.datetime(2023, 1, 1), datetime.datetime.now())
        extract_and_generate_json(db_dir, db_version, time_range) 