#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信社交关系图谱分析器

自动检测系统微信版本，解密数据库，提取聊天数据，生成社交关系图谱。

用法:
    python wechat_analyzer.py [选项]

选项:
    -h, --help           显示帮助信息
    -t, --time-range     设置时间范围，格式: YYYY-MM-DD,YYYY-MM-DD
    -o, --output-dir     设置输出目录
    -p, --port           设置服务器端口（默认: 8000）
    --no-browser         不自动打开浏览器
    --max-contacts       最大联系人数量（默认: 1000）
    --no-server          仅生成数据，不启动服务器
"""

import os
import sys
import argparse
import datetime
import time
from multiprocessing import freeze_support

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# 导入自定义模块
from version_detector import detect_wechat_version
from data_extractor import decrypt_database, extract_and_generate_json
from server import serve


def parse_time_range(time_range_str):
    """
    解析命令行传入的时间范围字符串
    
    格式: YYYY-MM-DD,YYYY-MM-DD
    """
    if not time_range_str:
        # 默认为过去一年
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=365)
        return (start_time, end_time)
        
    try:
        parts = time_range_str.split(',')
        if len(parts) != 2:
            print("错误：时间范围格式不正确，应为 YYYY-MM-DD,YYYY-MM-DD")
            return None
            
        start_date_str, end_date_str = parts
        start_time = datetime.datetime.strptime(start_date_str.strip(), '%Y-%m-%d')
        end_time = datetime.datetime.strptime(end_date_str.strip(), '%Y-%m-%d')
        
        # 确保结束时间为当天的23:59:59
        end_time = end_time.replace(hour=23, minute=59, second=59)
        
        return (start_time, end_time)
    except ValueError as e:
        print(f"错误：解析时间范围失败 - {str(e)}")
        return None


def initialize_output_dir(output_dir=None):
    """
    初始化输出目录
    """
    if not output_dir:
        # 使用时间戳创建唯一目录
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(os.getcwd(), f'wechat_analysis_{timestamp}')
        
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir


def main():
    """
    主函数，程序入口
    """
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='微信社交关系图谱分析器')
    parser.add_argument('-t', '--time-range', type=str, default=None, 
                        help='设置时间范围，格式: YYYY-MM-DD,YYYY-MM-DD')
    parser.add_argument('-o', '--output-dir', type=str, default=None,
                        help='设置输出目录')
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help='设置服务器端口（默认: 8000）')
    parser.add_argument('--no-browser', action='store_true',
                        help='不自动打开浏览器')
    parser.add_argument('--max-contacts', type=int, default=1000,
                        help='最大联系人数量（默认: 1000）')
    parser.add_argument('--no-server', action='store_true',
                        help='仅生成数据，不启动服务器')
    
    args = parser.parse_args()
    
    # 解析时间范围
    time_range = parse_time_range(args.time_range)
    if time_range is None:
        return
    
    # 初始化输出目录
    output_dir = initialize_output_dir(args.output_dir)
    print(f"输出目录: {output_dir}")
    
    # 检测微信版本
    print("\n步骤1: 检测微信版本")
    print("=" * 50)
    version, version_type = detect_wechat_version()
    
    if not version:
        print("错误: 未检测到微信版本，请确保微信已安装并处于登录状态")
        return
        
    print(f"检测到微信版本: {version} (类型: {version_type})")
    
    # 解密数据库
    print("\n步骤2: 解密微信数据库")
    print("=" * 50)
    db_dir, db_version = decrypt_database(version_type)
    
    if not db_dir or not db_version:
        print("错误: 解密数据库失败")
        return
    
    # 提取数据并生成JSON
    print("\n步骤3: 提取聊天数据并生成JSON")
    print("=" * 50)
    json_file = os.path.join(output_dir, 'chat_data.json')
    success = extract_and_generate_json(
        db_dir=db_dir,
        db_version=db_version,
        time_range=time_range,
        max_contacts=args.max_contacts,
        output_file=json_file
    )
    
    if not success:
        print("错误: 生成JSON数据失败")
        return
    
    print(f"JSON数据已保存到: {json_file}")
    
    # 启动HTTP服务器
    if not args.no_server:
        print("\n步骤4: 启动HTTP服务器")
        print("=" * 50)
        print(f"启动服务器查看社交关系图谱，端口: {args.port}")
        serve(
            data_dir=output_dir,
            port=args.port,
            open_browser=not args.no_browser
        )
    else:
        print("\n数据生成完成，未启动服务器")
        print(f"可以手动启动服务器: python server.py -d {output_dir}")


if __name__ == '__main__':
    freeze_support()  # Windows下多进程支持
    main() 