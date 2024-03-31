from flask import Flask, render_template, request
from reddit_sentiment_analyzer import analyze_post

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        post_url = request.form['post_url']
        result = analyze_post(post_url)
        
        if "error" in result:
            return render_template('error.html', error=result["error"])
        
        return render_template('results.html', result=result)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)