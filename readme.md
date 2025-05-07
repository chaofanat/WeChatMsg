# 说明
## 出于兴趣fork此项目进行研究后，做出了一些调整，以便于更好的使用。
## 新增了一个使用示例用于生成微信社交关系图谱
效果大概是这样：
![image](https://github.com/user-attachments/assets/a7bea210-7419-4da9-af6b-471035c9691d)
![image](https://github.com/user-attachments/assets/ebf5d074-cc44-4485-ac6c-1c8c0d573638)

## 快速开始
环境准备：
- windows
- python3.10
- wechat已经登陆，且聊天记录完整（只能分析电脑端已有的聊天记录，电脑端不全的可以先从手机同步过来）
- git

1. 克隆项目
```shell
git clone https://github.com/chaofanat/WeChatMsg.git
```

2. 使用pip安装依赖项
```shell
pip install -r requirements.txt
```

3. 进入示例文件夹并运行文件

```bash
cd example/auto_analysis
python wechat_analyzer.py -t "2025-04-01,2025-05-01"
```


更多示例的详细说明参见[示例文档](https://github.com/chaofanat/WeChatMsg/blob/master/example/auto_analysis/README.md)







# DatabaseConnection 接口方法示例  （由AI阅读代码后整理，仅供参考）

DatabaseConnection是微信数据管理的核心类，它提供了一系列方法来访问和操作微信数据库。以下是主要方法的示例：

## 1. 获取联系人相关方法

### 获取所有联系人
```python
from wxManager import DatabaseConnection

db_dir = 'wxid_xxx/Msg'  # 微信3.x版本
# db_dir = 'wxid_xxx/db_storage'  # 微信4.0版本
db_version = 3  # 或者4，取决于微信版本

conn = DatabaseConnection(db_dir, db_version)
database = conn.get_interface()

# 获取所有联系人
contacts = database.get_contacts()
for contact in contacts[:5]:  # 只打印前5个联系人
    print(f"昵称: {contact.nickname}, 微信ID: {contact.wxid}")
```

### 通过微信ID查找联系人
```python
# 查找特定联系人
wxid = "wxid_example123"
contact = database.get_contact_by_username(wxid)
if contact:
    print(f"联系人信息: {contact.nickname}, 性别: {contact.gender}, 地区: {contact.region}")
```

### 获取群成员信息
```python
# 获取群成员信息
group_wxid = "12345678@chatroom"
members = database.get_chatroom_members(group_wxid)
print(f"{group_wxid} 有 {len(members)} 个成员")
for wxid, member in list(members.items())[:3]:  # 只打印前3个成员
    print(f"成员: {member.nickname}, 微信ID: {wxid}")
```

### 获取头像
```python
# 获取联系人头像
wxid = "wxid_example123"
avatar_buffer = database.get_avatar_buffer(wxid)
# 保存头像
with open(f"{wxid}_avatar.jpg", "wb") as f:
    f.write(avatar_buffer)
```

## 2. 获取聊天记录相关方法

### 获取与指定联系人的聊天记录
```python
import time
from datetime import datetime

# 获取与特定联系人的聊天记录
wxid = "wxid_example123"
# 设置时间范围
time_range = ("2023-01-01 00:00:00", "2023-12-31 23:59:59")

messages = database.get_messages(wxid, time_range)
for msg in messages[:5]:  # 只显示前5条消息
    print(f"时间: {datetime.fromtimestamp(msg.create_time)}, 发送者: {msg.from_id}")
    print(f"内容: {msg.content[:50]}...")  # 只显示前50个字符
    print("-" * 30)
```

### 按消息类型获取聊天记录
```python
from wxManager import MessageType

# 获取与特定联系人的图片消息
wxid = "wxid_example123"
image_messages = database.get_messages_by_type(wxid, MessageType.Image)
print(f"共有 {len(image_messages)} 条图片消息")
```

### 按关键词搜索消息
```python
# 关键词搜索
keyword = "项目"
wxid = "wxid_example123"
search_results = database.get_messages_by_keyword(wxid, keyword, num=10)
print(f"找到 {len(search_results)} 条包含关键词 '{keyword}' 的消息")
```

## 3. 媒体文件处理方法

### 获取图片
```python
# 处理图片消息
wxid = "wxid_example123"
messages = database.get_messages_by_type(wxid, MessageType.Image)
if messages:
    msg = messages[0]
    # 假设图片消息有content和bytesExtra属性
    image_path = database.get_image(msg.content, msg.bytesExtra, up_dir="./images")
    print(f"图片已保存到: {image_path}")
```

### 获取语音消息
```python
# 处理语音消息
wxid = "wxid_example123"
messages = database.get_messages_by_type(wxid, MessageType.Audio)
if messages:
    msg = messages[0]
    # 假设语音消息有reserved0属性
    audio_path = database.get_audio_path(msg.reserved0, "./voices")
    print(f"语音文件已保存到: {audio_path}")
```

### 获取表情包
```python
# 处理表情包
# 假设我们知道表情包的md5值
emoji_md5 = "abcdef1234567890"
emoji_path = database.get_emoji_path(emoji_md5, output_path="./emojis")
print(f"表情包已保存到: {emoji_path}")
```

## 4. 统计分析方法

### 获取聊天记录数量
```python
# 获取与特定联系人的聊天记录总数
wxid = "wxid_example123"
msg_count = database.get_messages_number(wxid)
print(f"与 {wxid} 的聊天记录总数: {msg_count}")
```

### 获取聊天频率最高的联系人
```python
# 获取聊天频率最高的前10个联系人
top_contacts = database.get_chatted_top_contacts(top_n=10)
print("聊天频率最高的联系人:")
for i, (wxid, count) in enumerate(top_contacts, 1):
    contact = database.get_contact_by_username(wxid)
    print(f"{i}. {contact.nickname}: {count}条消息")
```

### 按时间统计消息
```python
# 按小时统计发送消息数量
hourly_stats = database.get_send_messages_number_by_hour()
print("每小时发送消息数量:")
for hour, count in enumerate(hourly_stats):
    print(f"{hour}时: {count}条消息")
```

## 数据合并与导出

### 合并数据库
```python
# 合并其他数据库
other_db_path = "wxid_another/Msg"
database.merge(other_db_path)
print("数据库合并完成")
```

### 收藏夹项目获取
```python
# 获取收藏夹内容
time_range = ("2023-01-01 00:00:00", "2023-12-31 23:59:59")
favorites = database.get_favorite_items(time_range)
print(f"收藏夹项目数量: {len(favorites)}")
```

以上示例覆盖了DatabaseConnection提供的主要方法。这些方法可以帮助用户全面地获取、处理和分析微信的数据，包括联系人信息、聊天记录、媒体文件等。使用这些接口，用户可以自由地导出和利用自己的微信数据。
