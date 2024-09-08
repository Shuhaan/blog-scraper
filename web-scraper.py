import requests
from bs4 import BeautifulSoup
import json

base_url = 'https://uk.iherb.com'
start_url = f'{base_url}/blog/all'
blog_links = set()  # Use a set to avoid duplicates

def get_next_page(soup):
    """Find the 'Next' page link from pagination."""
    next_link = soup.find('a', class_='pagination-next')
    if next_link:
        return base_url + next_link.get('href')
    return None

def scrape_blog_links(url):
    """Scrape blog links from a given page."""
    try:
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve {url}, status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <a> tags with aria-label and extract valid blog links
        for a_tag in soup.find_all('a', attrs={'aria-label': True}):
            href = a_tag.get('href')
            if href.startswith('/blog/') and 'all?sortBy=Newest&category=&p=' not in href:
                blog_links.add(f'{base_url}{href}')
        
        # Return the next page URL if exists
        return get_next_page(soup)
    
    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")
        return None

# Start scraping from the first page
next_page_url = start_url

while next_page_url:
    print(f"Scraping: {next_page_url}")
    next_page_url = scrape_blog_links(next_page_url)

# Output the extracted blog links
print(f"Total blog links scraped: {len(blog_links)}")
print(list(blog_links))


# def get_blog_content(blog_url):
#     try:
#         # Fetch the blog page
#         response = requests.get(blog_url)
#         if response.status_code != 200:
#             return {'error': f'Failed to retrieve the blog, status code: {response.status_code}'}
        
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         article_body = soup.find('div', class_='article-body').text.strip() if soup.find('div', class_='article-body').text.strip() else 'Blog not found'
        
#         # Create a JSON object with the scraped data
#         blog_data = {
#             'article_body': article_body,
#         }

#         return blog_data
    
#     except Exception as e:
#         return {'error': f'Error occurred while scraping the blog: {str(e)}'}

# for blog_url in blog_links:
#     blog_json = get_blog_content(blog_url)
#     blog_name = blog_url.replace(f'{base_url}/blog/', "").replace('/', '-') + '.json'
    
#     with open(f'blog/{blog_name}', 'w', encoding='utf-8') as file:
#         json.dump(blog_json, file, ensure_ascii=False, indent=4)