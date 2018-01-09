import requests
from lxml import html


# Parses info from the given url
def parsed_info(url_link):
    receive = requests.get(url_link)
    parsed_html = html.fromstring(receive.content)
    return parsed_html


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
