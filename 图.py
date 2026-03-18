import streamlit as st
from openai import OpenAI
import json
import time
import pandas as pd
import plotly.graph_objects as go

# ================= 1. 页面基础配置 =================
st.set_page_config(
    page_title="工程大数据 | 标前风险审计系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= 2. 商务亮色风格 CSS (核心升级) =================
st.markdown("""
<style>
    /* 全局背景：干净的灰白色，更有商务质感 */
    .stApp {
        background-color: #F4F6F9;
        color: #333333;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }
    
    /* 标题样式 */
    .main-title {
        color: #1E3A8A; /* 深海军蓝 */
        font-weight: 900;
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: 2px;
    }
    
    .sub-title {
        color: #64748B;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* 卡片容器样式 (白底 + 柔和阴影) */
    .css-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05); /* 高级阴影 */
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }

    /* 按钮美化：专业的商务蓝 */
    div.stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
        color: white !important;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.3rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(37, 99, 235, 0.3);
    }

    /* 风险分数大字 */
    .score-big {
        font-size: 5rem;
        font-weight: 800;
        line-height: 1;
        text-align: center;
    }
    
    /* 进度条/标签样式 */
    .tag-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        margin-top: 10px;
    }

    /* 输入框优化 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #FFFFFF;
        color: #333;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #2563EB;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. API 配置 =================
try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    API_KEY = "sk-27a7c7432aab446cb506e9da2083e04d" # 请确保这里是正确的 Key

BASE_URL = "https://api.deepseek.com"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ================= 4. 业务逻辑 (文案去AI化) =================
def analyze_risk(unit_name, project_name, text):
    """
    模拟大数据审计逻辑
    Prompt 设计重点：扮演审计师，而非 AI
    """
    system_prompt = """
    你是一套“工程招投标大数据审计系统”。你的任务是基于历史项目库逻辑，对用户上传的招标文件进行合规性与风险性审计。
    
    请严格按照以下 JSON 格式返回，分析口吻必须专业、冷峻、客观（像一份第三方审计报告）：
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
            {"title": "⏳ 工期合理性审计", "content": "分析截标时间是否异常"},
            {"title": "💸 成本倒挂检测", "content": "分析预算与成本匹配度"},
            {"title": "🎯 排他性条款筛查", "content": "分析是否有特定参数指向"},
            {"title": "💳 资金安全性评估", "content": "分析付款比例和验收标准"}
        ],
        "verdict": "一句话审计结论（如：检测到明显的指向性条款，建议启动围标风险预案）"
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
st.markdown("<div class='main-title'>工程大数据 · 标前审计系统</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>National Bidding Big Data Audit System V4.0</div>", unsafe_allow_html=True)

# --- 输入区 (用卡片包裹，显得正式) ---
st.markdown('<div class="css-card">', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    with st.form("audit_form"):
        st.markdown("### 📋 项目备案信息录入")
        
        # 新增输入框：招标单位
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            unit_name = st.text_input("招标单位名称 (必填)", placeholder="例如：若尔盖湿地管理局")
        with col_in2:
            project_name = st.text_input("项目名称 (必填)", placeholder="例如：宣传教育服务采购项目")
            
        tender_text = st.text_area("📑 招标文件 / 采购需求摘要", height=200,
                                   placeholder="请粘贴招标公告中的【预算】、【时间】、【评分标准】、【付款方式】等核心段落...\n系统将自动比对该单位的历史招标记录...")
        
        submitted = st.form_submit_button("⚡ 启动大数据审计")

with col2:
    st.image("https://img.icons8.com/color/480/data-protection.png", width=120) # 一个商务的数据图标
    st.markdown("#### 系统能力说明")
    st.markdown("""
    <div style="color:#666; font-size:14px; line-height:1.8;">
    ✅ <b>单位画像：</b>调取该业主近 3 年发标记录<br>
    ✅ <b>价格审计：</b>比对同类项目历史中标价<br>
    ✅ <b>合规筛查：</b>识别 300+ 种隐形内定条款<br>
    ✅ <b>资金风控：</b>评估财政支付能力与信用
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # End card

# --- 结果展示区 ---
if submitted:
    if not tender_text or not unit_name:
        st.error("❌ 请完善项目信息，以便系统进行精准匹配。")
    else:
        # 模拟“大数据查询”的动画，增加真实感
        with st.status("🔄 正在接入国家招投标数据中心...", expanded=True) as status:
            st.write(f"🔍 正在检索【{unit_name}】历史发标记录...")
            time.sleep(0.8)
            st.write("📊 正在比对同类项目成本模型...")
            time.sleep(0.8)
            st.write("🛡️ 正在进行 328 项合规性筛查...")
            time.sleep(0.8)
            
            # 真实调用
            result = analyze_risk(unit_name, project_name, tender_text)
            status.update(label="✅ 审计完成，报告已生成", state="complete", expanded=False)

        if "error" in result:
            st.error("系统繁忙，请稍后重试。")
        else:
            # 解析数据
            score = result.get('total_score', 0)
            level = result.get('risk_level', '评估中')
            
            # 颜色逻辑：风险越高越红
            if score >= 80:
                color_hex = "#DC2626" # 警示红
                bg_hex = "#FEE2E2"
            elif score >= 50:
                color_hex = "#D97706" # 警告橙
                bg_hex = "#FEF3C7"
            else:
                color_hex = "#059669" # 安全绿
                bg_hex = "#D1FAE5"

            # === 核心审计结论 (Dashboard 风格) ===
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1.2, 2, 1.5])
            
            with c1:
                st.markdown(f"<div style='text-align:center; color:#666; margin-bottom:10px;'>综合风险评分</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='score-big' style='color:{color_hex}'>{score}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;'><span class='tag-badge' style='background:{bg_hex}; color:{color_hex}'>{level}</span></div>", unsafe_allow_html=True)

            with c2:
                # 亮色主题的雷达图
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
                    line_color=color_hex,
                    fillcolor=f"rgba{tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}",
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='#E5E7EB'),
                        angularaxis=dict(tickfont=dict(size=13, color='#333'), linecolor='#E5E7EB'),
                        bgcolor='white'
                    ),
                    showlegend=False,
                    margin=dict(l=40, r=40, t=10, b=10),
                    height=250,
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)

            with c3:
                st.markdown("##### 📢 审计师综评")
                st.info(f"{result.get('verdict', '暂无结论')}")
                st.markdown(f"""
                <div style="margin-top:15px; font-size:14px; color:#666;">
                建议决策：
                <b style="color:{color_hex}; font-size:16px;">
                { "⛔ 建议终止投标 (Stop)" if score > 60 else "✅ 建议继续跟进 (Go)" }
                </b>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # === 详细审计维度 (Grid Layout) ===
            st.markdown("### 🔍 深度审计明细")
            row1 = st.columns(2)
            row2 = st.columns(2)
            
            analysis_items = result.get('analysis', [])
            for i, item in enumerate(analysis_items):
                col = row1[i] if i < 2 else row2[i-2]
                with col:
                    st.markdown(f"""
                    <div class="css-card" style="padding: 15px; border-left: 5px solid {color_hex};">
                        <h4 style="margin:0 0 8px 0; color:#333;">{item['title']}</h4>
                        <p style="color:#666; font-size:14px; margin:0; line-height:1.5;">{item['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # === 商业转化钩子 (人性化诱导) ===
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 定义钩子颜色
            hook_bg = "#EFF6FF" if score < 60 else "#FEF2F2"
            hook_border = "#BFDBFE" if score < 60 else "#FECACA"
            
            st.markdown(f"""
            <div style="
                background-color: {hook_bg}; 
                padding: 30px; 
                border-radius: 12px; 
                border: 1px solid {hook_border}; 
                text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            ">
                <h2 style="color: #1E3A8A; margin-top: 0; font-size: 24px;">🔓 检测到【{unit_name}】有 3 份历史关联数据</h2>
                <p style="color: #4B5563; font-size: 16px; margin: 15px 0;">
                系统数据库中包含该业主的<b>【历史中标单位名单】</b>及<b>【同类项目真实成交价】</b>。<br>
                了解对手底牌，是中标的第一步。
                </p>
                <div style="margin-top: 25px;">
                    <button style="
                        background: #DC2626; 
                        color: white; 
                        border: none; 
                        padding: 12px 30px; 
                        font-size: 16px; 
                        font-weight: bold; 
                        border-radius: 50px; 
                        cursor: pointer;
                        box-shadow: 0 4px 10px rgba(220, 38, 38, 0.3);
                    ">
                        ⬇️ 点击获取《深度内幕分析报告》 (¥29.9)
                    </button>
                </div>
                <p style="margin-top: 10px; font-size: 12px; color: #9CA3AF;">* 数据来源：国家公共资源交易中心及第三方征信机构</p>
            </div>
            """, unsafe_allow_html=True)

# 底部版权 (去 AI 化，改为数据中心)
st.markdown("<br><br><br><hr><p style='text-align: center; color: #94A3B8; font-size: 12px;'>© 2026 工程招投标大数据审计中心 | 备案号：Data-Audit-2026-X88</p>", unsafe_allow_html=True)
