from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

app = Flask(__name__)

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    movies_data = []
    
    try:
        url = "https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&count=250"
        print("1. Requesting page...")
        driver.get(url)

        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ipc-metadata-list-summary-item")))
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 4);")
        time.sleep(1)

        print("2. Page loaded. Extracting data...")
        rows = driver.find_elements(By.CLASS_NAME, "ipc-metadata-list-summary-item")
        
        for index, row in enumerate(rows):
            try:
                # 1. Title & Rank
                title_el = row.find_element(By.CSS_SELECTOR, "h3.ipc-title__text")
                raw_title = title_el.text
                
                # Default values
                rank = index + 1
                title = raw_title

                if '. ' in raw_title:
                    parts = raw_title.split('. ', 1)
                    # Safely try to parse rank, fallback to index if it fails
                    if parts[0].isdigit():
                        rank = int(parts[0])
                    title = parts[1]

                # 2. Year
                metadata_items = row.find_elements(By.CSS_SELECTOR, ".dli-title-metadata-item")
                year = 0
                if metadata_items:
                    year_text = metadata_items[0].text
                    year = int(''.join(filter(str.isdigit, year_text))) if any(c.isdigit() for c in year_text) else 0
                
                # 3. Rating
                rating_el = row.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--rating")
                rating = float(rating_el.text)

                # 4. Genre Detection
                full_text = row.text.lower()
                genres = []
                keyword_map = {
                    "comedy": "Comedy", "horror": "Horror", "romance": "Romance", 
                    "action": "Action", "drama": "Drama", "sci-fi": "Sci-Fi",
                    "thriller": "Thriller", "adventure": "Adventure", 
                    "crime": "Crime", "animation": "Animation", "biography": "Biography",
                    "mystery": "Mystery", "war": "War", "family": "Family"
                }
                for key, val in keyword_map.items():
                    if key in full_text:
                        genres.append(val)
                if not genres: genres.append("Other")

                movies_data.append({
                    "Rank": rank,
                    "Title": title,
                    "Year": year,
                    "Rating": rating,
                    "Genres": genres
                })
            except Exception:
                continue

        if movies_data:
            df = pd.DataFrame(movies_data)
            df.to_csv("imdb_top_movies.csv", index=False)
            print(f"4. Done. Scraped {len(movies_data)} movies.")
        
        return movies_data

    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['GET'])
def scrape():
    data = run_scraper()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
