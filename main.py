import requests
from lxml import html

import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from secrets import youtube_developer_key  # YouTube Data API key

DEVELOPER_KEY = youtube_developer_key()
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Parses info from the given url
def parsed_info(url_link):
    receive = requests.get(url_link)
    parsed_html = html.fromstring(receive.content)
    return parsed_html


# Performs a YouTube search for given argument
def youtube_search(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=options.q,
        part='id,snippet',
        maxResults=options.max_results
    ).execute()

    videos = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos
    for search_result in search_response.get('items', []):
        videos.append('%s' % (search_result['id']['videoId']))

    return videos[0]


if __name__ == '__main__':

    # Scraping song and artist name from Billboard
    site = 'https://www.billboard.com/charts/hot-100'
    parsed_site = parsed_info(site)

    for row in range(1, 101):
        # Scrapes song names
        song_xpath = ('//article[@class="chart-row chart-row--'
                      + str(row) + ' js-chart-row"]/'
                      + 'div[@class="chart-row__primary"]/'
                      + 'div[@class="chart-row__main-display"]/'
                      + 'div[@class="chart-row__container"]/'
                      + 'div[@class="chart-row__title"]/'
                      + 'h2[@class="chart-row__song"]/text()')

        # Scrapes artist names without hyperlinks
        artist_xpath = ('//article[@class="chart-row chart-row--'
                        + str(row) + ' js-chart-row"]/'
                        + 'div[@class="chart-row__primary"]/'
                        + 'div[@class="chart-row__main-display"]/'
                        + 'div[@class="chart-row__container"]/'
                        + 'div[@class="chart-row__title"]/'
                        + 'span[@class="chart-row__artist"]/text()')

        # Scrape artist names with hyperlink
        artist_link_xpath = ('//article[@class="chart-row chart-row--'
                             + str(row) + ' js-chart-row"]/'
                             + 'div[@class="chart-row__primary"]/'
                             + 'div[@class="chart-row__main-display"]/'
                             + 'div[@class="chart-row__container"]/'
                             + 'div[@class="chart-row__title"]/'
                             + 'a[@class="chart-row__artist"]/text()')

        song_info = (' - '.join(parsed_site.xpath(artist_xpath)) +
                     ' - '.join(parsed_site.xpath(artist_link_xpath)) +
                     (''.join(parsed_site.xpath(song_xpath))))
        print('\nSong #' + str(row) + ':' + song_info)

        # Creating args for searching song
        song_parser = argparse.ArgumentParser()
        song_parser.add_argument('--q', help='Search term', default=song_info)
        song_parser.add_argument('--max-results', help='Max results', default=1)
        args = song_parser.parse_args()

        # Searches for song
        try:
            song_id = youtube_search(args)
            print('The video ID of this song is:' + song_id)
            print('Link to song: https://www.youtube.com/watch?v=' + song_id)
        except HttpError as e:
            print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
