"""Interactive dashboard for the social media sentiment agent."""

import pandas as pd
import plotly.express as px
import streamlit as st

from sentiment_agent import SentimentAgent, classify_tweets


st.set_page_config(
    page_title="Sentiment Studio",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#182233; --muted:#738096; --line:#e9edf3; --blue:#5268e8; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    .stApp { background:#f6f8fb; }
    h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; }
    h1 { font-size:2.25rem !important; }
    [data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
    [data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stMetricValue"] { font-family:'Manrope',sans-serif; }
    .eyebrow { color:#596ce7; text-transform:uppercase; letter-spacing:.14em; font-weight:700; font-size:.72rem; }
    .subtle { color:#738096; }
    div.stButton > button[kind="primary"] { background:#5268e8; border:0; border-radius:10px; font-weight:600; }
    div.stButton > button { border-radius:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_agent():
    return SentimentAgent()


@st.cache_data(show_spinner=False)
def analyze_dataset(records):
    outputs = []
    records = list(records)
    for start in range(0, len(records), 5):
        batch = records[start : start + 5]
        batch_results = classify_tweets(batch)
        expected = {tweet["tweet_id"] for tweet in batch}
        returned = {item["tweet_id"] for item in batch_results}
        if expected != returned:
            missing = ", ".join(sorted(expected - returned))
            raise ValueError(f"The model omitted results for: {missing}")
        outputs.extend(batch_results)
    return outputs


LABEL_COLORS = {"Positive": "#35a987", "Neutral": "#8794aa", "Negative": "#e27668"}


def main():
    st.sidebar.markdown("<div class='eyebrow'>SOCIAL LISTENING</div>", unsafe_allow_html=True)
    st.sidebar.markdown("## ◉ Sentiment Studio")
    st.sidebar.markdown("<span class='subtle'>Understand the mood behind every message.</span>", unsafe_allow_html=True)
    st.sidebar.divider()
    page = st.sidebar.radio("Workspace", ["Overview", "Analyze a tweet", "Explore dataset"], label_visibility="collapsed")
    st.sidebar.divider()
    st.sidebar.caption("Powered by Groq · Context-aware classification")

    try:
        agent = get_agent()
    except Exception as error:
        st.error(f"Could not start the sentiment agent: {error}")
        st.info("Check that GROQ_API_KEY and GROQ_MODEL are set in your .env file and that the Excel dataset is available.")
        return

    if "results" not in st.session_state:
        st.session_state.results = None

    st.markdown("<div class='eyebrow'>SENTIMENT INTELLIGENCE</div>", unsafe_allow_html=True)
    st.title({"Overview": "Your audience, at a glance", "Analyze a tweet": "Analyze a message", "Explore dataset": "Explore the conversation"}[page])
    st.markdown("<p class='subtle'>A clear view of what people are saying and how they feel.</p>", unsafe_allow_html=True)

    if page == "Analyze a tweet":
        st.subheader("Quick analysis")
        text = st.text_area("Paste a tweet or social post", height=140, placeholder="What would you like to understand?")
        if st.button("Analyze sentiment", type="primary", disabled=not text.strip()):
            with st.spinner("Reading the context…"):
                try:
                    result = classify_tweets([{"tweet_id": "CUSTOM-001", "text": text.strip()}])
                    if result:
                        st.session_state.single_result = (text.strip(), result[0])
                    else:
                        st.error("No valid sentiment result was returned. Please try again.")
                except Exception as error:
                    st.error(f"Analysis failed: {error}")
        if "single_result" in st.session_state:
            message, result = st.session_state.single_result
            st.divider()
            st.markdown(f"### {result['sentiment']} sentiment")
            st.write(message)
            st.info(result.get("reason") or "No explanation provided.")
        return

    if page == "Explore dataset":
        query = st.text_input("Search tweets", placeholder="Filter by words or tweet ID")
        frame = agent.df.copy()
        if query:
            mask = frame["Tweet_Text"].str.contains(query, case=False, na=False) | frame["Tweet_ID"].str.contains(query, case=False, na=False)
            frame = frame.loc[mask]
        st.caption(f"Showing {len(frame):,} of {len(agent.df):,} tweets")
        st.dataframe(frame, use_container_width=True, hide_index=True)
        if st.button("Analyze full dataset", type="primary"):
            records = tuple({"tweet_id": str(row.Tweet_ID), "text": str(row.Tweet_Text)} for row in agent.df.itertuples(index=False))
            with st.spinner(f"Analyzing {len(records):,} tweets in small batches…"):
                try:
                    st.session_state.results = analyze_dataset(records)
                except Exception as error:
                    st.error(f"Dataset analysis failed: {error}")
        if st.session_state.results:
            show_results(st.session_state.results, agent.df)
        return

    st.markdown("### Start with your data")
    st.markdown(f"Your workspace contains **{len(agent.df):,} tweets** ready for analysis.")
    if st.button("Analyze all tweets", type="primary"):
        records = tuple({"tweet_id": str(row.Tweet_ID), "text": str(row.Tweet_Text)} for row in agent.df.itertuples(index=False))
        with st.spinner(f"Analyzing {len(records):,} tweets in small batches…"):
            try:
                st.session_state.results = analyze_dataset(records)
            except Exception as error:
                st.error(f"Dataset analysis failed: {error}")
    if st.session_state.results:
        show_results(st.session_state.results, agent.df)


def show_results(results, source):
    result_df = pd.DataFrame(results)
    result_df = result_df.merge(source[["Tweet_ID", "Tweet_Text"]], left_on="tweet_id", right_on="Tweet_ID", how="left")
    counts = result_df["sentiment"].value_counts().reindex(["Positive", "Neutral", "Negative"], fill_value=0)
    total = len(result_df)
    st.divider()
    st.markdown("### Sentiment overview")
    cols = st.columns(4)
    cols[0].metric("Analyzed", f"{total:,}")
    for col, label in zip(cols[1:], ["Positive", "Neutral", "Negative"]):
        col.metric(label, f"{counts[label]:,}", f"{counts[label] / total:.0%}" if total else "0%")

    left, right = st.columns([1, 1.6])
    with left:
        pie = px.pie(values=counts.values, names=counts.index, hole=.68, color=counts.index, color_discrete_map=LABEL_COLORS)
        pie.update_traces(textinfo="percent", textfont_size=13, marker_line_width=0)
        pie.update_layout(margin=dict(t=12,b=12,l=12,r=12), showlegend=True, legend=dict(orientation="h", y=-.12), height=320)
        st.plotly_chart(pie, use_container_width=True)
    with right:
        trend = result_df.copy()
        # Use a provided date column when available, otherwise show dataset order as a rolling trend.
        date_col = next((c for c in source.columns if "date" in c.lower() or "time" in c.lower()), None)
        if date_col:
            trend = trend.merge(source[["Tweet_ID", date_col]], on="Tweet_ID", how="left")
            trend["period"] = pd.to_datetime(trend[date_col], errors="coerce").dt.date.astype("string")
            trend = trend.dropna(subset=["period"]).groupby(["period", "sentiment"]).size().reset_index(name="Tweets")
            trend["period"] = pd.to_datetime(trend["period"])
            x_label = "Date"
        else:
            trend = trend.reset_index(drop=True)
            trend["period"] = (trend.index // max(1, len(trend) // 12 or 1) + 1).map(lambda n: f"Group {n}")
            trend = trend.groupby(["period", "sentiment"]).size().reset_index(name="Tweets")
            x_label = "Dataset sequence"
        line = px.line(trend, x="period", y="Tweets", color="sentiment", markers=True, color_discrete_map=LABEL_COLORS)
        line.update_layout(margin=dict(t=12,b=12,l=12,r=12), height=320, legend=dict(orientation="h", y=-.22), xaxis_title=x_label)
        st.plotly_chart(line, use_container_width=True)

    st.markdown("### Tweet-level results")
    display = result_df.rename(columns={"tweet_id": "Tweet ID", "Tweet_Text": "Tweet", "sentiment": "Sentiment", "reason": "Why"})
    wanted = [c for c in ["Tweet ID", "Tweet", "Sentiment", "Why"] if c in display]
    st.dataframe(display[wanted], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
