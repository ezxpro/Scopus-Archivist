import requests
from lxml import etree
from tinydb import TinyDB, Query
from pathlib import Path

with open('apiKey.txt', 'r', encoding='utf-8') as file:
    api_key = file.read().strip()  # Read the API key from the file and remove any leading/trailing whitespace


def get_latest_volume(issn, api_key):
    headers = {
        'Accept': 'application/xml',
        'X-ELS-APIKey': api_key
    }

    response = requests.get(f"https://api.elsevier.com/content/search/scopus?query=ISSN({issn})", headers=headers)
    root = etree.fromstring(response.content)

    # Extract the latest volume number
    latest_volume = None
    for entry in root.xpath('//atom:entry', namespaces={'atom': 'http://www.w3.org/2005/Atom'}):
        volume = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}volume')
        if volume is not None:
            latest_volume = volume.text
            break  # Assuming the first entry is the latest

    return latest_volume

def get_articles_for_volume(issn, volume, api_key):
    headers = {
        'Accept': 'application/xml',
        'X-ELS-APIKey': api_key
    }

    response = requests.get(f"https://api.elsevier.com/content/search/scopus?query=ISSN({issn})%20AND%20volume({volume})", headers=headers)
    root = etree.fromstring(response.content)

    # Extract the article metadata
    articles = []
    for entry in root.xpath('//atom:entry', namespaces={'atom': 'http://www.w3.org/2005/Atom'}):
        article = {}
        title = entry.find('{http://purl.org/dc/elements/1.1/}title')
        if title is not None:
            article['title'] = title.text
        author = entry.find('{http://purl.org/dc/elements/1.1/}creator')
        if author is not None:
            article['author'] = author.text
        doi = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}doi')
        if doi is not None:
            article['doi'] = doi.text
        articles.append(article)

    return articles

def save_to_tinydb(data, filename, existing_dois):
    # Get the directory of the current script
    script_dir = Path(__file__).resolve().parent
    # Create the full path to the file
    file_path = script_dir / filename
    db = TinyDB(file_path, indent=4, ensure_ascii=False)

    for item in data:
        # Use TinyDB query to check for existing DOI
        query_result = db.search(Query().doi == item['doi'])
        
        if not query_result:
            db.insert(item)
            existing_dois.add(item['doi'])
        else:
            print(f"Entry already exists: {item}")

    return existing_dois  # Return the updated set

# Usage
issn = input("Please enter the ISSN: ")  # Prompt for ISSN
filename = input("Please enter the name of the JSON file: ")  # Prompt for JSON filename

# Fetch all DOIs from the database first and store them in a set
existing_dois = set()
db = TinyDB(filename, indent=4, ensure_ascii=False)  # Use the provided filename
for item in db.all():
    existing_dois.add(item['doi'])

latest_volume = get_latest_volume(issn, api_key)

if latest_volume is None:
    print("No volumes found for this ISSN.")
else:
    print(f"Latest volume: {latest_volume}")

    for volume in range(int(latest_volume), 0, -1):
        print(f"volume {volume}:")
        articles = get_articles_for_volume(issn, volume, api_key)

        # Reset data for each volume
        data = []

        new_articles = [article for article in articles if 'doi' in article and article['doi'] not in existing_dois]
        for article in new_articles:
            article['volume'] = volume
            data.append(article)
            print(f"  - {article}")

        # Save to the database after each volume
        existing_dois = save_to_tinydb(data, filename, existing_dois)  # Update the set with the returned value