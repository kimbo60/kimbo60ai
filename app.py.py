import streamlit as st
from datetime import date
import pandas as pd

# 앱 기본 설정 (화면을 넓게 쓰기 위해 layout="wide"로 변경)
st.set_page_config(page_title="내가 찾는 농약", page_icon="🍊", layout="wide")

# 상단 타이틀
st.title("🍊 내가 찾는 농약")

# 1. 메인 메뉴 설정 (가로형 라디오 버튼 활용)
menu = st.radio(
    "메인 메뉴", 
    ["내가 필요한 농약 찾기", "농약명으로 찾기", "병해충명으로 찾기", "작용기작 설명 찾기", "정보교환마당"],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("---")

# 2. 엑셀 데이터베이스 불러오기 (캐싱하여 앱 속도 향상)
@st.cache_data
def load_data():
    try:
        # 실제 올려주신 엑셀 파일 연동 (헤더가 두 번째 줄인 것을 반영)
        df = pd.read_excel('농약목록-전체-prg.xlsx', header=1)
        # 빈 데이터(NaN)를 빈 문자열로 처리하여 검색 시 오류 방지
        df = df.fillna('')
        return df
    except Exception as e:
        # ✨ 이 부분이 추가되었습니다: 실제 에러 원인을 화면에 빨간 글씨로 출력합니다.
        st.error(f"🚨 엑셀 파일을 읽는 중 문제가 발생했습니다. 원인: {e}")
        
        # 엑셀 파일이 같은 폴더에 없을 경우를 대비한 가상 데이터
        st.warning("⚠️ 임시 데이터를 띄웁니다.")
        return pd.DataFrame({
            "종류": ["살균제", "살균제", "살충제", "살충제"],
            "상품명": ["가스란", "다이센엠-45", "코니도", "팬텀"],
            "규격": ["500g", "500g", "250ml", "250g"],
            "금액 (원)": [17200, 14000, 11000, 15000],
            "사용량": ["25말", "25말", "25말", "25말"],
            "작용기작": ["카+라3", "카", "4a", "13"],
            "적용병해충": ["궤양병, 꽃썩음병", "검은점무늬병(흑점병), 귤응애", "진딧물", "총채벌레"],
            "계통": ["코퍼옥시클로라이드", "만코제브", "이미다클로프리드", "클로르페나피르"]
        })

df_database = load_data()
# 리스트 '추가 보기'를 위한 세션 상태 초기화
if 'list_count' not in st.session_state:
    st.session_state.list_count = 5

# ==========================================
# 3. 메뉴별 화면 구성
# ==========================================

if menu == "내가 필요한 농약 찾기":
    
    # 화면을 3:1 비율로 분할
    col_main, col_img = st.columns([3, 1])
    
    with col_main:
        st.subheader("📋 방제 조건 입력")
        with st.form("search_form"):
            # 1. 약제살포 예정일
            spray_date = st.date_input("약제살포 예정일", value=date.today())
            
            # 2. 작물명 (기본값: 노지 감귤)
            crop_type = st.selectbox("작물명", ["노지 감귤", "하우스 감귤", "비가림 감귤", "기타 과수"], index=0)
            
            # 3. 희망 약제명 (DB에 있는 상품명 목록 연동)
            pesticide_list = df_database["상품명"].unique().tolist()
            pesticide_list = [name for name in pesticide_list if name] # 빈 이름 제거
            
            desired_pesticide = st.multiselect(
                "희망 약제명 (선택)", 
                pesticide_list,
                placeholder="약제명을 검색하거나 선택하세요"
            )
            
            # 4. 발생 병해충
            target_pest = st.multiselect(
                "방제 대상 병해충 (선택)", 
                ["궤양병", "더뎅이병", "검은점무늬병", "잿빛곰팡이병", "귤응애", "귤굴나방", "볼록총채벌레", "진딧물"],
                placeholder="병해충명을 검색하거나 선택하세요"
            )
            
            # 5. 총 살포량
            total_volume = st.text_input("총 살포량", placeholder="예: 1000L 또는 50말")
            
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
                    pattern = '|'.join(target_pest) 
                    filtered_df = filtered_df[filtered_df['적용병해충'].str.contains(pattern)]
                    
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
            # 깔끔한 출력을 위해 필요한 열만 선택
            display_columns = ['종류', '상품명', '작용기작', '규격', '사용량', '금액 (원)', '적용병해충']
            # 존재하는 열만 골라서 출력
            display_df = current_df[[col for col in display_columns if col in current_df.columns]]
            st.dataframe(display_df, hide_index=True, use_container_width=True)
            
            # 5개씩 더 보기 버튼
            if st.session_state.list_count < len(st.session_state.df_result):
                if st.button("➕ 5개 더 보기 (추가)"):
                    st.session_state.list_count += 5
                    st.rerun()

    # 우측 1/4 공간: 날씨 정보 및 애니메이션 이미지(GIF) 배치
    with col_img:
        st.info("📍 제주시 조천읍\n\n🌤️ 오늘 기온: 24℃\n\n바람: 3m/s (방제 양호)")
        # 농장/자연 느낌의 움직이는 식물 GIF 이미지
        st.image("https://cdn.pixabay.com/animation/2022/10/27/12/37/12-37-33-289_512.gif", use_container_width=True, caption="싱그러운 과수원의 하루")

elif menu == "농약명으로 찾기":
    st.subheader("🔍 농약명 검색")
    search_name = st.text_input("찾으시는 농약 상품명을 입력하세요:")
    if search_name:
        result = df_database[df_database['상품명'].str.contains(search_name)]
        st.dataframe(result, hide_index=True, use_container_width=True)
        
elif menu == "병해충명으로 찾기":
    st.subheader("🐛 병해충명 검색")
    search_pest = st.text_input("방제할 병해충명을 입력하세요:")
    if search_pest:
        result = df_database[df_database['적용병해충'].str.contains(search_pest)]
        st.dataframe(result, hide_index=True, use_container_width=True)
        
elif menu == "작용기작 설명 찾기":
    st.subheader("🔬 작용기작 사전")
    st.info("준비 중인 기능입니다. 향후 작용기작 코드(예: 카+라3, 4a)를 입력하면 세부 설명과 교차 살포 경고가 나타나도록 연동될 예정입니다.")
    
elif menu == "정보교환마당":
    st.subheader("💬 정보교환마당")
    tab1, tab2 = st.tabs(["📢 공지사항", "❓ 묻고 답하기 (Q&A)"])
    with tab1:
        st.write("**[필독]** 장마철 검은점무늬병 주의보 발령 (누적 강수량 200mm 초과 예상)")
    with tab2:
        st.write("👤 **제주농부**: 잎 뒷면에 이런 하얀 딱지가 생겼는데 더뎅이병일까요?")
        st.write(" └ 👨‍🌾 **KIMBO**: 사진상으로는 볼록총채벌레 피해 흔적과 유사해 보입니다.")

# 하단 공간 확보 및 서명
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("<div style='text-align: center; color: gray;'><b>Developed by KIMBO & Gemini</b></div>", unsafe_allow_html=True)