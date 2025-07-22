import os
import praw
from datetime import datetime
import pandas as pd
import openai
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from openai import AzureOpenAI
from tqdm import tqdm
tqdm.pandas()


# --- HARDCODED CREDENTIALS (for demo only; do not share these) ---
CLIENT_ID = 'CLIENT_ID' 
CLIENT_SECRET = 'CLIENT_SECRET'
USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD'
USER_AGENT = 'RedditScraper/0.1 by USERNAME'

client = AzureOpenAI(
  api_key = "api_key_here",  # Replace with your actual Azure OpenAI key
  api_type = "azure",
  api_base = "https://sduag1-openai.openai.azure.com/",
  api_version = "2023-05-15",
  azure_endpoint = "https://sduag1-openai.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15"
)

client_cc = AzureOpenAI(
  api_key = "api_key_here",  # Replace with your actual Azure OpenAI key
  api_type = "azure",
  api_base = "https://sduag1-openai.openai.azure.com/",

  api_version = "2025-01-01-preview",
  azure_endpoint = "https://sduag1-openai.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview")

if not all([CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD]):
    raise Exception("Please set CLIENT_ID in the script (see comment above). Do not share your credentials.")

def scrape_and_sort(subreddit_name, limit=5):
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
        user_agent=USER_AGENT
    )
    subreddit = reddit.subreddit(subreddit_name)
    posts = list(subreddit.new(limit=limit*3))  # Fetch more to ensure enough from last week
    # Filter posts from the last 7 days
    one_week_ago = datetime.utcnow().timestamp() - 7*24*60*60
    recent_posts = [post for post in posts if post.created_utc >= one_week_ago]
    # Sort by created_utc (descending)
    recent_posts.sort(key=lambda post: post.created_utc, reverse=True)

    data = []
    for post in recent_posts[:limit]:
        post_id = post.id
        title = post.title
        selftext = post.selftext
        upvotes = post.score
        # Fetch top-level comments (limit to 10 for demo)
        post.comments.replace_more(limit=0)
        comments = [comment.body for comment in post.comments.list()[:10]]
        created = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
        data.append({
            'id': post_id,
            'title': title,
            'selftext': selftext,
            'comments': comments,
            'upvotes': upvotes,
            'created_utc': created
        })

    df = pd.DataFrame(data)
    return df

def generate_topic_clusters(df, 
                            text_cols=['title', 'selftext'], 
                            embed_engine='text-embedding-ada-002', 
                            cluster_k=5,
                            azure_endpoint="https://sduag1-openai.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15",
                            azure_key="api_key_here",  # Replace with your actual Azure OpenAI key
                            azure_api_version="2023-05-15"):
    """
    Generate topic clusters using Azure OpenAI embeddings and KMeans clustering.
    
    Parameters:
        df (pd.DataFrame): Input dataframe with Reddit/Twitter-like data.
        text_cols (list): List of columns to concatenate for embedding.
        embed_engine (str): Your Azure OpenAI deployment name for embedding model.
        cluster_k (int): Number of clusters for KMeans.
        azure_endpoint (str): Azure OpenAI endpoint URL.
        azure_key (str): Azure OpenAI Key.
        azure_api_version (str): API version.

    Returns:
        pd.DataFrame: The input DataFrame with 'embedding' and 'topic_cluster' columns added.
    """

    # Setup OpenAI SDK
    openai.api_type = "azure"
    openai.api_base = azure_endpoint
    openai.api_version = azure_api_version
    openai.api_key = azure_key

    # Prepare combined column for embedding input
    df['combined'] = df[text_cols].fillna('').agg('\n'.join, axis=1)

    # Get embedding function (batch optional)
    def get_embedding(text):
        return client.embeddings.create(input = [text], model="text-embedding-ada-002").data[0].embedding

    # Generate embeddings
    print("Generating embeddings...")
    df['embedding'] = df['combined'].progress_map(get_embedding)

    # Cluster embeddings using KMeans
    print("Clustering embeddings...")
    embedding_matrix = np.vstack(df['embedding'].values)
    kmeans = KMeans(n_clusters=cluster_k, random_state=42)
    df['topic_cluster'] = kmeans.fit_predict(embedding_matrix)

    return df

def extract_feedback(text):
    prompt = (
        "Extract all user feedback, complaints, feature requests, or opinions from the following Reddit post in a valid format.\n"
        f"Text:\n{text}"
    )
    chat_prompt = [
        {"role": "system", "content": """Extract issues/topic/feedback from the text that will help in product development. Remember the text has the title, post and comments from reddit. Here the post is the main factor. The output should be in the following format:
         '{{
         "content": The feedback text here (title - post),
         "type": whether it is a 'complaint', 'feature request', or 'opinion',
         "build": 'optional build number if applicable (Windows build number)',
         "version": 'optional version number if applicable (Windows version like Windows 11, Windows 11 Pro)',
         "sentiment": positive/negative/neutral,
         "severity": 'low', 'medium', or 'high'
         "resolved": True/False based on the comments
         "resolve_text": "optional text if resolved, else leave empty"
         }}'"""},
        {"role": "user", "content": prompt}
    ]
    completion = client_cc.chat.completions.create(
        model="gpt-4o",
        messages=chat_prompt,
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content





# --- Graph Visualization Imports ---
import networkx as nx
import matplotlib.pyplot as plt

def parse_feedback(feedback_text):
    """
    Split feedback into individual items. Assumes feedback is a string with items separated by newlines or bullets.
    """
    if not isinstance(feedback_text, str):
        return []
    # Split by newlines and remove empty/whitespace lines
    items = [line.strip('-*• \n') for line in feedback_text.split('\n') if line.strip('-*• \n')]
    return items

def visualize_feedback_graph(df):
    G = nx.Graph()
    # Add topic cluster nodes
    topic_nodes = set(df['topic_cluster'])
    for topic in topic_nodes:
        G.add_node(f"Topic {topic}", type='topic')
    # Add post and feedback nodes, and connect them
    for idx, row in df.iterrows():
        post_node = f"Post {row['id']}"
        G.add_node(post_node, type='post', label=row['title'][:40]+('...' if len(row['title'])>40 else ''))
        G.add_edge(f"Topic {row['topic_cluster']}", post_node)
        feedback_items = parse_feedback(row['feedback'])
        for fb in feedback_items:
            fb_node = f"FB: {fb[:30]}"  # Shorten for display
            G.add_node(fb_node, type='feedback', label=fb)
            G.add_edge(post_node, fb_node)
    # Draw
    pos = nx.spring_layout(G, k=0.7, seed=42)
    plt.figure(figsize=(16, 10))
    # Draw topic nodes
    topic_nodes_list = [n for n, d in G.nodes(data=True) if d.get('type')=='topic']
    nx.draw_networkx_nodes(G, pos, nodelist=topic_nodes_list, node_color='skyblue', node_shape='s', node_size=1200, label='Topics')
    # Draw post nodes
    post_nodes_list = [n for n, d in G.nodes(data=True) if d.get('type')=='post']
    nx.draw_networkx_nodes(G, pos, nodelist=post_nodes_list, node_color='lightgreen', node_shape='o', node_size=800, label='Posts')
    # Draw feedback nodes
    fb_nodes_list = [n for n, d in G.nodes(data=True) if d.get('type')=='feedback']
    nx.draw_networkx_nodes(G, pos, nodelist=fb_nodes_list, node_color='salmon', node_shape='^', node_size=600, label='Feedback/Issues')
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.2, alpha=0.6)
    # Draw labels (only for topics and posts for clarity)
    labels = {n: d.get('label', n) for n, d in G.nodes(data=True) if d.get('type') in ['topic', 'post']}
    nx.draw_networkx_labels(G, pos, labels, font_size=9)
    plt.title('Reddit Posts, Topics, and Feedback Graph', fontsize=16)
    plt.legend(scatterpoints=1)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

import json
import re
import ast

def parse_feedback_dict(feedback_str):
    # Return empty if not a string
    if not isinstance(feedback_str, str):
        return pd.Series({
            'post_content': '',
            'post_type': '',
            'build': '',
            'version': '',
            'sentiment': '',
            'severity': '',
            'resolved': '',
            'resolution_text': ''
        })
    s = feedback_str.strip()
    # Remove code block markers (``` or ```json)
    s = re.sub(r"^```[a-zA-Z]*", "", s)
    s = re.sub(r"```$", "", s)
    s = s.strip()
    # Remove extra curly braces ({{ ... }})
    if s.startswith("{{") and s.endswith("}}"):
        s = s[1:-1].strip()
    # Find the first JSON object in the string
    match = re.search(r'\{.*\}', s, re.DOTALL)
    if match:
        s = match.group(0)
    # Replace True/False with true/false for JSON
    s = re.sub(r'\bTrue\b', 'true', s)
    s = re.sub(r'\bFalse\b', 'false', s)
    # Remove trailing commas before closing brace
    s = re.sub(r',\s*}', '}', s)
    # Try to load as JSON
    print("[DEBUG] Attempting to parse:", repr(s))
    try:
        data = json.loads(s)
    except Exception as e:
        print("[DEBUG] Exception:", e)
        if hasattr(e, 'pos'):
            print("[DEBUG] Error at position:", e.pos)
            print("[DEBUG] Surrounding text:", repr(s[max(0, e.pos-20):e.pos+20]))
        print("[DEBUG] Unicode code points:", [ord(c) for c in s])
        # Try to fix single quotes to double quotes
        s_fixed = s.replace("'", '"')
        try:
            data = json.loads(s_fixed)
        except Exception as e2:
            print("[DEBUG] Exception after fixing quotes:", e2)
            if hasattr(e2, 'pos'):
                print("[DEBUG] Error at position:", e2.pos)
                print("[DEBUG] Surrounding text:", repr(s_fixed[max(0, e2.pos-20):e2.pos+20]))
            print("[DEBUG] Unicode code points (fixed):", [ord(c) for c in s_fixed])
            # Try ast.literal_eval as a last resort
            try:
                data = ast.literal_eval(s)
            except Exception as e3:
                print("[DEBUG] Failed to parse feedback string:")
                print(feedback_str)
                print("[DEBUG] Cleaned string before json.loads:")
                print(s)
                print(f"[DEBUG] Exception: {e3}")
                # Optionally, save the string to a file for later inspection
                with open("bad_feedback.txt", "a", encoding="utf-8") as f:
                    f.write(feedback_str + "\n---\n")
                return pd.Series({
                    'post_content': feedback_str,  # fallback: put the raw string here
                    'post_type': '',
                    'build': '',
                    'version': '',
                    'sentiment': '',
                    'severity': '',
                    'resolved': '',
                    'resolution_text': ''
                })
    # Normalize resolved to bool
    resolved = data.get('resolved', '')
    if isinstance(resolved, str):
        resolved = resolved.strip().lower()
        if resolved in ['true', 'yes', '1']:
            resolved = True
        elif resolved in ['false', 'no', '0']:
            resolved = False
    return pd.Series({
        'post_content': data.get('content', ''),
        'post_type': data.get('type', ''),
        'build': data.get('build', ''),
        'version': data.get('version', ''),
        'sentiment': data.get('sentiment', ''),
        'severity': data.get('severity', ''),
        'resolved': resolved,
        'resolution_text': data.get('resolve_text', '')
    })

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    # Hardcoded subreddit as requested
    df = scrape_and_sort(subreddit_name = 'Windows11', limit=70)
    # Save partial results before feedback parsing
    df.to_csv('reddit_posts_partial.csv', index=False)
    # Create 'combined' column in the requested format
    def make_combined(row):
        title = row['title'] if pd.notnull(row['title']) else ''
        selftext = row['selftext'] if pd.notnull(row['selftext']) else ''
        comments = row['comments']
        # Fix: check for None, and ensure comments is a list
        if comments is None:
            comments = []
        if isinstance(comments, (list, np.ndarray)):
            comments_str = '\n'.join(map(str, comments))
        else:
            comments_str = str(comments)
        return f"title: {title}\n------\npost: {selftext}\n------\ncomments: {comments_str}"

    df['combined'] = df.apply(make_combined, axis=1)
    df['feedback'] = df['combined'].map(extract_feedback)

    # --- Parse feedback string into separate columns ---
    feedback_df = df['feedback'].apply(parse_feedback_dict)
    df = pd.concat([df, feedback_df], axis=1)
    df.to_csv('reddit_posts.csv', index=False)