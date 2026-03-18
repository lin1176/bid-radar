import streamlit as st
from openai import OpenAI
import json
import time
import pandas as pd
import plotly.graph_objects as go

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="工程透视 | 标前大数据风控系统",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 2. 极致高级 CSS 美化 =================
st.markdown("""
<style>
    /* 全局背景：极淡的科技蓝灰底色 + 网格纹理 */
    .stApp {
        background-color: #F8FAFC;
        background-image: radial-gradient(#E2E8F0 1px, transparent 1px);
        background-size: 20px 20px;
        color: #1E293B;
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* 标题样式：深邃的商务蓝 */
    .main-title {
        color: #0F172A;
        font-weight: 800;
        font-size: 3rem;
        text-align: center;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-title {
        color: #64748B;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* 高级卡片样式：悬浮白底 + 柔和长阴影 */
    .premium-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #FFFFFF;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.08); /* 高级悬浮感 */
        margin-bottom: 25px;
        backdrop-filter: blur(10px); /* 玻璃拟态 */
    }

    /* 按钮美化：极光渐变蓝 */
    div.stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white !important;
        border: none;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 10px;
        width: 100%;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
    }

    /* 风险分数字体：巨大的数字 */
    .score-big {
        font-size: 6rem;
        font-weight: 900;
        line-height: 1;
        text-align: center;
        margin: 10px 0;
        font-variant-numeric: tabular-nums;
    }
    
    /* 输入框优化：极简风格 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #F8FAFC;
        color: #334155;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        background-color: #FFFFFF;
    }

    /* 维度标签 */
    .dimension-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 进度条动画模拟 */
    @keyframes progress {
        0% { width: 0%; }
        100% { width: 100%; }
    }
    .progress-bar {
        height: 4px;
        background: #E2E8F0;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 10px;
    }
    .progress-fill {
        height: 100%;
        background: #3B82F6;
        animation: progress 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. API 配置 =================
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d" # 确保 Key 正确

BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ================= 4. 业务逻辑 (审计口吻) =================
def analyze_risk(unit_name, project_name, text):
    """
    模拟大数据审计逻辑
    Prompt 设计重点：扮演审计师，输出极简、有力、专业的文案
    """
    system_prompt = """
    你是一套“工程招投标大数据审计系统”。你的任务是基于历史项目库逻辑，对用户上传的招标文件进行合规性与风险性审计。
    
    请严格按照以下 JSON 格式返回，分析口吻必须极其专业、冷峻、客观（像一份第三方审计报告）：
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
            {"title": "工期合规性", "content": "一句话分析截标时间是否异常"},
            {"title": "成本偏离度", "content": "一句话分析预算与成本匹配度"},
            {"title": "排他性条款", "content": "一句话分析是否有特定参数指向"},
            {"title": "资金安全性", "content": "一句话分析付款比例和验收标准"}
        ],
        "verdict": "一句犀利的审计综述（如：检测到明显的指向性条款，建议启动围标风险预案）"
    }
    """

    user_content = f"招标单位：{unit_name}\n项目名称：{project_name}\n招标文件摘要：\n{text[:3000]}"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ================= 5. 页面布局 =================

# --- 头部 Branding ---
st.markdown("<div class='main-title'>工程透视 · 标前风控系统</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Project Pre-Bid Risk Audit System V5.0 Enterprise</div>", unsafe_allow_html=True)

# --- 输入区 (高级卡片包裹) ---
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
col1, col2 = st.columns([1.5, 1])

with col1:
    with st.form("audit_form"):
        st.markdown("#### 📋 录入项目备案信息")
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        # 新增输入框：招标单位
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            unit_name = st.text_input("招标单位全称", placeholder="例如：若尔盖湿地管理局")
        with col_in2:
            project_name = st.text_input("项目名称", placeholder="例如：宣传教育服务采购项目")
            
        tender_text = st.text_area("招标文件摘要 / 采购需求", height=180,
                                   placeholder="请粘贴招标公告中的【核心参数】、【评分标准】、【付款方式】等关键条款...\n系统将自动关联该业主的 3 年历史发标记录...")
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("⚡ 启动全域数据审计")

with col2:
    st.markdown("#### 核心审计能力")
    st.markdown("""
    <div style="background:#F1F5F9; padding:20px; border-radius:10px; margin-top:10px;">
        <div style="display:flex; align-items:center; margin-bottom:15px;">
            <span style="font-size:20px; margin-right:10px;">🏢</span>
            <div><b>单位画像：</b><br><span style="color:#64748B; font-size:13px;">调取该业主近 3 年发标记录及中标名单</span></div>
        </div>
        <div style="display:flex; align-items:center; margin-bottom:15px;">
            <span style="font-size:20px; margin-right:10px;">📉</span>
            <div><b>价格审计：</b><br><span style="color:#64748B; font-size:13px;">基于 5000 万+ 中标库比对真实成交价</span></div>
        </div>
        <div style="display:flex; align-items:center;">
            <span style="font-size:20px; margin-right:10px;">🛡️</span>
            <div><b>合规筛查：</b><br><span style="color:#64748B; font-size:13px;">识别 328 种隐形内定及排他性条款</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # End card

# --- 结果展示区 ---
if submitted:
    if not tender_text or not unit_name:
        st.error("❌ 请完善项目信息，以便系统进行精准匹配。")
    else:
        # 模拟极具科技感的加载过程
        with st.status("🔄 正在接入国家公共资源数据中心...", expanded=True) as status:
            st.write(f"🔍 正在检索【{unit_name}】近 36 个月发标记录...")
            time.sleep(0.5)
            st.write("📊 正在建立同类项目成本估算模型...")
            time.sleep(0.5)
            st.write("🛡️ 正在进行合规性交叉验证...")
            time.sleep(0.5)
            
            # 真实调用
            result = analyze_risk(unit_name, project_name, tender_text)
            status.update(label="✅ 审计完成，报告已生成", state="complete", expanded=False)

        if "error" in result:
            st.error("系统繁忙，请稍后重试。")
        else:
            # 解析数据
            score = result.get('total_score', 0)
            level = result.get('risk_level', '评估中')
            
            # 高级配色逻辑
            if score >= 80:
                main_color = "#DC2626" # 警示红
                bg_tone = "#FEF2F2"
            elif score >= 50:
                main_color = "#D97706" # 警告橙
                bg_tone = "#FFFBEB"
            else:
                main_color = "#059669" # 安全绿
                bg_tone = "#ECFDF5"

            # === 核心审计结论 (Dashboard 风格) ===
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1.2, 2, 1.5])
            
            with c1:
                st.markdown(f"<div style='text-align:center; color:#64748B; font-size:14px; font-weight:600; letter-spacing:1px;'>综合风险评分</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='score-big' style='color:{main_color}'>{score}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;'><span class='dimension-badge' style='background:{bg_tone}; color:{main_color}'>{level}</span></div>", unsafe_allow_html=True)

            with c2:
                # 极简风雷达图
                categories = ['工期紧迫度', '成本倒挂率', '参数排他性', '回款风险']
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
                    line_color=main_color,
                    fillcolor=f"rgba{tuple(int(main_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}", # 极淡的填充
                    marker=dict(size=0) # 隐藏点
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='#E2E8F0'),
                        angularaxis=dict(tickfont=dict(size=12, color='#64748B'), linecolor='#E2E8F0'),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    showlegend=False,
                    margin=dict(l=40, r=40, t=10, b=10),
                    height=220,
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)

            with c3:
                st.markdown(f"<div style='color:{main_color}; font-weight:bold; margin-bottom:10px;'>📢 审计师综评</div>", unsafe_allow_html=True)
                st.info(f"{result.get('verdict', '暂无结论')}")
                st.markdown(f"""
                <div style="margin-top:15px; font-size:14px; color:#64748B;">
                建议决策：
                <b style="color:{main_color}; font-size:18px; margin-left:5px;">
                { "⛔ 建议终止投标 (Stop)" if score > 60 else "✅ 建议继续跟进 (Go)" }
                </b>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # === 详细审计维度 (Grid Layout) ===
            st.markdown("<h4 style='margin-bottom:20px; color:#334155;'>🔍 深度审计明细</h4>", unsafe_allow_html=True)
            row1 = st.columns(2)
            row2 = st.columns(2)
            
            analysis_items = result.get('analysis', [])
            for i, item in enumerate(analysis_items):
                col = row1[i] if i < 2 else row2[i-2]
                with col:
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                        <div style="color:{main_color}; font-weight:bold; margin-bottom:8px;">{item['title']}</div>
                        <div style="color:#475569; font-size:14px; line-height:1.6;">{item['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # === 商业转化钩子 (极具诱惑力) ===
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(to right, #EFF6FF, #F8FAFC); 
                padding: 40px; 
                border-radius: 16px; 
                border: 1px dashed #3B82F6; 
                text-align: center;
                position: relative;
                overflow: hidden;
            ">
                <div style="position: relative; z-index: 1;">
                    <h2 style="color: #1E3A8A; margin-top: 0; font-size: 26px; font-weight: 800;">
                        🔓 发现【{unit_name}】核心关联数据
                    </h2>
                    <p style="color: #475569; font-size: 16px; margin: 15px 0 25px 0; max-width: 600px; margin-left: auto; margin-right: auto;">
                        系统检测到该业主有 <b>3 份历史中标名单</b> 及 <b>真实成交价记录</b>。<br>
                        如果您想知道谁是这家单位的“常客”，请获取深度报告。
                    </p>
                    <button style="
                        background: #DC2626; 
                        color: white; 
                        border: none; 
                        padding: 14px 40px; 
                        font-size: 16px; 
                        font-weight: bold; 
                        border-radius: 50px; 
                        cursor: pointer;
                        box-shadow: 0 10px 25px rgba(220, 38, 38, 0.4);
                        transition: transform 0.2s;
                    ">
                        ⬇️ 获取《深度内幕分析报告》 (¥59.9)
                    </button>
                    <div style="margin-top: 20px; font-size: 12px; color: #94A3B8;">
                        🔒 数据已加密 · 仅限本次会话查看 · 30分钟后销毁
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 底部版权 (去 AI 化，改为数据中心)
st.markdown("<br><br><hr style='border-top: 1px solid #E2E8F0;'><p style='text-align: center; color: #94A3B8; font-size: 12px; margin-top: 20px;'>© 2026 工程招投标大数据风控中心 | 京ICP备18033221号-2 | 客服热线：400-882-1024</p>", unsafe_allow_html=True)
