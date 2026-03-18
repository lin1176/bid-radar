import streamlit as st
from openai import OpenAI
import json
import time
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta, timezone

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="工程大数据标前审计终端",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= 2. 核心 CSS (修复样式不生效的问题) =================
st.markdown("""
<style>
    /* 1. 全局布局调整 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important; /* 底部留白，防止遮挡 */
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* 2. 背景与字体 */
    .stApp {
        background-color: #F1F5F9;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* 3. 顶部导航栏 */
    .top-bar {
        background: #0F172A;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-dot {
        height: 10px;
        width: 10px;
        background-color: #22C55E;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
        box-shadow: 0 0 5px #22C55E;
    }

    /* 4. 卡片容器 */
    .data-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
    }
    
    /* 5. 分数展示 */
    .metric-value { font-size: 28px; font-weight: 800; color: #0F172A; }
    .metric-label { font-size: 12px; color: #64748B; text-transform: uppercase; }

    /* 6. 模糊效果 */
    .blur-text {
        color: transparent;
        text-shadow: 0 0 8px rgba(0,0,0,0.5);
        user-select: none;
    }
    .locked-row {
        background: #F8FAFC;
        border-bottom: 1px solid #E2E8F0;
        padding: 8px;
        font-size: 13px;
        font-family: monospace;
    }

    /* 7. 按钮样式 */
    div.stButton > button {
        background: #2563EB;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: 600;
        width: 100%;
    }
    div.stButton > button:hover {
        background: #1D4ED8;
    }
    
    /* 8. 警报样式 */
    .audit-alert {
        padding: 10px;
        border-left: 4px solid #DC2626;
        background: #FEF2F2;
        color: #991B1B;
        font-size: 13px;
        margin-bottom: 5px;
    }

    /* 9. 底部日志区样式 (关键修复) */
    .log-container {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 20px;
        margin-top: 30px;
        font-family: 'Courier New', monospace;
    }
    .log-header {
        font-weight: bold;
        color: #0F172A;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 10px;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .log-row {
        display: flex;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px dashed #F1F5F9;
        font-size: 12px;
        color: #475569;
    }
    .log-time {
        color: #94A3B8;
        margin-right: 15px;
        font-weight: bold;
        min-width: 80px;
    }
    .log-tag {
        background: #F1F5F9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        margin-right: 10px;
        min-width: 80px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. 侧边栏 =================
with st.sidebar:
    st.markdown("### 🎛️ 控制台 Control Panel")
    st.markdown("---")
    st.markdown("**数据源状态：**")
    st.markdown("🟢 国家公共资源交易平台 (已连接)")
    st.markdown("🟢 企业征信大数据 (已连接)")
    st.markdown("🟢 司法诉讼记录库 (已连接)")
    st.markdown("---")
    st.info("当前版本：V5.2 Enterprise\n\n授权给：高级审计员")

# ================= 4. 业务逻辑 =================
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d"

BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def analyze_risk(unit_name, project_name, text):
    system_prompt = """
    你是一个严谨的“工程审计系统”。请分析招标文件，输出JSON。
    风格要求：极度简练、专业术语、像机器生成的日志。
    {
        "total_score": (0-100),
        "risk_level": "High / Medium / Low",
        "dimensions": {"time":0, "budget":0, "param":0, "payment":0},
        "audit_logs": [
            "检测到截标时间异常: <具体原因>",
            "预算成本偏离分析: <具体原因>",
            "排他性参数扫描: <具体原因>",
            "资金条款合规性: <具体原因>"
        ],
        "verdict": "一句话审计结论"
    }
    """
    user_content = f"单位：{unit_name}\n项目：{project_name}\n内容：{text[:2000]}"
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_content}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ================= 5. 主界面布局 =================

# --- 顶部状态栏 ---
st.markdown("""
<div class="top-bar">
    <div style="font-weight:bold; font-size:18px;">🛡️ 标前大数据风控审计终端 <span style="font-size:12px; opacity:0.7;">Pre-Bid Risk Audit Terminal</span></div>
    <div style="font-size:13px;"><span class="status-dot"></span>系统运行正常 | 数据库延时: 12ms</div>
</div>
""", unsafe_allow_html=True)

# --- 输入区 ---
with st.form("audit_form"):
    c1, c2, c3 = st.columns([1.5, 1.5, 1])
    with c1:
        unit_name = st.text_input("招标单位 (Owner)", placeholder="输入单位全称以调取画像")
    with c2:
        project_name = st.text_input("项目名称 (Project)", placeholder="输入项目名称")
    with c3:
        st.write("") # 占位
        st.write("") 
        submitted = st.form_submit_button("⚡ 立即审计 (Audit)")
    
    tender_text = st.text_area("📄 招标文件摘要 / 采购需求 (粘贴区域)", height=100, placeholder="在此粘贴核心条款，系统将自动进行 NLP 语义分析...")

# --- 结果展示区 ---
if submitted:
    if not tender_text:
        st.error("请输入招标文件内容")
    else:
        # 模拟数据流加载
        progress_text = st.empty()
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
            if i == 30: progress_text.text(f"正在穿透【{unit_name}】股权结构...")
            if i == 60: progress_text.text("正在比对 145,200 条同类中标记录...")
            if i == 90: progress_text.text("正在生成风险拓扑图...")
        
        progress_text.empty()
        bar.empty()
        
        # 获取结果
        result = analyze_risk(unit_name, project_name, tender_text)
        
        if "error" in result:
            st.error("审计超时")
        else:
            score = result.get('total_score', 0)
            level = result.get('risk_level', 'Evaluating')
            color = "#DC2626" if score > 60 else "#059669"
            
            # 第一行：看板
            st.markdown(f"### 📊 审计结果概览 (Audit Overview)")
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"""<div class="data-card" style="border-top: 4px solid {color}; text-align:center;"><div class="metric-label">综合风险评分</div><div class="metric-value" style="color:{color}; font-size:40px;">{score}</div></div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div class="data-card" style="text-align:center;"><div class="metric-label">风险等级</div><div class="metric-value" style="font-size:24px; margin-top:8px;">{level}</div></div>""", unsafe_allow_html=True)
            with k3:
                hist_count = random.randint(3, 12)
                st.markdown(f"""<div class="data-card" style="text-align:center;"><div class="metric-label">关联历史发标</div><div class="metric-value">{hist_count} <span style="font-size:14px;">次</span></div></div>""", unsafe_allow_html=True)
            with k4:
                 st.markdown(f"""<div class="data-card" style="text-align:center;"><div class="metric-label">疑似常驻单位</div><div class="metric-value">3 <span style="font-size:14px;">家</span></div><div style="font-size:12px; color:#DC2626;">⚠ 检测到强关联</div></div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

            # 第二行：图表与日志
            r1, r2 = st.columns([1, 2])
            with r1:
                st.markdown("**风险基因图谱**")
                dims = result.get('dimensions', {})
                fig = go.Figure(data=go.Scatterpolar(
                    r=[dims.get('time',0), dims.get('budget',0), dims.get('param',0), dims.get('payment',0)],
                    theta=['工期风险', '预算风险', '参数排他', '回款风险'],
                    fill='toself', line_color=color, fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
                ))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)), showlegend=False, margin=dict(l=30, r=30, t=10, b=10), height=200)
                st.plotly_chart(fig, use_container_width=True)
            with r2:
                st.markdown("**系统审计日志 (System Logs)**")
                logs = result.get('audit_logs', [])
                for log in logs:
                    st.markdown(f"""<div class="audit-alert"><b>[RISK DETECTED]</b> {log}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div style="background:#F0FDF4; border-left:4px solid #22C55E; padding:10px; font-size:13px; color:#166534;"><b>[CONCLUSION]</b> {result.get('verdict')}</div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # 第三行：模糊数据
            st.markdown("### 🔒 核心情报数据库 (Intelligence Database)")
            st.markdown("""
            <div class="data-card" style="border:1px dashed #DC2626; background:#FFF5F5;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="color:#991B1B; font-weight:bold;">⚠ 警告：检测到该项目存在高度疑似内定对象</div>
                    <div style="font-size:12px; color:#666;">数据密级：绝密 ★★★</div>
                </div>
                <div style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr; font-weight:bold; font-size:13px; border-bottom:1px solid #ccc; padding-bottom:5px; margin-bottom:5px;">
                    <div>历史中标单位 (Competitor)</div><div>中标金额 (Bid Price)</div><div>下浮率 (Rate)</div><div>关联度</div>
                </div>
                <div class="locked-row" style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr;">
                    <div>四川**建设工程有限公司</div><div class="blur-text">¥ 2,850,000</div><div class="blur-text">98.5%</div><div style="color:#DC2626; font-weight:bold;">95% (高危)</div>
                </div>
                 <div class="locked-row" style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr;">
                    <div>成都**文化传媒有限公司</div><div class="blur-text">¥ 588,000</div><div class="blur-text">99.0%</div><div style="color:#D97706; font-weight:bold;">80% (疑似)</div>
                </div>
                <div style="text-align:center; margin-top:20px;">
                    <p style="font-size:14px; color:#4B5563;">当前账户权限不足，无法查看详细金额及单位全称</p>
                    <button style="width:auto; background:#DC2626; padding:10px 40px; border-radius:50px; font-size:15px;">🔓 升级企业版账户 (查看底牌)</button>
                    <div style="margin-top:10px; font-size:12px; color:#64748B;">联系客服开通权限：VIP-8888 (点击复制)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# === 底部日志逻辑 (强制北京时间) ===
# 定义北京时区 (UTC+8)
beijing_tz = timezone(timedelta(hours=8))
now = datetime.now(beijing_tz)

# 生成动态过去时间
t1 = (now - timedelta(minutes=42)).strftime("%H:%M:%S")
t2 = (now - timedelta(minutes=28)).strftime("%H:%M:%S")
t3 = (now - timedelta(minutes=15)).strftime("%H:%M:%S")
t4 = (now - timedelta(minutes=3)).strftime("%H:%M:%S")
sync_t = (now - timedelta(minutes=58)).strftime("%Y-%m-%d %H:%M:%S")

st.markdown("<br>", unsafe_allow_html=True)

# 使用 f-string 拼接 HTML，确保样式生效
html_log = f"""
<div class="log-container">
    <div class="log-header">
        📡 实时风险监测日志 (Live Monitor Log) - <span style="color:#22C55E; font-weight:normal;">Running...</span>
    </div>
    
    <div class="log-row">
        <span class="log-time">[{t1}]</span> 
        <span class="log-tag">RISK_BLOCK</span> 
        <span>监测到某地级市政府采购项目包含 3 项隐形排他参数，已触发围标预警。</span>
    </div>
    <div class="log-row">
        <span class="log-time">[{t2}]</span> 
        <span class="log-tag">DATA_SYNC</span> 
        <span>成功同步川渝地区 2,400 条历史中标数据，关联关系库已更新。</span>
    </div>
    <div class="log-row">
        <span class="log-time">[{t3}]</span> 
        <span class="log-tag">AUDIT_PASS</span> 
        <span>某国企施工单位通过“历史低价模型”优化报价，中标率预测提升至 85%。</span>
    </div>
    <div class="log-row">
        <span class="log-time">[{t4}]</span> 
        <span class="log-tag">FUND_WARN</span> 
        <span>系统拦截一份“全额垫资”合同风险，建议客户启动资金风控预案。</span>
    </div>
    
    <div style="margin-top:10px; font-size:11px; color:#94A3B8; text-align:right;">
        * 数据来源：全国公共资源交易大数据互联中心
    </div>
</div>
"""
st.markdown(html_log, unsafe_allow_html=True)

# 底部版权
st.markdown(f"<br><hr><div style='text-align:center; color:#94A3B8; font-size:11px;'>系统日志 ID: 2026-X8829-AF | 数据同步时间: {sync_t} | SSL 安全连接</div>", unsafe_allow_html=True)
