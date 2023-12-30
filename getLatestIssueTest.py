import requests
from lxml import etree

def get_latest_issue(issn, api_key):
    headers = {
        'Accept':'application/xml',
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

# Usage
api_key = '1788986f6b20d9f6fe6115c588a06023'  # Replace with your actual API key
issn = '0024-3841'  # Replace with the ISSN you're interested in
print(get_latest_issue(issn, api_key))
