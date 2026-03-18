import streamlit as st
from openai import OpenAI
import json
import time
import pandas as pd
import plotly.graph_objects as go

# ================= 页面配置 =================
st.set_page_config(
    page_title="中标雷达 | 招投标风险智能预警系统",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 自定义 CSS (美化) =================
st.markdown("""
<style>
    /* 全局字体 */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* 标题样式 */
    h1 {
        color: #FF4B4B;
        text-align: center;
        font-weight: 800;
    }
    h3 {
        color: #FAFAFA;
    }
    /* 风险分数字体 */
    .risk-score {
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0px;
    }
    /* 卡片背景 */
    .stCard {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    /* 按钮样式 */
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
        border-color: #FF2B2B;
    }
</style>
""", unsafe_allow_html=True)

# ================= API 配置 =================
API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d"
BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ================= 核心分析函数 =================
def analyze_risk(text):
    """调用 DeepSeek 进行深度风险评估"""
    system_prompt = """
    你是一个资深的招投标风控专家。请分析用户提供的招标文本（项目概况/采购需求），识别潜在的“陪跑”、“亏损”和“内定”风险。
    请严格按照以下 JSON 格式返回：
    {
        "total_score": (0-100的整数，分数越高风险越大),
        "risk_level": "低风险 / 中风险 / 高风险 / 极高风险",
        "dimensions": {
            "time_score": (0-100, 时间紧迫程度),
            "budget_score": (0-100, 预算是否过低/亏损风险),
            "param_score": (0-100, 参数是否排他/萝卜坑),
            "payment_score": (0-100, 回款风险/付款条件)
        },
        "analysis": [
            {"title": "时间陷阱", "content": "分析工期和截标时间"},
            {"title": "利润陷阱", "content": "分析预算与成本匹配度"},
            {"title": "内定嫌疑", "content": "分析特定参数或排他性条款"},
            {"title": "回款毒药", "content": "分析付款比例和验收标准"}
        ],
        "verdict": "一句话犀利点评（如：典型的低价陪跑局，建议直接放弃）"
    }
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"待分析招标文本：\n{text[:3000]}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


# ================= 页面布局 =================

# 1. 顶部 Header
st.markdown("<h1>🛡️ 中标雷达 · 招投标风险预警系统</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>🚫 拒绝陪跑 | 💰 避免亏损 | 🔍 识别内定</p>",
            unsafe_allow_html=True)
st.divider()

# 2. 输入区域 (左右分栏，左边输入，右边说明)
col1, col2 = st.columns([2, 1])

with col1:
    with st.form("analysis_form"):
        st.subheader("📝 项目信息录入")
        project_name = st.text_input("项目名称（选填）", placeholder="例如：若尔盖湿地宣传片项目")
        tender_text = st.text_area("📄 招标公告/采购需求（核心内容粘贴处）", height=250,
                                   placeholder="请直接粘贴招标公告中的【项目概况】、【采购需求】、【评分标准】等核心文字...\n\n例如：\n预算金额：30万\n截止时间：3月26日\n要求：拍摄黑颈鹤繁衍镜头...")

        submitted = st.form_submit_button("开始深度风险扫描")

with col2:
    st.info("💡 **如何使用？**")
    st.markdown("""
    1. 打开招标公告网页。
    2. 复制**预算、时间、技术参数、付款方式**等关键段落。
    3. 粘贴到左侧文本框。
    4. 点击“开始扫描”。
    """)
    st.warning("⚠️ **注意：**\n本系统基于  大数据模型，仅供商业参考，不构成法律建议。")

# 3. 结果展示区域
if submitted and tender_text:
    # 进度条动画，增加科技感
    with st.status("🤖 AI 正在接入风控大脑...", expanded=True) as status:
        st.write("🔍 正在扫描时间陷阱...")
        time.sleep(1)
        st.write("💰 正在核算隐形成本...")
        time.sleep(1)
        st.write("⚖️ 正在比对排他性条款...")
        time.sleep(0.5)

        # 调用 API
        result = analyze_risk(tender_text)
        status.update(label="✅ 分析完成！", state="complete", expanded=False)

    if "error" in result:
        st.error(f"分析失败，请稍后重试。错误信息：{result['error']}")
    else:
        st.divider()

        # === 核心指标看板 ===
        score = result['total_score']
        level = result['risk_level']

        # 动态颜色
        score_color = "#FF4B4B" if score > 70 else "#FFA500" if score > 40 else "#00CC96"

        c1, c2, c3 = st.columns([1.5, 2, 1.5])

        with c1:
            # 显示大大的分数
            st.markdown(f"<div style='text-align: center; color: #888;'>风险综合指数</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='risk-score' style='color: {score_color};'>{score}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='text-align: center; font-size: 24px; font-weight: bold; background-color: {score_color}; border-radius: 5px; padding: 5px;'>{level}</div>",
                unsafe_allow_html=True)

        with c2:
            # 雷达图 (Plotly)
            categories = ['时间风险', '预算风险', '参数排他', '回款风险']
            values = [
                result['dimensions']['time_score'],
                result['dimensions']['budget_score'],
                result['dimensions']['param_score'],
                result['dimensions']['payment_score']
            ]

            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                line_color=score_color
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)

        with c3:
            st.markdown("### 🤖 AI 犀利点评")
            st.info(f"“{result['verdict']}”")
            if score > 60:
                st.error("🛑 建议操作：止损放弃 / 谨慎陪跑")
            else:
                st.success("✅ 建议操作：积极争取 / 正常投标")

        st.divider()

        # === 深度分析详情 ===
        st.subheader("🔍 四维深度拆解")

        row1 = st.columns(2)
        row2 = st.columns(2)

        # 为了美观，用卡片形式展示
        for i, item in enumerate(result['analysis']):
            # 动态决定放在哪一行
            col = row1[i] if i < 2 else row2[i - 2]
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {item['title']}")
                    st.write(item['content'])

        # === 引导转化钩子 (Monetization Hook) ===
        st.divider()
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #FF4B4B; text-align: center;">
            <h3 style="color: #FF4B4B;">🔓 解锁更高阶情报？</h3>
            <p style="color: #CCC;">本报告基于公开文本分析。如需获取<b>【该项目竞争对手历史报价数据】</b>及<b>【详细内定评分标准审计】</b>，请联系人工顾问。</p>
            <p style="font-size: 14px; color: #888;">限时优惠：¥29.9 / 份深度报告</p>
        </div>
        """, unsafe_allow_html=True)

        # 这里可以放你的二维码图片
        # st.image("your_qr_code.png", width=200)

elif submitted and not tender_text:
    st.warning("⚠️ 请先粘贴招标公告内容！")

# 底部版权
st.markdown(
    "<br><br><hr><p style='text-align: center; color: #555;'>© 2026 中标雷达系统 | Powered by  & Python</p>",
    unsafe_allow_html=True)
