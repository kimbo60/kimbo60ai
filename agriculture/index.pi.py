import streamlit as st
from datetime import date
import pandas as pd

# 앱 기본 설정
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="centered")

st.title("🍊 내가 찾는 농약")
st.markdown("---")

# 리스트 '추가 보기'를 위한 세션 상태 초기화
if 'list_count' not in st.session_state:
    st.session_state.list_count = 5

# --- [가상 데이터베이스 구축] ---
# 실제 개발 시에는 이 부분을 pd.read_excel('농약목록-전체-prg.xlsx') 로 대체합니다.
db_data = {
    "명칭": ["가스란", "골드타임", "깨끗탄", "나폴레옹", "네오보르도", "다이센엠-45", "코니도", "팬텀"],
    "작용기작": ["카+라3", "다2", "나1+나2", "다3", "카", "카", "4a", "13"],
    "사용량": ["25말", "25말", "5말", "25말", "25말", "25말", "25말", "25말"],
    "가격(원)": [17200, 20300, 8400, 16500, 12500, 14000, 11000, 15000],
    "적용병해충": ["궤양병, 꽃썩음병", "잿빛곰팡이병, 더뎅이병", "잿빛곰팡이병", "검은별무늬병, 잿빛곰팡이병", "더뎅이병, 궤양병", "검은점무늬병(흑점병), 귤응애", "진딧물", "총채벌레"]
}
df_database = pd.DataFrame(db_data)
# -------------------------------

st.subheader("📋 방제 조건 입력")

with st.form("search_form"):
    # 1. 약제살포 예정일
    spray_date = st.date_input("약제살포 예정일", value=date.today())
    
    # 2. 작물명
    crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
    
    # 3. 희망 약제명
    desired_pesticide = st.multiselect(
        "희망 약제명 (선택)", 
        df_database["명칭"].tolist(),
        placeholder="약제명을 검색하거나 선택하세요"
    )
    
    # 4. 발생 병해충
    target_pest = st.multiselect(
        "방제 대상 병해충 (선택)", 
        ["궤양병", "더뎅이병", "검은점무늬병", "잿빛곰팡이병", "귤응애", "총채벌레", "진딧물"],
        placeholder="병해충명을 검색하거나 선택하세요"
    )
    
    # 5. 총 살포량
    total_volume = st.text_input("총 살포량", placeholder="예: 1000L 또는 50말")
    
    # 검색 버튼
    submitted = st.form_submit_button("🔍 조건에 맞는 농약 찾기")

# 버튼이 눌렸을 때의 로직
if submitted:
    st.session_state.list_count = 5 # 검색 시 리스트 개수 초기화
    
    # 조건 검사
    if not desired_pesticide and not target_pest:
        st.error("⚠️ 희망 약제명 또는 발생 병해충 중 최소 한 가지는 입력해 주세요.")
    else:
        if not total_volume:
            st.warning("💡 총 살포량을 입력하지 않으셨습니다. 이 정보를 입력하시면 필요한 약제량을 정확히 제안해 드릴 수 없습니다.")
        
        # --- [검색 필터링 알고리즘] ---
        filtered_df = df_database.copy()
        
        # 1. 병해충으로 필터링 (선택한 병해충이 '적용병해충' 열에 포함되어 있는지 확인)
        if target_pest:
            # 선택된 병해충 중 하나라도 포함하는 행을 찾음
            pattern = '|'.join(target_pest) 
            filtered_df = filtered_df[filtered_df['적용병해충'].str.contains(pattern, na=False)]
            
        # 2. 희망 약제로 한 번 더 필터링 (선택한 경우)
        if desired_pesticide:
            filtered_df = filtered_df[filtered_df['명칭'].isin(desired_pesticide)]
        # -----------------------------
        
        # 결과 저장
        st.session_state.df_result = filtered_df

        if filtered_df.empty:
            st.error("조건에 맞는 약제가 없습니다. 다른 조건으로 검색해 보세요.")
        else:
            st.success(f"✅ 총 {len(filtered_df)}개의 약제가 검색되었습니다.")

# 결과 데이터프레임이 존재하고 비어있지 않으면 화면에 출력
if 'df_result' in st.session_state and not st.session_state.df_result.empty:
    current_df = st.session_state.df_result.head(st.session_state.list_count)
    st.dataframe(current_df, hide_index=True, use_container_width=True)
    
    # 5개씩 추가로 보여주기 버튼
    if st.session_state.list_count < len(st.session_state.df_result):
        if st.button("➕ 5개 더 보기 (추가)"):
            st.session_state.list_count += 5
            st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
# 하단 개발자 서명
st.caption("<div style='text-align: center; color: gray;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)