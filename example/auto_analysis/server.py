#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os
import sys
import webbrowser
import shutil
import argparse

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)


def copy_template_files(output_dir=''):
    """
    复制HTML模板文件到输出目录
    """
    # 模板路径
    template_dir = os.path.join(current_dir, 'templates')
    
    # 目标文件
    files_to_copy = {
        'wechat_graph.html': 'wechat_relationship_graph.html',
    }
    
    # 如果output_dir为空，则使用当前目录
    if not output_dir:
        output_dir = os.getcwd()
        
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 复制模板文件
    for src_name, dest_name in files_to_copy.items():
        src_path = os.path.join(template_dir, src_name)
        dest_path = os.path.join(output_dir, dest_name)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"已复制模板文件: {dest_path}")
        else:
            print(f"警告: 模板文件不存在: {src_path}")
    
    # 检查是否需要复制 echarts.min.js
    echarts_src = os.path.join(template_dir, 'echarts.min.js')
    echarts_dest = os.path.join(output_dir, 'echarts.min.js')
    
    if os.path.exists(echarts_src):
        shutil.copy2(echarts_src, echarts_dest)
        print(f"已复制ECharts库: {echarts_dest}")
    else:
        # 尝试从项目根目录查找
        root_echarts = os.path.join(root_dir, 'echarts.min.js')
        if os.path.exists(root_echarts):
            shutil.copy2(root_echarts, echarts_dest)
            print(f"已复制ECharts库: {echarts_dest}")
        else:
            print("警告: 未找到ECharts库文件，可能导致图表无法正常显示")


class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """
    自定义HTTP处理程序，支持默认访问社交关系图谱页面
    """
    def do_GET(self):
        # 如果请求根路径，重定向到社交关系图谱页面
        if self.path == '/':
            self.path = '/wechat_relationship_graph.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def start_server(data_dir, port=8000, open_browser=True):
    """
    启动HTTP服务器
    
    Args:
        data_dir: 数据目录，包含JSON文件和HTML模板
        port: 服务器端口号
        open_browser: 是否自动打开浏览器
    """
    # 切换到数据目录
    os.chdir(data_dir)
    
    # 创建处理程序
    handler = CustomHTTPHandler
    
    try:
        # 创建服务器
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"服务器启动在 http://localhost:{port}/")
            print(f"请访问 http://localhost:{port}/wechat_relationship_graph.html 查看社交关系图谱")
            print("按 Ctrl+C 关闭服务器")
            
            # 自动打开浏览器
            if open_browser:
                webbrowser.open(f"http://localhost:{port}/wechat_relationship_graph.html")
                
            # 启动服务器
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭")
    except OSError as e:
        if e.errno == 10048:  # Windows系统端口被占用的错误码
            print(f"错误: 端口 {port} 已被占用，尝试使用端口 {port + 1}")
            start_server(data_dir, port + 1, open_browser)  # 尝试下一个端口
        else:
            print(f"启动服务器时出错: {e}")


def serve(data_dir=None, port=8000, open_browser=True):
    """
    启动服务器查看社交关系图谱
    
    Args:
        data_dir: 数据目录，如果为None则使用当前目录
        port: 服务器端口号
        open_browser: 是否自动打开浏览器
    """
    # 如果未指定数据目录，使用当前目录
    if data_dir is None:
        data_dir = os.getcwd()
    
    # 检查数据文件是否存在
    json_file = os.path.join(data_dir, 'chat_data.json')
    if not os.path.exists(json_file):
        print(f"错误: 数据文件不存在: {json_file}")
        return False
    
    # 复制模板文件
    copy_template_files(data_dir)
    
    # 启动服务器
    start_server(data_dir, port, open_browser)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动HTTP服务器查看微信社交关系图谱")
    parser.add_argument("-d", "--data-dir", type=str, default=None, help="数据目录 (默认: 当前目录)")
    parser.add_argument("-p", "--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    
    args = parser.parse_args()
    
    serve(args.data_dir, args.port, not args.no_browser) 