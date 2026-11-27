# =============================================================
#  [팀원 페이지 템플릿 ①]  데이터 분석 페이지 (디자인 업그레이드 버전)
#
#  ✏️ 표시가 있는 곳을 우리 팀 데이터에 맞게 바꾸세요.
#  - 파일 이름은 영어와 숫자로 바꾸세요. 예: 1_good_price.py
#  - 데이터 파일은 data 폴더에 넣으세요.
#  - 실행은 항상 팀 폴더에서:  streamlit run app.py
#    (내 페이지만 확인할 때: streamlit run pages/1_good_price.py)
#
#  이 페이지에 꼭 들어가야 하는 것 (주제 선정 조건)
#    ① CSV 불러오기  ② 정제 1가지 이상  ③ 사용자가 조작하는 기능
#    ④ 차트 1개 이상  ⑤ 차트에서 알게 된 점 한 문장
# =============================================================
import html
import re
from pathlib import Path

import pandas as pd
import streamlit as st

# ✏️ 1. 페이지 정보 --------------------------------------------
PAGE_TITLE = "🏪 부산 착한가격업소 종류별 현황"
MY_NAME = "작성자 : 이하연 (불어불문학과, 202602173)"
DATA_FILE = "부산 착한가격업소 조회.csv"  # data 폴더 안의 파일 이름

# ✏️ 2. 사용할 열 이름 (내 CSV의 열 이름으로 바꾸세요) -----------
GROUP_COL = "업소구분"      # 고르는 기준이 되는 열 (글자)
VALUE_COL = "업소수"        # 집계 후 차트로 보여 줄 열 (숫자)
# -------------------------------------------------------------

# data 폴더 위치 (단독 실행 및 pages 폴더 내 실행 모두 지원)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data" if (BASE_DIR.parent / "data").exists() else BASE_DIR / "data"
if not DATA_DIR.exists():
    DATA_DIR = BASE_DIR  # 같은 폴더에 CSV가 있을 경우 대비


def inject_custom_style():
    st.markdown(
        """
        <style>
        .hero-card {
            background: linear-gradient(135deg, #fff5f5 0%, #fff9db 100%);
            border: 1px solid #ffd8a8;
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 16px;
        }
        .hero-badge {
            display: inline-block;
            background-color: #ff6b6b;
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
        }
        .hero-title {
            margin: 0;
            font-size: 1.75rem;
            font-weight: 800;
            color: #212529;
        }
        .hero-sub {
            margin: 6px 0 0 0;
            font-size: 0.95rem;
            color: #495057;
        }
        .section-card {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 14px;
            padding: 18px 20px;
            margin-top: 12px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        }
        div[data-testid="stMetric"] {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 12px 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# 데이터 불러오기
@st.cache_data
def load_data(file_name):
    file_path = DATA_DIR / file_name
    try:
        return pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="cp949")


# ✏️ 3. 데이터 정제: 내 데이터에 필요한 것만 남기세요 ------------
def clean_data(df):
    df = df.copy()
    df[GROUP_COL] = df[GROUP_COL].fillna("미분류").astype(str).str.strip()  # 결측치 처리 및 앞뒤 공백 제거
    df = df.drop_duplicates(subset=["업체번호"])                           # 중복 업소 행 제거

    # 소개 컬럼 HTML 태그 정제 및 결측치 정리
    def clean_html(text):
        if pd.isna(text):
            return "-"
        text = html.unescape(str(text))
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    df["소개"] = df["소개"].apply(clean_html)
    df["대표전화"] = df["대표전화"].fillna("-")
    df["영업시간"] = df["영업시간"].fillna("-")
    df["주차여부"] = df["주차여부"].map({"Y": "가능", "N": "불가"}).fillna("-")

    # 목록에 보여줄 주요 컬럼만 남기기
    keep_cols = ["업체번호", GROUP_COL, "업소명", "지역", "대표전화", "영업시간", "주차여부", "소개"]
    return df[keep_cols]


def show_cleaning(raw, df):
    with st.expander("🔍 데이터 미리보기와 정제 결과"):
        c1, c2 = st.columns(2)
        c1.metric("정제 전 행 수", f"{len(raw):,}개")
        c2.metric("정제 후 행 수", f"{len(df):,}개", delta=f"{len(df) - len(raw):,}개")
        st.dataframe(df.drop(columns=["업체번호"]), hide_index=True, use_container_width=True)


def main():
    st.set_page_config(
        page_title="부산 착한가격업소 종류별 현황",
        page_icon="🏪",
        layout="wide",
    )
    inject_custom_style()

    # 헤더 배너
    st.markdown(
        f"""
        <div class="hero-card">
            <span class="hero-badge">BUSAN GOOD PRICE</span>
            <h1 class="hero-title">{PAGE_TITLE}</h1>
            <p class="hero-sub">담당: {MY_NAME} · 업소 종류별 분포를 한눈에 보고 원하는 업종 목록을 조회할 수 있습니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    raw = load_data(DATA_FILE)
    df = clean_data(raw)
    show_cleaning(raw, df)

    summary_df = (
        df.groupby(GROUP_COL, as_index=False)
        .size()
        .rename(columns={"size": VALUE_COL})
        .sort_values(VALUE_COL, ascending=False)
        .reset_index(drop=True)
    )
    top = summary_df.iloc[0]
    parking_count = (df["주차여부"] == "가능").sum()

    # 요약 KPI 카드 3개
    k1, k2, k3 = st.columns(3)
    k1.metric("전체 착한가격업소", f"{len(df):,}곳")
    k2.metric("최다 등록 업종", f"{top[GROUP_COL]} ({top[VALUE_COL]:,}곳)")
    k3.metric("주차 가능 업소", f"{parking_count:,}곳")

    # ✏️ 4. 차트: 업소 종류별 막대그래프 ------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"① {GROUP_COL}별 {VALUE_COL} 현황")
    st.caption("종류별 등록 업소 수를 비교한 막대그래프입니다.")
    st.bar_chart(summary_df, x=GROUP_COL, y=VALUE_COL, color="#ff6b6b", height=320)
    st.markdown("</div>", unsafe_allow_html=True)

    # ✏️ 5. 기능: 업소 종류를 선택하면 목록 보여주기 ---------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"② {GROUP_COL} 선택 및 업소 목록 조회")

    col_sel, col_search = st.columns([1, 2])
    with col_sel:
        options = sorted(df[GROUP_COL].unique())
        selected = st.selectbox(f"조회할 {GROUP_COL}을(를) 선택하세요", options)
    with col_search:
        keyword = st.text_input("업소명 또는 지역 검색 (선택)", placeholder="예: 국밥, 남포동, 해운대")

    view = df[df[GROUP_COL] == selected].drop(columns=["업체번호"])
    if keyword.strip():
        kw = keyword.strip()
        view = view[
            view["업소명"].str.contains(kw, case=False, na=False)
            | view["지역"].str.contains(kw, case=False, na=False)
        ]

    st.markdown(f"**'{selected}'** 선택 결과: 총 **{len(view):,}곳**")
    st.dataframe(
        view,
        hide_index=True,
        use_container_width=True,
        column_config={
            GROUP_COL: st.column_config.TextColumn("종류", width="small"),
            "업소명": st.column_config.TextColumn("업소명", width="medium"),
            "지역": st.column_config.TextColumn("주소", width="large"),
            "대표전화": st.column_config.TextColumn("전화번호", width="medium"),
            "영업시간": st.column_config.TextColumn("영업시간", width="medium"),
            "주차여부": st.column_config.TextColumn("주차", width="small"),
            "소개": st.column_config.TextColumn("소개", width="large"),
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ✏️ 6. 차트에서 알게 된 점 --------------------------------
    st.subheader("③ 차트에서 알게 된 점")
    st.info("부산 착한가격업소는 음식점 비중이 가장 크며, 업종별로 매장 수 차이가 뚜렷하게 나타납니다.")


main()
