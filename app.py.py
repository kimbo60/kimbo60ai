import streamlit as st
from datetime import date
import pandas as pd
import re
import os
import base64  # 🌟 로컬 이미지 변환을 위한 모듈 추가


# 1. 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")


# ==========================================
# 🎨 UI 디자인 8.0 (로컬 아이콘 파일 적용 버전)
# ==========================================
st.markdown("""
    <style>
    /* 전체 배경 */
    .stApp { background-color: #fcf9f2; }


    .hallabong-title {
        background: linear-gradient(135deg, #ff9800 0%, #e65100 100%);
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-weight: 900;
        font-size: 2.8rem;
        box-shadow: 0px 6px 15px rgba(230, 81, 0, 0.3);
        margin-bottom: 20px;
        border: 3px solid #ffcc80;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex; flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 15px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] div[data-baseweb="radio"] div { display: none !important; }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: linear-gradient(145deg, #e8f5e9, #c8e6c9) !important; 
        border: 2px solid #a5d6a7 !important;
        padding: 8px 16px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 0px #81c784, 0px 6px 8px rgba(0,0,0,0.1) !important;
        cursor: pointer; transition: all 0.1s ease-in-out; margin: 0 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        font-size: 17px !important; 
        font-weight: 800 !important; 
        color: #1b5e20 !important; 
        margin: 0 !important; 
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:active,
    div[data-testid="stRadio"] div[role="radiogroup"] label:focus-within {
        transform: translateY(3px) !important; 
        box-shadow: 0px 1px 0px #81c784, 0px 3px 4px rgba(0,0,0,0.1) !important;
        background: linear-gradient(145deg, #c8e6c9, #a5d6a7) !important;
    }


    div[data-testid="stForm"] label p, div[data-testid="stSelectbox"] label p, div[data-testid="stMultiSelect"] label p, div[data-testid="stTextInput"] label p, div[data-testid="stDateInput"] label p {
        font-size: 18px !important; font-weight: 800 !important; color: #333333; margin-bottom: 5px;
    }
    
    input[type="text"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input {
        font-size: 16px !important; padding: 6px 10px !important;
    }


    div[data-testid="stForm"] {
        border: 3px solid #ffb74d; border-radius: 15px; padding: 25px; background-color: #ffffff; box-shadow: 0px 6px 15px rgba(255,183,77,0.15); margin-bottom: 15px;
    }


    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(to right, #4caf50, #2e7d32) !important; color: white !important; font-size: 20px !important; font-weight: 800 !important;
        border-radius: 12px !important; padding: 12px 20px !important; border: none !important; box-shadow: 0px 6px 0px #1b5e20, 0px 8px 10px rgba(0,0,0,0.2) !important;
        transition: all 0.1s; margin-top: 15px; width: 100%; 
    }
    button[kind="secondaryFormSubmit"]:active {
        box-shadow: 0px 2px 0px #1b5e20, 0px 4px 5px rgba(0,0,0,0.2) !important; transform: translateY(4px) !important;
    }


    .weather-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; border-radius: 15px; text-align: center;
        color: #3e2723; font-size: 1.3rem; font-weight: 900; box-shadow: 0px 6px 15px rgba(0,0,0,0.1); margin-bottom: 15px; border: 3px solid #ffcc80;
    }


    @media (max-width: 768px) {
        .hallabong-title { font-size: 2rem !important; padding: 15px !important; border-radius: 12px !important; margin-bottom: 15px !important;}
        .hallabong-title img { width: 40px !important; margin-right: 8px !important; }
        
        div[data-testid="stRadio"] div[role="radiogroup"] { gap: 6px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label { padding: 6px 10px !important; border-radius: 8px !important; border-width: 1px !important; }
        div[data-testid="stRadio"] div[role="radiogroup"] label p { font-size: 14px !important; }
        
        div[data-testid="stForm"] { padding: 15px !important; border-radius: 10px !important; border-width: 2px !important; }
        div[data-testid="stForm"] label p, div[data-testid="stSelectbox"] label p, div[data-testid="stMultiSelect"] label p, div[data-testid="stTextInput"] label p, div[data-testid="stDateInput"] label p { font-size: 16px !important; }
        
        input[type="text"], div[data-baseweb="select"] span, div[data-baseweb="select"] input, div[data-testid="stDateInput"] input { font-size: 14px !important; padding: 5px !important; }
        
        button[kind="secondaryFormSubmit"] { font-size: 18px !important; padding: 10px !important; border-radius: 10px !important; box-shadow: 0px 4px 0px #1b5e20, 0px 5px 8px rgba(0,0,0,0.3) !important; margin-top: 10px !important; }
        button[kind="secondaryFormSubmit"]:active { box-shadow: 0px 1px 0px #1b5e20, 0px 2px 4px rgba(0,0,0,0.3) !important; transform: translateY(3px) !important; }
        
        .weather-card { font-size: 1.1rem !important; padding: 15px !important; border-radius: 12px !important; border-width: 2px !important; }
    }
    </style>
""", unsafe_allow_html=True)


# 🌟 로컬 이미지 파일을 읽어서 Base64로 변환하는 함수
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None


# 아이콘 파일 불러오기 시도
icon_path = "아이콘001.png"
icon_base64 = get_image_base64(icon_path)


if icon_base64:
    icon_tag = f'<img src="{icon_base64}" width="60" style="vertical-align: middle; margin-right: 15px; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));">'
else:
    icon_tag = '🍊'  # 파일이 없을 경우 기본 오렌지 이모지 대체


# 🍊 메인 타이틀 (아이콘 적용)
st.markdown(f"""
    <div class='hallabong-title'>
        {icon_tag} 내가 찾는 농약
    </div>
""", unsafe_allow_html=True)


# 1. 메인 메뉴 설정
menu = st.radio(
    "메인 메뉴", 
    ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 설명 찾기", "정보교환마당"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("<br>", unsafe_allow_html=True)


# 2. 엑셀 데이터베이스 불러오기 및 목록 추출
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
            p_clean = re.sub(r'\(.*?\)', '', p)
            p_clean = p_clean.replace('(', '').replace(')', '').strip()
            if p_clean:
                pest_set.add(p_clean)
                
    pest_list = sorted(list(pest_set))
    return df, pesticide_list, pest_list


try:
    df_database, pesticide_list, pest_list = load_data()
except Exception as e:
    st.error(f"🚨 엑셀 파일을 읽지 못했습니다. 'listall_nongyak.xlsx' 파일 업로드 확인 요망.\n\n(상세 에러: {e})")
    st.stop()


if 'list_count' not in st.session_state:
    st.session_state.list_count = 5


# ==========================================
# 3. 메뉴별 화면 구성
# ==========================================


if menu == "내가 필요한 농약 찾기":
    col_main, col_img = st.columns([7, 3])
    
    with col_main:
        with st.form("search_form"):
            form_col1, form_empty = st.columns([7, 3]) 
            
            with form_col1:
                spray_date = st.date_input("약제살포 예정일", value=date.today())
                crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
                
                desired_pesticide = st.multiselect("희망 약제명 (클릭하거나 검색)", options=pesticide_list, placeholder="약제명 검색 또는 선택")
                target_pest = st.multiselect("방제 대상 병해충 (클릭하거나 검색)", options=pest_list, placeholder="병해충명 검색 또는 선택")
                
                st.markdown("<p style='font-size: 18px; font-weight: 800; color: #333333; margin-bottom: 5px; margin-top: 15px;'>총 살포량</p>", unsafe_allow_html=True)
                col_vol1, col_vol2 = st.columns([3, 1])
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


                if filtered_df.empty:
                    st.error("조건에 맞는 약제가 없습니다. 다른 조건으로 검색해 보세요.")
                else:
                    st.success(f"✅ 총 {len(filtered_df)}개의 약제가 검색되었습니다.")


        if 'df_result' in st.session_state and not st.session_state.df_result.empty:
            current_df = st.session_state.df_result.head(st.session_state.list_count).copy()
            display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충', '계통']
            display_df = current_df[[col for col in display_columns if col in current_df.columns]]
            
            if '금액 (원)' in display_df.columns:
                display_df['금액 (원)'] = pd.to_numeric(display_df['금액 (원)'], errors='coerce')
            
            center_cols = [col for col in display_df.columns if col not in ['적용병해충', '계통', '금액 (원)']]
            left_cols = [col for col in display_df.columns if col in ['적용병해충', '계통']]
            
            styled_df = display_df.style.set_properties(**{
                'font-size': '15px',
                'font-weight': '600',
                'padding': '8px 10px',
                'line-height': '1.3'
            })
            
            styled_df = styled_df.set_properties(subset=center_cols, **{'text-align': 'center'})
            if left_cols:
                styled_df = styled_df.set_properties(subset=left_cols, **{'text-align': 'left'})
            if '금액 (원)' in display_df.columns:
                styled_df = styled_df.set_properties(subset=['금액 (원)'], **{'text-align': 'right'})
                styled_df = styled_df.format({'금액 (원)': '{:,.0f}'}, na_rep="")
            
            st.dataframe(styled_df, hide_index=True, use_container_width=True)
            
            if st.session_state.list_count < len(st.session_state.df_result):
                if st.button("➕ 5개 더 보기 (추가)"):
                    st.session_state.list_count += 5
                    st.rerun()


    with col_img:
        st.markdown("""
            <div class="weather-card">
                📍 제주시 조천읍 감귤원<br><br>
                🌤️ 오늘 기온: 24℃<br><br>
                🍃 바람: 3m/s (방제 양호)
            </div>
        """, unsafe_allow_html=True)
        if os.path.exists("farm.gif"):
            st.image("farm.gif", use_container_width=True, caption="싱그러운 과수원의 하루")
        elif os.path.exists("farm.png"):
            st.image("farm.png", use_container_width=True, caption="싱그러운 과수원의 하루")
        else:
            st.info("💡 깃허브에 'farm.gif' 또는 'farm.png' 이미지를 올려주시면 여기에 나타납니다.")


elif menu == "농약명으로 찾기":
    col_limit, col_empty = st.columns([6, 4])
    with col_limit:
        st.subheader("🔍 농약명 검색")
        search_name = st.selectbox("찾으시는 농약 상품명을 선택하거나 입력하세요:", options=pesticide_list, index=None, placeholder="약제명 검색 또는 선택")
    if search_name:
        result = df_database[df_database['상품명'].astype(str) == search_name]
        styled_res = result.style.set_properties(**{'font-size': '15px', 'font-weight': '600', 'padding': '8px 10px'})
        st.dataframe(styled_res, hide_index=True, use_container_width=True)
        
elif menu == "병해충명으로 찾기":
    col_limit, col_empty = st.columns([6, 4])
    with col_limit:
        st.subheader("🐛 병해충명 검색")
        search_pest = st.selectbox("방제할 병해충명을 선택하거나 입력하세요:", options=pest_list, index=None, placeholder="병해충명 검색 또는 선택")
    if search_pest:
        result = df_database[df_database['적용병해충'].astype(str).str.contains(search_pest)]
        styled_res = result.style.set_properties(**{'font-size': '15px', 'font-weight': '600', 'padding': '8px 10px'})
        st.dataframe(styled_res, hide_index=True, use_container_width=True)
        
elif menu == "작용기작 설명 찾기":
    st.subheader("🔬 작용기작 사전")
    st.info("준비 중인 기능입니다. 향후 작용기작 코드를 입력하면 세부 설명과 교차 살포 경고가 연동될 예정입니다.")
    
elif menu == "정보교환마당":
    st.subheader("💬 정보교환마당")
    tab1, tab2 = st.tabs(["📢 공지사항", "❓ 묻고 답하기 (Q&A)"])
    with tab1:
        st.write("**[필독]** 장마철 검은점무늬병 주의보 발령 (누적 강수량 200mm 초과 예상)")
    with tab2:
        st.write("👤 **제주농부**: 잎 뒷면에 이런 하얀 딱지가 생겼는데 더뎅이병일까요?")
        st.write(" └ 👨‍🌾 **KIMBO**: 사진상으로는 볼록총채벌레 피해 흔적과 유사해 보입니다.")


st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("<div style='text-align: center; color: gray; font-size: 1.1em;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)