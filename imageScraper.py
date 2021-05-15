# Author: Karen Black
# Last Modified: May 15, 2021
# Description: Image Scraper - scrapes images from Wikipedia and returns URLs of scraped images

# import necessary modules
import requests
from bs4 import BeautifulSoup
import regex as re
import flask
from flask import request, jsonify
from lxml import etree

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Wikipedia Image Scraper</h1>"


@app.route('/api/images/', methods=['GET'])
def img_scraper():
    # check title supplied in query, set title variable to query param
    if 'title' in request.args:
        title = request.args['title']
    else:
        return jsonify(noTitleError="Error: No Wikipedia page title provided.")

    # check if only returning first image, set count variable to 1
    if 'ct' in request.args:
        if request.args['ct'] == 'main' or request.args['ct'] == 'logo':
            img_count = 1                               # only obtaining main Wiki page image
        elif request.args['ct'] == 'all':
            img_count = None                            # null variable to obtain all images
        else:
            return jsonify(noImageCt="'ct' parameter invalid value")
    else:
        return jsonify(noImageCt="'ct' parameter not provided")

    # scrape Wikipedia for images
    image_urls = []  # empty list to store scraped URLs

    wiki_page = 'https://en.wikipedia.org/wiki/' + title        # wiki page URL to scrape
    try:
        htmldata = requests.get(wiki_page).text                # query website and return html
    except requests.exceptions.RequestException as e:
        return jsonify(urlError="invalid Wikipedia page title")

    soup = BeautifulSoup(htmldata, 'html.parser')               # parse html

    for item in soup.find_all('img'):
        src = item.get('src')                                   # get url of image
        url = 'https:' + src

        # if only acquiring the team logo
        if request.args['ct'] == 'logo':
            alt = item.get('alt')
            if re.search('logo', alt):
                image_urls.append(url)
            # if re.search('logo', url):
            #     image_urls.append(url)
        else:
            # get .img files not .svg as they are vector graphics
            if not re.search('.svg', url) and not re.search('/footer/', url) and not re.search('CentralAutoLogin', url):
                image_urls.append(url)
        if img_count == 1 and len(image_urls) == 1:
            return jsonify(images=url)

    if len(image_urls) == 0:                                    # no images on page
        return jsonify(noImagesError="No images on Wikipedia page or incorrect Wikipedia page title.")
    else:
        return jsonify(images=image_urls)


@app.route('/api/infobox/', methods=['GET'])
def info_box():
    title = request.args['title']
    url = 'https://en.wikipedia.org/wiki/' + title        # wiki page URL to scrape
    req = requests.get(url)
    store = etree.fromstring(req.text)

    # get Established date
    if request.args['fld'] == 'est':
        output = store.xpath('//table[@class="infobox vcard"]/tbody/tr[th/text()="Established"]/td/text()')
    # get Visitors
    if request.args['fld'] == 'vis':
        output = store.xpath('//table[@class="infobox vcard"]/tbody/tr[th/text()="Visitors"]/td/text()')
    # Get NPS link
    if request.args['fld'] == 'web':
        output = store.xpath('//table[@class="infobox vcard"]/tbody/tr[th/text()="Website"]/td/a/@href')
        print('******', output)

    return jsonify(infobox=output[0])



if __name__ == '__main__':
    app.run(debug=False)


