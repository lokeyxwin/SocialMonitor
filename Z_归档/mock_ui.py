import streamlit as st
import pandas as pd
import time
import random

# ==========================================
# 1. 页面配置与全局样式
# ==========================================
st.set_page_config(
    page_title="SocialMonitor 舆情雷达",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入一点 CSS 让界面更好看 (模拟专业系统的感觉)
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
    /* 侧边栏高亮颜色 */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 侧边栏导航 (Sidebar)
# ==========================================
with st.sidebar:
    st.title("📡 SocialMonitor")
    st.caption("v1.0.0 | 智能舆情监控系统")
    st.markdown("---")

    # 导航菜单
    page = st.radio(
        "功能导航",
        ["🔍 全网雷达 (Discovery)", "👥 监控对象 (Management)", "📊 舆情大盘 (Dashboard)", "⚙️ 系统状态 (System)"],
        index=0
    )

    st.markdown("---")
    # 全局筛选
    st.selectbox("🌍 赛道/分组过滤", ["全部赛道", "🧬 细胞存储", "🌿 中医大健康", "🤖 人工智能"])

    st.markdown("---")
    with st.expander("当前资源占用"):
        st.progress(45, text="内存占用: 45%")
        st.progress(12, text="CPU占用: 12%")

# ==========================================
# 3. 页面逻辑路由
# ==========================================

# --- 页面 1: 全网雷达 ---
if "Discovery" in page:
    st.title("🔍 全网账号雷达")
    st.markdown("输入关键词，从抖音/小红书的海量数据中挖掘潜在监控目标。")

    # 顶部搜索区
    col1, col2 = st.columns([4, 1])
    with col1:
        keyword = st.text_input("输入关键词", placeholder="例如：干细胞、免疫细胞、抗衰老...",
                                label_visibility="collapsed")
    with col2:
        search_btn = st.button("🚀 开始扫描", type="primary")

    # 模拟搜索结果
    if search_btn or st.session_state.get('has_searched'):
        st.session_state['has_searched'] = True

        # 模拟加载动画
        if search_btn:
            with st.spinner("正在调度爬虫节点 (Node-01) 抓取中..."):
                time.sleep(1.5)  # 假装在加载

        # 结果统计卡片
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("命中账号", "52 个")
        m2.metric("包含蓝V/企业", "8 个")
        m3.metric("平均粉丝数", "12.5w")
        m4.metric("覆盖平台", "抖音 / 小红书")

        st.subheader("📝 扫描结果")

        # 模拟数据
        data = {
            "已选": [False, False, True, False, False],
            "头像": ["👤", "👩‍⚕️", "🏥", "🧪", "🧘"],
            "账号名称": ["干细胞科普小助手", "李医生聊健康", "XX生物科技官方", "每日科研", "中医养生坊"],
            "平台": ["小红书", "抖音", "抖音", "小红书", "抖音"],
            "粉丝数": ["5.2w", "89w", "120w", "1.2w", "35w"],
            "简介": ["专注分享干细胞知识...", "三甲医院主任医师...", "细胞存储领航者...", "最新文献解读...",
                     "传承千年智慧..."],
            "状态": ["未入库", "未入库", "已在库", "未入库", "未入库"]
        }
        df = pd.DataFrame(data)

        # 可编辑表格
        edited_df = st.data_editor(
            df,
            column_config={
                "已选": st.column_config.CheckboxColumn(required=True),
                "头像": st.column_config.TextColumn(width="small"),
            },
            disabled=["头像", "账号名称", "平台", "粉丝数", "简介", "状态"],
            hide_index=True,
            use_container_width=True
        )

        col_act1, col_act2 = st.columns([1, 5])
        with col_act1:
            if st.button("📥 加入监控池"):
                st.toast("✅ 已成功将选中账号加入 [默认分组]！", icon="🎉")

# --- 页面 2: 监控对象管理 ---
elif "Management" in page:
    st.title("👥 监控资产管理")

    # 工具栏
    t1, t2, t3, t4 = st.columns([1, 1, 2, 4])
    t1.button("➕ 新增账号")
    t2.button("🗑 批量删除")
    t3.selectbox("批量操作", ["移动分组", "暂停监控", "强制刷新"], label_visibility="collapsed")

    # 标签页
    tab1, tab2, tab3 = st.tabs(["全部 (50)", "🟢 运行中 (45)", "🔴 异常/断更 (5)"])

    with tab1:
        # 模拟监控列表数据
        monitor_data = pd.DataFrame({
            "账号名称": ["丁香医生", "XX生物", "老爸评测", "干细胞前沿", "黑中介曝光"],
            "分组": ["科普", "竞品", "科普", "学术", "敏感"],
            "平台": ["抖音", "抖音", "抖音", "小红书", "小红书"],
            "上次抓取": ["10分钟前", "1小时前", "10分钟前", "3天前", "昨天"],
            "状态": ["正常", "正常", "正常", "⚠️ 断更", "❌ 登录失效"],
            "最新粉丝": [5002000, 120000, 3000000, 5000, 100]
        })

        st.dataframe(
            monitor_data,
            column_config={
                "状态": st.column_config.TextColumn(help="监控系统的运行状态"),
                "最新粉丝": st.column_config.NumberColumn(format="%d")
            },
            use_container_width=True,
            hide_index=True
        )

# --- 页面 3: 舆情大盘 ---
elif "Dashboard" in page:
    st.title("📊 舆情大盘 - 细胞行业")

    # 核心KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("监控覆盖粉丝总数", "1,203 万", "+5.2%")
    k2.metric("昨日全网声量(提及)", "5,432 条", "+12%")
    k3.metric("爆款视频数(>1w赞)", "15 个", "-2")
    k4.metric("负面预警", "3 条", "↑ 1", delta_color="inverse")

    st.markdown("---")

    # 图表区
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("📈 声量趋势 (近7天)")
        # 模拟图表数据
        chart_data = pd.DataFrame({
            '日期': pd.date_range(start='2026-01-24', periods=7),
            '全网声量': [4200, 4500, 3800, 5600, 5400, 6100, 5432],
            '负面评论': [120, 150, 100, 200, 180, 220, 150]
        }).set_index('日期')
        st.line_chart(chart_data, color=["#3b8ed0", "#e23670"])

    with c2:
        st.subheader("☁️ 关键词云")
        # 这里用Markdown模拟词云效果，实际你可以用图片
        st.info("💡 热门话题：\n\n #干细胞治疗 \n #免疫细胞 \n #抗衰老黑科技 \n #智商税 \n #生物科技")

        st.subheader("🎭 情感分布")
        st.progress(70, text="🟢 正向情绪 (70%)")
        st.progress(25, text="⚪ 中立情绪 (25%)")
        st.progress(5, text="🔴 负面情绪 (5%)")

    # 详情下钻
    st.subheader("🚨 负面舆情预警 (Top 3)")
    with st.expander("1. [抖音] 某用户：花了5万存细胞，结果取不出来... (情感分: -0.9)", expanded=True):
        st.write("**原文摘要**：这就是个骗局，大家千万别信...")
        st.caption("来源：视频评论区 | 时间：2小时前 | 互动：120赞")
        st.button("处理/忽略", key="btn_warn_1")

# --- 页面 4: 系统状态 ---
elif "System" in page:
    st.title("⚙️ 系统运维中心")

    col_sys1, col_sys2 = st.columns([1, 2])

    with col_sys1:
        st.subheader("服务健康度")
        st.success("🟢 调度器 (Scheduler): 运行中")
        st.success("🟢 爬虫节点 (Crawler-WinPC): 空闲")
        st.info("🔵 数据库 (MySQL): 连接数 5/100")
        st.warning("🟡 代理池 (Proxy): 剩余 23 个可用")

        st.markdown("### 紧急操作")
        if st.button("♻️ 重启调度器"):
            st.toast("指令已发送！")
        if st.button("🧹 清理临时缓存"):
            st.toast("缓存已清理")

    with col_sys2:
        st.subheader("📝 实时日志流")
        log_text = """
[10:24:01 INFO] Scheduler: 扫描到 3 个新任务，准备派发...
[10:24:02 INFO] Crawler-PC: 领取任务 Task-10086 (抓取主页: 丁香医生)
[10:24:05 INFO] Crawler-PC: 正在启动 Playwright...
[10:24:08 INFO] Crawler-PC: 页面加载完成，开始解析...
[10:24:12 SUCC] Crawler-PC: 抓取成功！获取粉丝数 5,002,120
[10:24:13 INFO] DB: 数据已写入 raw_profile_snapshot
[10:24:15 WARN] Analysis: 发现 1 条潜在负面评论，情感分 -0.85
        """
        st.code(log_text, language="bash")