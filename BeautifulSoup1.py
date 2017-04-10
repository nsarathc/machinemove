from bs4 import BeautifulSoup

soup = BeautifulSoup('<META NAME="City" content="Austin">', 'html.parser')

print [ (meta.attrs['content'], meta.attrs['name']) for meta in soup.find_all('meta') ]
