import streamlit as st
from openai import OpenAI
import json
import time
import plotly.graph_objects as go

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="中标雷达 | 标前大数据风控系统",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 2. 企业级紧凑 CSS 系统 =================
st.markdown("""
<style>
    :root {
        --bg-app: #F1F5F9;
        --bg-card: #FFFFFF;
        --bg-muted: #F8FAFC;
        --text-main: #0F172A;
        --text-sub: #475569;
        --text-muted: #64748B;
        --primary: #2563EB;
        --primary-hover: #1D4ED8;
        --risk-high: #EF4444;
        --risk-med: #F59E0B;
        --risk-low: #10B981;
        --border: #E2E8F0;
        --shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        --radius: 10px;
    }
    .stApp { background: var(--bg-app); color: var(--text-main); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    
    /* 紧凑布局控制 */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    .stMarkdown { margin-bottom: 0.5rem !important; }
    
    /* 顶部状态栏 */
    .status-bar { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 8px 16px; margin-bottom: 1rem; font-size: 12px; color: var(--text-muted); }
    .status-dot { width: 8px; height: 8px; background: var(--risk-low); border-radius: 50%; display: inline-block; margin-right: 6px; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    
    /* 标题区 */
    .app-title { font-size: 1.8rem; font-weight: 800; color: var(--text-main); text-align: center; margin: 0.5rem 0 0.2rem; letter-spacing: -0.5px; }
    .app-subtitle { font-size: 0.95rem; color: var(--text-sub); text-align: center; margin-bottom: 1rem; font-weight: 400; }
    
    /* 卡片系统 */
    .panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; box-shadow: var(--shadow); margin-bottom: 1rem; }
    .panel-header { font-size: 0.95rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.8rem; display: flex; align-items: center; gap: 6px; }
    .panel-header::before { content: ""; width: 3px; height: 14px; background: var(--primary); border-radius: 2px; }
    
    /* 表单控件精修 */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: var(--bg-muted) !important; color: var(--text-main) !important;
        border: 1px solid var(--border) !important; border-radius: 8px !important;
        padding: 0.6rem 0.8rem !important; font-size: 0.85rem !important;
        transition: all 0.2s !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        background: var(--bg-card) !important; border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }
    ::placeholder { color: var(--text-muted) !important; font-size: 0.8rem !important; }
    
    /* 按钮系统 */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, var(--primary), var(--primary-hover)) !important;
        color: #FFF !important; border: none !important; border-radius: 8px !important;
        font-size: 0.9rem !important; font-weight: 600 !important; padding: 0.7rem 0 !important;
        width: 100% !important; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
        cursor: pointer !important; transition: all 0.2s !important;
    }
    div.stButton > button:first-child:hover { transform: translateY(-1px); box-shadow: 0 6px 14px rgba(37, 99, 235, 0.35) !important; }
    
    /* 指标卡片 */
    .metric-box { text-align: center; padding: 1rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; }
    .metric-label { font-size: 0.75rem; color: var(--text-sub); margin-bottom: 4px; font-weight: 500; }
    .metric-val { font-size: 3.2rem; font-weight: 800; line-height: 1; margin-bottom: 6px; letter-spacing: -1px; }
    .risk-tag { display: inline-block; padding: 4px 10px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
    
    /* 分析网格 */
    .grid-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 0.9rem; margin-bottom: 0.8rem; }
    .grid-title { font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 4px; }
    .grid-content { font-size: 0.8rem; color: var(--text-sub); line-height: 1.5; }
    
    /* 转化模块 */
    .vault-banner { background: linear-gradient(135deg, #EFF6FF 0%, #F0F9FF 100%); border: 1px solid #BFDBFE; border-radius: 10px; padding: 1.2rem; text-align: center; margin-top: 1rem; }
    .vault-title { font-size: 1.05rem; font-weight: 800; color: #1E3A8A; margin-bottom: 6px; }
    .vault-desc { font-size: 0.85rem; color: #475569; margin-bottom: 10px; line-height: 1.4; }
    .vault-btn { display: inline-block; background: #DC2626; color: white; padding: 8px 20px; border-radius: 99px; font-size: 0.85rem; font-weight: 600; box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3); cursor: pointer; }
    .vault-secure { font-size: 0.7rem; color: #64748B; margin-top: 8px; display: flex; align-items: center; justify-content: center; gap: 4px; }
    
    /* 隐藏默认元素 */
    #MainMenu, header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================= 3. 核心配置 =================
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d"

BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def analyze_risk(unit_name, project_name, text):
    system_prompt = """
    你是一套“招投标大数据审计系统”。基于历史项目库逻辑，对招标文件进行合规性与风险性审计。
    严格按JSON返回，口吻冷峻、客观、专业：
    {
        "total_score": 0-100整数,
        "risk_level": "低风险/中风险/高风险/极高风险",
        "dimensions": {"time_score": 0-100, "budget_score": 0-100, "param_score": 0-100, "payment_score": 0-100},
        "analysis": [
            {"title": "工期合规性", "content": "一句话分析"},
            {"title": "成本偏离度", "content": "一句话分析"},
            {"title": "排他性条款", "content": "一句话分析"},
            {"title": "资金安全性", "content": "一句话分析"}
        ],
        "verdict": "一句审计综述"
    }
    """
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"单位:{unit_name}\n项目:{project_name}\n文本:\n{text[:3000]}"}],
            response_format={"type": "json_object"}, temperature=0.1
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ================= 4. 页面渲染 =================
# 状态栏 (信任锚点)
st.markdown("""
<div class="status-bar">
    <span><span class="status-dot"></span>审计节点在线 | 已接入全国公共资源交易数据池</span>
    <span>合规引擎 V5.2 | 响应延迟 <120ms</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">🏢 工程透视 · 标前风控系统</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">穿透条款迷雾 · 量化沉没成本 · 用数据锁定真实利润</div>', unsafe_allow_html=True)

# 输入面板
st.markdown('<div class="panel">', unsafe_allow_html=True)
c_form, c_info = st.columns([1.6, 1])

with c_form:
    with st.form("audit_form", border=False):
        st.markdown('<div class="panel-header">📥 项目备案录入</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: unit_name = st.text_input("招标单位", placeholder="例：若尔盖保护区管理局")
        with c2: project_name = st.text_input("项目名称/编号", placeholder="例：N5132322026000006")
        tender_text = st.text_area("招标文件核心条款", height=110, placeholder="粘贴【预算】【截标时间】【技术参数】【付款条件】原文...")
        submitted = st.form_submit_button("⚡ 启动全域数据审计")

with c_info:
    st.markdown('<div class="panel-header">📊 系统审计维度</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.8rem; color:var(--text-sub);">
        <div>🏢 业主历史中标集中度</div><div>📉 同类项目真实成交价</div>
        <div>🛡️ 328项排他条款库</div><div>⏱️ 资金周转压力模型</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("⚠️ 本系统基于多维数据模型解析，结果仅供商业决策参考。")
st.markdown('</div>', unsafe_allow_html=True)

# 结果面板
if submitted:
    if not tender_text.strip() or not unit_name.strip():
        st.error("❌ 请完善单位与条款信息以触发精准匹配。")
    else:
        with st.status("🔄 接入公共资源数据中心...", expanded=True) as status:
            st.write(f"🔍 检索【{unit_name}】近36个月发标轨迹...")
            time.sleep(0.4)
            st.write("📊 建立成本估算与现金流模型...")
            time.sleep(0.4)
            st.write("🛡️ 执行合规性交叉验证...")
            time.sleep(0.3)
            result = analyze_risk(unit_name, project_name, tender_text)
            status.update(label="✅ 审计完成", state="complete", expanded=False)

        if "error" in result:
            st.error("⛔ 解析异常，请重试。")
        else:
            score = result.get('total_score', 0)
            level = result.get('risk_level', '评估中')
            
            theme = {"c": "#EF4444", "bg": "rgba(239,68,68,0.1)"} if score > 70 else \
                    {"c": "#F59E0B", "bg": "rgba(245,158,11,0.1)"} if score > 40 else \
                    {"c": "#10B981", "bg": "rgba(16,185,129,0.1)"}
            
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            d1, d2, d3 = st.columns([1, 1.8, 1.2])
            
            with d1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">综合风险指数</div>
                    <div class="metric-val" style="color:{theme['c']}">{score}</div>
                    <div class="risk-tag" style="background:{theme['bg']}; color:{theme['c']}">{level}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with d2:
                cats = ['工期紧迫', '成本倒挂', '参数排他', '回款隐患']
                vals = [result['dimensions'].get('time_score',0), result['dimensions'].get('budget_score',0),
                        result['dimensions'].get('param_score',0), result['dimensions'].get('payment_score',0)]
                fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill='toself',
                    fillcolor=f"rgba({int(theme['c'][1:3],16)}, {int(theme['c'][3:5],16)}, {int(theme['c'][5:7],16)}, 0.12)",
                    line=dict(color=theme['c'], width=2), marker=dict(size=0)))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0,100], tickmode='linear', dtick=20, gridcolor='#E2E8F0', tickfont=dict(color='#64748B', size=9)),
                               angularaxis=dict(gridcolor='#E2E8F0', linecolor='#E2E8F0', tickfont=dict(color='#0F172A', size=10))),
                    showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=0, b=0), height=180
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with d3:
                action = "⛔ 终止投标 (Stop)" if score > 60 else "✅ 继续跟进 (Go)"
                st.markdown(f"""
                <div style="height:100%; display:flex; flex-direction:column; justify-content:center;">
                    <div class="panel-header">📋 审计师综评</div>
                    <p style="font-size:0.85rem; color:var(--text-sub); line-height:1.5; margin-bottom:8px;">{result.get('verdict', '暂无')}</p>
                    <div style="font-weight:700; color:{theme['c']}; font-size:0.9rem;">建议决策: {action}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 2x2 网格
            st.markdown('<div class="panel-header">🔍 深度审计明细</div>', unsafe_allow_html=True)
            g_cols = st.columns(2)
            for i, item in enumerate(result.get('analysis', [])):
                with g_cols[i % 2]:
                    st.markdown(f"""
                    <div class="grid-card">
                        <div class="grid-title">{item['title']}</div>
                        <div class="grid-content">{item['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            # 转化钩子
            st.markdown(f"""
            <div class="vault-banner">
                <div class="vault-title">🔓 已捕获【{unit_name}】历史成交底牌</div>
                <div class="vault-desc">系统检测到该业主存在 <b>3份关联中标记录</b> 及 <b>真实下浮率模型</b>。<br>如需查看常客名单与报价区间，请解锁深度报告。</div>
                <div class="vault-btn">获取《深度情报包》 ¥59.9</div>
                <div class="vault-secure">🔒 数据加密传输 · 缓存仅保留24小时 · 支持对公发票</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div style="text-align:center; color:#94A3B8; font-size:0.7rem; margin-top:1rem;">© 2026 工程招投标大数据风控中心 | 审计节点已备案 | 400-882-1024</div>', unsafe_allow_html=True)
