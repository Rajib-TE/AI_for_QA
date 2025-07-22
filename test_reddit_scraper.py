import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import reddit_scraper

class TestRedditScraper(unittest.TestCase):
    @patch('reddit_scraper.praw.Reddit')
    def test_scrape_and_sort(self, mock_reddit):
        # Mock Reddit post
        mock_post = MagicMock()
        mock_post.id = 'abc123'
        mock_post.title = 'Test Title'
        mock_post.selftext = 'Test selftext'
        mock_post.score = 42
        mock_post.created_utc = reddit_scraper.datetime.utcnow().timestamp()
        mock_comment = MagicMock()
        mock_comment.body = 'Test comment'
        mock_post.comments.list.return_value = [mock_comment]
        mock_post.comments.replace_more.return_value = None
        mock_subreddit = MagicMock()
        mock_subreddit.new.return_value = [mock_post]
        mock_reddit.return_value.subreddit.return_value = mock_subreddit
        df = reddit_scraper.scrape_and_sort('sometest', limit=1)
        self.assertEqual(len(df), 1)
        self.assertIn('title', df.columns)
        self.assertIn('comments', df.columns)
        self.assertEqual(df.iloc[0]['title'], 'Test Title')
        self.assertEqual(df.iloc[0]['comments'][0], 'Test comment')

    @patch('reddit_scraper.client')
    @patch('reddit_scraper.openai')
    def test_generate_topic_clusters(self, mock_openai, mock_client):
        # Mock embedding
        mock_client.embeddings.create.return_value.data = [MagicMock(embedding=np.zeros(5))]
        mock_openai.api_type = 'azure'
        mock_openai.api_base = 'endpoint'
        mock_openai.api_version = 'version'
        mock_openai.api_key = 'key'
        df = pd.DataFrame({'title': ['A'], 'selftext': ['B']})
        # Patch tqdm to avoid progress bar in test
        with patch('reddit_scraper.tqdm'):
            df2 = reddit_scraper.generate_topic_clusters(df, cluster_k=1)
        self.assertIn('embedding', df2.columns)
        self.assertIn('topic_cluster', df2.columns)
        self.assertEqual(df2['topic_cluster'].iloc[0], 0)

    @patch('reddit_scraper.client_cc')
    def test_extract_feedback(self, mock_client_cc):
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content='Feedback 1\nFeedback 2'))]
        mock_client_cc.chat.completions.create.return_value = mock_completion
        result = reddit_scraper.extract_feedback('Some text')
        self.assertIn('Feedback 1', result)

    def test_parse_feedback(self):
        text = '- Feedback 1\n- Feedback 2\n\n- Feedback 3'
        items = reddit_scraper.parse_feedback(text)
        self.assertEqual(items, ['Feedback 1', 'Feedback 2', 'Feedback 3'])
        self.assertEqual(reddit_scraper.parse_feedback(None), [])

    @patch('reddit_scraper.nx')
    @patch('reddit_scraper.plt')
    def test_visualize_feedback_graph(self, mock_plt, mock_nx):
        # Minimal DataFrame
        df = pd.DataFrame({
            'id': ['1'],
            'title': ['Test'],
            'topic_cluster': [0],
            'feedback': ['Feedback 1']
        })
        # Should not raise
        reddit_scraper.visualize_feedback_graph(df)
        self.assertTrue(mock_nx.Graph.called)
        self.assertTrue(mock_plt.show.called)

if __name__ == '__main__':
    unittest.main()
