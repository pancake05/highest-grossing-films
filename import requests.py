import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import json
# URL page from Wiki
url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
# 
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64: x64) ApppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
# Request to page
response = requests.get(url, headers=headers)
# Response in HTML format
soup = BeautifulSoup(response.text, 'html.parser')
# Table film
table = soup.find('table', {'class': 'wikitable'}) # seek first element HTML 
rows = table.find_all('tr') # Extraction all element from table, tr - table row
films = [] # Create list to contains data
for row in rows[1:]: # Skip title
    columns = row.find_all('td') # td - table data
    # Extraction data from each colomns 
    if len(columns) >= 5:  
        id = int(columns[0].text.strip())
        title = row.find('th').text.strip()
        box_office = columns[2].text.strip()
        release_year = int(columns[3].text.strip())
        additional_info = columns[4].text.strip()
    # Extraction director and courtry
    director_match = re.search(r'Director:\s*(.*?)\s*\|', additional_info)
    director = director_match.group(1) if director_match else "Unknown"          
    country_match = re.search(r'Country:\s*(.*)', additional_info)
    country = country_match.group(1) if country_match else "Unknown"
    def clean_box_office(box_office):
    # cleaning code
        return int(box_office.replace('$', '').replace(',', '').replace("T", '').replace("MS", '').replace("SM", '').replace("F", '').replace("DKR", '').replace("F8", ''))
    box_office = clean_box_office(box_office)
    def clean_title(title):
        title = title.strip()
        title = re.sub(r'[^\w\s]', '', title)
        return title
    def clean_release_year(year):
        year = year.strip()
        year = re.sub(r'[^\d]', '', year)
        return int(year)
    def clean_director(director):
        director = director.strip()
        director = re.sub(r'[^\w\s]', '', director) 
        return director
    def clean_country(country):
        country = country.strip()
        country = re.sub(r'[^\w\s]', '', country)
        return country
    # Add data to list 
    films.append({
        'title': title,
        'release_year': release_year,
        'box_office': box_office,
        'director': director,
        'country': country
    })
# Connect/create to database 
conn = sqlite3.connect('highest_grossing_films.db')
cursor = conn.cursor()

# create table films
cursor.execute('''
CREATE TABLE IF NOT EXISTS films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    release_year INTEGER,
    director TEXT,
    box_office REAL,
    country TEXT
)
''')

# Put in table value
for film in films:
    cursor.execute('''
    INSERT INTO films (title, release_year, director, box_office, country)
    VALUES (?, ?, ?, ?, ?)
    ''', (film['title'], film['release_year'], film['director'], film['box_office'], film['country']))

# Save and close database
conn.commit()
conn.close()

# connection to database  
conn = sqlite3.connect('highest_grossing_films.db')
cursor = conn.cursor()

# Execute request
cursor.execute('SELECT * FROM films')
rows = cursor.fetchall()
# Rechange data in list dictionary
films_json = []
for row in rows:
    film = {
        'id': row[0],
        'title': row[1],
        'release_year': row[2],
        'director': row[3],
        'box_office': row[4],
        'country': row[5]
    }
    films_json.append(film)

# Save data to JSON-file
with open('films.json', 'w') as f:
    json.dump(films_json, f, indent=4)

# Close connection
conn.close()