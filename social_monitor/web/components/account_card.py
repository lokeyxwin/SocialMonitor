# social_monitor/web/components/account_card.py
import streamlit as st


def render_tag(text, color="blue"):
    """
    辅助函数：生成带颜色的标签 HTML (仿新红样式)
    colors: blue, green, red, gray
    """
    colors = {
        "blue": ("color: #1677ff; background: #e6f4ff; border-color: #91caff;", "🔵"),
        "green": ("color: #52c41a; background: #f6ffed; border-color: #b7eb8f;", "🟢"),
        "red": ("color: #f5222d; background: #fff1f0; border-color: #ffa39e;", "🔴"),
        "gray": ("color: #000000; background: #f5f5f5; border-color: #d9d9d9;", "⚪"),
    }
    style, icon = colors.get(color, colors["gray"])

    return f"""
    <span style="
        display: inline-block;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid;
        margin-right: 5px;
        {style.split(';')[0]}; 
        {style.split(';')[1]}; 
        {style.split(';')[2]};
    ">
        {text}
    </span>
    """


def render_account_card(account_data):
    """
    渲染单个账号的卡片行
    """
    # 使用 container(border=True) 制造卡片边框效果
    with st.container(border=True):
        # 布局：[勾选/头像 1.5] [信息主体 4] [粉丝数 1.5] [数据1 1.5] [数据2 1.5]
        c1, c2, c3, c4, c5 = st.columns([1, 4, 1.5, 1.5, 1.5])

        with c1:
            # 垂直居中稍微有点难，Streamlit 默认顶部对齐
            st.checkbox("选", key=f"chk_{account_data['id']}", label_visibility="collapsed")
            st.image(account_data['avatar'], width=60)

        with c2:
            # 第一行：名字 + ID + 等级
            st.markdown(
                f"**{account_data['name']}** <span style='color:gray; font-size:12px'>ID: {account_data['id']}</span>",
                unsafe_allow_html=True)

            # 第二行：彩色标签 (这是最像新红的地方)
            tags_html = ""
            for tag in account_data.get('tags', []):
                tags_html += render_tag(tag['text'], tag['color'])

            # 使用 st.html 或 st.markdown 渲染标签
            st.markdown(tags_html, unsafe_allow_html=True)

            # 第三行：简介 (灰色小字，限制字数)
            desc = account_data.get('desc', '暂无简介')
            if len(desc) > 30: desc = desc[:30] + "..."
            st.caption(f"简介：{desc}")

        with c3:
            st.metric("粉丝数", account_data['fans'], delta=account_data.get('fans_delta'))

        with c4:
            st.write(f"📅 **{account_data['last_active']}**")
            st.caption("最近发布时间")

        with c5:
            # 这里可以放一些核心指标，比如爆文率
            st.metric("爆文数", account_data['hot_count'], help="点赞过万的视频数")