import praw
import pandas as pd
import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from reddit_config import *

nltk.download('vader_lexicon')

# Authenticate with Reddit
reddit = praw.Reddit(
    client_id = reddit_client_id,
    client_secret = reddit_client_secret,
    user_agent = reddit_user_agent,
    username = reddit_username,
    password = reddit_password
)

# Create a SentimentIntensityAnalyzer object
sid = SentimentIntensityAnalyzer()

def get_sentiment_score(text):
    # Calculate sentiment score for the given text
    sentiment_scores = sid.polarity_scores(text)
    return sentiment_scores['compound']

def get_post_sentiment(submission):
    # Calculate sentiment score for the post
    post_sentiment = get_sentiment_score(submission.title + " " + submission.selftext)
    
    # Calculate sentiment scores for each comment and get average
    total_comment_sentiment = 0
    num_comments = 0
    for comment in submission.comments:
        # praw.models.MoreComments is a class representing a collapsed group of
        # comments that have not been fetched yet. 
        # used to skip over MoreComments objects, which are placeholders for collapsed comments. 
        # This ensures that only actual comments are analyzed.
        if isinstance(comment, praw.models.MoreComments):
            continue
        comment_sentiment = get_sentiment_score(comment.body)
        total_comment_sentiment += comment_sentiment
        num_comments += 1
    
    # Calculate average comment sentiment
    average_comment_sentiment = total_comment_sentiment / max(1, num_comments)
    
    # Weighted average: 70% post sentiment, 30% average comment sentiment
    overall_sentiment = 0.7 * post_sentiment + 0.3 * average_comment_sentiment
    
    return overall_sentiment

# URL or ID of the post you want to analyze
post_url = "https://www.reddit.com/r/Python/comments/1bpzfcb/python_state_management/"

# Retrieve the submission (post)
submission = reddit.submission(url=post_url)

# Get the overall sentiment score for the post
overall_sentiment_score = get_post_sentiment(submission)

# Determine sentiment label based on the sentiment score
if overall_sentiment_score > 0.1:
    sentiment_label = "Positive"
elif overall_sentiment_score < -0.1:
    sentiment_label = "Negative"
else:
    sentiment_label = "Neutral"

# Print the overall sentiment score
print("Overall Sentiment Score for the Post:", overall_sentiment_score)
print("Sentiment Label:", sentiment_label)


#TODO: Refactor code
#TODO: add a function for the sentiment label 
#TODO: Use pandas or create simple flask app to take a URL