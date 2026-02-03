import sys
import os

# --- 核心修复：强行把项目根目录加入 Python 搜索路径 ---
# 获取当前文件 (app.py) 的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录 (即 05_socialmonitor)
# 逻辑是：web -> social_monitor -> 05_socialmonitor (往上跳两级)
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
# 把根目录加到 sys.path 里，这样 Python 就能找到 'social_monitor' 包了
sys.path.append(project_root)

# social_monitor/web/app.py
import streamlit as st
# 引用我们拆分出去的模块
from social_monitor.web.components.sidebar import render_sidebar
from social_monitor.web.views import discovery, management

# 1. 全局配置
st.set_page_config(page_title="SocialMonitor", layout="wide")

# 2. 渲染左侧导航 (获取用户选了哪个)
selected_page = render_sidebar()

# 3. 路由控制 (大管家分发任务)
if selected_page == "全网雷达":
    discovery.render()  # 👈 只有这里会变，去执行 discovery.py 里的代码
elif selected_page == "监控对象":
    management.render()
elif selected_page == "舆情大盘":
    dashboard.render()
elif selected_page == "系统状态":
    system.render()