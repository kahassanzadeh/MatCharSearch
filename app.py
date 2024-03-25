from flask import Flask, request
from flask import render_template
import scholar_scraper


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    keywords = request.form['keywords']
    results = process_keywords(keywords)
    return render_template('results.html', comments=results)


def process_keywords(keywords):
    keywords = keywords.lower()
    results = scholar_scraper.doaj_request(keywords)
    # scholar_scraper.download_articles(results)
    results = scholar_scraper.image_of_articles(results)
    return results


if __name__ == '__main__':
    app.run()
