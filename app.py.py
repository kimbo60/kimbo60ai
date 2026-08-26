import streamlit as st
from datetime import date
import pandas as pd
import re

# 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

st.title("🍊 내가 찾는 농약")

# 1. 메인 메뉴 설정
menu = st.radio(
    "메인 메뉴", 
    ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 설명 찾기", "정보교환마당"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("---")

# 2. 엑셀 데이터베이스 불러오기 및 목록 추출
@st.cache_data
def load_data():
    df = pd.read_excel('listall_nongyak.xlsx', header=1)
    df = df.fillna('')
    
    # [농약명 목록 추출 및 가나다순 정렬]
    pesticide_raw = df["상품명"].astype(str).unique().tolist()
    pesticide_list = sorted([name.strip() for name in pesticide_raw if name.strip()])
    
    # [병해충명 목록 추출 (살균제/살충제만 포함, 괄호 완전 제거 및 가나다순 정렬)]
    # 제초제, 4종복비 등을 제외하고 오직 '살균제'와 '살충제' 행만 추려냄
    df_pest_only = df[df['종류'].isin(['살균제', '살충제'])]
    pest_raw = df_pest_only["적용병해충"].astype(str).tolist()
    
    pest_set = set()
    for pests in pest_raw:
        # 쉼표(,)를 기준으로 분리
        for p in pests.split(','):
            # 정규표현식을 사용하여 괄호()와 그 안의 내용 1차 제거
            p_clean = re.sub(r'\(.*?\)', '', p)
            # 남아있을 수 있는 열린/닫힌 괄호 기호 강제 삭제
            p_clean = p_clean.replace('(', '').replace(')', '')
            p_clean = p_clean.strip()
            
            if p_clean:
                pest_set.add(p_clean)
                
    pest_list = sorted(list(pest_set))
    
    return df, pesticide_list, pest_list

# 엑셀 파일 로드 시도 및 에러 처리
try:
    df_database, pesticide_list, pest_list = load_data()
except Exception as e:
    st.error(f"🚨 엑셀 파일을 읽지 못했습니다. 'listall_nongyak.xlsx' 파일이 깃허브에 정확히 업로드되었는지 확인해주세요.\n\n(상세 에러: {e})")
    st.stop()

# 리스트 '추가 보기'를 위한 세션 상태 초기화
if 'list_count' not in st.session_state:
    st.session_state.list_count = 5

# ==========================================
# 3. 메뉴별 화면 구성
# ==========================================

if menu == "내가 필요한 농약 찾기":
    col_main, col_img = st.columns([3, 1])
    
    with col_main:
        st.subheader("📋 방제 조건 입력")
        with st.form("search_form"):
            # 1. 약제살포 예정일
            spray_date = st.date_input("약제살포 예정일", value=date.today())
            
            # 2. 작물명
            crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
            
            # 3. 희망 약제명
            desired_pesticide = st.multiselect(
                "희망 약제명 (클릭하여 선택하거나 직접 검색하세요)", 
                options=pesticide_list,
                placeholder="약제명 검색 또는 선택"
            )
            
            # 4. 발생 병해충
            target_pest = st.multiselect(
                "방제 대상 병해충 (클릭하여 선택하거나 직접 검색하세요)", 
                options=pest_list,
                placeholder="병해충명 검색 또는 선택"
            )
            
            # 5. 총 살포량 및 단위 선택
            st.write("총 살포량")
            col_vol1, col_vol2 = st.columns([3, 1])
            with col_vol1:
                total_volume = st.text_input("살포량 입력", placeholder="예: 1000", label_visibility="collapsed")
            with col_vol2:
                volume_unit = st.selectbox("단위", ["L", "말"], index=0, label_visibility="collapsed")
            
            # 검색 버튼
            submitted = st.form_submit_button("🔍 조건에 맞는 농약 찾기")

        # 검색 로직
        if submitted:
            st.session_state.list_count = 5
            
            if not desired_pesticide and not target_pest:
                st.error("⚠️ 희망 약제명 또는 발생 병해충 중 최소 한 가지는 입력해 주세요.")
            else:
                if not total_volume:
                    st.warning("💡 총 살포량을 입력하지 않으셨습니다. 이 정보를 입력하시면 필요한 약제량을 정확히 제안해 드릴 수 없습니다.")
                
                # 검색 필터링
                filtered_df = df_database.copy()
                
                if target_pest:
                    # 선택된 병해충 필터링
                    pattern = '|'.join(target_pest) 
                    filtered_df = filtered_df[filtered_df['적용병해충'].astype(str).str.contains(pattern)]
                    
                if desired_pesticide:
                    filtered_df = filtered_df[filtered_df['상품명'].isin(desired_pesticide)]
                
                st.session_state.df_result = filtered_df

                if filtered_df.empty:
                    st.error("조건에 맞는 약제가 없습니다. 다른 조건으로 검색해 보세요.")
                else:
                    st.success(f"✅ 총 {len(filtered_df)}개의 약제가 검색되었습니다.")

        # 결과 데이터프레임 출력
        if 'df_result' in st.session_state and not st.session_state.df_result.empty:
            current_df = st.session_state.df_result.head(st.session_state.list_count)
            display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충']
            display_df = current_df[[col for col in display_columns if col in current_df.columns]]
            st.dataframe(display_df, hide_index=True, use_container_width=True)
            
            if st.session_state.list_count < len(st.session_state.df_result):
                if st.button("➕ 5개 더 보기 (추가)"):
                    st.session_state.list_count += 5
                    st.rerun()

    with col_img:
        st.info("📍 제주시 조천읍\n\n🌤️ 오늘 기온: 24℃\n\n바람: 3m/s (방제 양호)")
        st.image("https://cdn.pixabay.com/animation/2022/10/27/12/37/12-37-33-289_512.gif", use_container_width=True, caption="싱그러운 과수원의 하루")

elif menu == "농약명으로 찾기":
    st.subheader("🔍 농약명 검색")
    search_name = st.selectbox(
        "찾으시는 농약 상품명을 선택하거나 입력하세요:", 
        options=pesticide_list, 
        index=None, 
        placeholder="약제명 검색 또는 선택"
    )
    if search_name:
        result = df_database[df_database['상품명'].astype(str) == search_name]
        st.dataframe(result, hide_index=True, use_container_width=True)
        
elif menu == "병해충명으로 찾기":
    st.subheader("🐛 병해충명 검색")
    search_pest = st.selectbox(
        "방제할 병해충명을 선택하거나 입력하세요:", 
        options=pest_list, 
        index=None, 
        placeholder="병해충명 검색 또는 선택"
    )
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
st.caption("<div style='text-align: center; color: gray;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)