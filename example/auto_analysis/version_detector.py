#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import winreg
import re

def get_wechat_version_from_registry():
    """
    从注册表获取微信版本号
    """
    try:
        # 尝试打开微信的注册表项
        key_path = r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        # 遍历所有子键查找微信
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                try:
                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    if "微信" in display_name:
                        version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                        return version
                except:
                    pass
                finally:
                    winreg.CloseKey(subkey)
            except:
                continue
        
        # 如果在64位注册表下没找到，尝试32位注册表
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                try:
                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    if "微信" in display_name:
                        version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                        return version
                except:
                    pass
                finally:
                    winreg.CloseKey(subkey)
            except:
                continue
    except Exception as e:
        print(f"从注册表获取微信版本出错: {e}")
    
    return None

def get_wechat_version_from_file():
    """
    从微信安装目录获取版本号
    """
    try:
        # 尝试常见的微信安装路径
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\Tencent\WeChat\WeChat.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Tencent\WeChat\WeChat.exe"),
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
        ]
        
        # 检查每个可能的路径
        for path in possible_paths:
            if os.path.isfile(path):
                # 获取文件版本信息
                try:
                    # 使用PowerShell获取文件版本信息
                    cmd = f'powershell -command "(Get-Item \'{path}\').VersionInfo.FileVersion"'
                    result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                    if result:
                        return result
                except:
                    pass
                
                # 如果powershell方法失败，尝试使用wmic
                try:
                    # 先处理路径中的反斜杠
                    escaped_path = path.replace('\\', '\\\\')
                    cmd = f'wmic datafile where name="{escaped_path}" get Version /value'
                    result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                    version_match = re.search(r'Version=(.+)', result)
                    if version_match:
                        version = version_match.group(1)
                        return version
                except:
                    pass
    except Exception as e:
        print(f"从文件获取微信版本出错: {e}")
    
    return None

def detect_wechat_version():
    """
    检测系统安装的微信版本并返回主版本号(3或4)
    返回: 版本号和主版本类型 (full_version, major_version_type)
    """
    # 首先尝试从注册表获取
    version = get_wechat_version_from_registry()
    
    # 如果从注册表获取失败，尝试从文件获取
    if not version:
        version = get_wechat_version_from_file()
    
    if version:
        # 检查主版本号
        major_version = version.split('.')[0]
        if major_version == '3':
            return version, "3.x"
        elif major_version == '4':
            return version, "4.0"
        else:
            return version, "未知"
    
    return None, "未知"

if __name__ == "__main__":
    # 测试代码
    version, version_type = detect_wechat_version()
    if version:
        print(f"检测到微信版本: {version}")
        print(f"微信主版本类型: {version_type}")
    else:
        print("未检测到微信版本，请确认微信已安装") 