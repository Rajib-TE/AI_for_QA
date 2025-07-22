import streamlit as st
import pandas as pd
from reddit_scraper import scrape_and_sort, generate_topic_clusters, extract_feedback, visualize_feedback_graph
import matplotlib.pyplot as plt
import networkx as nx
import io

st.set_page_config(page_title="Reddit Feedback Analyzer", layout="wide")
st.title("Reddit Feedback Analyzer")

with st.form("input_form"):
    subreddit = st.text_input("Subreddit Name", value="Windows11")
    limit = st.number_input("Number of Posts", min_value=1, max_value=50, value=5)
    submitted = st.form_submit_button("Process")

if submitted:
    with st.spinner("Scraping and analyzing posts..."):
        df = scrape_and_sort(subreddit_name=subreddit, limit=int(limit))
        df = generate_topic_clusters(df)
        df['feedback'] = df['combined'].map(extract_feedback)
    st.subheader("Extracted Feedbacks")
    for idx, fb in enumerate(df['feedback']):
        st.markdown(f"**Post {idx+1}:** {fb}")
    st.subheader("Feedback Graph")
    # Visualize graph and show in Streamlit
    fig, ax = plt.subplots(figsize=(16, 10))
    # Patch: temporarily override plt.gca() to use our ax
    import matplotlib
    orig_gca = matplotlib.pyplot.gca
    matplotlib.pyplot.gca = lambda *args, **kwargs: ax
    try:
        visualize_feedback_graph(df)
    finally:
        matplotlib.pyplot.gca = orig_gca
    st.pyplot(fig)
    st.subheader("Raw DataFrame")
    st.dataframe(df)
