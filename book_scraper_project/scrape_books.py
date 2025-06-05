# Importing required libraries
import requests                     # To send HTTP requests to websites
from bs4 import BeautifulSoup       # To extract data from HTML content
import csv                          # To save the data into a CSV file
import time                         # To add delay between page requests

# Base URL pattern for pagination (pages 1, 2, 3,...)
BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

# Function to get the HTML content of a given URL
def get_soup(url):
    try:
        response = requests.get(url)           # Send GET request to the URL
        response.raise_for_status()            # Raise error for bad status (404, 503 etc.)
        return BeautifulSoup(response.text, 'html.parser')  # Parse the HTML using BeautifulSoup
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")              # Print HTTP error message
        return None
    except Exception as e:
        print(f"Some error occurred: {e}")     # Print other errors
        return None

# Function to extract book data from the page soup
def parse_books(soup):
    books = []  # List to store all book data

    # Find all book blocks on the page
    articles = soup.find_all('article', class_='product_pod')

    for article in articles:
        try:
            # Extract book title
            title = article.h3.a['title']

            # Extract book price
            price = article.find('p', class_='price_color').text.strip()

            # Extract availability (In stock / Out of stock)
            availability = article.find('p', class_='instock availability').text.strip()

            # Handle rating safely
            rating_tag = article.find('p', class_='star-rating')
            if rating_tag and 'class' in rating_tag.attrs:
                rating_class = rating_tag['class']
                rating_text = rating_class[1] if len(rating_class) > 1 else ''
                ratings_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
                rating_num = ratings_map.get(rating_text, 0)
            else:
                rating_num = 0  # Default rating if not found

            # Get product page URL
            relative_url = article.h3.a['href']
            product_url = "http://books.toscrape.com/catalogue/" + relative_url.replace('../../../', '')

            # Add book data to list
            books.append({
                'Title': title,
                'Price': price,
                'Rating': rating_num,
                'Availability': availability,
                'URL': product_url
            })
        except Exception as e:
            print(f"Error parsing book: {e}")
            continue  # Skip this book and continue with the next one
    return books

# Function to scrape all books from all pages
def scrape_all_books():
    all_books = []  # Final list of all books
    page = 1        # Start from page 1

    while True:
        print(f"Scraping page {page}...")  # Show progress
        url = BASE_URL.format(page)       # Form the page URL
        soup = get_soup(url)              # Get page content

        if soup is None:
            break  # Stop scraping if page not found

        books = parse_books(soup)         # Get book data from current page

        if not books:
            print("No books found on this page. Assuming last page reached.")
            break  # Stop if no more books (last page reached)

        all_books.extend(books)           # Add current page books to final list
        page += 1                         # Move to next page
        time.sleep(1)                     # Wait 1 second between requests (polite scraping)

    return all_books

# Function to save data into a CSV file
def save_to_csv(data, filename='books_data.csv'):
    keys = ['Title', 'Price', 'Rating', 'Availability', 'URL']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()             # Write column headers
        writer.writerows(data)           # Write book data rows

# Main part: only runs if this file is executed directly
if __name__ == "__main__":
    books_data = scrape_all_books()         # Scrape the book data
    print(f"Scraped {len(books_data)} books.")  # Show how many books were scraped
    save_to_csv(books_data)                 # Save data into a CSV file
    print("Data saved to 'books_data.csv'.")
