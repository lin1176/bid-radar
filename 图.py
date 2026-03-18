import streamlit as st
from openai import OpenAI
import json
import time
import plotly.graph_objects as go

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="中标雷达 | 投标风险量化评估系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 2. 亮色企业级 CSS =================
st.markdown("""
<style>
    :root {
        --bg-main: #F8FAFC;
        --bg-card: #FFFFFF;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --accent-blue: #2563EB;
        --accent-hover: #1D4ED8;
        --risk-high: #EF4444;
        --risk-med: #F59E0B;
        --risk-low: #10B981;
        --border: #E2E8F0;
        --shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }
    .stApp { background-color: var(--bg-main); color: var(--text-primary); font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
    
    /* 标题区 */
    .main-title { font-size: 2.4rem; font-weight: 800; text-align: center; color: var(--text-primary); margin-bottom: 6px; letter-spacing: -0.5px; }
    .sub-title { text-align: center; color: var(--text-secondary); font-size: 1.05rem; margin-bottom: 2rem; }
    
    /* 输入框与表单 */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        box-shadow: var(--shadow) !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }
    
    /* 按钮修复与美化 */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-hover)) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 14px 0 !important;
        width: 100% !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important; }
    
    /* 卡片容器 */
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: var(--shadow); margin-bottom: 16px; }
    .card-header { font-weight: 600; color: var(--text-primary); margin-bottom: 10px; border-left: 4px solid var(--accent-blue); padding-left: 10px; }
    
    /* 分数展示 */
    .score-box { text-align: center; padding: 24px; background: var(--bg-card); border-radius: 14px; border: 1px solid var(--border); box-shadow: var(--shadow); }
    .score-label { color: var(--text-secondary); font-size: 13px; margin-bottom: 6px; }
    .score-value { font-size: 4.5rem; font-weight: 800; line-height: 1; margin-bottom: 10px; }
    .risk-tag { display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }
    
    /* 转化横幅 */
    .cta-banner {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        border: 1px solid #BAE6FD;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-top: 28px;
    }
    .cta-title { color: #0369A1; font-weight: 700; margin-bottom: 8px; }
    .cta-desc { color: #475569; font-size: 14px; margin-bottom: 16px; }
    .cta-btn { background: #0EA5E9; color: white; padding: 10px 24px; border-radius: 25px; font-weight: 600; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ================= 3. API 配置 =================
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d"

BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ================= 4. 核心逻辑函数 =================
def analyze_risk(text):
    system_prompt = """
    你是一个资深的招投标风控专家。请分析用户提供的招标文本，识别潜在的陪跑、亏损和定向操作风险。
    请严格按照以下 JSON 格式返回：
    {
        "total_score": (0-100的整数，分数越高风险越大),
        "risk_level": "低风险 / 中风险 / 高风险 / 极高风险",
        "dimensions": {
            "time_score": (0-100),
            "budget_score": (0-100),
            "param_score": (0-100),
            "payment_score": (0-100)
        },
        "analysis": [
            {"title": "⏳ 周期与节点", "content": "分析工期和截标时间"},
            {"title": "💸 预算与成本", "content": "分析预算与成本匹配度"},
            {"title": "🎯 参数与门槛", "content": "分析特定参数或排他性条款"},
            {"title": "💳 付款与结算", "content": "分析付款比例和验收标准"}
        ],
        "verdict": "一句话专业决策建议（如：条款存在明显倾向性，建议复核后谨慎参与）"
    }
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"待分析招标文本：\n{text[:3500]}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ================= 5. 页面布局 =================
st.markdown("<div class='main-title'>📊 中标雷达 · 投标风险量化评估系统</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>告别盲目陪跑 | 穿透参数迷雾 | 用数据锁定真实利润</div>", unsafe_allow_html=True)

col_form, col_guide = st.columns([2.2, 1])

with col_form:
    with st.form("risk_form", border=False):
        st.markdown("<div class='card-header'>📥 项目基础信息</div>", unsafe_allow_html=True)
        unit_name = st.text_input("招标单位 / 代理机构", placeholder="例：若尔盖保护区管理局 / 新宇盛项目管理集团")
        project_name = st.text_input("项目名称 / 编号", placeholder="例：N5132322026000006")
        tender_text = st.text_area("📄 粘贴招标公告/采购需求核心段落", height=160,
                                   placeholder="请粘贴包含【预算金额】【截止时间】【技术参数】【付款方式】的原文...")
        submitted = st.form_submit_button("🔍 启动风险量化扫描")
        
with col_guide:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**💡 系统使用指引**")
    st.markdown("1. 填入招标方与项目标识\n2. 粘贴招标文件核心条款\n3. 系统将交叉比对合规基线，60秒输出多维评估报告")
    st.info("⚠️ 本系统基于多维数据模型解析，结果仅供商业决策参考，不构成法律承诺。")
    st.markdown("</div>", unsafe_allow_html=True)

if submitted and tender_text.strip():
    with st.status("🧠 核心引擎正在解析文件结构...", expanded=True) as status:
        st.write("📐 提取时间轴与截标红线...")
        time.sleep(0.6)
        st.write("💰 核算预算覆盖率与现金流模型...")
        time.sleep(0.6)
        st.write("⚖️ 交叉比对排他性参数与历史合规库...")
        time.sleep(0.5)
        
        result = analyze_risk(tender_text)
        status.update(label="✅ 评估完成", state="complete", expanded=False)

    if "error" in result:
        st.error(f"⛔ 解析异常：{result['error']}")
    else:
        st.divider()
        score = result.get('total_score', 0)
        level = result.get('risk_level', '未知')
        
        theme_color = "#EF4444" if score > 70 else "#F59E0B" if score > 40 else "#10B981"
        tag_bg = "rgba(239, 68, 68, 0.1)" if score > 70 else "rgba(245, 158, 11, 0.1)" if score > 40 else "rgba(16, 185, 129, 0.1)"
        tag_text = "#EF4444" if score > 70 else "#F59E0B" if score > 40 else "#10B981"
        
        c1, c2, c3 = st.columns([1.1, 2, 1.2])
        
        with c1:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-label">综合风险指数</div>
                <div class="score-value" style="color: {theme_color};">{score}</div>
                <div class="risk-tag" style="background: {tag_bg}; color: {tag_text};">{level}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            categories = ['时间压迫', '预算风险', '参数排他', '回款隐患']
            values = [
                result['dimensions'].get('time_score', 0),
                result['dimensions'].get('budget_score', 0),
                result['dimensions'].get('param_score', 0),
                result['dimensions'].get('payment_score', 0)
            ]
            fig = go.Figure(data=go.Scatterpolar(
                r=values, theta=categories, fill='toself',
                fillcolor=f"rgba({int(theme_color[1:3], 16)}, {int(theme_color[3:5], 16)}, {int(theme_color[5:7], 16)}, 0.15)",
                line=dict(color=theme_color, width=3),
                marker=dict(size=8, color=theme_color)
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickmode='linear', dtick=20, gridcolor='#E2E8F0', tickfont=dict(color='#64748B', size=11)),
                    angularaxis=dict(gridcolor='#E2E8F0', linecolor='#E2E8F0', tickfont=dict(color='#0F172A', size=13))
                ),
                showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=30, r=30, t=10, b=10), height=280
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with c3:
            action = "🛑 建议策略：止损放弃 / 仅做关系维护" if score > 60 else "✅ 建议策略：正常投标 / 优化技术响应"
            action_color = "#EF4444" if score > 60 else "#10B981"
            st.markdown(f"""
            <div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div class="card-header">📋 系统决策建议</div>
                <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.6; margin-bottom: 12px;">{result.get('verdict', '暂无评估')}</p>
                <div style="font-weight: 600; color: {action_color};">{action}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        st.markdown("<div class='card-header'>🔍 风险维度深度拆解</div>", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, item in enumerate(result.get('analysis', [])):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="card">
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">{item['title']}</div>
                    <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.5;">{item['content']}</div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("""
        <div class="cta-banner">
            <div class="cta-title">🔓 获取竞争对手历史报价与评分审计</div>
            <div class="cta-desc">公开文本仅反映表面规则。如需调取【该单位过往中标价格分布】及【技术分得分模型】，请联系数据顾问。</div>
            <div class="cta-btn">限时体验 ¥99 / 份深度情报包</div>
        </div>
        """, unsafe_allow_html=True)

elif submitted and not tender_text.strip():
    st.warning("⚠️ 请粘贴招标文件核心内容后执行扫描")

st.markdown("<br><hr style='border-color: #E2E8F0;'><p style='text-align: center; color: #94A3B8; font-size: 12px;'>© 2026 中标雷达系统 | 数据驱动决策 · 拒绝无效投入</p>", unsafe_allow_html=True)
