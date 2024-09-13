import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import re

base_url = "https://uk.iherb.com"
start_url = f"{base_url}/blog/all"
blog_links = set()  # Use a set to avoid duplicates


async def get_next_page(soup):
    """Find the 'Next' page link from pagination."""
    next_link = soup.find("a", class_="pagination-next")
    if next_link:
        return base_url + next_link.get("href")
    return None


async def scrape_blog_links(session, url):
    """Scrape blog links from a given page asynchronously."""
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Failed to retrieve {url}, status code: {response.status}")
                return None

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # Find all <a> tags with aria-label and extract valid blog links
            for a_tag in soup.find_all("a", attrs={"aria-label": True}):
                href = a_tag.get("href")
                if (
                    href.startswith("/blog/")
                    and "all?sortBy=Newest&category=&p=" not in href
                ):
                    blog_links.add(f"{base_url}{href}")

            # Return the next page URL if it exists
            return await get_next_page(soup)

    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")
        return None


async def get_blog_content(session, blog_url):
    """Fetch the content of a blog post asynchronously and preserve HTML structure."""
    try:
        async with session.get(blog_url) as response:
            if response.status != 200:
                return {"error": f"Failed to retrieve the blog, status code: {response.status}"}

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            article_body_div = soup.find("div", class_="article-body")
            
            # Assuming 'article_body_div' contains the relevant part of the HTML
            elements = article_body_div.find_all(recursive=False)

            content_list = []
            current_tag = None
            current_text = []

            for elem in elements:
                # If it's a heading or other tag that should act as a key
                if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:  # Add more tags if needed
                    # Save the previous tag's content
                    if current_tag is not None:
                        content_list.append({current_tag: ' '.join(current_text)})
                    
                    # Start a new tag
                    current_tag = elem.name
                    current_text = [re.sub(r'\s+', ' ', elem.get_text(strip=True)).strip()]
                else:
                    # Add content under the current tag if it's not a new tag
                    current_text.append(re.sub(r'\s+', ' ', elem.get_text(strip=True)).strip())

            # Add the last tag and its content
            if current_tag is not None:
                content_list.append({current_tag: ' '.join(current_text)})

            return content_list

    except Exception as e:
        return {"error": f"Error occurred while scraping the blog: {str(e)}"}


async def scrape_all_blogs(session):
    """Scrape content for all collected blog links asynchronously."""
    json_data = {}

    # Create tasks for fetching each blog content concurrently
    tasks = [get_blog_content(session, blog_url) for blog_url in blog_links]
    results = await asyncio.gather(*tasks)

    # Populate the JSON data with blog content
    for blog_url, article_body in zip(blog_links, results):
        json_data[blog_url] = article_body

    # Write the data to a JSON file
    with open("blogs.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)


async def main():
    async with aiohttp.ClientSession() as session:
        next_page_url = start_url

        # Sequentially scrape page by page and collect blog links
        while "blog" in next_page_url:
            print(f"Scraping: {next_page_url}")
            next_page_url = await scrape_blog_links(session, next_page_url)

        print(f"Total blog links scraped: {len(blog_links)}")

        # Now scrape all blog content concurrently
        await scrape_all_blogs(session)


if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main())