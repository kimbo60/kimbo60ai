import streamlit as st
from datetime import date
import pandas as pd
import re

# 1. 앱 기본 설정 (화면을 넓게 쓰고 감귤 테마 적용)
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 🎨 UI 디자인 2.0 업그레이드 (화려한 3D 테마)
# ==========================================
st.markdown("""
    <style>
    /* 전체 배경을 따뜻하고 밝은 톤으로 변경 */
    .stApp {
        background-color: #fcf9f2;
    }

    /* 메인 타이틀 화려한 배경 및 3D 효과 */
    .hallabong-title {
        background: linear-gradient(135deg, #ff9800 0%, #e65100 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-weight: 900;
        font-size: 3.5rem;
        box-shadow: 0px 10px 20px rgba(230, 81, 0, 0.4);
        margin-bottom: 30px;
        border: 3px solid #ffcc80;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }

    /* 🌟 메인 메뉴(라디오 버튼) 3D 버튼 스타일링 🌟 */
    /* 가로 정렬 및 간격 띄우기 */
    div.row-widget.stRadio > div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
        margin-bottom: 20px;
    }
    /* 기본 동그라미 선택 아이콘 숨기기 */
    div.row-widget.stRadio > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    /* 3D 입체 버튼 디자인 (글자 크기 3단계 업그레이드) */
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        background: linear-gradient(145deg, #ffb74d, #f57c00);
        border: 2px solid #e65100;
        padding: 20px 30px;
        border-radius: 15px;
        box-shadow: 0px 8px 0px #bf360c, 0px 12px 15px rgba(0,0,0,0.2);
        transition: all 0.15s ease-in-out;
        cursor: pointer;
    }
    /* 버튼 글씨 크기 3단계 업 및 중앙 정렬 */
    div.row-widget.stRadio > div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {
        font-size: 26px !important;
        font-weight: 900 !important;
        color: white !important;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.4);
    }
    /* 버튼이 클릭되었을 때 들어가는 액션 효과 */
    div.row-widget.stRadio > div[role="radiogroup"] > label:active,
    div.row-widget.stRadio > div[role="radiogroup"] > label:focus-within {
        background: linear-gradient(145deg, #f57c00, #e65100);
        box-shadow: 0px 3px 0px #bf360c, 0px 5px 10px rgba(0,0,0,0.2);
        transform: translateY(5px);
    }

    /* 검색 폼 스타일링 */
    div[data-testid="stForm"] {
        border: 3px solid #ffb74d;
        border-radius: 20px;
        padding: 30px;
        background-color: #ffffff;
        box-shadow: 0px 8px 20px rgba(255,183,77,0.15);
    }

    /* 제출 버튼 화려하게 변경 */
    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(to right, #4caf50, #2e7d32) !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        border: none !important;
        box-shadow: 0px 5px 0px #1b5e20, 0px 8px 10px rgba(0,0,0,0.2) !important;
        transition: all 0.1s;
    }
    button[kind="secondaryFormSubmit"]:active {
        box-shadow: 0px 2px 0px #1b5e20, 0px 4px 5px rgba(0,0,0,0.2) !important;
        transform: translateY(3px) !important;
    }

    /* 우측 날씨 카드 디자인 */
    .weather-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        color: #3e2723;
        font-size: 1.2rem;
        font-weight: bold;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 2px solid #ffcc80;
    }
    </style>
""", unsafe_allow_html=True)

# 🍊 메인 타이틀 (한라봉 이미지 적용)
st.markdown("""
    <div class='hallabong-title'>
        <img src="https://cdn3d.iconscout.com/3d/premium/thumb/orange-4623192-3837943.png" width="80" style="vertical-align: middle; margin-right: 15px; drop-shadow: 2px 2px 5px rgba(0,0,0,0.5);">
        내가 찾는 농약
    </div>
""", unsafe_allow_html=True)

# 1. 메인 메뉴 설정 (3D 버튼 스타일 적용됨)
menu = st.radio(
    "메인 메뉴", 
    ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 설명 찾기", "정보교환마당"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("<br><br>", unsafe_allow_html=True)

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
    col_main, col_img = st.columns([2.5, 1])
    
    with col_main:
        st.subheader("📋 방제 조건 입력")
        with st.form("search_form"):
            spray_date = st.date_input("약제살포 예정일", value=date.today())
            crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
            
            desired_pesticide = st.multiselect(
                "희망 약제명 (클릭하여 선택하거나 직접 검색하세요)", 
                options=pesticide_list,
                placeholder="약제명 검색 또는 선택"
            )
            
            target_pest = st.multiselect(
                "방제 대상 병해충 (클릭하여 선택하거나 직접 검색하세요)", 
                options=pest_list,
                placeholder="병해충명 검색 또는 선택"
            )
            
            st.write("총 살포량")
            col_vol1, col_vol2 = st.columns([3, 1])
            with col_vol1:
                total_volume = st.text_input("살포량 입력", placeholder="예: 1000", label_visibility="collapsed")
            with col_vol2:
                volume_unit = st.selectbox("단위", ["L", "말"], index=0, label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
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

        # ==========================================
        # 🌟 표 글자 크기 2단계 업그레이드
        # ==========================================
        if 'df_result' in st.session_state and not st.session_state.df_result.empty:
            current_df = st.session_state.df_result.head(st.session_state.list_count).copy()
            
            display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충', '계통']
            display_df = current_df[[col for col in display_columns if col in current_df.columns]]
            
            if '금액 (원)' in display_df.columns:
                display_df['금액 (원)'] = pd.to_numeric(display_df['금액 (원)'], errors='coerce')
            
            center_cols = [col for col in display_df.columns if col not in ['적용병해충', '계통', '금액 (원)']]
            left_cols = [col for col in display_df.columns if col in ['적용병해충', '계통']]
            
            # CSS를 통한 표 폰트 크기 및 높이 설정
            styled_df = display_df.style.set_properties(**{
                'font-size': '1.25rem',  # 글자 크기 대폭 확대
                'font-weight': '600',
                'padding': '15px'
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

    # 우측 날씨 카드 & 애니메이션 이미지
    with col_img:
        st.markdown("""
            <div class="weather-card">
                📍 제주시 조천읍 감귤원<br><br>
                🌤️ 오늘 기온: 24℃<br><br>
                🍃 바람: 3m/s (방제 양호)
            </div>
        """, unsafe_allow_html=True)
        st.image("https://cdn.pixabay.com/animation/2022/10/27/12/37/12-37-33-289_512.gif", use_container_width=True, caption="싱그러운 과수원의 하루")

elif menu == "농약명으로 찾기":
    st.subheader("🔍 농약명 검색")
    search_name = st.selectbox("찾으시는 농약 상품명을 선택하거나 입력하세요:", options=pesticide_list, index=None, placeholder="약제명 검색 또는 선택")
    if search_name:
        result = df_database[df_database['상품명'].astype(str) == search_name]
        styled_res = result.style.set_properties(**{'font-size': '1.25rem', 'padding': '10px'})
        st.dataframe(styled_res, hide_index=True, use_container_width=True)
        
elif menu == "병해충명으로 찾기":
    st.subheader("🐛 병해충명 검색")
    search_pest = st.selectbox("방제할 병해충명을 선택하거나 입력하세요:", options=pest_list, index=None, placeholder="병해충명 검색 또는 선택")
    if search_pest:
        result = df_database[df_database['적용병해충'].astype(str).str.contains(search_pest)]
        styled_res = result.style.set_properties(**{'font-size': '1.25rem', 'padding': '10px'})
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
st.caption("<div style='text-align: center; color: gray; font-size: 1.2em;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)