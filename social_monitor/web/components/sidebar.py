import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar():
    with st.sidebar:
        st.title("📡 SocialMonitor")
        selected = option_menu(
            menu_title="功能导航",
            options=["全网雷达", "监控对象", "舆情大盘", "系统状态"],
            icons=['search', 'list-task', 'bar-chart', 'cpu'],
            menu_icon="cast",
            default_index=0,
        )
    return selected