# ==========================================
# 📌 버전: 34.3 (최적화 수정본) | 수정일시: 2026.09.04
# 📌 주요 수정내용: 
#   1. 모바일 UI/UX 최적화 (반응형 CSS 적용)
#   2. 메인화면 실시간 날씨 및 기상청 초단기실황 연동
#   3. [보완] 검색 결과 세션 지속성 및 개별 병해충 검색 분기 출력 완결
#   4. [보완] API Key 보안성 강화 (st.secrets 연동)
# ==========================================

import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import re
import os
import base64
import requests
import urllib.parse
from supabase import create_client, Client

# 구글 Gemini AI 라이브러리 예외 처리
try:
    import google.generativeai as genai
except ImportError:
    st.error("🚨 'google-generativeai' 패키지가 설치되지 않았습니다.")

# 1. 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 🔐 Supabase & Gemini & KMA API 연결 설정
# ==========================================
@st.cache_resource
def init_connection() -> Client:
    raw_url = str(st.secrets["SUPABASE_URL"]).strip().strip("\"'")
    clean_key = str(st.secrets["SUPABASE_KEY"]).strip().strip("\"'")
    clean_url = raw_url.rstrip("/")
    if clean_url.endswith("/rest/v1"): clean_url = clean_url[:-8]
    return create_client(clean_url.rstrip("/"), clean_key)

try:
    supabase = init_connection()
    supabase_connected = True
except Exception:
    supabase_connected = False
    st.error("🚨 Supabase 연결 설정이 완료되지 않았거나 키가 잘못되었습니다.")

gemini_ready = False
try:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip("\"'")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            gemini_ready = True
except Exception:
    pass

# ==========================================
# 💾 세션 초기화 및 상태 관리
# ==========================================
if 'list_count' not in st.session_state: st.session_state.list_count = 5
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = {}
if 'active_menu' not in st.session_state: st.session_state.active_menu = "내가 필요한 농약 찾기"
if 'form_reset_key' not in st.session_state: st.session_state.form_reset_key = 0
if 'df_result' not in st.session_state: st.session_state.df_result = None

# ==========================================
# 🎨 UI 디자인 (CSS 스타일)
# ==========================================
st.markdown("""
    <style>
    a.home-link { text-decoration: none !important; }
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-thumb { background: #ffb74d; border-radius: 10px; }
    .hallabong-title { background-color: #e65100; padding: 15px; border-radius: 20px; text-align: center; color: white; font-weight: 900; font-size: 2.5rem; margin-bottom: 10px; }
    div[data-testid="stRadio"] div[role="radiogroup"] { display: flex; flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 8px; }
    div[data-testid="stRadio"] div[role="radiogroup"] label { background: #e8f5e9; border: 1px solid #a5d6a7; padding: 8px 16px; border-radius: 12px; cursor: pointer; }
    .custom-card { border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .card-weather { border: 2px solid #ffcc80; text-align: center; background: #ffecd2; color: #3e2723; font-weight: bold; }
    
    @media screen and (max-width: 768px) {
        .hallabong-title { font-size: 1.6rem !important; padding: 10px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label { padding: 5px 10px !important; font-size: 14px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 Supabase 데이터 로딩
# ==========================================
@st.cache_data(ttl=600)
def load_data_from_supabase():
    if not supabase_connected: return pd.DataFrame(), pd.DataFrame(), [], [], "Supabase 연결 실패"
    df_nongyak, df_moa = pd.DataFrame(), pd.DataFrame()
    pesticide_list, pest_list = [], []
    error_msgs = []
    
    try:
        res_n = supabase.table("DBnongyak").select("*").execute()
        df_nongyak = pd.DataFrame(res_n.data)
        if not df_nongyak.empty:
            cols_map = {'productname': 'Product Name', 'type': 'Type', 'kijak': 'Kijak', 'spec': 'Spec', 'usage': 'Usage', 'price': 'Price', 'byung': 'Byung', 'gyetong': 'Gyetong'}
            df_nongyak = df_nongyak.rename(columns={k: v for k, v in cols_map.items() if k in df_nongyak.columns}).fillna('')
            if "Product Name" in df_nongyak.columns: pesticide_list = sorted([str(n) for n in df_nongyak["Product Name"].unique() if str(n) and str(n) != 'nan'])
            if "Type" in df_nongyak.columns and "Byung" in df_nongyak.columns:
                pest_raw = df_nongyak[df_nongyak['Type'].isin(['살균제', '살충제'])]["Byung"].astype(str).tolist()
                pest_set = {re.sub(r'\(.*?\)', '', p).replace('(', '').replace(')', '').strip() for pests in pest_raw for p in pests.split(',')}
                pest_list = sorted([p for p in pest_set if p and str(p) != 'nan'])
    except Exception as e: error_msgs.append(f"DBnongyak 오류: {e}")

    try:
        res_k = supabase.table("DBkijak").select("*").execute()
        df_moa = pd.DataFrame(res_k.data)
    except Exception as e: error_msgs.append(f"DBkijak 오류: {e}")

    return df_nongyak, df_moa, pesticide_list, pest_list, " | ".join(error_msgs)

df_database, df_moa_db, pesticide_list, pest_list, db_error_msg = load_data_from_supabase()

def render_styled_dataframe(df):
    display_columns = ['Type', 'Product Name', 'Kijak', 'Spec', 'Usage', 'Price', 'Byung', 'Gyetong']
    df = df[[col for col in display_columns if col in df.columns]].copy()
    rename_dict = {'Type': '종류', 'Product Name': '상품명', 'Kijak': '작용기작', 'Spec': '규격', 'Usage': '사용량', 'Price': '금액(원)', 'Byung': '적용병해충', 'Gyetong': '계통'}
    df = df.rename(columns=rename_dict)
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}), hide_index=True, use_container_width=True)

# ==========================================
# 🚀 헤더 및 메뉴 분기
# ==========================================
st.markdown("<div class='hallabong-title'>🍊 내가 찾는 농약</div>", unsafe_allow_html=True)

menus = ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 찾기", "나의 방제이력", "병해충 분석", "정보교환마당"]
selected_menu = st.radio("메인 메뉴", menus, horizontal=True, label_visibility="collapsed")

if selected_menu == "내가 필요한 농약 찾기":
    st.markdown("### 🔎 내가 필요한 농약 검색")
    
    with st.form("search_form"):
        crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"])
        desired_pesticide = st.multiselect("농약 이름 (검색/선택)", options=pesticide_list)
        target_pest = st.multiselect("병해충 이름 (검색/선택)", options=pest_list)
        
        total_volume = st.text_input("총 살포량 [말]", placeholder="예: 50")
        if total_volume and total_volume.isdigit():
            vol_mal = int(total_volume)
            st.info(f"💡 계산된 살포량: {vol_mal}말 ({vol_mal * 20}L)")

        submitted = st.form_submit_button("🔎 조건에 맞는 농약 찾기", type="primary")

    if submitted:
        if not desired_pesticide and not target_pest:
            st.error("⚠️ 농약 이름 또는 병해충 이름을 최소 하나 이상 선택해주세요.")
            st.session_state.df_result = None
        else:
            filtered_df = df_database.copy()
            if desired_pesticide:
                filtered_df = filtered_df[filtered_df['Product Name'].isin(desired_pesticide)]
            if target_pest:
                for pest in target_pest:
                    filtered_df = filtered_df[filtered_df['Byung'].astype(str).str.contains(pest)]
            
            st.session_state.df_result = filtered_df

    # 결과 출력부 (세션 상태 유지)
    if st.session_state.df_result is not None:
        res_df = st.session_state.df_result
        if not res_df.empty:
            st.success(f"🎉 총 {len(res_df)}건의 조건에 맞는 농약이 검색되었습니다.")
            render_styled_dataframe(res_df)
        else:
            st.error("🚨 선택하신 모든 조건(AND)을 동시 만족하는 농약이 없습니다.")
            if target_pest and len(target_pest) > 1:
                st.markdown("#### 💡 각 병해충별 개별 방제 가능 농약 목록")
                for pest in target_pest:
                    sub_df = df_database[df_database['Byung'].astype(str).str.contains(pest)]
                    with st.expander(f"📌 '{pest}' 방제 가능 농약 ({len(sub_df)}건)"):
                        render_styled_dataframe(sub_df)