import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ==============================
# 기본 설정
# ==============================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
)


# ==============================
# 데이터 불러오기
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 여러 장르가 있는 경우 첫 번째 장르만 사용
    df["genre_first"] = (
        df["genre"]
        .fillna("알 수 없음")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    df["genre_first"] = df["genre_first"].replace("", "알 수 없음")

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # 문자형 열 결측값 처리
    df["movieNm"] = df["movieNm"].fillna("영화명 없음").astype(str)
    df["nation"] = df["nation"].fillna("알 수 없음").astype(str)
    df["nation"] = df["nation"].replace("", "알 수 없음")

    return df


try:
    df = load_data()
except Exception as error:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.code(str(error))
    st.stop()


# ==============================
# 제목과 데이터 요약
# ==============================
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "해당 기간에 개봉한 영화 데이터를 살펴봅니다."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("영화 편수", f"{len(df):,}편")

with col2:
    st.metric("장르 수", f"{df['genre_first'].nunique():,}개")

with col3:
    st.metric("제작 국가 수", f"{df['nation'].nunique():,}개")


# ==============================
# 1. 장르별 영화 편수 도넛 그래프
# ==============================
st.divider()
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre_first"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

genre_counts["비율"] = (
    genre_counts["영화 편수"]
    / genre_counts["영화 편수"].sum()
    * 100
)

fig_donut = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.48,
    title="장르별 영화 편수",
    color_discrete_sequence=px.colors.qualitative.Set3,
)

fig_donut.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
)

fig_donut.update_layout(
    height=550,
    legend_title_text="장르",
)

st.plotly_chart(fig_donut, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "장르별 영화 편수의 분포를 비교하면 어떤 장르의 영화가 "
    "박스오피스 10위권 영화에 많이 포함되었는지 알 수 있습니다."
)


# ==============================
# 2. 장르별 영화 트리맵
# ==============================
st.divider()
st.header("2. 장르별 영화 총 관객 트리맵")

treemap_data = df.dropna(subset=["total_audi"]).copy()

fig_treemap = px.treemap(
    treemap_data,
    path=["genre_first", "movieNm"],
    values="total_audi",
    color="genre_first",
    title="장르 안 영화별 총 관객",
    color_discrete_sequence=px.colors.qualitative.Set3,
    custom_data=["movieNm", "total_audi"],
)

fig_treemap.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "총 관객: %{customdata[1]:,}명<extra></extra>"
    )
)

fig_treemap.update_layout(height=650)

st.plotly_chart(fig_treemap, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "각 칸의 크기를 비교하면 장르별로 어떤 영화가 "
    "많은 관객을 모았는지 한눈에 살펴볼 수 있습니다."
)


# ==============================
# 3. 총 관객 히스토그램
# ==============================
st.divider()
st.header("3. 총 관객 분포")

hist_data = df.dropna(subset=["total_audi"]).copy()

fig_hist = px.histogram(
    hist_data,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수",
    },
    color_discrete_sequence=["#636EFA"],
)

fig_hist.update_layout(
    height=500,
    bargap=0.08,
)

fig_hist.update_xaxes(tickformat=",")

st.plotly_chart(fig_hist, use_container_width=True)

hist_counts, hist_bins = np.histogram(
    hist_data["total_audi"],
    bins=20,
)

most_common_bin_index = hist_counts.argmax()
most_common_start = hist_bins[most_common_bin_index]
most_common_end = hist_bins[most_common_bin_index + 1]

top_movie_row = hist_data.loc[hist_data["total_audi"].idxmax()]
top_movie = top_movie_row["movieNm"]
top_movie_audience = top_movie_row["total_audi"]

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    f"대부분의 영화는 총 관객 약 "
    f"{most_common_start:,.0f}명~{most_common_end:,.0f}명 "
    f"구간에 몰려 있습니다. "
    f"가장 관객이 많은 영화는 '{top_movie}'로 "
    f"총 {top_movie_audience:,.0f}명을 기록했습니다."
)


# ==============================
# 4. 산점도
# ==============================
st.divider()
st.header("4. 개봉일 스크린 수와 총 관객의 관계")

scatter_data = df.dropna(
    subset=["first_scrn", "total_audi"]
).copy()

fig_scatter = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    title="개봉일 스크린 수와 총 관객",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre_first": "장르",
    },
    custom_data=["movieNm"],
)

fig_scatter.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명<extra></extra>"
    )
)

fig_scatter.update_layout(height=600)
fig_scatter.update_yaxes(tickformat=",")

st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "개봉일 스크린 수가 많을수록 총 관객 수도 많아지는 경향이 있는지 "
    "영화별 점의 분포를 통해 비교할 수 있습니다."
)


# ==============================
# 5. 장르별 상자 그림
# ==============================
st.divider()
st.header("5. 영화가 10편 이상인 장르의 총 관객 분포")

genre_movie_counts = df["genre_first"].value_counts()

selected_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

box_data = df[
    df["genre_first"].isin(selected_genres)
    & df["total_audi"].notna()
].copy()

fig_box = px.box(
    box_data,
    x="genre_first",
    y="total_audi",
    color="genre_first",
    points="outliers",
    title="장르별 총 관객 상자 그림",
    labels={
        "genre_first": "장르",
        "total_audi": "총 관객 수",
    },
    custom_data=["movieNm"],
)

fig_box.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "총 관객: %{y:,}명<extra></extra>"
    )
)

fig_box.update_layout(
    height=600,
    showlegend=False,
)

fig_box.update_yaxes(tickformat=",")

st.plotly_chart(fig_box, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "영화가 10편 이상인 장르의 총 관객 중앙값과 분포를 비교하고, "
    "상자 밖의 점을 통해 특히 관객이 많거나 적은 영화를 찾을 수 있습니다."
)


# ==============================
# 6. 버블 산점도
# ==============================
st.divider()
st.header("6. 첫 주 관객을 표시한 버블 산점도")

bubble_data = df.dropna(
    subset=["first_scrn", "total_audi", "first_week_audi"]
).copy()

bubble_data["bubble_size"] = bubble_data["first_week_audi"].clip(
    lower=1
)

fig_bubble = px.scatter(
    bubble_data,
    x="first_scrn",
    y="total_audi",
    size="bubble_size",
    color="genre_first",
    size_max=55,
    title="개봉일 스크린 수, 총 관객, 첫 주 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre_first": "장르",
        "bubble_size": "첫 주 관객 수",
    },
    custom_data=["movieNm", "first_week_audi"],
)

fig_bubble.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{customdata[1]:,}명<extra></extra>"
    )
)

fig_bubble.update_layout(height=650)
fig_bubble.update_yaxes(tickformat=",")

st.plotly_chart(fig_bubble, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "점의 위치는 개봉일 스크린 수와 총 관객의 관계를, "
    "점의 크기는 첫 주 관객 규모를 나타냅니다."
)


# ==============================
# 7. 제작 국가와 장르 선버스트
# ==============================
st.divider()
st.header("7. 제작 국가와 장르별 영화 편수")

sunburst_data = (
    df.groupby(
        ["nation", "genre_first"],
        as_index=False,
    )
    .size()
    .rename(columns={"size": "영화 편수"})
)

fig_sunburst = px.sunburst(
    sunburst_data,
    path=["nation", "genre_first"],
    values="영화 편수",
    color="nation",
    title="제작 국가에서 장르로 내려가는 영화 편수",
    color_discrete_sequence=px.colors.qualitative.Bold,
)

fig_sunburst.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<extra></extra>"
    )
)

fig_sunburst.update_layout(height=700)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "제작 국가별로 어떤 장르의 영화가 많이 만들어졌는지, "
    "각 국가와 장르가 전체 영화 편수에서 차지하는 비중을 확인할 수 있습니다."
)


# ==============================
# 8. 흥행 기간 히스토그램
# ==============================
st.divider()
st.header("8. 영화가 10위권에 머문 기간")

days_data = df.dropna(
    subset=["days_in_top10"]
).copy()

days_data["흥행 기간"] = (
    days_data["days_in_top10"]
    .round()
    .astype(int)
)

fig_days_hist = px.histogram(
    days_data,
    x="흥행 기간",
    nbins=20,
    title="영화별 10위권 체류 기간 분포",
    labels={
        "흥행 기간": "10위권에 머문 날수",
        "count": "영화 편수",
    },
    color_discrete_sequence=["#00CC96"],
)

fig_days_hist.update_traces(
    hovertemplate=(
        "10위권 체류 기간: %{x}일<br>"
        "영화 편수: %{y}편<extra></extra>"
    )
)

fig_days_hist.update_layout(
    height=550,
    bargap=0.08,
)

st.plotly_chart(
    fig_days_hist,
    use_container_width=True,
)

days_counts, days_bins = np.histogram(
    days_data["days_in_top10"],
    bins=20,
)

most_common_days_index = days_counts.argmax()
most_common_days_start = days_bins[most_common_days_index]
most_common_days_end = days_bins[most_common_days_index + 1]

longest_movie_row = days_data.loc[
    days_data["days_in_top10"].idxmax()
]

longest_movie = longest_movie_row["movieNm"]
longest_days = longest_movie_row["days_in_top10"]

average_days = days_data["days_in_top10"].mean()
median_days = days_data["days_in_top10"].median()

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    f"대부분의 영화는 10위권에 약 "
    f"{most_common_days_start:,.0f}일~"
    f"{most_common_days_end:,.0f}일 "
    f"머문 구간에 몰려 있습니다. "
    f"영화들의 평균 체류 기간은 {average_days:,.1f}일, "
    f"중앙값은 {median_days:,.1f}일이며, "
    f"가장 오래 흥행한 영화는 '{longest_movie}'로 "
    f"{longest_days:,.0f}일 동안 10위권에 머물렀습니다."
)


# ==============================
# 8-1. 영화명별 흥행 기간 산점도
# ==============================
st.subheader("영화별 10위권 체류 기간")

# 보기 쉽게 오래 흥행한 영화 상위 30편만 표시
days_scatter_data = (
    days_data.sort_values(
        "days_in_top10",
        ascending=False,
    )
    .head(30)
    .copy()
)

# 산점도에서 위에서부터 오래 흥행한 영화가 보이도록 정렬
days_scatter_data = days_scatter_data.sort_values(
    "days_in_top10",
    ascending=True,
)

fig_days_scatter = px.scatter(
    days_scatter_data,
    x="days_in_top10",
    y="movieNm",
    color="genre_first",
    size="total_audi",
    size_max=35,
    title="10위권에 오래 머문 영화 TOP 30",
    labels={
        "days_in_top10": "10위권에 머문 날수",
        "movieNm": "영화명",
        "genre_first": "장르",
        "total_audi": "총 관객",
    },
    custom_data=[
        "movieNm",
        "genre_first",
        "days_in_top10",
        "total_audi",
    ],
)

fig_days_scatter.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "장르: %{customdata[1]}<br>"
        "10위권 체류 기간: %{customdata[2]:,.0f}일<br>"
        "총 관객: %{customdata[3]:,.0f}명"
        "<extra></extra>"
    )
)

fig_days_scatter.update_layout(
    height=900,
    xaxis_title="10위권에 머문 날수",
    yaxis_title="영화명",
)

st.plotly_chart(
    fig_days_scatter,
    use_container_width=True,
)

st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "점이 오른쪽에 있을수록 10위권에 오래 머문 영화이며, "
    "영화명과 장르를 함께 확인하여 장기 흥행 작품을 비교할 수 있습니다."
)


# ==============================
# 흥행 기간 순위표
# ==============================
with st.expander("흥행 기간이 긴 영화 순위표 보기"):
    longest_movies = (
        days_data[
            [
                "movieNm",
                "genre_first",
                "days_in_top10",
                "total_audi",
            ]
        ]
        .sort_values(
            "days_in_top10",
            ascending=False,
        )
        .head(20)
        .rename(
            columns={
                "movieNm": "영화명",
                "genre_first": "장르",
                "days_in_top10": "10위권 체류 일수",
                "total_audi": "총 관객",
            }
        )
    )

    st.dataframe(
        longest_movies,
        use_container_width=True,
        hide_index=True,
    )


# ==============================
# 전체 데이터 보기
# ==============================
st.divider()

with st.expander("전체 데이터 보기"):
    st.dataframe(
        df.drop(columns=["genre_first"]),
        use_container_width=True,
        hide_index=True,
    )
