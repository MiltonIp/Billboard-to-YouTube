# Billboard-to-YouTube
Scrapes the song name and artist name of the current hot 100 Billboard songs and adds all of them to a YouTube playlist

  Web scraping (from https://www.billboard.com/charts/hot-100) done in Python using the requests and lxml libraries
  
  On Unix machines:
  
  `git clone https://github.com/MiltonIp/Billboard-to-YouTube.git`
  
  `cd Billboard-to-YouTube`
  
  `pip3 install -r requirements.txt`
  
  To run the code, follow steps 1 to 3 here: https://developers.google.com/youtube/v3/quickstart/python
  
  Then get an API key for YouTube Data API v3 and set the environment variable YOUTUBE_API to your API key

  `export YOUTUBE_API=<Your YouTube API key>`

  `python3 main.py`
