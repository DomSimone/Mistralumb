import requests
import json

# Define African TLDs and Keywords
AFRICAN_TLDS = [".za", ".ng", ".ke", ".et", ".gh", ".ma", ".dz", ".ug", ".tz", ".ng"]
INDEX = "CC-MAIN-2024-33"  # Try another recent crawl
SEARCH_URL = f"https://index.commoncrawl.org/{INDEX}-index"

def get_african_locations(query_domain):
    params = {
        'url': f'*.{query_domain}/*', 
        'output': 'json',
        'filter': '=status:200', # Only successful pages
        'fl': 'filename,offset,length' # Only the info needed for AWS CLI
    }
    
    try:
        response = requests.get(SEARCH_URL, params=params)
        if response.status_code == 200 and response.text.strip():
            return [json.loads(line) for line in response.text.strip().split('\n')]
    except Exception as e:
        print(f"Error querying {query_domain}: {e}")
    
    return []

# Example: Finding South African News/Policy nodes
# We use "gov.za" as an example query
locations = get_african_locations("gov.za") 

# Result: [{'filename': 'crawl-data/...warc.gz', 'offset': '54321', 'length': '1200'}, ...]

print(f"Found {len(locations)} documents. Generating unique download commands:\n")

# Deduplicate filenames to avoid downloading the same WARC file multiple times
unique_filenames = set()

for record in locations:
    filename = record.get('filename')
    if filename and filename not in unique_filenames:
        unique_filenames.add(filename)
        # Format the command as specified
        command = f"aws s3 cp s3://commoncrawl/{filename} ./local_dir/ --no-sign-request"
        print(command)
