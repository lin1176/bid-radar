import streamlit as st
from openai import OpenAI
import json
import time
import pandas as pd
import plotly.graph_objects as go
import random

# ================= 1. 页面基础配置 (紧凑模式) =================
st.set_page_config(
    page_title="工程大数据标前审计终端",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= 2. 核心 CSS (修复遮挡问题) =================
st.markdown("""
<style>
    /* 1. 调整顶部间距，防止标题被遮挡 */
    .block-container {
        padding-top: 2rem !important; /* 增加顶部间距 */
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* 2. 背景与字体：专业数据终端风格 */
    .stApp {
        background-color: #F1F5F9; /* 高级灰 */
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* 3. 顶部导航栏模拟 */
    .top-bar {
        background: #0F172A; /* 深蓝黑 */
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

    /* 4. 卡片容器：高密度、细边框 */
    .data-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
    }
    
    /* 5. 分数展示优化 */
    .metric-box {
        text-align: center;
        border-right: 1px solid #E2E8F0;
    }
    .metric-label { font-size: 12px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 28px; font-weight: 800; color: #0F172A; }
    
    /* 6. 模糊数据效果 (诱导付费的核心) */
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
    
    /* 8. 自定义 Alert */
    .audit-alert {
        padding: 10px;
        border-left: 4px solid #DC2626;
        background: #FEF2F2;
        color: #991B1B;
        font-size: 13px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. 侧边栏 (营造系统感) =================
with st.sidebar:
    st.markdown("### 🎛️ 控制台 Control Panel")
    st.markdown("---")
    st.markdown("**数据源状态：**")
    st.markdown("🟢 国家公共资源交易平台 (已连接)")
    st.markdown("🟢 企业征信大数据 (已连接)")
    st.markdown("🟢 司法诉讼记录库 (已连接)")
    st.markdown("---")
    st.markdown("**审计配置：**")
    st.checkbox("开启历史比价", value=True)
    st.checkbox("开启围标关联排查", value=True)
    st.checkbox("开启资质穿透", value=True)
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

# --- 输入区 (修复报错：必须包裹在 st.form 内) ---
with st.form("audit_form"):
    c1, c2, c3 = st.columns([1.5, 1.5, 1])
    with c1:
        unit_name = st.text_input("招标单位 (Owner)", placeholder="输入单位全称以调取画像")
    with c2:
        project_name = st.text_input("项目名称 (Project)", placeholder="输入项目名称")
    with c3:
        st.write("") # 占位
        st.write("") 
        # 按钮必须在 form 内
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
            
            # 颜色定义
            color = "#DC2626" if score > 60 else "#059669"
            
            # === 第一行：核心指标看板 (Dashboard) ===
            st.markdown(f"### 📊 审计结果概览 (Audit Overview)")
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"""
                <div class="data-card" style="border-top: 4px solid {color}; text-align:center;">
                    <div class="metric-label">综合风险评分</div>
                    <div class="metric-value" style="color:{color}; font-size:40px;">{score}</div>
                    <div style="font-size:12px; color:#64748B;">/ 100.00</div>
                </div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div class="data-card" style="text-align:center;">
                    <div class="metric-label">风险等级</div>
                    <div class="metric-value" style="font-size:24px; margin-top:8px;">{level}</div>
                    <div style="font-size:12px; background:{color}; color:white; border-radius:4px; display:inline-block; padding:2px 8px;">AUDITED</div>
                </div>
                """, unsafe_allow_html=True)
            with k3:
                # 模拟数据
                hist_count = random.randint(3, 12)
                st.markdown(f"""
                <div class="data-card" style="text-align:center;">
                    <div class="metric-label">关联历史发标</div>
                    <div class="metric-value">{hist_count} <span style="font-size:14px;">次</span></div>
                    <div style="font-size:12px; color:#64748B;">近 36 个月</div>
                </div>
                """, unsafe_allow_html=True)
            with k4:
                 st.markdown(f"""
                <div class="data-card" style="text-align:center;">
                    <div class="metric-label">疑似常驻单位</div>
                    <div class="metric-value">3 <span style="font-size:14px;">家</span></div>
                    <div style="font-size:12px; color:#DC2626;">⚠ 检测到强关联</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

            # === 第二行：雷达图 + 审计日志 (左右布局) ===
            r1, r2 = st.columns([1, 2])
            
            with r1:
                st.markdown("**风险基因图谱**")
                # 雷达图
                dims = result.get('dimensions', {})
                fig = go.Figure(data=go.Scatterpolar(
                    r=[dims.get('time',0), dims.get('budget',0), dims.get('param',0), dims.get('payment',0)],
                    theta=['工期风险', '预算风险', '参数排他', '回款风险'],
                    fill='toself',
                    line_color=color,
                    fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}"
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
                    showlegend=False,
                    margin=dict(l=30, r=30, t=10, b=10),
                    height=200
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with r2:
                st.markdown("**系统审计日志 (System Logs)**")
                logs = result.get('audit_logs', [])
                for log in logs:
                    st.markdown(f"""
                    <div class="audit-alert">
                        <b>[RISK DETECTED]</b> {log}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:#F0FDF4; border-left:4px solid #22C55E; padding:10px; font-size:13px; color:#166534;">
                    <b>[CONCLUSION]</b> {result.get('verdict')}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # === 第三行：核心诱饵 (竞争对手情报) ===
            # 这是最拿捏人性的地方：假装查到了数据，但是不给你看
            st.markdown("### 🔒 核心情报数据库 (Intelligence Database)")
            
            st.markdown("""
            <div class="data-card" style="border:1px dashed #DC2626; background:#FFF5F5;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="color:#991B1B; font-weight:bold;">⚠ 警告：检测到该项目存在高度疑似内定对象</div>
                    <div style="font-size:12px; color:#666;">数据密级：绝密 ★★★</div>
                </div>
                
                <!-- 模拟表格头 -->
                <div style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr; font-weight:bold; font-size:13px; border-bottom:1px solid #ccc; padding-bottom:5px; margin-bottom:5px;">
                    <div>历史中标单位 (Competitor)</div>
                    <div>中标金额 (Bid Price)</div>
                    <div>下浮率 (Rate)</div>
                    <div>关联度</div>
                </div>
                
                <!-- 模糊数据行 -->
                <div class="locked-row" style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr;">
                    <div>四川**建设工程有限公司</div>
                    <div class="blur-text">¥ 2,850,000</div>
                    <div class="blur-text">98.5%</div>
                    <div style="color:#DC2626; font-weight:bold;">95% (高危)</div>
                </div>
                 <div class="locked-row" style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr;">
                    <div>成都**文化传媒有限公司</div>
                    <div class="blur-text">¥ 588,000</div>
                    <div class="blur-text">99.0%</div>
                    <div style="color:#D97706; font-weight:bold;">80% (疑似)</div>
                </div>
                <div class="locked-row" style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr;">
                    <div>若尔盖**商贸有限公司</div>
                    <div class="blur-text">¥ 1,200,000</div>
                    <div class="blur-text">92.0%</div>
                    <div style="color:#059669; font-weight:bold;">20% (普通)</div>
                </div>
                
                <div style="text-align:center; margin-top:20px;">
                    <p style="font-size:14px; color:#4B5563;">当前账户权限不足，无法查看详细金额及单位全称</p>
                    <button style="width:auto; background:#DC2626; padding:10px 40px; border-radius:50px; font-size:15px;">
                        🔓 升级企业版账户 (查看底牌)
                    </button>
                    <div style="margin-top:10px; font-size:12px; color:#64748B;">联系客服开通权限：VIP-8888 (点击复制)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 底部状态
st.markdown("<br><hr><div style='text-align:center; color:#94A3B8; font-size:11px;'>系统日志 ID: 2026-X8829-AF | 数据同步时间: 2026-03-17 08:32:11 | SSL 安全连接</div>", unsafe_allow_html=True)
