import datetime

import requests
from lxml import html

import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_auth_oauthlib.flow import InstalledAppFlow

from secrets import youtube_developer_key  # YouTube Data API key

DEVELOPER_KEY = youtube_developer_key()
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

CLIENT_SECRETS_FILE = 'client_secret.json'


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


# Authorizes the request and store authorization credentials.
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)


# Adds a resource to a playlist
def add_playlist(youtube, args):
    body = dict(
        snippet=dict(
            title=args.title,
            description=args.description
        ),
        status=dict(
            privacyStatus='public'
        )
    )

    playlists_insert_response = youtube.playlists().insert(
        part='snippet,status',
        body=body
    ).execute()

    return playlists_insert_response['id']


def build_resource(properties):
    resource = {}

    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key) - 2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def playlist_items_insert(client, properties, **kwargs):
    resource = build_resource(properties)

    kwargs = remove_empty_kwargs(**kwargs)

    client.playlistItems().insert(
        body=resource,
        **kwargs
    ).execute()

    print('Song added to playlist')


if __name__ == '__main__':

    date = 'The week of ' + str(datetime.date.today())

    # Creates the args of the new playlist
    playlist_parser = argparse.ArgumentParser()
    playlist_parser.add_argument('--title',
                                 default='Billboard Hot 100 - ' + date,  # Title of playlist with date
                                 help='The title of the new playlist.')
    playlist_parser.add_argument('--description',
                                 default='A public playlist of Billboard Hot 100 Songs.',
                                 help='The description of the new playlist.')

    args = playlist_parser.parse_args()
    youtube = get_authenticated_service()

    # Creates a new playlist
    try:
        playlist_id = add_playlist(youtube, args)
        print('The newly created playlist ID is:' + playlist_id)
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))

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

        # Adding song to the playlist
        playlist_items_insert(youtube,
                              {'snippet.playlistId': playlist_id,
                               'snippet.resourceId.kind': 'youtube#video',
                               'snippet.resourceId.videoId': song_id,
                               'snippet.position': ''},
                              part='snippet',
                              onBehalfOfContentOwner='')

    print('The URL of the newly created playlist is '
          'https://www.youtube.com/playlist?list=' + playlist_id)
