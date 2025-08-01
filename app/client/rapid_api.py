import http.client
import urllib.parse
import json
from dotenv import load_dotenv
import os
import requests
import re
from bs4 import BeautifulSoup

load_dotenv()


class LyricsScraper:

    def __init__(self):
        self.api_key = os.getenv("RAPID_API_KEY")
        if not self.api_key:
            raise ValueError("RAPID_API_KEY not set in environment variables")


    def search_songs(self, query):
        """Search for songs using the Genius API"""
        conn = http.client.HTTPSConnection("genius-song-lyrics1.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': "genius-song-lyrics1.p.rapidapi.com"
        }
        params = {
            'q': query,
            'per_page': 1
        }

        # Construct the query string manually
        query_string = urllib.parse.urlencode(params)
        url = f"/search/?{query_string}"
        
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        # Parse JSON response
        response_data = json.loads(data.decode("utf-8"))
        return response_data

    def extract_song_info(self, search_results):
        """Extract artist and song information from search results"""
        songs = []
        
        if 'hits' in search_results:
            for hit in search_results['hits']:
                if hit['type'] == 'song':
                    result = hit['result']
                    song_info = {
                        'id': result['id'],
                        'title': result['title'],
                        'artist': result['primary_artist']['name'],
                        'full_title': result['full_title'],
                        'url': result['url'],
                        'release_date': result.get('release_date_for_display', 'Unknown'),
                        'pageviews': result['stats'].get('pageviews', 0)
                    }
                    songs.append(song_info)
        
        return songs[0] if songs else None
    

    def get_lyrics_from_genius_url(self, url: str) -> str:
        """Extract lyrics from a Genius URL using web scraping"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        print(f"Fetching lyrics from: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            raise Exception("Request timed out after 10 seconds")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

        if response.status_code != 200:
            raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Genius uses divs with class Lyrics__Container for each lyrics block
        containers = soup.find_all("div", class_="Lyrics__Container")

        if not containers:
            # Try alternative selectors for lyrics
            containers = soup.find_all("div", {"data-lyrics-container": "true"})
            
        if not containers:
            raise Exception("Lyrics container not found. The structure might have changed.")

        lyrics = ""
        for container in containers:
            # Replace <br> with \n
            for br in container.find_all("br"):
                br.replace_with("\n")
            lyrics += container.get_text(separator="\n").strip() + "\n"

        return self.__clean_lyrics(lyrics.strip())

    def __clean_lyrics(self, lyrics: str) -> str:
        """Clean up lyrics by removing extra whitespace and formatting properly"""
        # Remove extra whitespace and normalize line breaks
        lines = lyrics.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace from each line
            cleaned_line = line.strip()
            # Only add non-empty lines
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        # Join lines back together with single line breaks
        cleaned_lyrics = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive line breaks (more than 2)
        cleaned_lyrics = re.sub(r'\n{3,}', '\n\n', cleaned_lyrics)
        
        return cleaned_lyrics


if __name__ == "__main__":
    scraper = LyricsScraper()
    search_results = scraper.search_songs("The Night We Met")
    song_info = scraper.extract_song_info(search_results)

    if song_info:
        print(f"Found song: {song_info['title']} by {song_info['artist']}")
        lyrics = scraper.get_lyrics_from_genius_url(song_info['url'])
        print(f"Lyrics for {song_info['title']}:\n{lyrics}")
    else:
        print("No song found.")