import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
import os
import csv

from scrape_books import get_soup, parse_books, save_to_csv


SAMPLE_HTML_VALID = '''
<html>
    <body>
        <article class="product_pod">
            <h3><a title="Test Book" href="../../../test-book_1/index.html"></a></h3>
            <p class="price_color">£20.00</p>
            <p class="instock availability">In stock</p>
            <p class="star-rating Three"></p>
        </article>
    </body>
</html>
'''

SAMPLE_HTML_MISSING_RATING = '''
<html>
    <body>
        <article class="product_pod">
            <h3><a title="No Rating Book" href="../../../book.html"></a></h3>
            <p class="price_color">£9.99</p>
            <p class="instock availability">In stock</p>
        </article>
    </body>
</html>
'''


class TestBookScraper(unittest.TestCase):

    @patch('scrape_books.requests.get')
    def test_parse_books_from_mocked_html(self, mock_get):
        # Test Case 1: Verify parsing works and CSV saving can follow
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_HTML_VALID
        mock_get.return_value = mock_response

        soup = get_soup("http://mocked.url")
        books = parse_books(soup)

        self.assertEqual(len(books), 1)
        book = books[0]
        self.assertEqual(book['Title'], 'Test Book')
        self.assertEqual(book['Price'], '£20.00')
        self.assertEqual(book['Availability'], 'In stock')
        self.assertEqual(book['Rating'], 3)
        self.assertTrue(book['URL'].endswith('test-book_1/index.html'))

    def test_csv_file_download(self):
        # Test Case 2: Verify CSV file is created
        data = [{
            'Title': 'CSV Book',
            'Price': '£15.00',
            'Rating': 4,
            'Availability': 'In stock',
            'URL': 'http://example.com/csv-book'
        }]
        filename = 'test_books_data.csv'
        save_to_csv(data, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_csv_file_content(self):
        # Test Case 3: Verify CSV content
        data = [{
            'Title': 'Content Book',
            'Price': '£10.00',
            'Rating': 5,
            'Availability': 'In stock',
            'URL': 'http://example.com/book'
        }]
        filename = 'test_books_data.csv'
        save_to_csv(data, filename)

        with open(filename, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(reader[0]['Title'], 'Content Book')
            self.assertEqual(reader[0]['Price'], '£10.00')
            self.assertEqual(reader[0]['Rating'], '5')
            self.assertEqual(reader[0]['Availability'], 'In stock')
        os.remove(filename)

    def test_file_format_and_header(self):
        # Test Case 4: Validate file extension and header
        data = [{
            'Title': 'Format Book',
            'Price': '£8.99',
            'Rating': 2,
            'Availability': 'In stock',
            'URL': 'http://example.com/book'
        }]
        filename = 'test_books_data.csv'
        save_to_csv(data, filename)

        self.assertTrue(filename.endswith('.csv'))
        with open(filename, encoding='utf-8') as f:
            header = f.readline().strip()
            self.assertEqual(header, 'Title,Price,Rating,Availability,URL')
        os.remove(filename)

    def test_data_structure(self):
        # Test Case 5: Validate dictionary structure
        soup = BeautifulSoup(SAMPLE_HTML_VALID, 'html.parser')
        books = parse_books(soup)
        self.assertIn('Title', books[0])
        self.assertIn('Price', books[0])
        self.assertIn('Rating', books[0])
        self.assertIn('Availability', books[0])
        self.assertIn('URL', books[0])

    def test_missing_rating_handling(self):
        # Test Case 6: Handle missing or invalid data (rating missing)
        soup = BeautifulSoup(SAMPLE_HTML_MISSING_RATING, 'html.parser')
        books = parse_books(soup)
        self.assertEqual(books[0]['Rating'], 0)


if __name__ == '__main__':
    unittest.main()
