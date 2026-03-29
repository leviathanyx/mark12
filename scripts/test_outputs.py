import os
import glob
from bs4 import BeautifulSoup

def verify_html():
    html_files = glob.glob("dist/packages/*.html")
    if not html_files:
        print("No HTML files found in dist/packages/")
        return False

    success = True
    for f in html_files:
        with open(f, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')

            # Check for title
            if not soup.title:
                print(f"FAILED: {f} has no title")
                success = False

            # Check for pricing section
            pricing_section = soup.find('section', string=lambda t: t and 'Price Summary' in t)
            if not pricing_section:
                # Try finding by h2
                h2s = soup.find_all('h2')
                if not any('Price Summary' in h2.text for h2 in h2s):
                    print(f"FAILED: {f} has no Price Summary section")
                    success = False

            # Check for itinerary
            h2s = soup.find_all('h2')
            if not any('Your Itinerary' in h2.text for h2 in h2s):
                print(f"FAILED: {f} has no Your Itinerary section")
                success = False

    if success:
        print(f"Successfully verified {len(html_files)} HTML brochure pages.")
    return success

if __name__ == '__main__':
    verify_html()
