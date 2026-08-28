import streamlit as st
from datetime import date
import pandas as pd
import re
import os
import base64

# 1. 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 🎨 UI 디자인 14.1 (마크다운 코드 블록 에러 수정)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #fcf9f2; }
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
        font-size: 18px !important; font-weight: 800 !important; color: #333333; margin-bottom: 5px;
    }
    input[type="text"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input, textarea { font-size: 16px !important; padding: 6px 10px !important; }
    div[data-testid="stForm"] { border: 3px solid #ffb74d; border-radius: 15px; padding: 25px; background-color: #ffffff; box-shadow: 0px 6px 15px rgba(255,183,77,0.15); margin-bottom: 15px; }
    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(to right, #4caf50, #2e7d32) !important; color: white !important; font-size: 20px !important; font-weight: 800 !important;
        border-radius: 12px !important; padding: 12px 20px !important; border: none !important; box-shadow: 0px 6px 0px #1b5e20, 0px 8px 10px rgba(0,0,0,0.2) !important;
        transition: all 0.1s; margin-top: 15px; width: 100%; 
    }
    button[kind="secondaryFormSubmit"]:active { box-shadow: 0px 2px 0px #1b5e20, 0px 4px 5px rgba(0,0,0,0.2) !important; transform: translateY(4px) !important; }
    .weather-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 15px 20px; border-radius: 15px; text-align: center;
        color: #3e2723; font-size: 1.15rem; font-weight: 800; line-height: 1.4; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); margin-bottom: 15px; border: 3px solid #ffcc80;
    }
    @media (max-width: 768px) {
        .hallabong-title { font-size: 2rem !important; padding: 15px !important; border-radius: 12px !important; margin-bottom: 15px !important;}
        .hallabong-title img { width: 40px !important; margin-right: 8px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] { gap: 6px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label { padding: 6px 10px !important; border-radius: 8px !important; border-width: 1px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label p { font-size: 14px !important; }
        div[data-testid="stForm"] { padding: 15px !important; border-radius: 10px !important; border-width: 2px !important; }
        div[data-testid="stForm"] label p, div[data-testid="stSelectbox"] label p, div[data-testid="stMultiSelect"] label p, div[data-testid="stTextInput"] label p, div[data-testid="stDateInput"] label p, div[data-testid="stTextArea"] label p { font-size: 16px !important; }
        input[type="text"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input, textarea { font-size: 14px !important; padding: 5px !important; }
        button[kind="secondaryFormSubmit"] { font-size: 18px !important; padding: 10px !important; border-radius: 10px !important; box-shadow: 0px 4px 0px #1b5e20, 0px 5px 8px rgba(0,0,0,0.3) !important; margin-top: 10px !important; }
        button[kind="secondaryFormSubmit"]:active { box-shadow: 0px 1px 0px #1b5e20, 0px 2px 4px rgba(0,0,0,0.3) !important; transform: translateY(3px) !important; }
        .weather-card { font-size: 1.05rem !important; padding: 12px 15px !important; border-radius: 12px !important; border-width: 2px !important; }
        
        div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important; flex-wrap: nowrap !important; gap: 10px !important;
        }
        div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: auto !important; min-width: 0 !important; flex: 1 1 0% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

if 'notices' not in st.session_state:
    st.session_state.notices = [
        "<b>[필독]</b> 장마철 검은점무늬병 주의보 발령 (누적 강수량 200mm 초과 예상)",
        "[안내] 신규 등록 약제(살균제) 3종 리스트 업데이트 완료"
    ]
if 'qnas' not in st.session_state:
    st.session_state.qnas = [
        {"author": "제주농부", "content": "잎 뒷면에 이런 하얀 딱지가 생겼는데 더뎅이병일까요?", "reply": "👨‍🌾 KIMBO: 사진상으로는 볼록총채벌레 피해 흔적과 유사해 보입니다."}
    ]

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None

icon_path = "아이콘001.png"
icon_base64 = get_image_base64(icon_path)

if icon_base64:
    icon_tag = f'<img src="{icon_base64}" width="60" style="vertical-align: middle; margin-right: 15px; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));">'
else:
    icon_tag = '🍊'

# 🌟 들여쓰기 제거
st.markdown(f"""
<a href="/" target="_self" class="home-link">
    <div class='hallabong-title'>
        {icon_tag} 내가 찾는 농약
    </div>
</a>
""", unsafe_allow_html=True)

menu = st.radio(
    "메인 메뉴", 
    ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 설명 찾기", "정보교환마당"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("<br>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel('listall_nongyak.xlsx', header=1)
    df = df.fillna('')
    pesticide_raw = df["상품명"].astype(str).unique().tolist()
    pesticide_list = sorted([name.strip() for name in pesticide_raw if name.strip()])
    df_pest_only = df[df['종류'].isin(['살균제', '살충제'])]
    pest_raw = df_pest_only["적용병해충"].astype(str).tolist()
    pest_set = set()
    for pests in pest_raw:
        for p in pests.split(','):
            p_clean = re.sub(r'\(.*?\)', '', p).replace('(', '').replace(')', '').strip()
            if p_clean: pest_set.add(p_clean)
    pest_list = sorted(list(pest_set))
    return df, pesticide_list, pest_list

@st.cache_data
def load_moa_data():
    try:
        df_moa = pd.read_excel('kijak.xlsx')
        df_moa = df_moa.fillna('')
        return df_moa
    except:
        return pd.DataFrame()

try:
    df_database, pesticide_list, pest_list = load_data()
except Exception as e:
    st.error(f"🚨 엑셀 파일을 읽지 못했습니다.\n\n(상세 에러: {e})")
    st.stop()

if 'list_count' not in st.session_state:
    st.session_state.list_count = 5

def get_styled_dataframe(df, list_count=None):
    if list_count: df = df.head(list_count).copy()
    else: df = df.copy()
        
    display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충', '계통']
    df = df[[col for col in display_columns if col in df.columns]]
    
    if '금액 (원)' in df.columns:
        df['금액 (원)'] = pd.to_numeric(df['금액 (원)'], errors='coerce')
    
    center_cols = [col for col in df.columns if col in ['종류', '상품명', '작용기작', '규격', '사용량']]
    left_cols = [col for col in df.columns if col in ['적용병해충', '계통']]
    
    styled_df = df.style.set_properties(**{
        'font-size': '15px', 'font-weight': '600', 'padding': '8px 10px', 'line-height': '1.3'
    })
    
    if center_cols: styled_df = styled_df.set_properties(subset=center_cols, **{'text-align': 'center'})
    if left_cols: styled_df = styled_df.set_properties(subset=left_cols, **{'text-align': 'left'})
    if '금액 (원)' in df.columns:
        styled_df = styled_df.set_properties(subset=['금액 (원)'], **{'text-align': 'right'})
        styled_df = styled_df.format({'금액 (원)': '{:,.0f}'}, na_rep="")
        
    return styled_df

# ==========================================
# 3. 메뉴별 화면 구성
# ==========================================

if menu == "내가 필요한 농약 찾기":
    col_main, col_img = st.columns([7, 3])
    with col_main:
        form_col_out1, form_empty_out = st.columns([7, 3])
        with form_col_out1:
            spray_date = st.date_input("약제살포 예정일", value=date.today())
            weekdays = ['월', '화', '수', '목', '금', '토', '일']
            weekday_str = weekdays[spray_date.weekday()]
            formatted_date = spray_date.strftime(f"%Y년 %m월 %d일 ({weekday_str}요일)")
            st.markdown(f"<div style='color: #1565c0; font-size: 16px; font-weight: bold; margin-top: -10px; margin-bottom: 15px; padding-left: 5px;'>👉 선택된 날짜: {formatted_date}</div>", unsafe_allow_html=True)

        with st.form("search_form"):
            form_col1, form_empty = st.columns([7, 3]) 
            with form_col1:
                crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
                desired_pesticide = st.multiselect("희망 약제명 (클릭하거나 검색)", options=pesticide_list, placeholder="약제명 검색 또는 선택")
                target_pest = st.multiselect("방제 대상 병해충 (클릭하거나 검색)", options=pest_list, placeholder="병해충명 검색 또는 선택")
                
                st.markdown("<p style='font-size: 18px; font-weight: 800; color: #333333; margin-bottom: 5px; margin-top: 15px;'>총 살포량</p>", unsafe_allow_html=True)
                col_vol1, col_vol2, col_vol3 = st.columns([2.5, 1.2, 3.3])
                with col_vol1:
                    total_volume = st.text_input("살포량 입력", placeholder="예: 1000", label_visibility="collapsed")
                with col_vol2:
                    volume_unit = st.selectbox("단위", ["L", "말"], index=0, label_visibility="collapsed")
            
            submitted = st.form_submit_button("🔎 조건에 맞는 농약 찾기")

        if submitted:
            st.session_state.list_count = 5
            if not desired_pesticide and not target_pest:
                st.error("⚠️ 희망 약제명 또는 발생 병해충 중 최소 한 가지는 입력해 주세요.")
            else:
                if not total_volume:
                    st.warning("💡 총 살포량을 입력하지 않으셨습니다. 필요한 약제량을 제안해 드릴 수 없습니다.")
                filtered_df = df_database.copy()
                if target_pest:
                    pattern = '|'.join(target_pest) 
                    filtered_df = filtered_df[filtered_df['적용병해충'].astype(str).str.contains(pattern)]
                if desired_pesticide:
                    filtered_df = filtered_df[filtered_df['상품명'].isin(desired_pesticide)]
                
                st.session_state.df_result = filtered_df
                if filtered_df.empty: st.error("조건에 맞는 약제가 없습니다.")
                else: st.success(f"✅ 총 {len(filtered_df)}개의 약제가 검색되었습니다. (💡 표의 열 제목을 클릭하면 정렬됩니다)")

        if 'df_result' in st.session_state and not st.session_state.df_result.empty:
            styled_df = get_styled_dataframe(st.session_state.df_result, st.session_state.list_count)
            st.dataframe(styled_df, hide_index=True, use_container_width=True)
            
            if st.session_state.list_count < len(st.session_state.df_result):
                if st.button("➕ 5개 더 보기 (추가)"):
                    st.session_state.list_count += 5
                    st.rerun()

    with col_img:
        # 🌟 들여쓰기 제거
        st.markdown("""
<div class="weather-card">
    📍 제주시 조천읍 감귤원 실시간 날씨<br>
    🌤️ 기온: 28℃ | 습도: 75%<br>
    🍃 풍속: 3.2 m/s (방제 최적)
</div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-size: 15px; font-weight: 800; color: #333333; margin-bottom: 8px; margin-top: 10px;'>📅 향후 10일 방제 날씨 예보</p>", unsafe_allow_html=True)
        
        forecast_data = [
            {"일자": "8/27(목)", "날씨": "☀️ 맑음", "기온": "24°/29°", "방제": "🟢 최적"},
            {"일자": "8/28(금)", "날씨": "⛅ 구름", "기온": "25°/30°", "방제": "🔵 양호"},
            {"일자": "8/29(토)", "날씨": "🌧️ 비", "기온": "24°/27°", "방제": "🔴 불가"},
            {"일자": "8/30(일)", "날씨": "☁️ 흐림", "기온": "23°/26°", "방제": "🟠 보통"},
            {"일자": "8/31(월)", "날씨": "☀️ 맑음", "기온": "24°/28°", "방제": "🟢 최적"},
            {"일자": "9/1(화)",  "날씨": "☀️ 맑음", "기온": "23°/28°", "방제": "🟢 최적"},
            {"일자": "9/2(수)",  "날씨": "⛅ 구름", "기온": "24°/29°", "방제": "🔵 양호"},
            {"일자": "9/3(목)",  "날씨": "🌦️ 소나기", "기온": "23°/27°", "방제": "🟠 주의"},
            {"일자": "9/4(금)",  "날씨": "☀️ 맑음", "기온": "23°/28°", "방제": "🟢 최적"},
            {"일자": "9/5(토)",  "날씨": "☀️ 맑음", "기온": "24°/29°", "방제": "🟢 최적"},
        ]
        
        df_weather = pd.DataFrame(forecast_data)
        styled_weather = df_weather.style.set_properties(**{
            'font-size': '13.5px', 'font-weight': '600', 'text-align': 'center', 'padding': '6px 5px'
        })
        st.dataframe(styled_weather, hide_index=True, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if os.path.exists("farm.gif"): st.image("farm.gif", use_container_width=True, caption="싱그러운 과수원의 하루")
        elif os.path.exists("farm.png"): st.image("farm.png", use_container_width=True, caption="싱그러운 과수원의 하루")

elif menu == "농약명으로 찾기":
    col_limit, col_empty = st.columns([7, 3])
    with col_limit:
        st.subheader("🔍 농약명 검색")
        search_name = st.selectbox("찾으시는 농약 상품명을 선택하거나 입력하세요:", options=pesticide_list, index=None, placeholder="약제명 검색 또는 선택")
    
    if search_name and search_name.strip() != "":
        result = df_database[df_database['상품명'].astype(str) == search_name]
        st.success("💡 표의 열 제목('상품명', '금액' 등)을 클릭하면 정렬됩니다.")
        styled_res = get_styled_dataframe(result)
        st.dataframe(styled_res, hide_index=True, use_container_width=True)
    else:
        st.info("👆 위 입력창에 찾으시는 농약명(상품명)을 검색하거나 선택해주세요.")
        
elif menu == "병해충명으로 찾기":
    col_limit, col_empty = st.columns([7, 3])
    with col_limit:
        st.subheader("🐛 병해충명 검색")
        search_pest = st.selectbox("방제할 병해충명을 선택하거나 입력하세요:", options=pest_list, index=None, placeholder="병해충명 검색 또는 선택")
    
    if search_pest and search_pest.strip() != "":
        result = df_database[df_database['적용병해충'].astype(str).str.contains(search_pest)]
        st.success("💡 표의 열 제목('상품명', '금액' 등)을 클릭하면 정렬됩니다.")
        styled_res = get_styled_dataframe(result)
        st.dataframe(styled_res, hide_index=True, use_container_width=True)
    else:
        st.info("👆 위 입력창에 찾으시는 병해충명을 검색하거나 선택해주세요.")
        
elif menu == "작용기작 설명 찾기":
    col_limit, col_empty = st.columns([7, 3])
    with col_limit:
        st.subheader("🔬 작용기작 사전")
        
        df_moa = load_moa_data()
        if df_moa.empty:
            st.error("🚨 작용기작 엑셀 파일('kijak.xlsx')을 찾을 수 없거나 읽을 수 없습니다. 깃허브에 파일이 정확히 올라가 있는지 확인해주세요.")
        else:
            moa_codes = sorted([str(code).strip() for code in df_moa['표시기호'].unique() if str(code).strip()])
            
            search_moa = st.selectbox("궁금한 작용기작 코드(표시기호)를 선택하거나 직접 입력하세요:", options=moa_codes, index=None, placeholder="예: 가1, 1a, H01")
            
            if search_moa and search_moa.strip() != "":
                moa_result = df_moa[df_moa['표시기호'].astype(str) == search_moa].iloc[0]
                
                nongyak_type = moa_result.get('농약종류', '')
                type_icon = "🧪"
                if "살균" in nongyak_type: type_icon = "🛡️"
                elif "살충" in nongyak_type: type_icon = "🐛"
                elif "제초" in nongyak_type: type_icon = "🌿"
                
                # 🌟 마크다운 코드 블록 오류 방지를 위해 왼쪽으로 바짝 붙여서 작성 (들여쓰기 제거)
                st.markdown(f"""
<div style='background-color: #f8fbfa; padding: 25px; border-radius: 20px; border: 3px solid #66bb6a; box-shadow: 0px 8px 20px rgba(0,0,0,0.1); margin-top: 20px; position: relative; overflow: hidden;'>
    <div style='position: absolute; top: -15px; right: -15px; font-size: 110px; opacity: 0.04;'>{type_icon}</div>
    <h2 style='color: #1b5e20; margin-top: 0; font-size: 26px; font-weight: 900; margin-bottom: 25px;'>
        <span style='background-color: #e65100; color: white; padding: 5px 15px; border-radius: 12px; font-size: 30px;'>{search_moa}</span>
        <span style='margin-left: 10px; color: #43a047;'>작용기작 상세 정보</span>
    </h2>
    <div style='background-color: white; padding: 15px 20px; border-radius: 12px; box-shadow: 0px 2px 5px rgba(0,0,0,0.03); margin-bottom: 15px; border-left: 5px solid #1565c0;'>
        <p style='margin: 0; font-size: 14px; color: #757575; font-weight: 600;'>분류 (농약종류)</p>
        <p style='margin: 0; font-size: 20px; color: #1565c0; font-weight: 800;'>{type_icon} {nongyak_type}</p>
    </div>
    <div style='background-color: white; padding: 15px 20px; border-radius: 12px; box-shadow: 0px 2px 5px rgba(0,0,0,0.03); margin-bottom: 15px; border-left: 5px solid #e65100;'>
        <p style='margin: 0; font-size: 14px; color: #757575; font-weight: 600;'>작용기작 구분 (대분류)</p>
        <p style='margin: 0; font-size: 20px; color: #e65100; font-weight: 800;'>🧬 {moa_result.get('작용기작 구분', '')}</p>
    </div>
    <div style='background-color: #e8f5e9; padding: 20px; border-radius: 12px; border-left: 5px solid #2e7d32; box-shadow: 0px 2px 5px rgba(0,0,0,0.05);'>
        <p style='margin: 0; font-size: 15px; color: #2e7d32; font-weight: 800; margin-bottom: 8px;'>세부 작용기작 및 계통(성분)</p>
        <p style='margin: 0; font-size: 24px; color: #b71c1c; font-weight: 900; line-height: 1.4;'>🔬 {moa_result.get('세부 작용기작 및 계통(성분)', '')}</p>
    </div>
</div>
""", unsafe_allow_html=True)
            else:
                st.info("👆 약제 라벨에 적힌 작용기작 코드(예: 가1, 1a, H01)를 검색창에 입력하시거나 목록에서 선택해주세요.")

elif menu == "정보교환마당":
    st.subheader("💬 정보교환마당")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_notice, col_qa = st.columns(2)
    
    with col_notice:
        # 🌟 들여쓰기 제거
        notice_html = """
<div style='background-color: #fffde7; padding: 25px; border-radius: 15px; border: 2px solid #fdd835; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); height: 100%; min-height: 350px;'>
    <h4 style='color: #f57f17; margin-top: 0; font-size: 22px;'>📢 공지사항</h4>
    <hr style='border-color: #fdd835; margin-top: 10px; margin-bottom: 15px;'>
    <ul style='font-size: 16px; color: #333; line-height: 1.8;'>
        """
        for n in st.session_state.notices:
            notice_html += f"<li>{n}</li>"
        notice_html += "</ul></div>"
        st.markdown(notice_html, unsafe_allow_html=True)
        
        with st.expander("➕ 새로운 공지 등록하기"):
            with st.form("notice_form", clear_on_submit=True):
                new_notice = st.text_input("공지 내용 입력")
                notice_submit = st.form_submit_button("등록")
                if notice_submit and new_notice:
                    st.session_state.notices.append(new_notice)
                    st.rerun()

    with col_qa:
        # 🌟 들여쓰기 제거
        qa_html = """
<div style='background-color: #e3f2fd; padding: 25px; border-radius: 15px; border: 2px solid #64b5f6; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); height: 100%; min-height: 350px;'>
    <h4 style='color: #1565c0; margin-top: 0; font-size: 22px;'>❓ 묻고 답하기 (Q&A)</h4>
    <hr style='border-color: #64b5f6; margin-top: 10px; margin-bottom: 15px;'>
    <div style='font-size: 16px; color: #333; line-height: 1.6;'>
        """
        for q in st.session_state.qnas:
            qa_html += f"<p>👤 <b>{q['author']}</b>: {q['content']}</p>"
            if q['reply']:
                qa_html += f"<p style='margin-left: 15px; color: #1565c0; font-weight: bold;'> └ {q['reply']}</p>"
        qa_html += "</div></div>"
        st.markdown(qa_html, unsafe_allow_html=True)
        
        with st.expander("➕ 새로운 질문 남기기"):
            with st.form("qa_form", clear_on_submit=True):
                q_author = st.text_input("작성자 (이름 또는 닉네임)", placeholder="예: 조천읍 감귤농부")
                q_content = st.text_area("질문 내용", placeholder="과수원 관리 중 궁금한 점을 자유롭게 남겨주세요.")
                qa_submit = st.form_submit_button("질문 등록")
                if qa_submit and q_author and q_content:
                    st.session_state.qnas.append({"author": q_author, "content": q_content, "reply": ""})
                    st.rerun()

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("<div style='text-align: center; color: gray; font-size: 1.1em;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)