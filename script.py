import requests
from lxml import etree
from tinydb import TinyDB, Query
from pathlib import Path

# Function to get the API key
def get_api_key():
    apikey_path = Path(__file__).resolve().parent / 'apiKey.txt'
    with open(apikey_path, 'r', encoding='utf-8') as file:
        api_key = file.read().strip()  # Read the API key from the file and remove any leading/trailing whitespace
    return api_key

# Function to get the latest volume number
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

# Function to get articles for a specific volume
def get_articles_for_volume(issn, volume, api_key):
    headers = {
        'Accept': 'application/xml',
        'X-ELS-APIKey': api_key
    }

    response = requests.get(f"https://api.elsevier.com/content/search/scopus?query=ISSN({issn})%20AND%20volume({volume})", headers=headers)
    root = etree.fromstring(response.content)

    # Check if the total results are zero
    total_results = root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults')
    if total_results is not None and int(total_results.text) == 0:
        print(f"Volume number {volume} is empty, skipping to the next one.")
        return []

    # Extract the article metadata
    articles = []
    for entry in root.xpath('//atom:entry', namespaces={'atom': 'http://www.w3.org/2005/Atom'}):
        article = {}
        title = entry.find('{http://purl.org/dc/elements/1.1/}title')
        article['title'] = title.text if title is not None else None
        author = entry.find('{http://purl.org/dc/elements/1.1/}creator')
        article['author'] = author.text if author is not None else None
        pub_name = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}publicationName')
        article['issn'] = issn
        article['publicationName'] = pub_name.text if pub_name is not None else None
        doi = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}doi')
        article['doi'] = doi.text if doi is not None else None
        article['volume'] = volume
        cover_date = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}coverDate')
        article['cover_date'] = cover_date.text if cover_date is not None else None
        display_date = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}coverDisplayDate')
        article['display_date'] = display_date.text if display_date is not None else None
        issue_identifier = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}issueIdentifier')
        article['issue_identifier'] = issue_identifier.text if issue_identifier is not None else None
        page_range = entry.find('{http://prismstandard.org/namespaces/basic/2.0/}pageRange')
        article['page_range'] = page_range.text if page_range is not None else None
        open_access = entry.find('{http://www.w3.org/2005/Atom}openaccessFlag')
        article['open_access'] = open_access.text if open_access is not None else None
        affiliations = entry.findall('{http://www.w3.org/2005/Atom}affiliation')
        article['affiliations'] = [{'name': aff.find('{http://www.w3.org/2005/Atom}affilname').text, 'country': aff.find('{http://www.w3.org/2005/Atom}affiliation-country').text} for aff in affiliations] if affiliations else None
        articles.append(article)

    return articles


# Function to save data to TinyDB
def save_to_tinydb(data, filename, existing_dois):
    # Get the directory of the current script
    script_dir = Path(__file__).resolve().parent
    # Create the full path to the file
    file_path = script_dir / filename
    db = TinyDB(file_path, indent=4, ensure_ascii=False)

    for item in data:
        # Check if 'doi' key is in the item
        if 'doi' in item:
            # Use TinyDB query to check for existing DOI
            query_result = db.search(Query().doi == item['doi'])
            
            if not query_result:
                db.insert(item)
                existing_dois.add(item['doi'])
                print(f"Inserting in database: {item['title']}")
            else:
                # If the entry exists, update it only if it doesn't have all the fields
                if not all(key in query_result[0] for key in item):
                    db.update(item, Query().doi == item['doi'])
                    print(f"Entry updated: {item}")

    return existing_dois  # Return the updated set

# Function to get existing DOIs from TinyDB
def get_existing_dois(filename):
    script_dir = Path(__file__).resolve().parent
    db_path = script_dir / filename

    # Fetch all DOIs from the database first and store them in a set
    existing_dois = set()
    db = TinyDB(db_path, indent=4, ensure_ascii=False)
    for item in db.all():
        existing_dois.add(item['doi'])
    
    return existing_dois

# Function to process all volumes
def process_volumes(issn, latest_volume, api_key, existing_dois, filename):
    if latest_volume is None:
        print("No volumes found for this ISSN.")
    else:
        print(f"Latest volume: {latest_volume}")

        for volume in range(int(latest_volume), 0, -1):
            print(f"volume {volume}:")
            articles = get_articles_for_volume(issn, volume, api_key)
            existing_dois = save_to_tinydb(articles, filename, existing_dois)  # Update the set with the returned value

# Main function to run the script
def main():
    issn = "1574-0137"
    filename = "teste.json"
    # issn = input("Please enter the ISSN: ")  # Prompt for ISSN
    # filename = input("Please enter the name of the JSON file: ")  # Prompt for JSON filename

    existing_dois = get_existing_dois(filename)
    api_key = get_api_key()
    latest_volume = get_latest_volume(issn, api_key)
    process_volumes(issn, latest_volume, api_key, existing_dois, filename)

if __name__ == "__main__":
    main()
