from datetime import datetime

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import json
import re


def search_bing(query):
    encoded_query = quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        for i, result in enumerate(soup.select("div.g")):
            title_element = result.select_one("h3")
            link_element = result.select_one("a")

            if title_element and link_element:
                title = title_element.text
                link = link_element['href']
                results.append({"id": i, "title": title, "link": link})

        if not results:
            print("No results found.")

        return results
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def extract_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.title.text.strip() if soup.title else "No title"

        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(
            r'content|article|news'))

        # Extract metadata
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description = meta_description['content'] if meta_description else ""

        # Extract publication date
        date_element = soup.find('time') or soup.find('span', class_=re.compile(r'date|time|published'))
        date = date_element.text.strip() if date_element else "Date not found"

        # Extract author
        author_element = soup.find('span', class_=re.compile(r'author|byline')) or soup.find('meta',
                                                                                             attrs={'name': 'author'})
        author = author_element.text.strip() if author_element else "Author not found"

        # Extract main article text
        content = []
        if main_content:
            paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = [p.text.strip() for p in paragraphs if len(p.text.strip()) > 20]

        # If content is not found, use alternative method
        if not content:
            all_text = soup.find_all(text=True)
            content = [text.strip() for text in all_text if
                       text.parent.name not in ['style', 'script', 'head', 'title', 'meta', '[document]'] and len(
                           text.strip()) > 20]

        # Extract keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords_meta['content'].split(',') if keywords_meta else []

        # Extract links from the article
        links = [a['href'] for a in main_content.find_all('a', href=True)] if main_content else []

        # Remove duplicates from content
        content = list(dict.fromkeys(content))

        return {
            "title": title,
            "description": description,
            "date": date,
            "author": author,
            "content": content,
            "keywords": keywords,
            "related_links": links[:10],  # Limit to 10 links
            "word_count": sum(len(text.split()) for text in content),
            "url": url,
            "extracted_at": datetime.now().isoformat()
        }
    except requests.RequestException as e:
        print(f"An error occurred while extracting data: {e}")
        return {"error": str(e)}


def search(query):
    """Performs a Google search and returns the results."""
    results = search_bing(query)
    return json.dumps(results, ensure_ascii=False, indent=2)


def click(result_id, results):
    """Extracts data from the selected website."""
    results = json.loads(results)
    if 0 <= result_id < len(results):
        url = results[result_id]['link']
        data = extract_data(url)
        return json.dumps(data, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": "Invalid result ID"})


def main():
    last_results = None
    while True:
        command = input("Enter command (/search=\"query\", /click=ID, or /search_exit): ").strip()

        if command.startswith("/search="):
            match = re.match(r'/search="([^"]+)"', command)
            if match:
                query = match.group(1)
                results = search(query)
                print(results)
                last_results = results
            else:
                print("Invalid search command. Use format: /search=\"query\"")

        elif command.startswith("/click="):
            if last_results:
                try:
                    result_id = int(command.split("=")[1])
                    data = click(result_id, last_results)
                    print(data)
                except ValueError:
                    print("Invalid result ID. Please enter a number.")
            else:
                print("No search results available. Please perform a search first.")

        elif command == "/search_exit":
            print("Exiting the program.")
            break

        else:
            print("Invalid command. Use /search=\"query\", /click=ID, or /search_exit")


if __name__ == "__main__":
    main()