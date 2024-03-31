import praw
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
    print("Analyzing Original Post.." + "\nTitle: " + submission.title + "\nPost Body: " + submission.selftext)

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
        print("Comment: " + comment.body)
        comment_sentiment = get_sentiment_score(comment.body)
        total_comment_sentiment += comment_sentiment
        num_comments += 1
    
    # Calculate average comment sentiment
    average_comment_sentiment = total_comment_sentiment / max(1, num_comments)
    
    # Weighted average: 70% post sentiment, 30% average comment sentiment
    overall_sentiment = 0.7 * post_sentiment + 0.3 * average_comment_sentiment

    # Determine sentiment label based on the sentiment score
    if overall_sentiment > 0.1:
        sentiment_label = "Positive"
    elif overall_sentiment < -0.1:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
    
    return {
        "title": submission.title,
        "body": submission.selftext,
        "comments": [comment.body for comment in submission.comments],
        "overall_sentiment": overall_sentiment,
        "sentiment_label": sentiment_label
    }

def analyze_post(post_url):
    try: 
        submission = reddit.submission(url=post_url)
        result = get_post_sentiment(submission)
        result["url"] = post_url  # Add the post URL to the result
        
        return result

    except Exception as e:
        return {
            "error": str(e)
        }
