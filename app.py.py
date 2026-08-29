import streamlit as st
from datetime import date
import pandas as pd
import re
import os
import base64

# 1. 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 🎨 UI 디자인 17.0 (나의 방제이력 메뉴 추가)
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

    div[data-testid="stForm"] label p, div[data-testid="stSelectbox"] label p, div[data-testid="stMultiSelect"] label p, div[data-testid="stTextInput"] label p, div[data-testid="stDateInput"] label p, div[data-testid="stTextArea"] label p {
        font-size: 18px !important; font-weight: 800 !important; margin-bottom: 5px;
    }
    input[type="text"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input, textarea { 
        font-size: 16px !important; padding: 6px 10px !important; 
    }
    
    div[data-testid="stForm"] { 
        border: 3px solid #ffb74d; border-radius: 15px; padding: 25px; box-shadow: 0px 6px 15px rgba(255,183,77,0.15); margin-bottom: 15px; 
    }
    
    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(to right, #4caf50, #2e7d32) !important; color: white !important; font-size: 20px !important; font-weight: 800 !important;
        border-radius: 12px !important; padding: 12px 20px !important; border: none !important; box-shadow: 0px 6px 0px #1b5e20, 0px 8px 10px rgba(0,0,0,0.2) !important;
        transition: all 0.1s; margin-top: 15px; width: 100%; 
    }
    button[kind="secondaryFormSubmit"]:active { box-shadow: 0px 2px 0px #1b5e20, 0px 4px 5px rgba(0,0,0,0.2) !important; transform: translateY(4px) !important; }

    .custom-card { border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .card-weather { border: 3px solid #ffcc80; text-align: center; font-size: 1.15rem; font-weight: 800; line-height: 1.4; }
    .card-notice { border: 2px solid #fdd835; height: 100%; min-height: 350px; }
    .card-qa { border: 2px solid #64b5f6; height: 100%; min-height: 350px; }
    .card-moa { border: 3px solid #66bb6a; margin-top: 20px; position: relative; overflow: hidden; }
    .moa-inner { padding: 15px 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0px 2px 5px rgba(0,0,0,0.03); }

    .card-weather { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #3e2723; }
    .card-notice { background-color: #fffde7; color: #333; }
    .card-qa { background-color: #e3f2fd; color: #333; }
    .card-moa { background-color: #f8fbfa; }
    .moa-inner.type { background-color: white; border-left: 5px solid #1565c0; color: #333;}
    .moa-inner.desc { background-color: white; border-left: 5px solid #e65100; color: #333;}
    .moa-inner.detail { background-color: #e8f5e9; border-left: 5px solid #2e7d32; color: #333;}

    @media (prefers-color-scheme: dark) {
        input[type="text"], div[data-baseweb="select"] > div, div[data-testid="stDateInput"] > div, textarea {
            background-color: #3b3b3b !important; border: 1px solid #555555 !important; color: #f1f1f1 !important;
        }
        div[data-testid="stForm"] { background-color: #1e1e1e !important; border-color: #555 !important; }
        div[data-testid="stForm"] label p { color: #e0e0e0 !important; }
        .card-weather { background: linear-gradient(135deg, #424242 0%, #303030 100%); color: #e0e0e0; border-color: #555; }
        .card-notice { background-color: #2c2c2c; color: #e0e0e0; border-color: #555; }
        .card-qa { background-color: #2a3138; color: #e0e0e0; border-color: #555; }
        .card-moa { background-color: #2c3e30; border-color: #4CAF50; }
        .moa-inner.type, .moa-inner.desc, .moa-inner.detail { background-color: #383838; color: #e0e0e0; }
        h4, h3, h2, p { color: #e0e0e0 !important; }
        span.moa-highlight { color: #ffcc80 !important; }
    }

    @media (max-width: 768px) {
        .hallabong-title { font-size: 2rem !important; padding: 15px !important; border-radius: 12px !important; margin-bottom: 15px !important;}
        .hallabong-title img { width: 40px !important; margin-right: 8px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] { gap: 6px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label { padding: 6px 10px !important; border-radius: 8px !important; border-width: 1px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label p { font-size: 14px !important; }
        div[data-testid="stForm"] { padding: 15px !important; border-radius: 10px !important; border-width: 2px !important; }
        div[data-testid="stForm"] label p { font-size: 16px !important; }
        button[kind="secondaryFormSubmit"] { font-size: 18px !important; padding: 10px !important; margin-top: 10px !important; }
        .custom-card { padding: 15px !important; }
        div[data-testid="column"] > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 5px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 세션 초기화 및 데이터 로딩
# ==========================================
if 'notices' not in st.session_state:
    st.session_state.notices = [
        "<b>[필독]</b> 장마철 검은점무늬병 주의보 발령 (누적 강수량 200mm 초과 예상)",
        "[안내] 신규 등록 약제(살균제) 3종 리스트 업데이트 완료"
    ]
if 'qnas' not in st.session_state:
    st.session_state.qnas = [
        {"author": "제주농부", "content": "잎 뒷면에 이런 하얀 딱지가 생겼는데 더뎅이병일까요?", "reply": "👨‍🌾 KIMBO: 사진상으로는 볼록총채벌레 피해 흔적과 유사해 보입니다."}
    ]
# 🌟 방제 이력 저장용 세션 데이터 초기화 (미리 보기용 샘플 2개 포함)
if 'spray_history' not in st.session_state:
    st.session_state.spray_history = pd.DataFrame({
        "방제일자": ["2026-08-10", "2026-08-20"],
        "작물명": ["노지 감귤", "노지 감귤"],
        "사용약제": ["다이센엠", "모스피란"],
        "대상병해충": ["검은점무늬병", "진딧물, 깍지벌레"],
        "살포량": ["1000 L", "1000 L"],
        "메모": ["장마 후 예방살포", "발생 초기 방제"]
    })

@st.cache_data
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
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
    except:
        return pd.DataFrame(), [], []

@st.cache_data
def load_moa_data():
    try: return pd.read_excel('kijak.xlsx').fillna('')
    except: return pd.DataFrame()

df_database, pesticide_list, pest_list = load_data()
if df_database.empty:
    st.error("🚨 엑셀 파일('listall_nongyak.xlsx')을 읽을 수 없습니다.")
    st.stop()

if 'list_count' not in st.session_state: st.session_state.list_count = 5

# ==========================================
# 🧩 UI 컴포넌트 함수
# ==========================================
def render_styled_dataframe(df):
    display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충', '계통']
    df = df[[col for col in display_columns if col in df.columns]].copy()
    if '금액 (원)' in df.columns:
        df['금액 (원)'] = pd.to_numeric(df['금액 (원)'], errors='coerce')
    
    styled_df = df.style.set_properties(**{'font-size': '15px', 'font-weight': '600', 'padding': '8px 10px', 'text-align': 'center'})
    
    left_cols = [c for c in df.columns if c in ['적용병해충', '계통']]
    if left_cols: styled_df = styled_df.set_properties(subset=left_cols, **{'text-align': 'left'})
    if '금액 (원)' in df.columns:
        styled_df = styled_df.set_properties(subset=['금액 (원)'], **{'text-align': 'right'}).format({'금액 (원)': '{:,.0f}'}, na_rep="")
    
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

@st.dialog("🔬 작용기작 상세 팝업")
def show_moa_popup(moa_string):
    df_moa = load_moa_data()
    if df_moa.empty: return st.error("🚨 'kijak.xlsx' 파일 누락")
    
    moa_list = [m.strip() for m in str(moa_string).replace(',', '+').replace('/', '+').split('+') if m.strip()]
    cols = st.columns(len(moa_list))
    
    for i, code in enumerate(moa_list):
        with cols[i]:
            moa_result = df_moa[df_moa['표시기호'].astype(str) == code]
            if not moa_result.empty:
                res = moa_result.iloc[0]
                ntype = res.get('농약종류', '')
                icon = "🛡️" if "살균" in ntype else ("🐛" if "살충" in ntype else ("🌿" if "제초" in ntype else "🧪"))
                st.markdown(f"""
                <div style='background-color: transparent; border: 2px solid #66bb6a; border-radius: 12px; padding: 15px; margin-bottom:10px;'>
                    <h3 style='color: #4CAF50; margin:0 0 10px 0;'>{code}</h3>
                    <p style='margin:0; font-weight:bold;'>{icon} {ntype}</p>
                    <p style='margin:5px 0; font-size:13px;'>{res.get('작용기작 구분', '')}</p>
                    <hr style='margin: 10px 0; border-color: #555;'>
                    <span style='color: #ff9800; font-weight: bold;'>{res.get('세부 작용기작 및 계통(성분)', '')}</span>
                </div>
                """, unsafe_allow_html=True)
            else: st.warning(f"'{code}' 정보 없음")
    if st.button("❌ 닫기", use_container_width=True): st.rerun()

def render_moa_popup_trigger(df_current_result):
    unique_moas = [m for m in df_current_result['작용기작'].dropna().unique() if str(m).strip() and str(m).strip() != 'nan']
    if unique_moas:
        col_sel, col_btn, _ = st.columns([3, 2, 5])
        with col_sel:
            selected_moa = st.selectbox("팝업으로 볼 코드 선택", options=unique_moas, label_visibility="collapsed")
        with col_btn:
            if st.button("팝업 열기 🔍"): show_moa_popup(str(selected_moa))

def render_weather_section():
    st.markdown("""
        <div class="custom-card card-weather">
            📍 제주시 조천읍 감귤원 실시간 날씨<br>
            🌤️ 기온: 28℃ | 습도: 75%<br>
            🍃 풍속: 3.2 m/s (방제 최적)
        </div>
        <p style='font-size: 15px; font-weight: 800; margin-bottom: 8px; margin-top: 10px;'>📅 향후 10일 방제 날씨 예보</p>
    """, unsafe_allow_html=True)
    
    forecast_data = [
        {"일자": "8/27(목)", "날씨": "☀️ 맑음", "기온": "24°/29°", "방제": "🟢 최적"},
        {"일자": "8/28(금)", "날씨": "⛅ 구름", "기온": "25°/30°", "방제": "🔵 양호"},
        {"일자": "8/29(토)", "날씨": "🌧️ 비", "기온": "24°/27°", "방제": "🔴 불가"},
        {"일자": "8/30(일)", "날씨": "☁️ 흐림", "기온": "23°/26°", "방제": "🟠 보통"},
        {"일자": "8/31(월)", "날씨": "☀️ 맑음", "기온": "24°/28°", "방제": "🟢 최적"},
    ]
    styled_weather = pd.DataFrame(forecast_data).style.set_properties(**{
        'font-size': '13.5px', 'font-weight': '600', 'text-align': 'center', 'padding': '6px 5px'
    })
    st.dataframe(styled_weather, hide_index=True, use_container_width=True)
    if os.path.exists("farm.gif"): st.image("farm.gif", use_container_width=True)
    elif os.path.exists("farm.png"): st.image("farm.png", use_container_width=True)

# ==========================================
# 🚀 메인 화면 구성 시작
# ==========================================
icon_base64 = get_image_base64("아이콘001.png")
icon_tag = f'<img src="{icon_base64}" width="60" style="vertical-align: middle; margin-right: 15px; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));">' if icon_base64 else '🍊'

st.markdown(f"<a href='/' target='_self' class='home-link'><div class='hallabong-title'>{icon_tag} 내가 찾는 농약</div></a>", unsafe_allow_html=True)

# 🌟 메뉴 이름 변경 및 방제이력 메뉴 추가 적용
menu = st.radio(
    "메인 메뉴", 
    ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 찾기", "나의 방제이력", "정보교환마당"],
    horizontal=True, label_visibility="collapsed"
)
st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------
# 메뉴 1: 내가 필요한 농약 찾기
# ----------------------------------------
if menu == "내가 필요한 농약 찾기":
    col_main, col_img = st.columns([7, 3])
    with col_main:
        spray_date = st.date_input("약제살포 예정일", value=date.today())
        formatted_date = spray_date.strftime(f"%Y년 %m월 %d일 ({['월','화','수','목','금','토','일'][spray_date.weekday()]}요일)")
        st.markdown(f"<div style='color: #4CAF50; font-size: 16px; font-weight: bold; margin-top: -10px; margin-bottom: 15px; padding-left: 5px;'>👉 선택된 날짜: {formatted_date}</div>", unsafe_allow_html=True)

        with st.form("search_form"):
            crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
            desired_pesticide = st.multiselect("희망 약제명 (클릭하거나 검색)", options=pesticide_list, placeholder="약제명 검색 또는 선택")
            target_pest = st.multiselect("방제 대상 병해충 (클릭하거나 검색)", options=pest_list, placeholder="병해충명 검색 또는 선택")
            
            st.markdown("<p style='font-size: 18px; font-weight: 800; margin-bottom: 5px; margin-top: 15px;'>총 살포량</p>", unsafe_allow_html=True)
            col_vol1, col_vol2 = st.columns([2, 1], gap="small")
            with col_vol1: total_volume = st.text_input("살포량 입력", placeholder="예: 1000", label_visibility="collapsed")
            with col_vol2: volume_unit = st.selectbox("단위", ["L", "말"], index=0, label_visibility="collapsed")
            
            submitted = st.form_submit_button("🔎 조건에 맞는 농약 찾기")

        if submitted:
            st.session_state.list_count = 5
            if not desired_pesticide and not target_pest: st.error("⚠️ 희망 약제명 또는 발생 병해충을 하나 이상 입력해 주세요.")
            else:
                filtered_df = df_database.copy()
                if target_pest: filtered_df = filtered_df[filtered_df['적용병해충'].astype(str).str.contains('|'.join(target_pest))]
                if desired_pesticide: filtered_df = filtered_df[filtered_df['상품명'].isin(desired_pesticide)]
                st.session_state.df_result = filtered_df
                
                if filtered_df.empty: st.error("조건에 맞는 약제가 없습니다.")
                else: st.success(f"✅ 총 {len(filtered_df)}개의 약제가 검색되었습니다.")

        if 'df_result' in st.session_state and not st.session_state.df_result.empty:
            render_styled_dataframe(st.session_state.df_result.head(st.session_state.list_count))
            render_moa_popup_trigger(st.session_state.df_result.head(st.session_state.list_count))
            if st.session_state.list_count < len(st.session_state.df_result):
                if st.button("➕ 5개 더 보기"): st.session_state.list_count += 5; st.rerun()

    with col_img:
        render_weather_section()

# ----------------------------------------
# 메뉴 2 & 3: 농약명 / 병해충명으로 찾기
# ----------------------------------------
elif menu in ["농약명으로 찾기", "병해충명으로 찾기"]:
    col_limit, _ = st.columns([7, 3])
    with col_limit:
        if menu == "농약명으로 찾기":
            st.subheader("🔍 농약명 검색")
            search_val = st.selectbox("농약 상품명 선택/입력:", options=pesticide_list, index=None)
            target_col = '상품명'
        else:
            st.subheader("🐛 병해충명 검색")
            search_val = st.selectbox("병해충명 선택/입력:", options=pest_list, index=None)
            target_col = '적용병해충'
            
    if search_val and search_val.strip():
        if target_col == '상품명': res = df_database[df_database[target_col].astype(str) == search_val]
        else: res = df_database[df_database[target_col].astype(str).str.contains(search_val)]
        
        st.success("💡 표의 열 제목을 클릭하면 정렬됩니다.")
        render_styled_dataframe(res)
        render_moa_popup_trigger(res)
    else:
        st.info("👆 위 검색창에 찾으시는 명칭을 입력해주세요.")

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
            search_moa = st.selectbox("궁금한 작용기작 코드 선택/입력:", options=moa_codes, index=None)
            
            if search_moa and search_moa.strip():
                res = df_moa[df_moa['표시기호'].astype(str) == search_moa].iloc[0]
                ntype = res.get('농약종류', '')
                icon = "🛡️" if "살균" in ntype else ("🐛" if "살충" in ntype else ("🌿" if "제초" in ntype else "🧪"))
                
                st.markdown(f"""
                <div class='custom-card card-moa'>
                    <div style='position: absolute; top: -15px; right: -15px; font-size: 110px; opacity: 0.05;'>{icon}</div>
                    <h2 style='margin-top: 0; font-size: 26px; font-weight: 900; margin-bottom: 25px;'>
                        <span style='background-color: #e65100; color: white; padding: 5px 15px; border-radius: 12px;'>{search_moa}</span>
                        <span class='moa-highlight' style='margin-left: 10px;'>작용기작 상세</span>
                    </h2>
                    <div class='moa-inner type'>
                        <p style='margin: 0; font-size: 14px; opacity: 0.8;'>분류 (농약종류)</p>
                        <p style='margin: 0; font-size: 20px; font-weight: 800;'>{icon} {ntype}</p>
                    </div>
                    <div class='moa-inner desc'>
                        <p style='margin: 0; font-size: 14px; opacity: 0.8;'>작용기작 구분 (대분류)</p>
                        <p style='margin: 0; font-size: 20px; font-weight: 800;'>🧬 {res.get('작용기작 구분', '')}</p>
                    </div>
                    <div class='moa-inner detail'>
                        <p style='margin: 0; font-size: 15px; font-weight: 800; margin-bottom: 8px;'>세부 작용기작 및 계통(성분)</p>
                        <p style='margin: 0; font-size: 24px; color: #e57373; font-weight: 900; line-height: 1.4;'>🔬 {res.get('세부 작용기작 및 계통(성분)', '')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("👆 코드(예: 가1, 1a, H01)를 검색창에 입력해주세요.")

# ----------------------------------------
# 🌟 메뉴 5: 나의 방제이력 (신규 추가) 🌟
# ----------------------------------------
elif menu == "나의 방제이력":
    st.subheader("📋 나의 방제이력 (방제 일지)")
    
    # 1. 저장된 이력 표로 보여주기
    if st.session_state.spray_history.empty:
        st.info("아직 등록된 방제 이력이 없습니다. 아래에서 새로운 기록을 추가해보세요!")
    else:
        styled_history = st.session_state.spray_history.style.set_properties(**{
            'font-size': '15px', 'text-align': 'center', 'padding': '8px 10px'
        })
        st.dataframe(styled_history, hide_index=True, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. 새로운 이력 등록 폼
    with st.expander("➕ 새로운 방제 기록 추가하기", expanded=False):
        with st.form("history_form", clear_on_submit=True):
            col_h1, col_h2 = st.columns(2)
            
            with col_h1:
                h_date = st.date_input("방제일자", value=date.today())
                h_crop = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"])
                h_pest = st.text_input("대상 병해충", placeholder="예: 검은점무늬병, 응애 등")
                
            with col_h2:
                h_pesticide = st.text_input("사용 약제명", placeholder="예: 다이센엠, 기계유유제 등")
                col_vol1, col_vol2 = st.columns([2, 1], gap="small")
                with col_vol1: h_vol = st.text_input("살포량", placeholder="예: 1000")
                with col_vol2: h_unit = st.selectbox("단위", ["L", "말"])
                h_memo = st.text_input("특이사항 (메모)", placeholder="예: 비 오기 전 예방살포")
            
            if st.form_submit_button("💾 기록 저장하기"):
                if h_pesticide and h_pest:
                    new_record = pd.DataFrame([{
                        "방제일자": h_date.strftime("%Y-%m-%d"),
                        "작물명": h_crop,
                        "사용약제": h_pesticide,
                        "대상병해충": h_pest,
                        "살포량": f"{h_vol} {h_unit}",
                        "메모": h_memo
                    }])
                    st.session_state.spray_history = pd.concat([st.session_state.spray_history, new_record], ignore_index=True)
                    st.success("✅ 방제 기록이 성공적으로 저장되었습니다.")
                    st.rerun()
                else:
                    st.error("⚠️ '사용 약제명'과 '대상 병해충'은 반드시 입력해 주세요.")

# ----------------------------------------
# 메뉴 6: 정보교환마당
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
                new_notice = st.text_input("내용 입력")
                if st.form_submit_button("등록") and new_notice:
                    st.session_state.notices.append(new_notice); st.rerun()

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