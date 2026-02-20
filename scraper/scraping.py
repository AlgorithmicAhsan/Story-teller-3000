import cloudscraper
from bs4 import BeautifulSoup
import time
import json
import random

targetCount = 500
outputFile = "urdu_stories.json"
baseUrl = "https://www.urdupoint.com/kids/section/stories.html"
pageUrlTemplate = "https://www.urdupoint.com/kids/section/stories-page{}.html"

def getScraper():
    return cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )

def getSoup(scraper, url):
    try:
        # Random delay (1.5 to 3 seconds)
        time.sleep(random.uniform(1.5, 3.0))
        response = scraper.get(url, timeout=20)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extractText(soup):
    """
    HTML Cleanup & Preprocessing
    """
    contentDiv = soup.find('div', class_='txt_detail') or soup.find('div', class_='detail_txt')
    
    if not contentDiv:
        return None

    # ads, hidden text, scripts, styles
    for tag in contentDiv(['script', 'style', 'iframe', 'object', 'ins']):
        tag.decompose()
    
    # classes used for ads/banners
    for badClass in ['txt_banner', 'hide_desk', 'related_container']:
        for tag in contentDiv.find_all(class_=badClass):
            tag.decompose()

    # elements with inline styles for centering
    for tag in contentDiv.find_all('div', attrs={'align': 'center'}):
        tag.decompose()

    text = contentDiv.get_text(separator='\n')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleanedLines = []
    
    for line in lines:
        # contains Urdu characters ? (Unicode range 0600-06FF)
        if any('\u0600' <= char <= '\u06FF' for char in line):
            # in case any menu items
            if len(line) > 5 and "UrduPoint" not in line:
                cleanedLines.append(line)

        elif line in ['.', '،', '۔', '!', '?', '"', "'"]:
            cleanedLines.append(line)

    return "\n".join(cleanedLines)

def scrapeStories():
    storiesData = []
    pageNum = 1
    scraper = getScraper()
    
    globalVisitedUrls = set() # to avoid dups

    print(f"Scraping for {targetCount} stories")

    while len(storiesData) < targetCount:
        if pageNum == 1:
            url = baseUrl
        else:
            url = pageUrlTemplate.format(pageNum)
        
        print(f"\n--- Scraping Page {pageNum} ---")
        soup = getSoup(scraper, url)
        
        if not soup:
            print("Failed to load page. Stopping.")
            break

        # links
        mainCol = soup.find('div', class_='col-md-8') or soup
        allAnchors = mainCol.find_all('a', href=True)
        pageLinks = []
        seenOnThisPage = set()

        for link in allAnchors:
            href = link['href']
            
            if '/kids/detail/' in href:
                # fix relative URLs
                if not href.startswith('http'):
                    href = "https://www.urdupoint.com" + href
                
                if href not in seenOnThisPage and href not in globalVisitedUrls:
                    pageLinks.append(href)
                    seenOnThisPage.add(href)

        pageLinks = pageLinks[:12] # stories always in first 12 links
        if not pageLinks:
            print("No new valid stories found on this page.")
            if pageNum > 50: break
        
        for link in pageLinks:
            if len(storiesData) >= targetCount:
                break
            globalVisitedUrls.add(link)
            
            print(f"Fetching {len(storiesData) + 1}/{targetCount}: {link}")
            storySoup = getSoup(scraper, link)
            
            if storySoup:
                try:
                    # title
                    titleTag = storySoup.find('h1')
                    title = titleTag.get_text(strip=True) if titleTag else "No Title"
                    
                    # content
                    content = extractText(storySoup)
                    
                    if content and len(content) > 100:
                        storiesData.append({
                            "title": title,
                            "url": link,
                            "content": content
                        })
                    else:
                        print("  -> Skipped (Content too short/empty)")

                except Exception as e:
                    print(f"  -> Error parsing story: {e}")

        pageNum += 1

    print(f"\nScraping complete. Saving {len(storiesData)} stories to {outputFile}...")
    with open(outputFile, 'w', encoding='utf-8') as f:
        json.dump(storiesData, f, ensure_ascii=False, indent=4)
    print("Done!")

if __name__ == "__main__":
    scrapeStories()