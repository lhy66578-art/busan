import re
import html
import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="부산 착한가격업소 조회",
    page_icon="🏪",
    layout="wide"
)

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    # 인코딩 자동 감지 로드
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="cp949")

    # 결측치 처리
    df["업소구분"] = df["업소구분"].fillna("미분류")
    df["대표전화"] = df["대표전화"].fillna("-")
    df["영업시간"] = df["영업시간"].fillna("-")
    df["주차여부"] = df["주차여부"].map({"Y": "가능", "N": "불가"}).fillna("-")

    # '소개' 컬럼의 HTML 엔티티 및 태그 정제
    def clean_text(text):
        if pd.isna(text):
            return "-"
        text = html.unescape(str(text))
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    df["소개_정제"] = df["소개"].apply(clean_text)
    return df

# 데이터 불러오기
FILE_PATH = "부산 착한가격업소 조회.csv"
try:
    df = load_data(FILE_PATH)
except FileNotFoundError:
    st.error(f"'{FILE_PATH}' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 CSV 파일을 위치시켜 주세요.")
    st.stop()

# 타이틀 영역
st.title("🏪 부산광역시 착한가격업소 현황 및 조회")
st.markdown("업소 종류별 분포를 확인하고, 원하는 종류를 선택해 상세 업소 목록을 조회할 수 있습니다.")

# 요약 지표(KPI) 표시
col1, col2, col3 = st.columns(3)
col1.metric("전체 착한가격업소 수", f"{len(df):,}개")
col2.metric("업소 종류 수", f"{df['업소구분'].nunique()}종")
col3.metric("주차 가능 업소 수", f"{(df['주차여부'] == '가능').sum():,}개")

st.divider()

# 1. 업소 종류별 막대그래프 섹션
st.subheader("📊 업소 종류별 등록 현황")

category_counts = (
    df["업소구분"]
    .value_counts()
    .reset_index()
)
category_counts.columns = ["업소구분", "업소수"]

fig = px.bar(
    category_counts,
    x="업소구분",
    y="업소수",
    text="업소수",
    color="업소구분",
    labels={"업소구분": "업소 종류", "업소수": "업소 수(개)"},
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig.update_traces(texttemplate="%{text:,}개", textposition="outside")
fig.update_layout(
    showlegend=False,
    yaxis_title="업소 수 (개)",
    xaxis_title="업소 종류",
    height=420,
    margin=dict(t=30, b=20)
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# 2. 업소 종류 선택 및 상세 목록 조회 섹션
st.subheader("📋 업소 종류별 상세 목록")

filter_col1, filter_col2 = st.columns([1, 2])

with filter_col1:
    categories = ["전체"] + category_counts["업소구분"].tolist()
    selected_category = st.selectbox(
        "조회할 업소 종류를 선택하세요:",
        options=categories,
        index=0
    )

with filter_col2:
    search_keyword = st.text_input(
        "업소명 또는 지역(동/구) 검색 (선택 사항):",
        placeholder="예: 국밥, 남포동, 해운대..."
    )

# 선택 조건에 따른 데이터 필터링
filtered_df = df.copy()
if selected_category != "전체":
    filtered_df = filtered_df[filtered_df["업소구분"] == selected_category]

if search_keyword.strip():
    kw = search_keyword.strip()
    filtered_df = filtered_df[
        filtered_df["업소명"].str.contains(kw, case=False, na=False) |
        filtered_df["지역"].str.contains(kw, case=False, na=False) |
        filtered_df["지역구분"].str.contains(kw, case=False, na=False)
    ]

st.write(f"선택된 조건의 업소: 총 **{len(filtered_df):,}곳**")

# 표에 보여줄 주요 컬럼 선택 및 정리
display_cols = ["업소구분", "업소명", "지역", "대표전화", "영업시간", "주차여부", "소개_정제"]
display_df = filtered_df[display_cols].rename(columns={"소개_정제": "업소 소개"})

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "업소구분": st.column_config.TextColumn("종류", width="small"),
        "업소명": st.column_config.TextColumn("업소명", width="medium"),
        "지역": st.column_config.TextColumn("주소", width="large"),
        "대표전화": st.column_config.TextColumn("전화번호", width="medium"),
        "영업시간": st.column_config.TextColumn("영업시간", width="medium"),
        "주차여부": st.column_config.TextColumn("주차", width="small"),
        "업소 소개": st.column_config.TextColumn("소개", width="large"),
    }
)
