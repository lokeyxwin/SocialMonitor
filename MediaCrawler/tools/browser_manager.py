# 文件路径: MediaCrawler/tools/browser_manager.py
import os
import sys
import time
import socket
import subprocess
import platform
from tools import utils

# ================= 配置 =================
DEBUG_PORT = 9222
# 数据存储目录 (相对于项目根目录)
DATA_DIR_NAME = "browser_data/chrome_profile"

# 不同系统的 Chrome 默认路径
CHROME_PATHS = {
    "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "Windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
}

def is_port_open(port):
    """检查端口是否被占用 (说明浏览器已经开着了)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_chrome_path():
    """根据系统自动找 Chrome"""
    system_name = platform.system()
    if system_name == "Darwin":
        if os.path.exists(CHROME_PATHS["Darwin"]):
            return CHROME_PATHS["Darwin"]
    elif system_name == "Windows":
        for path in CHROME_PATHS["Windows"]:
            if os.path.exists(path):
                return path
    return None

def init_browser_environment():
    """
    【核心逻辑】
    1. 检查端口 9222 是否通了？
    2. 通了 -> 说明你已经手动开了，直接返回，不重复开。
    3. 没通 -> 自动找到 Chrome，带上独立环境参数，启动它！
    """
    if is_port_open(DEBUG_PORT):
        utils.logger.info(f"✅ [机器管理员] 检测到浏览器已经在运行 (端口 {DEBUG_PORT})，直接接管...")
        return

    utils.logger.info("💤 [机器管理员] 浏览器未启动，正在寻找 Chrome...")
    
    chrome_path = find_chrome_path()
    if not chrome_path:
        utils.logger.error("❌ 未找到 Chrome 浏览器！请检查安装路径。")
        sys.exit(1)

    # 计算绝对路径，确保数据存到项目里
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_data_dir = os.path.join(project_root, DATA_DIR_NAME)
    
    # 自动创建目录
    if not os.path.exists(user_data_dir):
        try:
            os.makedirs(user_data_dir)
        except:
            pass

    utils.logger.info(f"🚀 [机器管理员] 正在启动独立环境浏览器...")
    utils.logger.info(f"📂 数据存档路径: {user_data_dir}")

    cmd = [
        chrome_path,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={user_data_dir}"
    ]

    try:
        # 启动进程
        if platform.system() == "Windows":
            subprocess.Popen(cmd, shell=False)
        else:
            # Mac 下使用 start_new_session=True 让它脱离当前终端独立运行
            # 这样你关掉 python 脚本，浏览器也不会崩
            subprocess.Popen(cmd, start_new_session=True)
            
        # 给它一点时间启动，防止立刻连接报错
        utils.logger.info("⏳ 等待浏览器启动 (3秒)...")
        time.sleep(3) 
        
    except Exception as e:
        utils.logger.error(f"❌ 启动浏览器失败: {e}")
        sys.exit(1)