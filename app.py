from flask import Flask, request
from flask import render_template
import datetime
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    keywords = request.form['keywords']
    # results = process_keywords(keywords)
    return render_template('results.html', results=keywords)


if __name__ == '__main__':
    app.run()
