import requests
from bs4 import BeautifulSoup

# List of URLs to scrape
urls = ['https://uk.iherb.com/blog/all'] + [f'https://uk.iherb.com/blog/all?sortBy=Newest&category=&p={i}' for i in range(2, 104)]
blog_links = set()  # Use a set to avoid duplicates

for url in urls:
    try:
        response = requests.get(url)
        
        # Ensure the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve {url}, status code: {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <a> tags with an aria-label attribute and extract href
        for a_tag in soup.find_all('a', attrs={'aria-label': True}):
            href = a_tag.get('href')
            if href.startswith('/blog/') and 'all?sortBy=Newest&category=&p=' not in href:
                blog_links.add(f'https://uk.iherb.com{href}')

    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")

# Output the extracted unique href links
print(list(blog_links))