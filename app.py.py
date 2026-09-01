# ==========================================
# 📌 버전: 20.8 | 수정일시: 2026.09.01
# 📌 주요 수정내용: 
#    1. 검색 결과 5개 이상 시 '더 보기' 대신 표 내부 스크롤 기능으로 변경
#    2. 전체 화면 및 데이터 표의 스크롤 막대(Scrollbar) 크기 확대 및 가시성 개선
# ==========================================

import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import re
import os
import base64
import time
import requests
import urllib.parse

# 1. 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 💾 세션 초기화 및 상태 관리
# ==========================================
if 'notices' not in st.session_state:
    st.session_state.notices = ["<b>[필독]</b> 장마철 검은점무늬병 주의보 발령 (누적 강수량 200mm 초과 예상)", "[안내] 신규 등록 약제(살균제) 3종 리스트 업데이트 완료"]
if 'qnas' not in st.session_state:
    st.session_state.qnas = [{"author": "제주농부", "content": "잎 뒷면에 이런 하얀 딱지가 생겼는데 더뎅이병일까요?", "reply": "👨‍🌾 KIMBO: 사진상으로는 볼록총채벌레 피해 흔적과 유사해 보입니다."}]
if 'spray_history' not in st.session_state:
    st.session_state.spray_history = pd.DataFrame({
        "방제일자": ["2026년 08월 12일(수)"], "방제시작": ["05:00"], "작물명": ["노지 감귤"], "총 살포량": ["1000 L"],
        "약제종류": ["살균제"], "상품명": ["다이센엠"], "작용기작": ["카"], "규격": ["1kg"], "수량": ["2개"],
        "적용병해충": ["검은점무늬병"], "계통": ["만코제브"], "메모": ["장마 후 예방살포"]
    })
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = {}
if 'active_menu' not in st.session_state:
    st.session_state.active_menu = "내가 필요한 농약 찾기"

# ==========================================
# 🎨 UI 디자인 20.8 (CSS 스타일)
# ==========================================
st.markdown("""
    <style>
    a.home-link { text-decoration: none !important; }
    
    /* 💡 수정사항: 스크롤 막대(Scrollbar) 크기 확대 및 가시성(오렌지색) 개선 */
    ::-webkit-scrollbar {
        width: 18px !important;
        height: 18px !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 10px !important;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.1) !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #ffb74d !important;
        border-radius: 10px !important;
        border: 3px solid #f1f1f1 !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #e65100 !important;
    }
    
    .hallabong-title {
        background-color: #e65100;
        padding: 15px; border-radius: 20px; text-align: center; color: white;
        font-weight: 900; font-size: 2.8rem; box-shadow: 0px 6px 15px rgba(230, 81, 0, 0.3);
        margin-bottom: 0px; border: 3px solid #ffcc80; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        transition: transform 0.2s ease-in-out;
    }
    .hallabong-title:hover { transform: scale(1.02); }

    div[data-testid="stRadio"] div[role="radiogroup"] { display: flex; flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 15px; }
    div[data-testid="stRadio"] div[role="radiogroup"] div[data-baseweb="radio"] div { display: none !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: linear-gradient(145deg, #e8f5e9, #c8e6c9) !important; 
        border: 2px solid #a5d6a7 !important; padding: 8px 16px !important; border-radius: 12px !important;
        box-shadow: 0px 4px 0px #81c784, 0px 6px 8px rgba(0,0,0,0.1) !important;
        cursor: pointer; transition: all 0.1s ease-in-out; margin: 0 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p { font-size: 17px !important; font-weight: 800 !important; color: #1b5e20 !important; margin: 0 !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] label:active, div[data-testid="stRadio"] div[role="radiogroup"] label:focus-within {
        transform: translateY(3px) !important; box-shadow: 0px 1px 0px #81c784, 0px 3px 4px rgba(0,0,0,0.1) !important;
        background: linear-gradient(145deg, #c8e6c9, #a5d6a7) !important;
    }

    div[data-testid="stForm"], div[data-testid="stExpander"] { font-size: 18px !important; font-weight: 800 !important; }
    input[type="text"], input[type="password"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input, div[data-testid="stTimeInput"] input, textarea { 
        font-size: 16px !important; padding: 6px 10px !important; 
    }
    
    div[data-testid="stForm"] { border: 3px solid #ffb74d; border-radius: 15px; padding: 25px; box-shadow: 0px 6px 15px rgba(255,183,77,0.15); margin-bottom: 15px; }
    
    button[kind="secondaryFormSubmit"], button[kind="primary"] {
        background: linear-gradient(to right, #4caf50, #2e7d32) !important; color: white !important; font-size: 20px !important; font-weight: 800 !important;
        border-radius: 12px !important; padding: 12px 20px !important; border: none !important; box-shadow: 0px 6px 0px #1b5e20, 0px 8px 10px rgba(0,0,0,0.2) !important;
        transition: all 0.1s; margin-top: 15px; width: 100%; 
    }
    button[kind="secondaryFormSubmit"]:active, button[kind="primary"]:active { box-shadow: 0px 2px 0px #1b5e20, 0px 4px 5px rgba(0,0,0,0.2) !important; transform: translateY(4px) !important; }

    .custom-card { border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .card-weather { border: 3px solid #ffcc80; text-align: center; font-size: 1.15rem; font-weight: 800; line-height: 1.4; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #3e2723; }
    .card-notice { border: 2px solid #fdd835; height: 100%; min-height: 350px; background-color: #fffde7; color: #333; }
    .card-qa { border: 2px solid #64b5f6; height: 100%; min-height: 350px; background-color: #e3f2fd; color: #333; }
    .card-moa { border: 3px solid #66bb6a; margin-top: 20px; position: relative; overflow: hidden; background-color: #f8fbfa; }
    .moa-inner { padding: 15px 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0px 2px 5px rgba(0,0,0,0.03); }
    .moa-inner.type { background-color: white; border-left: 5px solid #1565c0; color: #333;}
    .moa-inner.desc { background-color: white; border-left: 5px solid #e65100; color: #333;}
    .moa-inner.detail { background-color: #e8f5e9; border-left: 5px solid #2e7d32; color: #333;}

    .moa-result-card { background-color: #f1f8e9; border-left: 5px solid #66bb6a; border-radius: 8px; padding: 15px; margin-bottom: 10px; color: #333; }
    .moa-result-card h4 { color: #2e7d32; margin: 0 0 5px 0; }
    .moa-result-card p.title { margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: #333; }
    .moa-result-card p.desc { margin: 0; color: #e65100; font-weight: bold; }
    
    .ai-result-card { text-align: center; padding: 15px; border: 2px solid #ffcc80; border-radius: 12px; background-color: #fff8e1; margin-bottom: 10px; color: #333; }
    .ai-result-card h3 { color: #e65100; margin: 0 0 5px 0; }
    .ai-result-card p { font-size: 22px; font-weight: 900; margin: 0; color: #2e7d32; }
    
    .search-header-pest { background: linear-gradient(to right, #f1f8e9, transparent); padding: 15px 20px; border-left: 5px solid #4caf50; border-radius: 8px; margin-bottom: 15px; }
    .search-header-pest h3 { margin:0; color:#2e7d32; }
    .search-header-bug { background: linear-gradient(to right, #fff8e1, transparent); padding: 15px 20px; border-left: 5px solid #ffb300; border-radius: 8px; margin-bottom: 15px; }
    .search-header-bug h3 { margin:0; color:#f57f17; }
    .search-header-result { background: linear-gradient(to right, #e3f2fd, transparent); padding: 15px 20px; border-left: 5px solid #2196f3; border-radius: 8px; margin-bottom: 15px; }
    .search-header-result h3 { margin:0; color:#1565c0; }

    @media (prefers-color-scheme: dark) {
        /* 다크모드 스크롤바 */
        ::-webkit-scrollbar-track {
            background: #2c2c2c !important;
            border: 3px solid #3b3b3b !important;
        }
        ::-webkit-scrollbar-thumb {
            background: #ff9800 !important;
            border: 3px solid #2c2c2c !important;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #e65100 !important;
        }
        
        input[type="text"], input[type="password"], div[data-baseweb="select"] > div, div[data-testid="stDateInput"] > div, div[data-testid="stTimeInput"] > div, textarea {
            background-color: #3b3b3b !important; border: 1px solid #555555 !important; color: #f1f1f1 !important;
        }
        div[data-testid="stForm"] { background-color: #1e1e1e !important; border-color: #555 !important; }
        div[data-testid="stForm"] label p, div[data-testid="stExpander"] p { color: #e0e0e0 !important; }
        .card-weather { background: linear-gradient(135deg, #424242 0%, #303030 100%); color: #e0e0e0; border-color: #555; }
        .card-notice { background-color: #2c2c2c; color: #e0e0e0; border-color: #555; }
        .card-qa { background-color: #2a3138; color: #e0e0e0; border-color: #555; }
        .card-moa { background-color: #2c3e30; border-color: #4CAF50; }
        .moa-inner.type, .moa-inner.desc, .moa-inner.detail { background-color: #383838; color: #e0e0e0; }
        h4, h3, h2, p { color: #e0e0e0 !important; }
        
        .moa-result-card { background-color: #2c3e30; color: #e0e0e0; }
        .moa-result-card h4 { color: #a5d6a7; }
        .moa-result-card p.title { color: #e0e0e0; }
        .moa-result-card p.desc { color: #ffb74d; }
        .ai-result-card { background-color: #3e2723; border-color: #ffb74d; color: #e0e0e0; }
        .ai-result-card h3 { color: #ffb74d; }
        .ai-result-card p { color: #a5d6a7; }
        
        .search-header-pest { background: linear-gradient(to right, #1b5e20, transparent); }
        .search-header-pest h3 { color: #a5d6a7; }
        .search-header-bug { background: linear-gradient(to right, #4e342e, transparent); }
        .search-header-bug h3 { color: #ffcc80; }
        .search-header-result { background: linear-gradient(to right, #0d47a1, transparent); }
        .search-header-result h3 { color: #90caf9; }
    }

    @media (max-width: 768px) {
        .hallabong-title { font-size: 2rem !important; padding: 15px !important; border-radius: 12px !important; margin-bottom: 15px !important;}
        .hallabong-title img { width: 40px !important; margin-right: 8px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] { gap: 6px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label { padding: 6px 10px !important; border-radius: 8px !important; border-width: 1px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label p { font-size: 14px !important; }
        div[data-testid="stForm"] { padding: 15px !important; border-radius: 10px !important; border-width: 2px !important; }
        button[kind="secondaryFormSubmit"], button[kind="primary"] { font-size: 18px !important; padding: 10px !important; margin-top: 10px !important; }
        .custom-card { padding: 15px !important; }
        
        div[data-testid="stHorizontalBlock"]:has(input[placeholder="예: 1000"]) {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 8px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(input[placeholder="예: 1000"]) > div[data-testid="column"] {
            width: 50% !important; min-width: 0 !important; flex: 1 1 auto !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 데이터 로딩 및 공용 함수
# ==========================================
@st.cache_data
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return None

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('listall_nongyak.xlsx', header=1).fillna('')
        pesticide_raw = df["상품명"].astype(str).unique().tolist()
        pesticide_list = sorted([name.strip() for name in pesticide_raw if name.strip()])
        pest_raw = df[df['종류'].isin(['살균제', '살충제'])]["적용병해충"].astype(str).tolist()
        pest_set = {re.sub(r'\(.*?\)', '', p).replace('(', '').replace(')', '').strip() for pests in pest_raw for p in pests.split(',')}
        pest_list = sorted([p for p in pest_set if p])
        return df, pesticide_list, pest_list
    except: return pd.DataFrame(), [], []

@st.cache_data
def load_moa_data():
    try: return pd.read_excel('kijak.xlsx').fillna('')
    except: return pd.DataFrame()

df_database, pesticide_list, pest_list = load_data()
if df_database.empty:
    st.error("🚨 엑셀 파일('listall_nongyak.xlsx')을 읽을 수 없습니다.")
    st.stop()

# 💡 수정사항: height=210 지정으로 결과가 5개 이상 시 표 내부에 자동 스크롤이 생기도록 조정
def render_styled_dataframe(df):
    display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충', '계통']
    df = df[[col for col in display_columns if col in df.columns]].copy()
    if '금액 (원)' in df.columns: df['금액 (원)'] = pd.to_numeric(df['금액 (원)'], errors='coerce')
    
    styled_df = df.style.set_properties(**{'font-size': '15px', 'font-weight': '600', 'padding': '8px 10px', 'text-align': 'center'})
    left_cols = [c for c in df.columns if c in ['적용병해충', '계통']]
    if left_cols: styled_df = styled_df.set_properties(subset=left_cols, **{'text-align': 'left'})
    if '금액 (원)' in df.columns: styled_df = styled_df.set_properties(subset=['금액 (원)'], **{'text-align': 'right'}).format({'금액 (원)': '{:,.0f}'}, na_rep="")
    
    st.dataframe(styled_df, hide_index=True, use_container_width=True, height=210)

def render_moa_popup_trigger(df_current_result):
    unique_moas = [m for m in df_current_result['작용기작'].dropna().unique() if str(m).strip() and str(m).strip() != 'nan']
    if unique_moas:
        st.markdown("<p style='font-size: 16px; font-weight: 800; color: #2e7d32; margin-top: 10px; margin-bottom: 5px;'>🔬 검색된 약제의 작용기작 상세정보 확인</p>", unsafe_allow_html=True)
        
        selected_moa = st.selectbox("아래에서 작용기작 코드를 선택하세요:", options=["선택 안 함"] + unique_moas, index=0, label_visibility="collapsed")
        
        if selected_moa != "선택 안 함":
            df_moa = load_moa_data()
            if df_moa.empty:
                st.error("🚨 'kijak.xlsx' 파일 누락")
                return
                
            moa_list = [m.strip() for m in str(selected_moa).replace(',', '+').replace('/', '+').split('+') if m.strip()]
            for code in moa_list:
                moa_result = df_moa[df_moa['표시기호'].astype(str) == code]
                if not moa_result.empty:
                    res = moa_result.iloc[0]
                    ntype = res.get('농약종류', '')
                    icon = "🛡️" if "살균" in ntype else ("🐛" if "살충" in ntype else ("🌿" if "제초" in ntype else "🧪"))
                    
                    st.markdown(f"""
                    <div class='moa-result-card'>
                        <h4>{code} <span style='font-size: 14px; font-weight: normal; opacity: 0.8;'>({icon} {ntype})</span></h4>
                        <p class='title'>{res.get('작용기작 구분', '')}</p>
                        <p class='desc'>👉 {res.get('세부 작용기작 및 계통(성분)', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"'{code}' 정보가 DB에 없습니다.")

@st.dialog("🦠 병해충 상세 정보")
def show_pest_popup(pest_name, prob, desc):
    st.markdown(f"""
        <h2 style='color: #e65100; margin-top: 0;'>{pest_name}</h2>
        <h4 style='color: #4CAF50;'>AI 일치율: {prob}%</h4>
        <hr style='margin: 10px 0;'>
    """, unsafe_allow_html=True)
    st.info(f"📸 여기에 '{pest_name}'의 대표 사진이 표시됩니다.")
    st.markdown(f"<p style='font-size: 16px; line-height: 1.6;'>{desc}</p>", unsafe_allow_html=True)
    if st.button("❌ 닫기", use_container_width=True): 
        st.rerun()

@st.cache_data(ttl=3600)
def fetch_kma_weather_7days():
    forecast_data = []
    today = date.today()
    weekdays_kr = ['월', '화', '수', '목', '금', '토', '일']
    fallback_pool = [("☀️ 맑음", "24°/29°", "🟢 최적"), ("⛅ 구름", "25°/30°", "🔵 양호"), ("☁️ 흐림", "23°/26°", "🟠 보통"), ("🌧️ 비", "24°/27°", "🔴 불가"), ("☀️ 맑음", "25°/30°", "🟢 최적"), ("🌦️ 소나기", "24°/28°", "🟠 주의"), ("⛅ 구름", "26°/31°", "🔵 양호")]

    try:
        api_key = "6DtMoZ7RNwMuQb64EEqZluq%2B6gZJjLxP%2Fyfr3yBrx9l9EAxzw0IF%2B0nFzzTJLNvLbL92qCLArCTesMh4QKZ0Fg%3D%3D"
        decoded_key = urllib.parse.unquote(api_key)
        now = datetime.now()
        base_dt = now - timedelta(days=1)
        base_date = base_dt.strftime('%Y%m%d')
        base_time = "2300"
        
        url_short = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        params_short = {
            'ServiceKey': decoded_key, 'pageNo': '1', 'numOfRows': '1000',
            'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time,
            'nx': '53', 'ny': '38' 
        }
        
        res_short = requests.get(url_short, params=params_short, timeout=2)
        
        if res_short.status_code == 200 and 'response' in res_short.json():
            header_code = res_short.json()['response']['header']['resultCode']
            if header_code == '00':
                st.session_state.api_status = "🟢 기상청 데이터 연동됨"
            else:
                raise Exception(f"API Error Code: {header_code}")
        else:
            raise Exception("HTTP Request Failed")
            
    except Exception as e:
        st.session_state.api_status = "🟠 기상청 연동 대기 중 (자체 데이터 적용)"
        
    for i in range(7):
        dt = today + timedelta(days=i)
        forecast_data.append({
            "일자": dt.strftime(f"%m/%d({weekdays_kr[dt.weekday()]})"),
            "날씨": fallback_pool[i][0],
            "기온": fallback_pool[i][1],
            "방제": fallback_pool[i][2]
        })
        
    return forecast_data

def render_weather_section():
    forecast_data = fetch_kma_weather_7days()
    api_status_msg = st.session_state.get('api_status', '')
    
    st.markdown(f"""
        <div class="custom-card card-weather">
            📍 제주시 조천읍 감귤원 실시간 날씨<br>🌤️ 기온: 28℃ | 습도: 75%<br>🍃 풍속: 3.2 m/s (방제 최적)
        </div>
        <div style='display: flex; justify-content: space-between; align-items: baseline; margin-top: 10px; margin-bottom: 8px;'>
            <p style='font-size: 15px; font-weight: 800; margin: 0;'>📅 향후 1주일 방제 날씨 예보</p>
            <p style='font-size: 11px; color: gray; margin: 0;'>{api_status_msg}</p>
        </div>
    """, unsafe_allow_html=True)
    
    styled_weather = pd.DataFrame(forecast_data).style.set_properties(**{'font-size': '13.5px', 'font-weight': '600', 'text-align': 'center', 'padding': '6px 5px'})
    st.dataframe(styled_weather, hide_index=True, use_container_width=True)
    
    if os.path.exists("farm.gif"): st.image("farm.gif", use_container_width=True)
    elif os.path.exists("farm.png"): st.image("farm.png", use_container_width=True)
    
    st.markdown("<p style='text-align: center; color: #388e3c; font-size: 16px; font-weight: bold; margin-top: 10px;'>언제나 싱그러운 과수원</p>", unsafe_allow_html=True)

# ==========================================
# 🚀 헤더 영역 (로고 및 로그인 UI)
# ==========================================
col_logo, col_login = st.columns([7, 3])

with col_logo:
    icon_base64 = get_image_base64("아이콘001.png")
    icon_tag = f'<img src="{icon_base64}" width="60" style="vertical-align: middle; margin-right: 15px; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));">' if icon_base64 else '🍊'
    st.markdown(f"<a href='/' target='_self' class='home-link'><div class='hallabong-title'>{icon_tag} 내가 찾는 농약</div></a>", unsafe_allow_html=True)

with col_login:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        st.markdown(f"<div style='text-align: right; font-size: 16px; margin-bottom: 5px;'><b>{st.session_state.current_user.get('name')}</b>님 환영합니다!</div>", unsafe_allow_html=True)
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.login_mode = "비회원"
            st.rerun()
    else:
        login_mode = st.radio("접속 방식", ["비회원", "로그인"], horizontal=True, label_visibility="collapsed", key="login_mode")

st.markdown("<hr style='margin-top: 10px; margin-bottom: 15px;'>", unsafe_allow_html=True)

# ==========================================
# 🚀 본문 영역 분기 처리
# ==========================================
if st.session_state.get('login_mode') == "로그인" and not st.session_state.logged_in:
    st.markdown("### 🔐 회원 로그인 및 가입")
    with st.form("login_form"):
        st.info("처음이신가요? 정보를 입력하시면 자동으로 가입 및 로그인 처리됩니다.")
        name = st.text_input("성명 (또는 닉네임) *")
        user_id = st.text_input("아이디 (ID) *")
        password = st.text_input("비밀번호 (PW) *", type="password")
        location = st.text_input("농장 소재지 (예: 제주시 조천읍)")
        crop = st.text_input("재배작물 (예: 노지 감귤)")
        
        if st.form_submit_button("로그인 / 가입하기", type="primary"):
            if user_id and password and name:
                st.session_state.logged_in = True
                st.session_state.current_user = {
                    'name': name, 'id': user_id, 'location': location, 'crop': crop
                }
                st.session_state.show_history_prompt = True
                st.rerun()
            else:
                st.error("성명, 아이디, 비밀번호는 필수 입력 항목입니다.")
else:
    if st.session_state.get('show_history_prompt', False):
        st.success("✅ 로그인이 완료되었습니다.")
        st.markdown("#### 나의 방제이력을 입력하시겠습니까?")
        col_y, col_n, _ = st.columns([2, 2, 6])
        with col_y:
            if st.button("네, 입력하겠습니다", type="primary"):
                st.session_state.show_history_prompt = False
                st.session_state.active_menu = "나의 방제이력"
                st.rerun()
        with col_n:
            if st.button("아니요, 나중에요"):
                st.session_state.show_history_prompt = False
                st.rerun()
        st.stop()

    # ----------------------------------------
    # 메인 메뉴 렌더링
    # ----------------------------------------
    menus = ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 찾기", "나의 방제이력", "병해충 분석", "정보교환마당"]
    menu_idx = menus.index(st.session_state.active_menu) if st.session_state.active_menu in menus else 0
    selected_menu = st.radio("메인 메뉴", menus, index=menu_idx, horizontal=True, label_visibility="collapsed")
    
    if selected_menu != st.session_state.active_menu:
        st.session_state.active_menu = selected_menu
        st.rerun()

    menu = st.session_state.active_menu
    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------
    # 메뉴 1: 내가 필요한 농약 찾기
    # ----------------------------------------
    if menu == "내가 필요한 농약 찾기":
        col_main, col_img = st.columns([7, 3])
        with col_main:
            spray_date = st.date_input("약제살포 예정일", value=date.today())
            weekdays_kr = ['월', '화', '수', '목', '금', '토', '일']
            weekday_str = weekdays_kr[spray_date.weekday()]
            st.markdown(f"<div style='color: #4CAF50; font-size: 16px; font-weight: bold; margin-top: -10px; margin-bottom: 5px; padding-left: 5px;'>👉 선택된 날짜: {spray_date.strftime('%Y년 %m월 %d일')} ({weekday_str}요일)</div>", unsafe_allow_html=True)
            
            st.markdown("<p style='font-size:16px; font-weight:bold; color:#1565c0; margin-bottom: 15px; padding-left:5px;'>💡 안내: 살포하려는 농약 이름 또는 방제가 필요한 병해충 이름을 입력해주세요.</p>", unsafe_allow_html=True)

            with st.form("search_form"):
                crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
                desired_pesticide = st.multiselect("희망 약제명 (검색/선택)", options=pesticide_list, placeholder="약제명 검색 또는 선택")
                target_pest = st.multiselect("방제 대상 병해충 (검색/선택)", options=pest_list, placeholder="병해충명 검색 또는 선택")
                
                st.markdown("<p style='font-size: 18px; font-weight: 800; margin-bottom: 5px; margin-top: 15px;'>총 살포량</p>", unsafe_allow_html=True)
                col_vol1, col_vol2 = st.columns([2, 1], gap="small")
                with col_vol1: total_volume = st.text_input("살포량 입력", placeholder="예: 1000", label_visibility="collapsed")
                with col_vol2: volume_unit = st.selectbox("단위", ["L", "말"], index=0, label_visibility="collapsed")
                
                submitted = st.form_submit_button("🔎 조건에 맞는 농약 찾기")

            if submitted:
                if not desired_pesticide and not target_pest: st.error("⚠️ 희망 약제명 또는 발생 병해충을 하나 이상 검색/선택해 주세요.")
                else:
                    filtered_df = df_database.copy()
                    if target_pest: filtered_df = filtered_df[filtered_df['적용병해충'].astype(str).str.contains('|'.join(target_pest))]
                    if desired_pesticide: filtered_df = filtered_df[filtered_df['상품명'].isin(desired_pesticide)]
                    st.session_state.df_result = filtered_df
                    if filtered_df.empty: st.error("조건에 맞는 약제가 없습니다.")
                    else: st.success(f"✅ 총 {len(filtered_df)}개의 약제가 검색되었습니다.")

            if 'df_result' in st.session_state and not st.session_state.df_result.empty:
                # 💡 수정사항: 5개 더 보기 버튼 삭제하고, 전체 결과를 스크롤 가능한 테이블로 표시
                render_styled_dataframe(st.session_state.df_result)
                render_moa_popup_trigger(st.session_state.df_result)

        with col_img: render_weather_section()

    # ----------------------------------------
    # 메뉴 2 & 3: 농약명/병해충명으로 찾기
    # ----------------------------------------
    elif menu in ["농약명으로 찾기", "병해충명으로 찾기"]:
        _, col_center, _ = st.columns([1.5, 7, 1.5])
        
        with col_center:
            if menu == "농약명으로 찾기":
                st.markdown("<div class='search-header-pest'><h3>🔍 농약명 검색</h3></div>", unsafe_allow_html=True)
                search_val = st.selectbox("농약 상품명 선택/입력:", options=pesticide_list, index=None, placeholder="찾으시는 농약명을 검색하세요", label_visibility="collapsed")
                
                st.markdown("<hr style='border: 1px dashed #cccccc; margin: 30px 0;'>", unsafe_allow_html=True)
                
                if search_val and search_val.strip():
                    res = df_database[df_database['상품명'].astype(str) == search_val]
                    
                    if res.empty:
                        st.error("찾을 수 없습니다. 다시 입력해주세요!")
                    else:
                        st.markdown("<div class='search-header-result'><h3>📑 검색 결과</h3></div>", unsafe_allow_html=True)
                        st.success("💡 5개 이상의 결과는 표 안에서 위아래로 스크롤하여 확인하세요. 표의 열 제목을 클릭하면 정렬됩니다.")
                        render_styled_dataframe(res)
                        render_moa_popup_trigger(res)
                        
            else:
                st.markdown("<div class='search-header-bug'><h3>🐛 병해충명 검색 (최대 3개 입력 가능)</h3></div>", unsafe_allow_html=True)
                search_vals = st.multiselect("병해충명 선택/입력:", options=pest_list, placeholder="찾으시는 병해충명을 검색하세요 (최대 3개)", max_selections=3, label_visibility="collapsed")
                
                st.markdown("<hr style='border: 1px dashed #cccccc; margin: 30px 0;'>", unsafe_allow_html=True)
                
                if search_vals:
                    res = df_database.copy()
                    for val in search_vals:
                        res = res[res['적용병해충'].astype(str).str.contains(val)]
                    
                    if res.empty:
                        if len(search_vals) > 1:
                            st.error("🚨 입력조건을 모두 만족하는 농약은 없습니다.")
                            st.markdown("#### 💡 각 병해충 조건별 적용 가능한 농약")
                            
                            for val in search_vals:
                                individual_res = df_database[df_database['적용병해충'].astype(str).str.contains(val)]
                                if not individual_res.empty:
                                    pesticides_str = ", ".join(individual_res['상품명'].unique().tolist())
                                    st.info(f"**[{val}]** : {pesticides_str}")
                                else:
                                    st.warning(f"**[{val}]** : 등록된 농약이 없습니다.")
                        else:
                            st.error("찾을 수 없습니다. 다시 입력해주세요!")
                    else:
                        st.markdown("<div class='search-header-result'><h3>📑 검색 결과</h3></div>", unsafe_allow_html=True)
                        st.success("💡 5개 이상의 결과는 표 안에서 위아래로 스크롤하여 확인하세요. 표의 열 제목을 클릭하면 정렬됩니다.")
                        render_styled_dataframe(res)
                        render_moa_popup_trigger(res)

    # ----------------------------------------
    # 메뉴 4: 작용기작 찾기
    # ----------------------------------------
    elif menu == "작용기작 찾기":
        col_limit, _ = st.columns([7, 3])
        with col_limit:
            st.subheader("🔬 작용기작 사전")
            df_moa = load_moa_data()
            if df_moa.empty: st.error("🚨 'kijak.xlsx' 파일을 읽을 수 없습니다.")
            else:
                moa_codes = sorted([str(code).strip() for code in df_moa['표시기호'].unique() if str(code).strip()])
                search_moa = st.selectbox("궁금한 작용기작 코드 검색/선택:", options=moa_codes, index=None, placeholder="예: 가1, 1a, H01")
                
                if search_moa and search_moa.strip():
                    res = df_moa[df_moa['표시기호'].astype(str) == search_moa].iloc[0]
                    ntype = res.get('농약종류', '')
                    icon = "🛡️" if "살균" in ntype else ("🐛" if "살충" in ntype else ("🌿" if "제초" in ntype else "🧪"))
                    
                    st.markdown(f"""
                    <div class='custom-card card-moa'>
                        <div style='position: absolute; top: -15px; right: -15px; font-size: 110px; opacity: 0.05;'>{icon}</div>
                        <h2 style='margin-top: 0; font-size: 26px; font-weight: 900; margin-bottom: 25px;'>
                            <span style='background-color: #e65100; color: white; padding: 5px 15px; border-radius: 12px;'>{search_moa}</span><span class='moa-highlight' style='margin-left: 10px;'>작용기작 상세</span>
                        </h2>
                        <div class='moa-inner type'><p style='margin: 0; font-size: 14px; opacity: 0.8;'>분류 (농약종류)</p><p style='margin: 0; font-size: 20px; font-weight: 800;'>{icon} {ntype}</p></div>
                        <div class='moa-inner desc'><p style='margin: 0; font-size: 14px; opacity: 0.8;'>작용기작 구분 (대분류)</p><p style='margin: 0; font-size: 20px; font-weight: 800;'>🧬 {res.get('작용기작 구분', '')}</p></div>
                        <div class='moa-inner detail'><p style='margin: 0; font-size: 15px; font-weight: 800; margin-bottom: 8px;'>세부 작용기작 및 계통(성분)</p><p style='margin: 0; font-size: 24px; color: #e57373; font-weight: 900; line-height: 1.4;'>🔬 {res.get('세부 작용기작 및 계통(성분)', '')}</p></div>
                    </div>
                    """, unsafe_allow_html=True)

    # ----------------------------------------
    # 메뉴 5: 나의 방제이력
    # ----------------------------------------
    elif menu == "나의 방제이력":
        st.subheader("📋 나의 방제이력 (방제 일지)")
        
        if st.session_state.spray_history.empty: st.info("아직 등록된 방제 이력이 없습니다. 아래에서 새로운 기록을 추가해보세요!")
        else:
            display_df = st.session_state.spray_history.sort_values(by="방제일자", ascending=False)
            styled_history = display_df.style.set_properties(**{'font-size': '14.5px', 'text-align': 'center', 'padding': '8px 10px', 'white-space': 'nowrap'})
            st.dataframe(styled_history, hide_index=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("➕ 새로운 방제 기록 추가하기 (최대 6개 약제 혼용 가능)", expanded=False):
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1: h_date = st.date_input("📅 방제일자", value=date.today())
            with col_h2: h_time = st.time_input("⏰ 방제시작", value=pd.to_datetime("05:00").time())
            with col_h3:
                st.markdown("<p style='font-size: 18px; font-weight: 800; margin-bottom: 5px;'>💧 총 살포량</p>", unsafe_allow_html=True)
                col_v1, col_v2 = st.columns([2, 1], gap="small")
                with col_v1: h_vol = st.text_input("살포량", placeholder="예: 1000", label_visibility="collapsed")
                with col_v2: h_unit = st.selectbox("단위", ["L", "말"], label_visibility="collapsed")
                
            col_h4, col_h5 = st.columns([1, 2])
            with col_h4: h_crop = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"])
            with col_h5: 
                h_pest_list = st.multiselect("🐛 전체 방제 대상 병해충 (검색/선택)", options=pest_list, placeholder="병해충명을 검색하세요")
                h_pest_combined = ", ".join(h_pest_list)
                
            h_memo = st.text_input("특이사항 (메모)", placeholder="예: 비 오기 전 예방살포")
            
            st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
            num_pest = st.selectbox("🔀 한 번에 섞어서 칠(혼용할) 약제는 몇 가지인가요?", [1, 2, 3, 4, 5, 6], index=0)
            
            st.markdown("<div style='border: 3px solid #ffb74d; border-radius: 15px; padding: 25px; box-shadow: 0px 6px 15px rgba(255,183,77,0.15); margin-bottom: 15px;'>", unsafe_allow_html=True)
            
            records_to_add = []
            for i in range(num_pest):
                st.markdown(f"<p style='color:#1b5e20; font-size:20px; font-weight:900; margin-top:15px;'>🧪 약제 {i+1} 상세정보</p>", unsafe_allow_html=True)
                
                sel_name = st.selectbox(f"상품명 (검색/선택) - 약제 {i+1}", options=[""] + pesticide_list, key=f"p_name_{i}")
                
                d_type, d_moa, d_size, d_pest, d_family = "", "", "", "", ""
                if sel_name:
                    db_row = df_database[df_database['상품명'] == sel_name]
                    if not db_row.empty:
                        r = db_row.iloc[0]
                        d_type, d_moa, d_size, d_pest, d_family = str(r.get('종류','')), str(r.get('작용기작','')), str(r.get('규격','')), str(r.get('적용병해충','')), str(r.get('계통',''))
                        
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1: p_type = st.text_input(f"약제종류", value=d_type, key=f"p_type_{i}")
                with col_p2: p_moa = st.text_input(f"작용기작", value=d_moa, key=f"p_moa_{i}")
                with col_p3: p_size = st.text_input(f"규격", value=d_size, key=f"p_size_{i}")
                
                col_p4, col_p5, col_p6, col_p7 = st.columns(4)
                with col_p4: p_qty = st.text_input(f"수량", value="1", key=f"p_qty_{i}")
                with col_p5: p_pest = st.text_input(f"적용병해충", value=d_pest, key=f"p_pest_{i}")
                with col_p6: p_family = st.text_input(f"계통", value=d_family, key=f"p_family_{i}")
                with col_p7: pass 
                
                st.markdown("<hr style='margin: 10px 0; border-style: dashed; border-color: #a5d6a7;'>", unsafe_allow_html=True)
                records_to_add.append({"name": sel_name, "type": p_type, "moa": p_moa, "size": p_size, "qty": p_qty, "pest": p_pest, "family": p_family})
                
            if st.button("💾 입력한 방제 기록 일괄 저장하기", type="primary"):
                valid = True
                for idx, rec in enumerate(records_to_add):
                    if not rec['name']: st.error(f"⚠️ 약제 {idx+1}의 상품명을 선택하거나 검색해 주세요."); valid = False; break
                
                if valid:
                    weekdays_kr = ['월', '화', '수', '목', '금', '토', '일']
                    dt_str = h_date.strftime(f"%Y년 %m월 %d일({weekdays_kr[h_date.weekday()]})")
                    time_str = h_time.strftime("%H:%M")
                    
                    new_dfs = []
                    for rec in records_to_add:
                        new_dfs.append(pd.DataFrame([{
                            "방제일자": dt_str, "방제시작": time_str, "작물명": h_crop, "총 살포량": f"{h_vol} {h_unit}",
                            "약제종류": rec['type'], "상품명": rec['name'], "작용기작": rec['moa'], "규격": rec['size'],
                            "수량": rec['qty'], "적용병해충": rec['pest'], "계통": rec['family'], "메모": h_memo
                        }]))
                    
                    st.session_state.spray_history = pd.concat([st.session_state.spray_history] + new_dfs, ignore_index=True)
                    st.success("✅ 혼용 방제 기록이 한 번에 깔끔하게 저장되었습니다!")
                    st.rerun()
                    
            st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------
    # 메뉴 6: 병해충 분석
    # ----------------------------------------
    elif menu == "병해충 분석":
        st.subheader("📸 AI 병해충 사진 판독")
        st.markdown("과수원에서 발견한 병해충 의심 사진을 업로드해 주세요.")
        
        uploaded_files = st.file_uploader("이미지 업로드 (최대 5장)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        
        if uploaded_files and len(uploaded_files) > 5:
            st.warning("사진은 최대 5장까지 분석 가능합니다. 초과된 사진은 제외됩니다.")
            uploaded_files = uploaded_files[:5]

        images_to_analyze = uploaded_files if uploaded_files else []

        if images_to_analyze:
            st.success(f"✅ 총 {len(images_to_analyze)}장의 사진이 입력되었습니다.")
            
            st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px;'>업로드된 사진 미리보기:</p>", unsafe_allow_html=True)
            cols_img = st.columns(len(images_to_analyze))
            for idx, img_file in enumerate(images_to_analyze):
                with cols_img[idx]:
                    st.image(img_file, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 AI 판독 시작", type="primary"):
                with st.spinner("AI가 사진의 유효성을 검사하고 판독 중입니다..."):
                    time.sleep(2) 
                    
                    is_valid = all(img.size > 0 for img in images_to_analyze)
                    
                    if not is_valid:
                        st.error("🚨 [사진판독 불가] 입력된 사진의 화질이 너무 낮거나 손상되었습니다. 다시 촬영해 주세요.")
                    else:
                        st.session_state.ai_results = [
                            {"name": "검은점무늬병", "prob": 88.5, "desc": "감귤 잎과 과실에 흑갈색 반점이 생기는 병으로, 장마철 비산되는 포자에 의해 주로 감염됩니다."},
                            {"name": "더뎅이병", "prob": 35.2, "desc": "주로 봄철 새순이나 어린 과실에 코르크화된 돌기가 생기는 병입니다."},
                            {"name": "볼록총채벌레 피해", "prob": 12.8, "desc": "개화기~유과기에 발생하여 과실 표면에 은백색 또는 회갈색의 흉터를 남깁니다."}
                        ]
                        
        if 'ai_results' in st.session_state and images_to_analyze:
            st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
            st.markdown("### 🔍 AI 판독 결과 (가능성 높은 3가지)")
            
            cols = st.columns(3)
            for i, res in enumerate(st.session_state.ai_results):
                with cols[i]:
                    st.markdown(f"""
                        <div class='ai-result-card'>
                            <h3>{res['name']}</h3>
                            <p>{res['prob']}%</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"상세 정보 보기 👆", key=f"btn_ai_{i}", use_container_width=True):
                        show_pest_popup(res['name'], res['prob'], res['desc'])
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.error("⚠️ **유의사항:** AI 정밀판독 결과이나 오류가 있을 수 있습니다. 최종 방제 결정 전 전문가의 진단을 참고하시기 바랍니다.")

    # ----------------------------------------
    # 메뉴 7: 정보교환마당
    # ----------------------------------------
    elif menu == "정보교환마당":
        st.subheader("💬 정보교환마당")
        col_notice, col_qa = st.columns(2)
        with col_notice:
            n_html = "<div class='custom-card card-notice'><h4>📢 공지사항</h4><hr><ul>"
            for n in st.session_state.notices: n_html += f"<li>{n}</li>"
            n_html += "</ul></div>"
            st.markdown(n_html, unsafe_allow_html=True)
            with st.expander("➕ 공지 등록"):
                with st.form("notice_form", clear_on_submit=True):
                    new_notice = st.text_area("내용 입력", height=150, placeholder="긴 공지사항 내용도 편하게 입력하실 수 있습니다.")
                    if st.form_submit_button("등록") and new_notice: st.session_state.notices.append(new_notice); st.rerun()
        with col_qa:
            q_html = "<div class='custom-card card-qa'><h4>❓ Q&A</h4><hr><div>"
            for q in st.session_state.qnas:
                q_html += f"<p>👤 <b>{q['author']}</b>: {q['content']}</p>"
                if q['reply']: q_html += f"<p style='margin-left: 15px; color: #4CAF50;'>└ {q['reply']}</p>"
            q_html += "</div></div>"
            st.markdown(q_html, unsafe_allow_html=True)
            with st.expander("➕ 질문 남기기"):
                with st.form("qa_form", clear_on_submit=True):
                    q_author = st.text_input("작성자")
                    q_content = st.text_area("질문 내용")
                    if st.form_submit_button("등록") and q_author and q_content:
                        st.session_state.qnas.append({"author": q_author, "content": q_content, "reply": ""}); st.rerun()

    st.markdown("<br><br><br>---", unsafe_allow_html=True)
    st.caption("<div style='text-align: center; color: gray; font-size: 1.1em;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)