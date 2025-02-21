import requests
import pdfplumber
from io import BytesIO
from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup
import time
import json
import os
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Logging setup
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_scraped_data(file_path="scraped_data.json"):
    """Load existing scraped data or initialize an empty list."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            scraped_data = json.load(f)
            latest_date = max(
            datetime.datetime.strptime(entry["Date"], "%Y-%m-%d %H:%M:%S")
            for entry in scraped_data
        )
        
    else:
        scraped_data = []
        latest_date = datetime.datetime.min  # Default to earliest possible date
    return scraped_data, latest_date


def extract_date_from_link(link):
    """Extract the date from the link as a datetime object."""
    try:
        date_str = "-".join(link.split("/")[-1][:-4].split("-")[-3:])  # e.g., "31-Dec-24"
        return datetime.datetime.strptime(date_str, "%d-%b-%y")
    except Exception:
        logging.warning(f"Invalid date format in link: {link}")
        return None


def get_pdf_links(page, year, latest_date):
    """Retrieve PDF links for a specific year and check against latest date."""
    pdf_links_to_scrape = []
    should_exit = False

    # Select year in the dropdown
    page.select_option("select[name='year']", year)
    time.sleep(1)

    # Refresh page content and retrieve months
    page_source = page.content()
    soup = BeautifulSoup(page_source, "html.parser")
    dropdown_month = soup.find("select", {"name": "month"})
    months = [option.text.strip() for option in dropdown_month.find_all("option")][::-1]

    for month in months:
        # Select month in the dropdown
        page.select_option("select[name='month']", month)
        time.sleep(1)

        # Refresh page content and find PDF links
        page_source = page.content()
        soup = BeautifulSoup(page_source, "html.parser")
        links_to_pdf = soup.find_all("a", {"target": "_blank"})

        for link in links_to_pdf:
            href = link.get("href")
            pdf_url = f"https://www.sbp.org.pk{href[2:]}"
            link_date = extract_date_from_link(pdf_url)

            if not link_date:
                continue  # Skip invalid links

            if link_date > latest_date:
                pdf_links_to_scrape.append(pdf_url)
            elif link_date <= latest_date:
                logging.info(f"Encountered older or already-scraped link: {pdf_url}. Exiting...")
                should_exit = True
                break

        if should_exit:
            break

    return pdf_links_to_scrape, should_exit


def get_data_from_pdf(pdf_url):
    """Fetch and extract data from a PDF."""
    try:
        response = requests.get(pdf_url, timeout=10)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch PDF: {pdf_url}")
            return None

        link_date = extract_date_from_link(pdf_url)
        logging.info(f"Scraping started for date: {link_date}")

        pdf_stream = BytesIO(response.content)
        with pdfplumber.open(pdf_stream) as pdf:
            table = pdf.pages[0].extract_tables()  # Only process the first page
            table = table[0][1:] if table else []  # Remove header if table exists

        return {
            "Date": link_date,
            "Data": table
        }
    except Exception as e:
        logging.error(f"Error processing PDF at {pdf_url}: {e}")
        return None


def save_scraped_data(scraped_data, file_path="scraped_data.json"):
    """Save scraped data to a JSON file."""
    with open(file_path, "w") as json_file:
        json.dump(scraped_data, json_file, indent=4, default=str)
    logging.info("Data scraping completed. JSON saved.")


# Main script execution
def main():
    scraped_data, latest_date = load_scraped_data()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://www.sbp.org.pk/ecodata/kibor_index.asp")
            time.sleep(5)

            page_source = page.content()
            soup = BeautifulSoup(page_source, "html.parser")
            dropdown_year = soup.find("select", {"name": "year"})
            years = [option.text.strip() for option in dropdown_year.find_all("option")]

            pdf_links_to_scrape = []
            for year in years:
                links, should_exit = get_pdf_links(page, year, latest_date)
                pdf_links_to_scrape.extend(links)
                if should_exit:
                    break

        finally:
            browser.close()
            print(latest_date)
            quit

    # Fetch and process PDFs concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(get_data_from_pdf, link) for link in pdf_links_to_scrape]
        for future in as_completed(futures):
            result = future.result()
            if result:
                scraped_data.insert(0,result)

    save_scraped_data(scraped_data)


if __name__ == "__main__":
    main()

