import streamlit as st
from datetime import date
import pandas as pd
import re

# 1. 앱 기본 설정 (화면을 넓게 쓰고 감귤 테마 적용)
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# ==========================================
# 🎨 UI 디자인 업그레이드 (Custom CSS)
# ==========================================
st.markdown("""
    <style>
    /* 메인 메뉴(라디오 버튼) 세련된 스타일링 */
    div.row-widget.stRadio > div {
        background-color: #ffffff;
        padding: 15px 25px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    /* 검색 폼 스타일링 (감귤톤 테두리와 부드러운 배경) */
    div[data-testid="stForm"] {
        border: 2px solid #ffb74d;
        border-radius: 15px;
        padding: 25px;
        background-color: #fffdf8;
        box-shadow: 0px 4px 15px rgba(255,183,77,0.1);
    }
    /* 타이틀 중앙 정렬 및 색상 포인트 */
    .main-title {
        text-align: center;
        color: #e65100;
        font-weight: 800;
        margin-bottom: 20px;
    }
    /* 우측 조천읍 기상 정보 카드 스타일링 */
    .weather-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: #4a4a4a;
        font-weight: bold;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #ffcc80;
    }
    /* 우측 이미지 둥근 모서리 및 그림자 효과 */
    div[data-testid="stImage"] img {
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🍊 내가 찾는 농약</h1>", unsafe_allow_html=True)

# 2. 메인 메뉴 설정
menu = st.radio(
    "메인 메뉴", 
    ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 설명 찾기", "정보교환마당"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("<br>", unsafe_allow_html=True)

# 3. 엑셀 데이터베이스 불러오기 및 목록 추출
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
# 4. 메뉴별 화면 구성
# ==========================================

if menu == "내가 필요한 농약 찾기":
    col_main, col_img = st.columns([2.5, 1]) # 화면 비율을 조금 더 보기 좋게 조정
    
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
            
            # 버튼 디자인 변경(이모지 추가)
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
        # 🌟 데이터프레임 디자인 및 정렬 적용 (Pandas Styler 활용)
        # ==========================================
        if 'df_result' in st.session_state and not st.session_state.df_result.empty:
            current_df = st.session_state.df_result.head(st.session_state.list_count).copy()
            
            # 표시할 열 선택 ('계통' 추가 가능)
            display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충', '계통']
            display_df = current_df[[col for col in display_columns if col in current_df.columns]]
            
            # 금액 열을 숫자형으로 변환 (콤마 처리를 위함)
            if '금액 (원)' in display_df.columns:
                display_df['금액 (원)'] = pd.to_numeric(display_df['금액 (원)'], errors='coerce')
            
            # 정렬 기준 세팅
            center_cols = [col for col in display_df.columns if col not in ['적용병해충', '계통', '금액 (원)']]
            left_cols = [col for col in display_df.columns if col in ['적용병해충', '계통']]
            
            # 스타일 적용 (중앙, 좌측, 우측 정렬 및 천 단위 콤마)
            styled_df = display_df.style.set_properties(subset=center_cols, **{'text-align': 'center'})
            if left_cols:
                styled_df = styled_df.set_properties(subset=left_cols, **{'text-align': 'left'})
            if '금액 (원)' in display_df.columns:
                styled_df = styled_df.set_properties(subset=['금액 (원)'], **{'text-align': 'right'})
                # 천 단위 콤마 포맷팅
                styled_df = styled_df.format({'금액 (원)': '{:,.0f}'}, na_rep="")
            
            # 표 출력 (화면 꽉 차게)
            st.dataframe(styled_df, hide_index=True, use_container_width=True)
            
            if st.session_state.list_count < len(st.session_state.df_result):
                if st.button("➕ 5개 더 보기 (추가)"):
                    st.session_state.list_count += 5
                    st.rerun()

    # 우측 세련된 정보 카드 및 이미지
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
        st.dataframe(result, hide_index=True, use_container_width=True)
        
elif menu == "병해충명으로 찾기":
    st.subheader("🐛 병해충명 검색")
    search_pest = st.selectbox("방제할 병해충명을 선택하거나 입력하세요:", options=pest_list, index=None, placeholder="병해충명 검색 또는 선택")
    if search_pest:
        result = df_database[df_database['적용병해충'].astype(str).str.contains(search_pest)]
        st.dataframe(result, hide_index=True, use_container_width=True)
        
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

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("<div style='text-align: center; color: gray; font-size: 1.1em;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)