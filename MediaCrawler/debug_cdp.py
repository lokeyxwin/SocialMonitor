# debug_cdp.py
from playwright.sync_api import sync_playwright


def test_connect():
    print("🔌 正在尝试连接 9222 端口...")
    try:
        with sync_playwright() as p:
            # 尝试直接连接你的"特工浏览器"
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ 连接成功！")

            # 看看连上的是不是你打开的那个网页
            context = browser.contexts[0]
            page = context.pages[0]
            print(f"📄 当前页面标题: {page.title()}")

            # 试着控制一下（让它跳个舞）
            print("💃 正在让浏览器跳转到百度...")
            page.goto("https://www.baidu.com")

    except Exception as e:
        print(f"❌ 连接失败，原因如下:\n{e}")


if __name__ == "__main__":
    test_connect()