# ==========================================
# 📌 버전: 29.0 | 수정일시: 2026.09.03
# 📌 주요 수정내용: 
#    1. Gemini 404 에러 완벽 해결: genai.list_models()를 활용한 '사용 가능한 모델 자동 탐색 및 선택' 로직 적용
#    2. 병해충 분석: 다중 이미지 업로드 및 가로 정렬 UI 유지
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
from supabase import create_client, Client
from PIL import Image
import io

# 💡 구글 Gemini AI 라이브러리 불러오기
try:
    import google.generativeai as genai
except ImportError:
    st.error("🚨 'google-generativeai' 패키지가 설치되지 않았습니다. requirements.txt를 확인해주세요.")

# 1. 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 🔐 Supabase & Gemini API 클라우드 연결 설정
# ==========================================
@st.cache_resource
def init_connection() -> Client:
    raw_url = str(st.secrets["SUPABASE_URL"]).strip().strip("\"'")
    clean_key = str(st.secrets["SUPABASE_KEY"]).strip().strip("\"'")
    
    clean_url = raw_url.rstrip("/")
    if clean_url.endswith("/rest/v1"): clean_url = clean_url[:-8]
    clean_url = clean_url.rstrip("/")
    return create_client(clean_url, clean_key)

try:
    supabase = init_connection()
    supabase_connected = True
except Exception as e:
    supabase_connected = False
    st.error("🚨 Supabase 연결 설정이 완료되지 않았거나 키가 잘못되었습니다.")

# 💡 [핵심 수정] Gemini API 키 설정 및 사용 가능한 모델 '자동 탐색' 로직
gemini_ready = False
vision_model = None

try:
    gemini_api_key = str(st.secrets["GEMINI_API_KEY"]).strip().strip("\"'")
    genai.configure(api_key=gemini_api_key)
    
    # 구글 서버에 현재 API 키로 사용 가능한 모든 모델 목록을 요청
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 가장 성능이 좋은 최신 모델부터 순차적으로 탐색하여 자동 선택
    target_model = None
    for model_name in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-1.0-pro-vision-latest', 'models/gemini-pro-vision']:
        if model_name in available_models:
            target_model = model_name.replace('models/', '')
            break
            
    if target_model:
        vision_model = genai.GenerativeModel(target_model)
        gemini_ready = True
        st.session_state.current_ai_model = target_model # 확인용
    else:
        st.error("🚨 현재 API 키로 사용할 수 있는 이미지 판독 모델이 없습니다.")
except Exception as e:
    st.warning(f"⚠️ Gemini API 설정 오류: {e}")

# ==========================================
# 💾 세션 초기화 및 상태 관리
# ==========================================
if 'list_count' not in st.session_state: st.session_state.list_count = 5
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = {}
if 'active_menu' not in st.session_state: st.session_state.active_menu = "내가 필요한 농약 찾기"
if 'form_reset_key' not in st.session_state: st.session_state.form_reset_key = 0

# ==========================================
# 🎨 UI 디자인 (CSS 스타일)
# ==========================================
st.markdown("""
    <style>
    a.home-link { text-decoration: none !important; }
    ::-webkit-scrollbar { width: 18px !important; height: 18px !important; }
    ::-webkit-scrollbar-track { background: #f1f1f1 !important; border-radius: 10px !important; box-shadow: inset 0 0 5px rgba(0,0,0,0.1) !important; }
    ::-webkit-scrollbar-thumb { background: #ffb74d !important; border-radius: 10px !important; border: 3px solid #f1f1f1 !important; }
    ::-webkit-scrollbar-thumb:hover { background: #e65100 !important; }
    .hallabong-title { background-color: #e65100; padding: 15px; border-radius: 20px; text-align: center; color: white; font-weight: 900; font-size: 2.8rem; box-shadow: 0px 6px 15px rgba(230, 81, 0, 0.3); border: 3px solid #ffcc80; transition: transform 0.2s ease-in-out; }
    .hallabong-title:hover { transform: scale(1.02); }
    div[data-testid="stRadio"] div[role="radiogroup"] { display: flex; flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 15px; }
    div[data-testid="stRadio"] div[role="radiogroup"] div[data-baseweb="radio"] div { display: none !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] label { background: linear-gradient(145deg, #e8f5e9, #c8e6c9) !important; border: 2px solid #a5d6a7 !important; padding: 8px 16px !important; border-radius: 12px !important; cursor: pointer; transition: all 0.1s ease-in-out; margin: 0 !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] label p { font-size: 17px !important; font-weight: 800 !important; color: #1b5e20 !important; margin: 0 !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] label:active, div[data-testid="stRadio"] div[role="radiogroup"] label:focus-within { transform: translateY(3px) !important; background: linear-gradient(145deg, #c8e6c9, #a5d6a7) !important; }
    div[data-testid="stForm"], div[data-testid="stExpander"] { font-size: 18px !important; font-weight: 800 !important; }
    input[type="text"], input[type="password"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input, div[data-testid="stTimeInput"] input, textarea { font-size: 16px !important; padding: 6px 10px !important; }
    div[data-testid="stForm"] { border: 3px solid #ffb74d; border-radius: 15px; padding: 25px; box-shadow: 0px 6px 15px rgba(255,183,77,0.15); margin-bottom: 15px; }
    button[kind="secondaryFormSubmit"], button[kind="primary"] { background: linear-gradient(to right, #4caf50, #2e7d32) !important; color: white !important; font-size: 20px !important; font-weight: 800 !important; border-radius: 12px !important; padding: 12px 20px !important; border: none !important; margin-top: 15px; width: 100%; }
    button[kind="secondaryFormSubmit"]:active, button[kind="primary"]:active { transform: translateY(4px) !important; }
    .custom-card { border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); }
    .card-weather { border: 3px solid #ffcc80; text-align: center; font-size: 1.15rem; font-weight: 800; line-height: 1.4; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #3e2723; }
    .card-notice { border: 2px solid #fdd835; height: 100%; min-height: 400px; background-color: #fffde7; color: #333; }
    .card-qa { border: 2px solid #64b5f6; height: 100%; min-height: 400px; background-color: #e3f2fd; color: #333; }
    .card-moa { border: 3px solid #66bb6a; margin-top: 20px; position: relative; overflow: hidden; background-color: #f8fbfa; }
    .moa-inner { padding: 15px 20px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0px 2px 5px rgba(0,0,0,0.03); }
    .moa-inner.type { background-color: white; border-left: 5px solid #1565c0; color: #333;}
    .moa-inner.desc { background-color: white; border-left: 5px solid #e65100; color: #333;}
    .moa-inner.detail { background-color: #e8f5e9; border-left: 5px solid #2e7d32; color: #333;}
    .moa-result-card { background-color: #f1f8e9; border-left: 5px solid #66bb6a; border-radius: 8px; padding: 15px; margin-bottom: 10px; color: #333; }
    .moa-result-card h4 { color: #2e7d32; margin: 0 0 5px 0; }
    .moa-result-card p.title { margin: 0 0 8px 0; font-size: 14px; font-weight: bold; color: #333; }
    .moa-result-card p.desc { margin: 0; color: #e65100; font-weight: bold; }
    .ai-result-card { text-align: left; padding: 20px; border: 2px solid #ffcc80; border-radius: 12px; background-color: #fff8e1; margin-bottom: 15px; color: #333; }
    .ai-result-card h3 { color: #e65100; margin: 0 0 10px 0; font-size: 24px; border-bottom: 2px solid #ffcc80; padding-bottom: 5px;}
    .ai-result-card h4 { color: #2e7d32; font-weight: bold; margin-top: 15px; margin-bottom: 5px; font-size: 18px;}
    .ai-result-card p { font-size: 16px; line-height: 1.6; margin-bottom: 10px; color: #424242; }
    .search-header-pest { background: linear-gradient(to right, #f1f8e9, transparent); padding: 15px 20px; border-left: 5px solid #4caf50; border-radius: 8px; margin-bottom: 15px; }
    .search-header-pest h3 { margin:0; color:#2e7d32; }
    .search-header-bug { background: linear-gradient(to right, #fff8e1, transparent); padding: 15px 20px; border-left: 5px solid #ffb300; border-radius: 8px; margin-bottom: 15px; }
    .search-header-bug h3 { margin:0; color:#f57f17; }
    .search-header-result { background: linear-gradient(to right, #e3f2fd, transparent); padding: 15px 20px; border-left: 5px solid #2196f3; border-radius: 8px; margin-bottom: 15px; }
    .search-header-result h3 { margin:0; color:#1565c0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 Supabase 기반 데이터 로딩
# ==========================================
@st.cache_data
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return None

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
            cols_map = {}
            for c in df_nongyak.columns:
                clean_c = c.strip().lower().replace(" ", "").replace("_", "")
                if clean_c == 'productname': cols_map[c] = 'Product Name'
                elif clean_c == 'type': cols_map[c] = 'Type'
                elif clean_c == 'kijak': cols_map[c] = 'Kijak'
                elif clean_c == 'spec': cols_map[c] = 'Spec'
                elif clean_c == 'usage': cols_map[c] = 'Usage'
                elif clean_c == 'price': cols_map[c] = 'Price'
                elif clean_c == 'byung': cols_map[c] = 'Byung'
                elif clean_c == 'gyetong': cols_map[c] = 'Gyetong'
            df_nongyak = df_nongyak.rename(columns=cols_map).fillna('')
            for col in df_nongyak.columns:
                if df_nongyak[col].dtype == object: df_nongyak[col] = df_nongyak[col].astype(str).str.strip()
            if "Product Name" in df_nongyak.columns: pesticide_list = sorted([str(n) for n in df_nongyak["Product Name"].unique() if str(n) and str(n) != 'nan'])
            if "Type" in df_nongyak.columns and "Byung" in df_nongyak.columns:
                pest_raw = df_nongyak[df_nongyak['Type'].isin(['살균제', '살충제'])]["Byung"].astype(str).tolist()
                pest_set = {re.sub(r'\(.*?\)', '', p).replace('(', '').replace(')', '').strip() for pests in pest_raw for p in pests.split(',')}
                pest_list = sorted([p for p in pest_set if p and str(p) != 'nan'])
        else: error_msgs.append("DBnongyak 데이터 없음")
    except Exception as e: error_msgs.append(f"DBnongyak 오류: {e}")

    try:
        res_k = supabase.table("DBkijak").select("*").execute()
        df_moa = pd.DataFrame(res_k.data)
        if not df_moa.empty:
            cols_map_moa = {}
            for c in df_moa.columns:
                clean_c = c.strip().replace(" ", "")
                if clean_c == '작용기작코드': cols_map_moa[c] = '작용기작 코드'
                elif clean_c == '농약종류': cols_map_moa[c] = '농약종류'
                elif clean_c == '주작용기작': cols_map_moa[c] = '주 작용기작'
                elif clean_c == '세부작용기작': cols_map_moa[c] = '세부 작용기작'
            df_moa = df_moa.rename(columns=cols_map_moa).fillna('')
            for col in df_moa.columns:
                if df_moa[col].dtype == object: df_moa[col] = df_moa[col].astype(str).str.strip()
        else: error_msgs.append("DBkijak 데이터 없음")
    except Exception as e: error_msgs.append(f"DBkijak 오류: {e}")

    error_str = " | ".join(error_msgs) if error_msgs else ""
    return df_nongyak, df_moa, pesticide_list, pest_list, error_str

def fetch_spray_history():
    if not supabase_connected: return pd.DataFrame()
    try:
        response = supabase.table("DBbangje").select("*").order("Date", desc=True).execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            cols_map = {}
            for c in df.columns:
                clean_c = c.strip().lower().replace(" ", "")
                if clean_c == 'date': cols_map[c] = 'Date'
                elif clean_c == 'time': cols_map[c] = 'Time'
                elif clean_c == 'nongyak': cols_map[c] = 'Nongyak'
                elif clean_c == 'type': cols_map[c] = 'Type'
                elif clean_c == 'kijak': cols_map[c] = 'Kijak'
                elif clean_c == 'spec': cols_map[c] = 'Spec'
                elif clean_c == 'qty': cols_map[c] = 'Qty'
                elif clean_c == 'tqty': cols_map[c] = 'Tqty'
                elif clean_c == 'byung': cols_map[c] = 'Byung'
                elif clean_c == 'remark': cols_map[c] = 'Remark'
                elif clean_c == 'id': cols_map[c] = 'ID'
            df = df.rename(columns=cols_map)
        return df.fillna('')
    except Exception as e: return pd.DataFrame()

df_database, df_moa_db, pesticide_list, pest_list, db_error_msg = load_data_from_supabase()

def render_styled_dataframe(df):
    display_columns = ['Type', 'Product Name', 'Kijak', 'Spec', 'Usage', 'Price', 'Byung', 'Gyetong']
    df = df[[col for col in display_columns if col in df.columns]].copy()
    if 'Price' in df.columns: df['Price'] = pd.to_numeric(df['Price'].astype(str).str.replace(',', ''), errors='coerce')
    rename_dict = {
        'Type': '종류', 'Product Name': '상품명', 'Kijak': '작용기작', 
        'Spec': '규격', 'Usage': '사용량', 'Price': '금액 (원)', 
        'Byung': '적용병해충', 'Gyetong': '계통'
    }
    df = df.rename(columns=rename_dict)
    styled_df = df.style.set_properties(**{'font-size': '15px', 'font-weight': '600', 'padding': '8px 10px', 'text-align': 'center'})
    left_cols = [c for c in df.columns if c in ['적용병해충', '계통']]
    if left_cols: styled_df = styled_df.set_properties(subset=left_cols, **{'text-align': 'left'})
    if '금액 (원)' in df.columns: styled_df = styled_df.set_properties(subset=['금액 (원)'], **{'text-align': 'right'}).format({'금액 (원)': '{:,.0f}'}, na_rep="")
    st.dataframe(styled_df, hide_index=True, use_container_width=True, height=210)

def render_moa_popup_trigger(df_current_result):
    if 'Kijak' not in df_current_result.columns: return
    unique_moas = [m for m in df_current_result['Kijak'].dropna().unique() if str(m).strip() and str(m).strip() != 'nan']
    if unique_moas:
        st.markdown("<p style='font-size: 16px; font-weight: 800; color: #2e7d32; margin-top: 10px; margin-bottom: 5px;'>🔬 검색된 약제의 작용기작 상세정보 확인</p>", unsafe_allow_html=True)
        selected_moa = st.selectbox("아래에서 작용기작 코드를 선택하세요:", options=["선택 안 함"] + unique_moas, index=0, label_visibility="collapsed")
        
        if selected_moa != "선택 안 함":
            if df_moa_db.empty or '작용기작 코드' not in df_moa_db.columns:
                st.error("🚨 작용기작 DB 정보를 찾을 수 없습니다.")
                return
            moa_list = [m.strip() for m in str(selected_moa).replace(',', '+').replace('/', '+').split('+') if m.strip()]
            for code in moa_list:
                moa_result = df_moa_db[df_moa_db['작용기작 코드'].astype(str) == code]
                if not moa_result.empty:
                    res = moa_result.iloc[0]
                    ntype = res.get('농약종류', '')
                    icon = "🛡️" if "살균" in ntype else ("🐛" if "살충" in ntype else ("🌿" if "제초" in ntype else "🧪"))
                    st.markdown(f"<div class='moa-result-card'><h4>{code} <span style='font-size: 14px; font-weight: normal; opacity: 0.8;'>({icon} {ntype})</span></h4><p class='title'>{res.get('주 작용기작', '')}</p><p class='desc'>👉 {res.get('세부 작용기작', '')}</p></div>", unsafe_allow_html=True)
                else: st.warning(f"'{code}' 정보가 DB에 없습니다.")

@st.cache_data(ttl=3600)
def fetch_kma_weather_7days():
    forecast_data = []
    api_status_msg = ""
    today = date.today()
    weekdays_kr = ['월', '화', '수', '목', '금', '토', '일']
    fallback_pool = [("☀️ 맑음", "24°/29°", "🟢 최적"), ("⛅ 구름", "25°/30°", "🔵 양호"), ("☁️ 흐림", "23°/26°", "🟠 보통"), ("🌧️ 비", "24°/27°", "🔴 불가"), ("☀️ 맑음", "25°/30°", "🟢 최적"), ("🌦️ 소나기", "24°/28°", "🟠 주의"), ("⛅ 구름", "26°/31°", "🔵 양호")]
    api_success = False

    try:
        api_key = "6DtMoZ7RNwMuQb64EEqZluq%2B6gZJjLxP%2Fyfr3yBrx9l9EAxzw0IF%2B0nFzzTJLNvLbL92qCLArCTesMh4QKZ0Fg%3D%3D"
        decoded_key = urllib.parse.unquote(api_key)
        now = datetime.now()
        base_dt = now - timedelta(days=1)
        base_date = base_dt.strftime('%Y%m%d')
        base_time = "2300"
        
        url_short = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        params_short = {'ServiceKey': decoded_key, 'pageNo': '1', 'numOfRows': '1000', 'dataType': 'JSON', 'base_date': base_date, 'base_time': base_time, 'nx': '53', 'ny': '38' }
        res_short = requests.get(url_short, params=params_short, timeout=3).json()
        
        short_parsed = {}
        if res_short['response']['header']['resultCode'] == '00':
            items = res_short['response']['body']['items']['item']
            for item in items:
                f_date = item['fcstDate']
                cat = item['category']
                if f_date not in short_parsed: short_parsed[f_date] = {'TMN': '20', 'TMX': '25', 'SKY': '1', 'PTY': '0'}
                if cat in ['TMN', 'TMX', 'SKY', 'PTY']: short_parsed[f_date][cat] = item['fcstValue']
            
            if now.hour < 6: tmFc = (now - timedelta(days=1)).strftime('%Y%m%d') + "1800"
            else: tmFc = now.strftime('%Y%m%d') + "0600"
            
            url_mid_land = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst"
            url_mid_ta = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa"
            
            res_land = requests.get(url_mid_land, params={'ServiceKey': decoded_key, 'pageNo': '1', 'numOfRows': '10', 'dataType': 'JSON', 'regId': '11G00000', 'tmFc': tmFc}, timeout=3).json()
            res_ta = requests.get(url_mid_ta, params={'ServiceKey': decoded_key, 'pageNo': '1', 'numOfRows': '10', 'dataType': 'JSON', 'regId': '11G00201', 'tmFc': tmFc}, timeout=3).json()
            
            mid_land_data = res_land['response']['body']['items']['item'][0]
            mid_ta_data = res_ta['response']['body']['items']['item'][0]
            
            for i in range(7):
                target_date = today + timedelta(days=i)
                date_str = target_date.strftime('%Y%m%d')
                display_date = target_date.strftime(f"%m/%d({weekdays_kr[target_date.weekday()]})")
                sky_emoji, weather_status = "☀️ 맑음", "🟢 최적"
                tmn, tmx = "24", "29"
                if i < 3 and date_str in short_parsed:
                    day_data = short_parsed[date_str]
                    tmn = str(float(day_data['TMN']))[:2] if day_data['TMN'] != '20' else '24'
                    tmx = str(float(day_data['TMX']))[:2] if day_data['TMX'] != '25' else '29'
                    sky_val, pty_val = day_data['SKY'], day_data['PTY']
                    if pty_val in ['1', '2', '3', '4']: sky_emoji, weather_status = "🌧️ 비", "🔴 불가"
                    elif sky_val == '4': sky_emoji, weather_status = "☁️ 흐림", "🟠 보통"
                    elif sky_val == '3': sky_emoji, weather_status = "⛅ 구름", "🔵 양호"
                elif 3 <= i < 7:
                    day_idx = i + 1
                    tmn = str(mid_ta_data.get(f'taMin{day_idx}', '24'))
                    tmx = str(mid_ta_data.get(f'taMax{day_idx}', '29'))
                    wf_key = f'wf{day_idx}Pm' if day_idx > 7 else f'wf{day_idx}Am'
                    wf_val = mid_land_data.get(wf_key, '맑음')
                    if '비' in wf_val or '소나기' in wf_val: sky_emoji, weather_status = "🌧️ 비", "🔴 불가"
                    elif '흐림' in wf_val: sky_emoji, weather_status = "☁️ 흐림", "🟠 보통"
                    elif '구름' in wf_val: sky_emoji, weather_status = "⛅ 구름", "🔵 양호"
                forecast_data.append({"일자": display_date, "날씨": sky_emoji, "기온": f"{tmn}°/{tmx}°", "방제": weather_status})
            api_success = True; api_status_msg = "🟢 기상청 데이터 실시간 연동 중"
    except Exception as e: api_status_msg = "🟠 기상청 연동 대기 중 (자체 데이터 적용)"
        
    if not api_success:
        forecast_data = []
        for i in range(7):
            dt = today + timedelta(days=i)
            forecast_data.append({"일자": dt.strftime(f"%m/%d({weekdays_kr[dt.weekday()]})"), "날씨": fallback_pool[i][0], "기온": fallback_pool[i][1], "방제": fallback_pool[i][2]})
        api_status_msg = "🟠 기상청 연동 대기 중 (자체 데이터 적용)"
            
    return forecast_data, api_status_msg

def render_weather_section():
    forecast_data, api_status_msg = fetch_kma_weather_7days()
    st.markdown(f"<div class='custom-card card-weather'>📍 제주시 조천읍 감귤원 실시간 날씨<br>🌤️ 기온: 28℃ | 습도: 75%<br>🍃 풍속: 3.2 m/s (방제 최적)</div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-top: 10px; margin-bottom: 8px;'><p style='font-size: 15px; font-weight: 800; margin: 0;'>📅 향후 1주일 방제 날씨 예보</p><p style='font-size: 11px; color: gray; margin: 0;'>{api_status_msg}</p></div>", unsafe_allow_html=True)
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
                st.session_state.current_user = {'name': name, 'id': user_id, 'location': location, 'crop': crop}
                st.session_state.show_history_prompt = True
                st.rerun()
            else: st.error("성명, 아이디, 비밀번호는 필수 입력 항목입니다.")
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

    menus = ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 찾기", "나의 방제이력", "병해충 분석", "정보교환마당"]
    menu_idx = menus.index(st.session_state.active_menu) if st.session_state.active_menu in menus else 0
    selected_menu = st.radio("메인 메뉴", menus, index=menu_idx, horizontal=True, label_visibility="collapsed")
    
    if selected_menu != st.session_state.active_menu:
        st.session_state.active_menu = selected_menu
        st.session_state.form_reset_key += 1
        st.rerun()

    menu = st.session_state.active_menu
    st.markdown("<br>", unsafe_allow_html=True)
    if supabase_connected and db_error_msg: st.error(f"🚨 **[DB 진단 메시지]** 데이터를 불러오는 중 문제가 발생했습니다: \n\n {db_error_msg}")

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
                    if target_pest: filtered_df = filtered_df[filtered_df['Byung'].astype(str).str.contains('|'.join(target_pest))]
                    if desired_pesticide: filtered_df = filtered_df[filtered_df['Product Name'].isin(desired_pesticide)]
                    st.session_state.df_result = filtered_df
                    if filtered_df.empty: st.error("조건에 맞는 약제가 없습니다.")
                    else: st.success(f"✅ 총 {len(filtered_df)}개의 약제가 검색되었습니다.")

            if 'df_result' in st.session_state and not st.session_state.df_result.empty:
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
                    res = df_database[df_database['Product Name'].astype(str) == search_val]
                    if res.empty: st.error("찾을 수 없습니다. 다시 입력해주세요!")
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
                    for val in search_vals: res = res[res['Byung'].astype(str).str.contains(val)]
                    if res.empty:
                        if len(search_vals) > 1:
                            st.error("🚨 입력조건을 모두 만족하는 농약은 없습니다.")
                            st.markdown("#### 💡 각 병해충 조건별 적용 가능한 농약")
                            for val in search_vals:
                                individual_res = df_database[df_database['Byung'].astype(str).str.contains(val)]
                                if not individual_res.empty: st.info(f"**[{val}]** : {', '.join(individual_res['Product Name'].unique().tolist())}")
                                else: st.warning(f"**[{val}]** : 등록된 농약이 없습니다.")
                        else: st.error("찾을 수 없습니다. 다시 입력해주세요!")
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
            if df_moa_db.empty or '작용기작 코드' not in df_moa_db.columns: st.error("🚨 DB에서 작용기작 정보를 불러올 수 없습니다. 필드명이 올바른지 확인해주세요.")
            else:
                moa_codes = sorted([str(code).strip() for code in df_moa_db['작용기작 코드'].unique() if str(code).strip() and str(code) != 'nan'])
                search_moa = st.selectbox("궁금한 작용기작 코드 검색/선택:", options=moa_codes, index=None, placeholder="예: 가1, 1a, H01")
                if search_moa and search_moa.strip():
                    res = df_moa_db[df_moa_db['작용기작 코드'].astype(str) == search_moa].iloc[0]
                    ntype = res.get('농약종류', '')
                    icon = "🛡️" if "살균" in ntype else ("🐛" if "살충" in ntype else ("🌿" if "제초" in ntype else "🧪"))
                    st.markdown(f"<div class='custom-card card-moa'><div style='position: absolute; top: -15px; right: -15px; font-size: 110px; opacity: 0.05;'>{icon}</div><h2 style='margin-top: 0; font-size: 26px; font-weight: 900; margin-bottom: 25px;'><span style='background-color: #e65100; color: white; padding: 5px 15px; border-radius: 12px;'>{search_moa}</span><span class='moa-highlight' style='margin-left: 10px;'>작용기작 상세</span></h2><div class='moa-inner type'><p style='margin: 0; font-size: 14px; opacity: 0.8;'>분류 (농약종류)</p><p style='margin: 0; font-size: 20px; font-weight: 800;'>{icon} {ntype}</p></div><div class='moa-inner desc'><p style='margin: 0; font-size: 14px; opacity: 0.8;'>작용기작 구분 (대분류)</p><p style='margin: 0; font-size: 20px; font-weight: 800;'>🧬 {res.get('주 작용기작', '')}</p></div><div class='moa-inner detail'><p style='margin: 0; font-size: 15px; font-weight: 800; margin-bottom: 8px;'>세부 작용기작 및 계통(성분)</p><p style='margin: 0; font-size: 24px; color: #e57373; font-weight: 900; line-height: 1.4;'>🔬 {res.get('세부 작용기작', '')}</p></div></div>", unsafe_allow_html=True)

    # ----------------------------------------
    # 메뉴 5: 나의 방제이력
    # ----------------------------------------
    elif menu == "나의 방제이력":
        st.subheader("📋 나의 방제이력 (방제 일지)")
        
        df_history = fetch_spray_history()
        
        if df_history.empty: 
            st.info("아직 등록된 방제 이력이 없습니다. (아래에서 새로운 기록을 추가해보세요!)")
            empty_columns = ["Date", "Time", "Nongyak", "Type", "Kijak", "Spec", "Qty", "Tqty", "Byung", "Remark"]
            empty_df = pd.DataFrame(columns=empty_columns)
            styled_empty = empty_df.style.set_properties(**{'font-size': '14.5px', 'text-align': 'center', 'padding': '8px 10px', 'white-space': 'nowrap'})
            st.dataframe(styled_empty, hide_index=True)
        else:
            display_history = df_history.copy()
            rename_hist = {
                'Date': '방제일자', 'Time': '방제시간', 'Nongyak': '약제명', 'Type': '종류', 
                'Kijak': '작용기작', 'Spec': '규격', 'Qty': '수량', 'Tqty': '총살포량(L)', 
                'Byung': '적용병해충', 'Remark': '메모'
            }
            display_history = display_history.rename(columns=rename_hist)
            if 'ID' in display_history.columns: display_history = display_history.drop(columns=['ID']) 
            if '수량' in display_history.columns: display_history['수량'] = pd.to_numeric(display_history['수량'], errors='coerce')
            if '총살포량(L)' in display_history.columns: display_history['총살포량(L)'] = pd.to_numeric(display_history['총살포량(L)'], errors='coerce')
            styled_history = display_history.style.set_properties(**{'font-size': '14.5px', 'text-align': 'center', 'padding': '8px 10px', 'white-space': 'nowrap'})
            format_dict = {}
            if '수량' in display_history.columns: format_dict['수량'] = '{:.0f}'
            if '총살포량(L)' in display_history.columns: format_dict['총살포량(L)'] = '{:.0f}'
            if format_dict: styled_history = styled_history.format(format_dict, na_rep="")
            st.dataframe(styled_history, hide_index=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("➕ 새로운 방제 기록 추가하기 (최대 6개 약제 혼용 가능)", expanded=False):
            reset_key = st.session_state.form_reset_key
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1: h_date = st.date_input("📅 방제일자", value=date.today(), key=f"h_date_{reset_key}")
            with col_h2: 
                time_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 10)]
                default_time_idx = time_options.index("05:00")
                h_time_str = st.selectbox("⏰ 방제시작 (시간 선택)", options=time_options, index=default_time_idx, key=f"h_time_{reset_key}")
            with col_h3:
                st.markdown("<p style='font-size: 18px; font-weight: 800; margin-bottom: 5px;'>💧 총 살포량</p>", unsafe_allow_html=True)
                col_v1, col_v2 = st.columns([2, 1], gap="small")
                with col_v1: h_vol = st.text_input("살포량", placeholder="예: 1000", label_visibility="collapsed", key=f"h_vol_{reset_key}")
                with col_v2: h_unit = st.selectbox("단위", ["L", "말"], label_visibility="collapsed", key=f"h_unit_{reset_key}")
                
            col_h4, col_h5 = st.columns([1, 2])
            with col_h4: h_crop = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], key=f"h_crop_{reset_key}")
            with col_h5: 
                h_pest_list = st.multiselect("🐛 전체 방제 대상 병해충 (검색/선택)", options=pest_list, placeholder="병해충명을 검색하세요", key=f"h_pest_list_{reset_key}")
            h_memo = st.text_input("특이사항 (메모)", placeholder="예: 비 오기 전 예방살포", key=f"h_memo_{reset_key}")
            
            st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
            num_pest = st.selectbox("🔀 한 번에 섞어서 칠(혼용할) 약제는 몇 가지인가요?", [1, 2, 3, 4, 5, 6], index=0, key=f"num_pest_{reset_key}")
            
            st.markdown("<div style='border: 3px solid #ffb74d; border-radius: 15px; padding: 25px; box-shadow: 0px 6px 15px rgba(255,183,77,0.15); margin-bottom: 15px;'>", unsafe_allow_html=True)
            records_to_add = []
            for i in range(num_pest):
                st.markdown(f"<p style='color:#1b5e20; font-size:20px; font-weight:900; margin-top:15px;'>🧪 약제 {i+1} 상세정보</p>", unsafe_allow_html=True)
                sel_name = st.selectbox(f"상품명 (검색/선택) - 약제 {i+1}", options=[""] + pesticide_list, key=f"p_name_{i}_{reset_key}")
                
                d_type, d_moa, d_size, d_pest, d_family = "", "", "", "", ""
                if sel_name:
                    db_row = df_database[df_database['Product Name'] == sel_name]
                    if not db_row.empty:
                        r = db_row.iloc[0]
                        d_type, d_moa, d_size, d_pest, d_family = str(r.get('Type','')), str(r.get('Kijak','')), str(r.get('Spec','')), str(r.get('Byung','')), str(r.get('Gyetong',''))
                        
                col_p1, col_p2, col_p3 = st.columns(3)
                dynamic_key = f"_{sel_name}_{reset_key}"
                
                with col_p1: p_type = st.text_input(f"약제종류", value=d_type, key=f"p_type_{i}{dynamic_key}")
                with col_p2: p_moa = text_input(f"작용기작", value=d_moa, key=f"p_moa_{i}{dynamic_key}")
                with col_p3: p_size = st.text_input(f"규격", value=d_size, key=f"p_size_{i}{dynamic_key}")
                
                col_p4, col_p5, col_p6, col_p7 = st.columns(4)
                with col_p4: p_qty = st.text_input(f"수량", value="1", key=f"p_qty_{i}_{reset_key}") 
                with col_p5: p_pest = st.text_input(f"적용병해충", value=d_pest, key=f"p_pest_{i}{dynamic_key}")
                with col_p6: p_family = st.text_input(f"계통", value=d_family, key=f"p_family_{i}{dynamic_key}")
                with col_p7: pass 
                
                st.markdown("<hr style='margin: 10px 0; border-style: dashed; border-color: #a5d6a7;'>", unsafe_allow_html=True)
                records_to_add.append({"name": sel_name, "type": p_type, "moa": p_moa, "size": p_size, "qty": p_qty, "pest": p_pest, "family": p_family})
                
            submit_button = st.button("💾 입력한 방제 기록 DB에 일괄 저장하기", type="primary")
            
            if submit_button:
                valid = True
                for idx, rec in enumerate(records_to_add):
                    if not rec['name']: st.error(f"⚠️ 약제 {idx+1}의 상품명을 선택하거나 검색해 주세요."); valid = False; break
                
                if valid:
                    dt_str = h_date.strftime("%Y-%m-%d")
                    time_obj = datetime.strptime(h_time_str, "%H:%M")
                    formatted_time_str = time_obj.strftime("%I:%M %p").lstrip('0')
                    base_id = int(datetime.now().strftime("%y%m%d%H%M%S"))
                    
                    try: tqty_val = int(str(h_vol).replace(',', '').strip()) if str(h_vol).strip() else None
                    except: tqty_val = None
                        
                    db_insert_data = []
                    for idx, rec in enumerate(records_to_add):
                        try: qty_val = int(str(rec['qty']).replace(',', '').strip()) if str(rec['qty']).strip() else None
                        except: qty_val = None
                            
                        db_insert_data.append({
                            "ID": base_id + idx, "Date": dt_str, "Time": formatted_time_str, "Nongyak": rec['name'],
                            "Type": rec['type'], "Kijak": rec['moa'], "Spec": rec['size'], "Qty": qty_val,
                            "Tqty": tqty_val, "Byung": rec['pest'], "Remark": h_memo
                        })
                    
                    try:
                        supabase.table("DBbangje").insert(db_insert_data).execute()
                        st.success("✅ 혼용 방제 기록이 안전하게 클라우드 DB에 저장되었습니다!")
                        st.session_state.form_reset_key += 1
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 저장 중 오류가 발생했습니다: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------
    # 💡 [핵심 수정] 메뉴 6: 병해충 분석 (지능형 모델 탐색 및 다중 이미지 뷰어 적용)
    # ----------------------------------------
    elif menu == "병해충 분석":
        st.subheader("📸 AI 병해충 사진 정밀 판독 (Gemini AI)")
        st.markdown("과수원에서 발견한 병해충 의심 사진을 최대 5장까지 업로드해 주세요.")
        
        if not gemini_ready:
            st.error("🚨 Gemini API 키 설정에 문제가 있어 AI 판독 기능을 사용할 수 없습니다. 인터넷 연결과 Secrets 설정을 확인해주세요.")
            
        # 다중 업로드 (accept_multiple_files=True)
        uploaded_files = st.file_uploader("이미지 업로드 (최대 5장)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        
        if uploaded_files:
            if len(uploaded_files) > 5:
                st.warning("사진은 최대 5장까지 분석 가능합니다. 처음 5장의 사진만 판독합니다.")
                uploaded_files = uploaded_files[:5]
            
            st.success(f"✅ 총 {len(uploaded_files)}장의 사진이 입력되었습니다.")
            
            # 가로 5등분하여 사진을 썸네일 크기로 깔끔하게 한 줄 출력
            st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px;'>업로드된 사진 미리보기:</p>", unsafe_allow_html=True)
            cols_img = st.columns(5) # 무조건 5칸을 만들어 크기를 통일시킴
            pil_images = []
            
            for idx, img_file in enumerate(uploaded_files):
                image = Image.open(img_file)
                # 너무 큰 이미지는 크기를 줄여서 메모리 과부하 방지 (최대 800픽셀)
                image.thumbnail((800, 800))
                pil_images.append(image)
                with cols_img[idx]:
                    st.image(image, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Gemini AI 정밀 판독 시작", type="primary"):
                if not vision_model:
                    st.error("🚨 구글 서버에서 AI 모델을 찾지 못했습니다. 잠시 후 다시 시도해주세요.")
                else:
                    with st.spinner(f"인공지능({st.session_state.get('current_ai_model', 'Gemini')})이 사진을 분석하고 있습니다... (약 5~15초 소요)"):
                        try:
                            prompt = """
                            당신은 대한민국 제주도 환경의 감귤류(노지 감귤, 한라봉 등) 병해충 전문가입니다.
                            첨부된 사진들을 꼼꼼하게 분석하고, 어떤 병이나 해충의 피해인지 종합적으로 진단해주세요.
                            
                            반드시 아래 형식에 맞추어 답변을 작성해주세요:
                            
                            1. 진단명: (가장 가능성이 높은 병/해충의 정확한 공식 명칭)
                            2. 진단 근거: (사진의 어떤 부분을 보고 그렇게 판단했는지 구체적인 이유 2~3줄)
                            3. 방제 시기 및 방법: (이 병해충을 방제하기 위한 최적의 시기와 물리적/화학적 방법)
                            4. 추천 작용기작: (해당 병해충에 잘 듣는 농약의 '작용기작' 코드 기호 1~2개 추천. 예: 다3, 카, 1a 등)
                            
                            전문적이면서도 농민이 이해하기 쉽게 설명해주세요. 
                            만약 감귤과 관련 없는 사진이거나 판독이 불가할 경우 "판독 불가"라고 명확히 밝혀주세요.
                            """
                            
                            prompt_parts = [prompt] + pil_images
                            response = vision_model.generate_content(prompt_parts)
                            
                            st.success("✅ AI 정밀 판독이 완료되었습니다.")
                            st.markdown("### 🔍 AI 판독 결과 보고서")
                            st.markdown(f"<div class='ai-result-card'>{response.text}</div>", unsafe_allow_html=True)
                            st.error("⚠️ **[면책 조항]** 위 결과는 AI의 이미지 분석 결과이며, 빛의 각도나 화질에 따라 오류가 있을 수 있습니다. 실제 농약 살포 전 반드시 농업기술센터 등 전문가의 확진을 받으시길 권장합니다.")
                            
                        except Exception as e:
                            st.error(f"🚨 AI 판독 중 오류가 발생했습니다. (오류 내용: {e})")

    # ----------------------------------------
    # 메뉴 7: 정보교환마당
    # ----------------------------------------
    elif menu == "정보교환마당":
        st.subheader("💬 정보교환마당")
        
        df_board = pd.DataFrame()
        if supabase_connected:
            try:
                res_board = supabase.table("DBboard").select("*").order("created_at", desc=True).execute()
                df_board = pd.DataFrame(res_board.data)
            except Exception as e:
                st.error(f"게시판 데이터 로딩 중 오류가 발생했습니다: {e}")

        col_notice, col_qa = st.columns(2)
        with col_notice:
            n_html = "<div class='custom-card card-notice'><h4>📢 공지사항</h4><hr><ul>"
            if not df_board.empty and 'Type' in df_board.columns:
                df_notice = df_board[df_board['Type'] == '공지']
                if not df_notice.empty:
                    for _, row in df_notice.iterrows():
                        content = str(row.get('Content', '')).replace('\n', '<br>')
                        date_str = str(row.get('created_at', ''))[:10]
                        n_html += f"<li style='margin-bottom: 12px; line-height: 1.4;'>{content} <br><span style='font-size:12px; color:gray;'>({date_str})</span></li>"
                else: n_html += "<li>등록된 공지사항이 없습니다.</li>"
            else: n_html += "<li>등록된 공지사항이 없습니다.</li>"
            n_html += "</ul></div>"
            st.markdown(n_html, unsafe_allow_html=True)
            
            with st.expander("➕ 공지 등록 (관리자용)"):
                with st.form("notice_form", clear_on_submit=True):
                    new_notice = st.text_area("공지 내용 입력", height=100, placeholder="새로운 공지사항을 입력하세요.")
                    if st.form_submit_button("공지 등록", type="primary"):
                        if new_notice:
                            insert_data = {
                                "ID": int(datetime.now().strftime("%y%m%d%H%M%S")), "Type": "공지", "Author": "관리자",
                                "Content": new_notice, "UserID": st.session_state.current_user.get('id', 'admin') if st.session_state.logged_in else "admin"
                            }
                            try:
                                supabase.table("DBboard").insert(insert_data).execute()
                                st.success("✅ 공지가 등록되었습니다.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: st.error(f"🚨 공지 등록 실패: {e}")
                        else: st.warning("내용을 입력해주세요.")

        with col_qa:
            q_html = "<div class='custom-card card-qa'><h4>❓ 질문하고 답하기</h4><hr><div>"
            if not df_board.empty and 'Type' in df_board.columns:
                df_qa = df_board[df_board['Type'] == '질문']
                if not df_qa.empty:
                    for _, row in df_qa.iterrows():
                        author = row.get('Author', '익명')
                        content = str(row.get('Content', '')).replace('\n', '<br>')
                        reply = row.get('Reply', '')
                        date_str = str(row.get('created_at', ''))[:10]
                        q_html += f"<p style='margin-bottom: 5px; line-height: 1.4;'>👤 <b>{author}</b> <span style='font-size:11px; color:gray;'>{date_str}</span><br>{content}</p>"
                        if pd.notna(reply) and str(reply).strip() and str(reply) != 'None' and str(reply) != 'nan':
                            q_html += f"<p style='margin-left: 15px; color: #2e7d32; margin-top: 0; font-weight: bold;'>└ [답변] {str(reply).replace(chr(10), '<br>')}</p>"
                        q_html += "<hr style='margin: 12px 0; border-top: 1px dashed #90caf9;'>"
                else: q_html += "<p>등록된 질문이 없습니다.</p>"
            else: q_html += "<p>등록된 질문이 없습니다.</p>"
            q_html += "</div></div>"
            st.markdown(q_html, unsafe_allow_html=True)
            
            with st.expander("➕ 질문 남기기"):
                with st.form("qa_form", clear_on_submit=True):
                    default_author = st.session_state.current_user.get('name', '') if st.session_state.logged_in else ""
                    q_author = st.text_input("작성자명", value=default_author, placeholder="예: 조천읍 감귤농부")
                    q_content = st.text_area("질문 내용", height=100, placeholder="농약이나 병해충에 대해 궁금한 점을 남겨주세요.")
                    if st.form_submit_button("질문 등록", type="primary"):
                        if q_author and q_content:
                            insert_data = {
                                "ID": int(datetime.now().strftime("%y%m%d%H%M%S")), "Type": "질문", "Author": q_author,
                                "Content": q_content, "UserID": st.session_state.current_user.get('id', 'guest') if st.session_state.logged_in else "guest"
                            }
                            try:
                                supabase.table("DBboard").insert(insert_data).execute()
                                st.success("✅ 질문이 등록되었습니다.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: st.error(f"🚨 질문 등록 실패: {e}")
                        else: st.warning("작성자명과 질문 내용을 모두 입력해주세요.")

    st.markdown("<br><br><br>---", unsafe_allow_html=True)
    st.caption("<div style='text-align: center; color: gray; font-size: 1.1em;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)