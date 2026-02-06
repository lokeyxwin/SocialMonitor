import os
import sys
import subprocess
import platform

# ================= 配置区域 =================
# 定义不同系统的 Chrome 默认安装路径
# 如果你的 Chrome 安装在非常规位置，请手动修改这里
CHROME_PATHS = {
    "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "Windows": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe") # 用户目录安装
    ]
}

# 端口号
DEBUG_PORT = "9222"
# 数据存储目录名称 (会自动创建在当前脚本同级目录下)
DATA_DIR_NAME = "browser_data/chrome_profile"

def main():
    # 1. 检测操作系统
    system_name = platform.system()
    print(f"🖥️  检测到操作系统: {system_name}")

    # 2. 确定 Chrome 可执行文件路径
    chrome_path = None
    if system_name == "Darwin": # Mac
        if os.path.exists(CHROME_PATHS["Darwin"]):
            chrome_path = CHROME_PATHS["Darwin"]
    elif system_name == "Windows": # PC
        for path in CHROME_PATHS["Windows"]:
            if os.path.exists(path):
                chrome_path = path
                break
    
    if not chrome_path:
        print("❌ 未找到 Chrome 浏览器！")
        print("请检查是否安装了 Chrome，或者手动修改脚本中的 CHROME_PATHS 路径。")
        input("按回车键退出...")
        return

    # 3. 确定用户数据目录 (核心：确保它是独立的)
    # 获取当前脚本所在的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(current_dir, DATA_DIR_NAME)
    
    # 如果目录不存在，自动创建（防止报错，虽然 Chrome 也会自己建）
    if not os.path.exists(user_data_dir):
        try:
            os.makedirs(user_data_dir)
        except OSError:
            pass # 忽略创建错误，交给 Chrome 处理

    print(f"📂 浏览器独立数据目录: {user_data_dir}")
    print(f"🔧 调试端口: {DEBUG_PORT}")
    print(f"🚀 正在启动爬虫专用浏览器...")

    # 4. 构造启动命令
    cmd = [
        chrome_path,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={user_data_dir}"
    ]

    try:
        # 5. 启动进程 (非阻塞模式，脚本运行完不关闭浏览器)
        if system_name == "Windows":
            # Windows 下使用 Popen 并不等待
            subprocess.Popen(cmd, shell=False)
        else:
            # Mac/Linux 下
            subprocess.Popen(cmd, start_new_session=True)
            
        print("\n✅ 启动成功！")
        print("------------------------------------------------")
        print("1. 这是一个【独立】的浏览器窗口，和你的主浏览器互不干扰。")
        print("2. 扫码登录后，Cookie 会自动保存在项目目录下。")
        print("3. 请勿关闭此黑框(如果是Windows)，或者直接最小化。")
        print("------------------------------------------------")

    except Exception as e:
        print(f"❌ 启动发生错误: {e}")

if __name__ == "__main__":
    main()