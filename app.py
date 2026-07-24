import streamlit as st
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go
import requests

# ---------------------------------------------------------
# 1. Page Config & SF Minority Report Theme
# ---------------------------------------------------------
st.set_page_config(page_title="Monster Insight - AI 미디어 몬스터 헌터", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #0369a1 100%);
        color: #e0f2fe;
    }
    .hud-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.15);
        margin-bottom: 15px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%);
        color: #020617;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 몬스터별 사건 데이터베이스 (사례 랜덤 추출용)
# ---------------------------------------------------------
CASES_DB = {
    "🤖 딥페이크 로봇": {
        "external_link": "https://whichfaceisreal.com/",
        "cases": [
            {
                "title": "사건 #101: 유명 연예인의 가짜 투자 권유 영상",
                "content": "SNS에 유명 배우가 특정 주식에 투자하면 10배를 번다고 말하는 숏폼 영상이 올라왔다. 입모양이 살짝 어색하고 목소리 억양이 부자연스럽다.",
                "options": ["진짜 연예인이 찍은 정보 영상이다", "AI 딥페이크로 합성된 사기 영상이다"],
                "answer": 1,
                "solution": "정답! AI 음성 합성 및 딥페이크 영상입니다. 얼굴 윤곽선과 입모양이 어색한지 교차 검증해야 합니다."
            },
            {
                "title": "사건 #102: 진짜 사람 vs AI 인물 구분하기",
                "content": "아래 사이트(Which Face is Real)로 이동하여 AI가 만든 가짜 얼굴과 진짜 사람 사진을 구분해 보세요!",
                "options": ["수사 완료 (진짜/가짜 구분 체득)", "수사 실패"],
                "answer": 0,
                "solution": "AI가 만든 얼굴은 안경 테 대칭, 배경의 뭉개짐, 귀걸이 형태에서 오차가 발생합니다."
            }
        ]
    },
    "🧠 AI 환각 몬스터": {
        "external_link": "https://toolbox.google.com/factcheck/explorer",
        "cases": [
            {
                "title": "사건 #201: AI가 가공해낸 존재하지 않는 역사적 사건",
                "content": "AI 챗봇에게 '조선왕조실록에 기록된 세종대왕의 맥북 던짐 사건'에 대해 물어보니 상세히 연도까지 들어 설명해주었다. 이 정보는 사실일까?",
                "options": ["AI가 사실에 기초해 답변한 것이다", "AI 환각(Hallucination) 현상으로 날조된 거짓이다"],
                "answer": 1,
                "solution": "정답! AI는 그럴듯한 문장을 생성할 뿐, 없는 사실을 진짜처럼 만들어내는 '환각 현상'이 있습니다."
            }
        ]
    },
    "🕷️ 알고리즘 거미": {
        "external_link": None,
        "cases": [
            {
                "title": "사건 #301: 내 피드가 한쪽 의견으로만 가득 찬 이유",
                "content": "내가 자극적인 뉴스를 누를 때마다 알고리즘은 비슷한 시각의 영상만 계속 보여준다. 이 상태를 무엇이라 할까?",
                "options": ["필터 버블 (Filter Bubble)", "에코 체임버 (Echo Chamber)", "둘 다 맞다"],
                "answer": 2,
                "solution": "정답! 알고리즘은 편향된 정보의 확증편향을 일으킵니다."
            }
        ]
    }
}

# ---------------------------------------------------------
# 3. Helper: Solar AI & 국립국어원 수사지원 도구
# ---------------------------------------------------------
def ask_solar_ai(prompt):
    api_key = st.secrets.get("SOLAR_API_KEY", "")
    if not api_key:
        return "Solar API 키가 설정되지 않았습니다. Secrets를 확인하세요."
    try:
        url = "https://api.upstage.ai/v1/solar/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "json"}
        payload = {
            "model": "solar-1-mini-chat",
            "messages": [
                {"role": "system", "content": "너는 미디어 리터러시 수사를 돕는 친절한 AI 수사 조교야. 학생의 단어 질문이나 질문에 명쾌하고 쉽게 답해줘."},
                {"role": "user", "content": prompt}
            ]
        }
        res = requests.post(url, headers=headers, json=payload, timeout=5)
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 연결 중 오류 발생: {e}"

# ---------------------------------------------------------
# 4. 사이드바 - 수사관 정보 & AI/사전 수사지원 도우미
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🕵️‍♂️ SF 수사관 본부")
    investigator = st.text_input("수사관 이름", value="하랑")
    
    st.markdown("---")
    st.markdown("### 🤖 24시간 AI & 어휘 수사 도우미")
    query_word = st.text_input("모르는 단어/용어 질문", placeholder="예: 딥페이크, 필터버블")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📖 표준사전 검색"):
            if query_word:
                st.info(f"[{query_word}] 사전 뜻 검색 링크 연결 중...")
                st.markdown(f"[국립국어원 바로가기](https://stdict.korean.go.kr/search/searchResult.do?searchKeyword={query_word})")
    with col_btn2:
        if st.button("🤖 Solar AI 질문"):
            if query_word:
                with st.spinner("AI 조교 답변 생성 중..."):
                    answer = ask_solar_ai(f"중고등학생 눈높이에서 '{query_word}'의 뜻을 쉽게 설명해줘.")
                    st.success(answer)

    st.markdown("---")
    selected_monster = st.radio("👾 몬스터 사건 현장 바로가기", list(CASES_DB.keys()))

# ---------------------------------------------------------
# 5. 메인 화면 - 마이너리티 리포트 HUD 사건 수사
# ---------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #38bdf8;'>🔮 MONSTER INSIGHT : MINORITY HUD</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>수사관 <b>[{investigator}]</b>님, AI 미디어 몬스터의 이상 징후를 추적하세요.</p>", unsafe_allow_html=True)

tab_game, tab_teacher = st.tabs(["🕵️‍♂️ 사건 현장 수사", "📊 교사용 시각화 대시보드"])

with tab_game:
    st.markdown(f"<div class='hud-card'><h3>현장 타겟: {selected_monster}</h3></div>", unsafe_allow_html=True)
    
    monster_data = CASES_DB[selected_monster]
    
    # 1. 외부 실시간 웹 바로가기 지원
    if monster_data.get("external_link"):
        st.markdown(f"🔗 **[수사 도구]** [실제 {selected_monster} 검증 웹사이트 열기]({monster_data['external_link']})")
    
    # 2. 사건 수사 시작 (랜덤 추출)
    if st.button("🚨 사건 수사 시작 (랜덤 케이스 배정)"):
        st.session_state['current_case'] = random.choice(monster_data["cases"])
        
    if 'current_case' in st.session_state:
        cur_case = st.session_state['current_case']
        
        st.markdown(f"""
        <div class='hud-card'>
            <h4>{cur_case['title']}</h4>
            <p style='font-size: 1.1rem;'>{cur_case['content']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_choice = st.radio("수사관의 선택:", cur_case['options'])
        
        if st.button("판정 제출"):
            chosen_idx = cur_case['options'].index(user_choice)
            if chosen_idx == cur_case['answer']:
                st.balloons()
                st.success(f"🎯 수사 성공! {cur_case['solution']}")
            else:
                st.error("⚠️ 잘못된 판단입니다! 다시 분석해보세요.")

# ---------------------------------------------------------
# 6. 교사용 Plotly 시각화 대시보드
# ---------------------------------------------------------
with tab_teacher:
    st.markdown("<div class='hud-card'><h3>📊 학급 전체 몬스터 수사 통계 (Plotly HUD)</h3></div>", unsafe_allow_html=True)
    
    # 예시 집계 데이터
    dummy_data = pd.DataFrame({
        "몬스터": ["🤖 딥페이크", "🧠 AI 환각", "🕷️ 알고리즘", "👻 루머 유령", "📦 피싱 박스"],
        "검거 횟수": [45, 32, 28, 19, 38],
        "위험도": [85, 90, 70, 60, 95]
    })
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Plotly 파이 차트
        fig_pie = px.pie(dummy_data, values='검거 횟수', names='몬스터', hole=0.4,
                         title="몬스터별 해결 비율", template="plotly_dark")
        fig_pie.update_traces(marker=dict(colors=['#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#fb7185']))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        # Plotly 3D/막대 차트
        fig_bar = px.bar(dummy_data, x='몬스터', y='위험도', color='몬스터',
                         title="몬스터별 평균 미디어 위협도", template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)
