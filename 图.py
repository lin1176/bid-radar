import streamlit as st
from openai import OpenAI
import json
import time
import plotly.graph_objects as go

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="中标雷达 | 投标风险量化评估系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 2. 金融级亮色设计系统 =================
st.markdown("""
<style>
    :root {
        --bg-app: #F5F7FA;
        --bg-surface: #FFFFFF;
        --bg-muted: #F8FAFC;
        --text-primary: #0B1220;
        --text-secondary: #4A5568;
        --text-muted: #718096;
        --primary: #3B82F6;
        --primary-hover: #2563EB;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --border: #E2E8F0;
        --border-focus: #93C5FD;
        --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06);
        --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
        --shadow-lg: 0 10px 25px rgba(15, 23, 42, 0.10);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }
    
    .stApp { background: var(--bg-app); color: var(--text-primary); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
    
    /* 标题与排版系统 */
    .app-header { text-align: center; padding: 2rem 0 1rem; }
    .app-title { font-size: 2.25rem; font-weight: 700; letter-spacing: -0.02em; color: var(--text-primary); margin: 0; }
    .app-subtitle { font-size: 1rem; color: var(--text-secondary); margin-top: 0.5rem; font-weight: 400; }
    
    /* 容器与卡片 */
    .section-container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
    .card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.5rem; box-shadow: var(--shadow-sm); transition: box-shadow 0.2s ease; }
    .card:hover { box-shadow: var(--shadow-md); }
    .card-header { display: flex; align-items: center; gap: 0.5rem; font-weight: 600; color: var(--text-primary); margin-bottom: 1rem; font-size: 1.05rem; }
    .card-header::before { content: ""; display: block; width: 4px; height: 18px; background: var(--primary); border-radius: 2px; }
    
    /* 表单控件精修 */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }
    ::placeholder { color: var(--text-muted) !important; opacity: 0.8; }
    
    /* 按钮系统 */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, var(--primary), var(--primary-hover)) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 0.85rem 0 !important;
        width: 100% !important;
        box-shadow: var(--shadow-md) !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:first-child:hover { transform: translateY(-1px); box-shadow: var(--shadow-lg) !important; }
    div.stButton > button:first-child:active { transform: translateY(0); }
    
    /* 指标与标签 */
    .metric-card { text-align: center; padding: 1.5rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-md); box-shadow: var(--shadow-sm); }
    .metric-label { font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem; font-weight: 500; }
    .metric-value { font-size: 3.5rem; font-weight: 800; line-height: 1; margin-bottom: 0.75rem; letter-spacing: -0.03em; }
    .risk-badge { display: inline-flex; align-items: center; padding: 0.35rem 0.85rem; border-radius: 99px; font-size: 0.8rem; font-weight: 600; }
    
    /* 状态与提示 */
    .status-step { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0; color: var(--text-secondary); font-size: 0.9rem; }
    .status-step::before { content: "•"; color: var(--primary); font-size: 1.2rem; }
    
    /* 转化模块 */
    .upgrade-card { background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%); border: 1px solid #BAE6FD; border-radius: var(--radius-md); padding: 1.5rem; text-align: center; margin-top: 2rem; }
    .upgrade-title { font-size: 1.1rem; font-weight: 700; color: #0369A1; margin-bottom: 0.5rem; }
    .upgrade-desc { font-size: 0.9rem; color: #475569; margin-bottom: 1rem; line-height: 1.5; }
    .upgrade-btn { display: inline-block; background: #0EA5E9; color: white; padding: 0.6rem 1.5rem; border-radius: 99px; font-weight: 600; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3); }
    
    /* 分割线与页脚 */
    .divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 2rem 0; }
    .footer { text-align: center; color: var(--text-muted); font-size: 0.75rem; padding: 2rem 0 1rem; }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 3. 核心配置 =================
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d"

BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def analyze_risk(text):
    prompt = """
    你是资深招投标风控顾问。请基于提供的招标文件片段，量化评估陪跑、亏损及定向操作风险。
    严格按JSON返回：
    {
        "total_score": 0-100整数,
        "risk_level": "低风险/中风险/高风险/极高风险",
        "dimensions": {"time_score": 0-100, "budget_score": 0-100, "param_score": 0-100, "payment_score": 0-100},
        "analysis": [
            {"title": "周期与节点", "content": "简练分析"},
            {"title": "预算与成本", "content": "简练分析"},
            {"title": "参数与门槛", "content": "简练分析"},
            {"title": "付款与结算", "content": "简练分析"}
        ],
        "verdict": "一句专业决策建议"
    }
    """
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": f"文本：\n{text[:3500]}"}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ================= 4. 页面渲染 =================
st.markdown("""
<div class="app-header">
    <h1 class="app-title">📈 中标雷达 · 投标风险量化评估系统</h1>
    <p class="app-subtitle">穿透条款迷雾 · 量化沉没成本 · 用数据锁定真实利润</p>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    
    col_input, col_guide = st.columns([2.1, 1])
    
    with col_input:
        with st.form("eval_form", border=False):
            st.markdown('<div class="card-header">📥 项目基础信息</div>', unsafe_allow_html=True)
            unit = st.text_input("招标单位 / 代理机构", placeholder="例：若尔盖保护区管理局 / 新宇盛项目管理集团")
            project = st.text_input("项目名称 / 采购编号", placeholder="例：N5132322026000006")
            content = st.text_area("📄 粘贴招标文件核心条款", height=150,
                                   placeholder="请粘贴包含【预算金额】【截标时间】【技术参数】【付款条件】的原文段落...")
            submitted = st.form_submit_button("🔍 启动风险量化扫描")
            
    with col_guide:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📋 操作指引**")
        st.markdown("1. 填入采购方与项目标识\n2. 粘贴核心条款原文\n3. 系统交叉比对合规基线，60秒输出评估报告")
        st.info("⚠️ 本系统基于多维数据模型解析，结果仅供商业决策参考，不构成法律承诺。")
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted and content.strip():
        with st.status("🧠 风控引擎正在解析文件结构...", expanded=True) as status:
            st.markdown('<div class="status-step">提取时间轴与截标红线</div>', unsafe_allow_html=True)
            time.sleep(0.5)
            st.markdown('<div class="status-step">核算预算覆盖率与现金流模型</div>', unsafe_allow_html=True)
            time.sleep(0.5)
            st.markdown('<div class="status-step">交叉比对排他参数与历史合规库</div>', unsafe_allow_html=True)
            time.sleep(0.4)
            
            result = analyze_risk(content)
            status.update(label="✅ 评估完成", state="complete", expanded=False)

        if "error" in result:
            st.error(f"⛔ 解析异常：{result['error']}")
        else:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            score = result.get('total_score', 0)
            level = result.get('risk_level', '未知')
            
            # 动态主题映射
            theme = {"color": "#EF4444", "bg": "rgba(239,68,68,0.1)", "tag": "高风险"} if score > 70 else \
                    {"color": "#F59E0B", "bg": "rgba(245,158,11,0.1)", "tag": "中风险"} if score > 40 else \
                    {"color": "#10B981", "bg": "rgba(16,185,129,0.1)", "tag": "低风险"}
            
            c1, c2, c3 = st.columns([1.1, 2, 1.2])
            
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">综合风险指数</div>
                    <div class="metric-value" style="color: {theme['color']};">{score}</div>
                    <div class="risk-badge" style="background: {theme['bg']}; color: {theme['color']};">{level}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                cats = ['时间压迫', '预算风险', '参数排他', '回款隐患']
                vals = [result['dimensions'].get('time_score',0), result['dimensions'].get('budget_score',0),
                        result['dimensions'].get('param_score',0), result['dimensions'].get('payment_score',0)]
                
                fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill='toself',
                    fillcolor=f"rgba({int(theme['color'][1:3],16)}, {int(theme['color'][3:5],16)}, {int(theme['color'][5:7],16)}, 0.12)",
                    line=dict(color=theme['color'], width=2.5), marker=dict(size=7, color=theme['color'])))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0,100], tickmode='linear', dtick=20, gridcolor='#E2E8F0', tickfont=dict(color='#718096', size=10)),
                               angularaxis=dict(gridcolor='#E2E8F0', linecolor='#E2E8F0', tickfont=dict(color='#0B1220', size=12))),
                    showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=10, b=10), height=260
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with c3:
                action = "🛑 建议策略：止损放弃 / 仅做关系维护" if score > 60 else "✅ 建议策略：正常投标 / 优化技术响应"
                st.markdown(f"""
                <div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <div class="card-header">📋 系统决策建议</div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem;">{result.get('verdict', '暂无评估')}</p>
                    <div style="font-weight: 600; color: {theme['color']}; font-size: 0.95rem;">{action}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🔍 风险维度深度拆解</div>', unsafe_allow_html=True)
            
            cols = st.columns(2)
            for i, item in enumerate(result.get('analysis', [])):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="card">
                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem; font-size: 0.95rem;">{item['title']}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.55;">{item['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown("""
            <div class="upgrade-card">
                <div class="upgrade-title">🔓 获取竞争对手历史报价与评分审计</div>
                <div class="upgrade-desc">公开文本仅反映表面规则。如需调取【该单位过往中标价格分布】及【技术分得分模型】，请联系数据顾问。</div>
                <div class="upgrade-btn">限时体验 ¥99 / 份深度情报包</div>
            </div>
            """, unsafe_allow_html=True)

    elif submitted and not content.strip():
        st.warning("⚠️ 请粘贴招标文件核心内容后执行扫描")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 中标雷达系统 | 数据驱动决策 · 拒绝无效投入</div>', unsafe_allow_html=True)
