# Scopus-Archivist

Scopus-Archivist is a Python script that utilizes the Scopus API to fetch and archive metadata for all articles ever published under a given ISSN. This tool is specifically tailored for Elsevier publications.

You can check all the journals published by Elsevier [here](https://www.elsevier.com/products/journals)

## Requirements
- Python 3.x
- A valid Elsevier API Key. You can learn more about it [here](https://dev.elsevier.com/)

## Usage
1. Clone this repository.
2. Create a file named `apiKey.txt` in the root directory of the repository and paste your API key there.
3. Execute the script with the command `python script.py`.
4. When prompted, input the ISSN (International Standard Serial Number) for which you wish to extract data.
5. Specify the name of the output file, ensuring to append `.json` as the extension.
6. Wait for the script to complete its execution. The output file will contain an entry for each article published in the specified journal.
### Example
```shell
$ python script.py
Please enter the ISSN: 0024-3841
Please enter the name of the JSON file: Elsevier Lingua.json
```

Each entry will have the following structure:
```json
{
    "2971": {
        "title": "Scene analysis using regions",
        "author": "Brice C.",
        "doi": "10.1016/0004-3702(70)90008-1",
        "volume": 1,
        "cover_date": "1970-01-01",
        "display_date": "1970",
        "issue_identifier": "3-4",
        "page_range": "205-226",
        "open_access": "false",
        "affiliations": [
            {
                "name": "SRI International",
                "country": "United States"
            }
        ],
        "issn": "0004-3702",
        "publicationName": "Artificial Intelligence"
    },
}
```
You can then utilize the data as per your requirements. Enjoy exploring!
