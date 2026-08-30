import streamlit as st
from datetime import date, timedelta
import pandas as pd
import re
import os
import base64
import time

# 1. 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 🎨 UI 디자인 20.0 (모든 입력창 자동완성 통일)
# ==========================================
st.markdown("""
    <style>
    a.home-link { text-decoration: none !important; }
    
    .hallabong-title {
        background: linear-gradient(135deg, #ff9800 0%, #e65100 100%);
        padding: 15px; border-radius: 20px; text-align: center; color: white;
        font-weight: 900; font-size: 2.8rem; box-shadow: 0px 6px 15px rgba(230, 81, 0, 0.3);
        margin-bottom: 20px; border: 3px solid #ffcc80; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
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
    input[type="text"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input, div[data-testid="stTimeInput"] input, textarea { 
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

    @media (prefers-color-scheme: dark) {
        input[type="text"], div[data-baseweb="select"] > div, div[data-testid="stDateInput"] > div, div[data-testid="stTimeInput"] > div, textarea {
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
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 세션 초기화 및 데이터 로딩
# ==========================================
if 'notices' not in st.session_state:
    st.session_state.notices = ["<b>[필독]</b> 장마철 검은점무늬병 주의보 발령", "[안내] 신규 등록 약제(살균제) 3종 리스트 업데이트 완료"]
if 'qnas' not in st.session_state:
    st.session_state.qnas = [{"author": "제주농부", "content": "잎 뒷면에 이런 하얀 딱지가 생겼는데 더뎅이병일까요?", "reply": "👨‍🌾 KIMBO: 사진상으로는 볼록총채벌레 피해 흔적과 유사해 보입니다."}]
if 'spray_history' not in st.session_state:
    st.session_state.spray_history = pd.DataFrame({
        "방제일자": ["2026년 08월 12일(수)"], "방제시작": ["05:00"], "작물명": ["노지 감귤"], "총 살포량": ["1000 L"],
        "약제종류": ["살균제"], "상품명": ["다이센엠"], "작용기작": ["카"], "규격": ["1kg"], "수량": ["2개"],
        "적용병해충": ["검은점무늬병"], "계통": ["만코제브"], "메모": ["장마 후 예방살포"]
    })

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
if 'list_count' not in st.session_state: st.session_state.list_count = 5

# ==========================================
# 🧩 UI 컴포넌트 함수 (팝업 등)
# ==========================================
def render_styled_dataframe(df):
    display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충', '계통']
    df = df[[col for col in display_columns if col in df.columns]].copy()
    styled_df = df.style.set_properties(**{'font-size': '15px', 'font-weight': '600', 'padding': '8px 10px', 'text-align': 'center'})
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

@st.dialog("🔬 작용기작 상세 팝업")
def show_moa_popup(moa_string):
    df_moa = load_moa_data()
    moa_list = [m.strip() for m in str(moa_string).replace(',', '+').replace('/', '+').split('+') if m.strip()]
    for code in moa_list:
        res = df_moa[df_moa['표시기호'].astype(str) == code]
        if not res.empty:
            r = res.iloc[0]
            st.markdown(f"### {code} | {r.get('농약종류', '')}<br>세부: **{r.get('세부 작용기작 및 계통(성분)', '')}**", unsafe_allow_html=True)
    if st.button("❌ 닫기", use_container_width=True): st.rerun()

def render_moa_popup_trigger(df_current_result):
    unique_moas = [m for m in df_current_result['작용기작'].dropna().unique() if str(m).strip() and str(m).strip() != 'nan']
    if unique_moas:
        col_sel, col_btn, _ = st.columns([3, 2, 5])
        with col_sel: selected_moa = st.selectbox("팝업 코드", options=unique_moas, label_visibility="collapsed")
        with col_btn: 
            if st.button("팝업 열기 🔍"): show_moa_popup(str(selected_moa))

@st.dialog("🦠 병해충 상세 정보")
def show_pest_popup(pest_name, prob, desc):
    st.markdown(f"<h2 style='color: #e65100; margin-top: 0;'>{pest_name}</h2><h4 style='color: #4CAF50;'>AI 일치율: {prob}%</h4><hr>", unsafe_allow_html=True)
    st.info(f"📸 여기에 '{pest_name}'의 대표 사진이 표시됩니다.")
    st.markdown(f"<p style='font-size: 16px; line-height: 1.6;'>{desc}</p>", unsafe_allow_html=True)
    if st.button("❌ 닫기", use_container_width=True): st.rerun()

def render_weather_section():
    st.markdown("<div class='custom-card card-weather'>📍 제주시 조천읍 감귤원 날씨<br>🌤️ 28℃ | 습도 75% | 풍속 3.2m/s</div>", unsafe_allow_html=True)

# ==========================================
# 🚀 메인 화면 구성
# ==========================================
icon_tag = '🍊'
st.markdown(f"<a href='/' target='_self' class='home-link'><div class='hallabong-title'>{icon_tag} 내가 찾는 농약</div></a>", unsafe_allow_html=True)

# 🌟 메뉴에 "병충해 찾기" 추가 완료
menu = st.radio("메인 메뉴", ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 찾기", "나의 방제이력", "병충해 찾기", "정보교환마당"], horizontal=True, label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------
if menu == "내가 필요한 농약 찾기":
    col_main, col_img = st.columns([7, 3])
    with col_main:
        with st.form("search_form"):
            target_pest = st.multiselect("방제 대상 병해충", options=pest_list)
            desired_pesticide = st.multiselect("희망 약제명", options=pesticide_list)
            submitted = st.form_submit_button("🔎 농약 찾기")
        if submitted:
            st.session_state.df_result = df_database.copy()
            if target_pest: st.session_state.df_result = st.session_state.df_result[st.session_state.df_result['적용병해충'].astype(str).str.contains('|'.join(target_pest))]
        if 'df_result' in st.session_state and not st.session_state.df_result.empty:
            render_styled_dataframe(st.session_state.df_result.head(5))
            render_moa_popup_trigger(st.session_state.df_result.head(5))
    with col_img: render_weather_section()

# ----------------------------------------
elif menu in ["농약명으로 찾기", "병해충명으로 찾기"]:
    search_val = st.selectbox("검색어 입력:", options=pesticide_list if menu=="농약명으로 찾기" else pest_list)
    if search_val:
        col = '상품명' if menu=="농약명으로 찾기" else '적용병해충'
        res = df_database[df_database[col].astype(str).str.contains(search_val)]
        render_styled_dataframe(res)
        render_moa_popup_trigger(res)

# ----------------------------------------
elif menu == "작용기작 찾기":
    st.info("작용기작 코드를 선택하세요.")

# ----------------------------------------
elif menu == "나의 방제이력":
    st.subheader("📋 나의 방제이력")
    st.dataframe(st.session_state.spray_history)
    with st.expander("➕ 방제 기록 추가 (최대 6개 혼용)"):
        with st.form("history_form"):
            h_date = st.date_input("방제일자")
            sel_name = st.selectbox("약제 1 상품명", options=[""] + pesticide_list)
            if st.form_submit_button("저장"): st.success("저장되었습니다! (약식 구현)")

# ----------------------------------------
# 🌟 신규 기능: 병충해 찾기 (AI 판독)
# ----------------------------------------
elif menu == "병충해 찾기":
    st.subheader("📸 AI 병해충 사진 판독")
    st.markdown("과수원에서 발견한 병해충 의심 사진을 업로드하거나 직접 촬영해 주세요.")
    
    col_upload, col_camera = st.columns(2)
    with col_upload:
        uploaded_files = st.file_uploader("이미지 업로드 (최대 5장)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        if len(uploaded_files) > 5:
            st.warning("사진은 최대 5장까지 분석 가능합니다. 초과된 사진은 제외됩니다.")
            uploaded_files = uploaded_files[:5]
    with col_camera:
        camera_image = st.camera_input("또는 카메라로 직접 촬영")

    images_to_analyze = uploaded_files if uploaded_files else []
    if camera_image: images_to_analyze.append(camera_image)

    if images_to_analyze:
        st.success(f"✅ 총 {len(images_to_analyze)}장의 사진이 입력되었습니다.")
        
        if st.button("🚀 AI 판독 시작", type="primary"):
            with st.spinner("AI가 사진의 유효성을 검사하고 판독 중입니다..."):
                time.sleep(2) # 통신 지연 시뮬레이션
                
                # 1) 유효성 검사
                is_valid = all(img.size > 0 for img in images_to_analyze)
                
                if not is_valid:
                    st.error("🚨 [사진판독 불가] 입력된 사진이 손상되었거나 인식할 수 없습니다. 다시 촬영해 주세요.")
                else:
                    # 2) 판독 결과 생성 (현재는 가상 데이터)
                    st.session_state.ai_results = [
                        {"name": "검은점무늬병", "prob": 88.5, "desc": "주로 장마철 빗물에 의해 감염되며 잎과 과실에 흑갈색 점이 생깁니다."},
                        {"name": "더뎅이병", "prob": 35.2, "desc": "봄철 새순이나 어린 과실에 코르크화된 돌기가 생기는 병입니다."},
                        {"name": "볼록총채벌레 피해", "prob": 12.8, "desc": "과실 표면에 은백색 또는 회갈색의 흉터를 남깁니다."}
                    ]
                    
    # 3) 결과 및 유의사항 출력
    if 'ai_results' in st.session_state and images_to_analyze:
        st.markdown("### 🔍 AI 판독 결과 (가능성 높은 3가지)")
        cols = st.columns(3)
        for i, res in enumerate(st.session_state.ai_results):
            with cols[i]:
                st.markdown(f"""
                    <div style='text-align:center; padding:15px; border:2px solid #ffcc80; border-radius:12px; background-color:#fff8e1; margin-bottom:10px;'>
                        <h3 style='color:#e65100; margin:0 0 5px 0;'>{res['name']}</h3>
                        <p style='font-size:22px; font-weight:900; margin:0; color:#2e7d32;'>{res['prob']}%</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # 4) 선택 시 팝업 호출
                if st.button(f"상세 정보 보기 👆", key=f"btn_ai_{i}", use_container_width=True):
                    show_pest_popup(res['name'], res['prob'], res['desc'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("⚠️ **유의사항:** AI 정밀판독 결과이나 오류가 있을 수 있습니다. 최종 방제 결정 전 전문가의 진단이나 농업기술원의 안내를 참고하시기 바랍니다.")

# ----------------------------------------
elif menu == "정보교환마당":
    st.subheader("💬 정보교환마당")
    st.info("공지사항 및 Q&A 게시판")