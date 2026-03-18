import streamlit as st
from openai import OpenAI
import json
import time
import pandas as pd
import plotly.graph_objects as go

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="中标雷达 | 招投标风险智能预警系统",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 2. 高级 CSS 美化 (核心升级) =================
st.markdown("""
<style>
    /* 全局背景色与字体 */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* 标题渐变色特效 */
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* 副标题 */
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* 修复按钮显示问题：强制设置按钮背景色和文字颜色 */
    div.stButton > button {
        background: linear-gradient(45deg, #FF4B4B, #D32F2F);
        color: white !important;
        border: none;
        padding: 0.6rem 2rem;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        width: 100%;
    }
    
    /* 按钮悬停特效 */
    div.stButton > button:hover {
        background: linear-gradient(45deg, #FF6B6B, #E53935);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.6);
        transform: translateY(-2px);
        color: white !important; /* 确保悬停时文字也是白色 */
    }

    /* 风险分数字体优化 */
    .risk-score-container {
        text-align: center;
        padding: 20px;
        background: #1F2229;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #333;
    }
    .risk-score {
        font-size: 5rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 10px;
        text-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    
    /* 输入框样式微调 */
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
        border: 1px solid #444;
    }
    .stTextArea>div>div>textarea {
        background-color: #262730;
        color: white;
        border: 1px solid #444;
    }
    
    /* 分析卡片样式 */
    .analysis-card {
        background-color: #1F2229;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FF4B4B;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. API 配置 =================
# 注意：正式部署时建议使用 st.secrets，本地运行时可直接写 Key
# 如果你已经配置了 .streamlit/secrets.toml，请使用 st.secrets["DEEPSEEK_API_KEY"]
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d" # 本地备用

BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ================= 4. 核心逻辑函数 =================
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
            {"title": "⏳ 时间陷阱", "content": "简练分析工期和截标时间"},
            {"title": "💸 利润陷阱", "content": "简练分析预算与成本匹配度"},
            {"title": "🎯 内定嫌疑", "content": "简练分析特定参数或排他性条款"},
            {"title": "💳 回款毒药", "content": "简练分析付款比例和验收标准"}
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

# ================= 5. 页面布局 =================

# --- 标题区 ---
st.markdown("<div class='gradient-text'>🛡️ 中标雷达 · 智能预警系统</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>大数据风控引擎 | 识别内定 · 规避亏损 · 拒绝陪跑</div>", unsafe_allow_html=True)
st.divider()

# --- 输入区 ---
col_input, col_tips = st.columns([2, 1])

with col_input:
    with st.form("analysis_form"):
        st.markdown("### 📝 项目情报录入")
        project_name = st.text_input("项目名称（选填）", placeholder="例如：若尔盖湿地宣传片项目")
        tender_text = st.text_area("📄 招标公告/采购需求（核心情报粘贴处）", height=280,
                                   placeholder="💡 智能分析需要以下信息：\n1. 预算金额（如：30万）\n2. 时间节点（获取文件及开标时间）\n3. 核心参数（如：指定品牌、特定证书）\n4. 付款方式（预付款比例）\n\n请直接粘贴公告原文...")
        
        # 这里的按钮现在会被 CSS 完美渲染为红色
        submitted = st.form_submit_button("🚀 启动深度风险扫描")

with col_tips:
    st.markdown("### 💡 使用指南")
    st.info("""
    **仅需三步，识破标书陷阱：**
    
    1. **复制**：打开招标公告，复制核心段落。
    2. **粘贴**：将内容粘贴到左侧文本框。
    3. **扫描**：AI 将在 5 秒内输出体检报告。
    """)
    st.markdown("""
    <div style="background-color:#262730; padding:15px; border-radius:10px; font-size:14px; color:#888;">
    ⚠️ <b>免责声明：</b><br>
    本系统基于大语言模型逻辑推理，结果仅供商业决策参考，不构成法律效力。
    </div>
    """, unsafe_allow_html=True)

# --- 结果展示区 ---
if submitted and tender_text:
    # 动态加载效果
    with st.status("🤖 风控大脑正在高速运转...", expanded=True) as status:
        st.write("🔍 正在扫描时间陷阱...")
        time.sleep(0.5)
        st.write("💰 正在核算隐形成本...")
        time.sleep(0.5)
        st.write("⚖️ 正在比对排他性条款...")
        time.sleep(0.5)
        
        # 调用 API
        result = analyze_risk(tender_text)
        status.update(label="✅ 分析完成！", state="complete", expanded=False)

    if "error" in result:
        st.error(f"分析失败，请稍后重试。错误信息：{result['error']}")
    else:
        st.markdown("---")
        
        # 解析数据
        score = result.get('total_score', 0)
        level = result.get('risk_level', '未知')
        
        # 动态颜色逻辑
        if score >= 80:
            theme_color = "#FF4B4B" # 红色
        elif score >= 50:
            theme_color = "#FFA500" # 橙色
        else:
            theme_color = "#00CC96" # 绿色

        # === 核心看板 ===
        c1, c2, c3 = st.columns([1, 1.5, 1])
        
        with c1:
            # 分数展示卡片
            st.markdown(f"""
            <div class="risk-score-container">
                <div style="color: #888; margin-bottom: 5px;">综合风险指数</div>
                <div class="risk-score" style="color: {theme_color};">{score}</div>
                <div style="background: {theme_color}; color: black; font-weight: bold; padding: 5px 15px; border-radius: 20px; display: inline-block;">
                    {level}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            # 高级雷达图 (Plotly)
            categories = ['时间风险', '预算风险', '参数排他', '回款风险']
            values = [
                result['dimensions'].get('time_score', 0),
                result['dimensions'].get('budget_score', 0),
                result['dimensions'].get('param_score', 0),
                result['dimensions'].get('payment_score', 0)
            ]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='风险维度',
                line_color=theme_color,
                fillcolor=f"rgba({int(theme_color[1:3], 16)}, {int(theme_color[3:5], 16)}, {int(theme_color[5:7], 16)}, 0.3)", # 动态半透明填充
                marker=dict(color=theme_color)
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='#444'),
                    angularaxis=dict(tickfont=dict(size=14, color='#EEE'), linecolor='#444'),
                    bgcolor='#1F2229'
                ),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        with c3:
            # AI 点评卡片
            st.markdown(f"""
            <div style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div style="background: #1F2229; padding: 20px; border-radius: 15px; border-left: 5px solid {theme_color};">
                    <h3 style="margin-top:0;">🤖 AI 犀利点评</h3>
                    <p style="font-size: 16px; line-height: 1.6;">“{result.get('verdict', '暂无点评')}”</p>
                    <hr style="border-color: #333;">
                    <div style="font-weight: bold; color: {theme_color};">
                        { "🛑 建议操作：止损放弃" if score > 60 else "✅ 建议操作：可以尝试" }
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # === 详情分析 ===
        st.markdown("<br>", 
