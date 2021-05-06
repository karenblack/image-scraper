# Author: Karen Black
# Last Modified: May 6, 2021
# Description: Image Scraper - scrapes images from Wikipedia and returns URLs of scraped images

# import necessary modules
import requests
from bs4 import BeautifulSoup
import regex as re
import flask
from flask import request, jsonify

app = flask.Flask(__name__)


@app.route('/', methods = ['GET'])
def home():
    return "<h1>Wikipedia Image Scraper</h1>"


@app.route('/images/', methods = ['GET'])
def img_scraper():
    # check title supplied in query, set title variable to query param
    if 'title' in request.args:
        title = request.args['title']
    else:
        return "Error: No Wikipedia page title provided."

    # check if only returning first image, set count variable to 1
    if 'ct' in request.args:
        img_count = 1               # only obtaining main Wiki page image
    else:
        img_count = None               # null variable to obtain all images

    # scrape Wikipedia for images
    image_urls = []  # empty list to store scraped URLs

    wiki_page = 'https://en.wikipedia.org/wiki/' + title        # wiki page URL to scrape
    htmldata = requests.get(wiki_page).text                     # query website and return html
    soup = BeautifulSoup(htmldata, 'html.parser')               # parse html

    for item in soup.find_all('img'):
        url = item.get('src')                                   # get url of image

        # get .img files not .svg as they are vector graphics
        if not re.search('.svg', url) and not re.search('/footer/', url) and not re.search('CentralAutoLogin', url):
            image_urls.append(url)
        if img_count == 1 and len(image_urls) == 1:
            return url

    if len(image_urls) == 0:                                    # no images on page
        return "Error: No images on Wikipedia page."
    else:
        return jsonify(image_urls)


if __name__ == '__main__':
    app.run(debug=False)


