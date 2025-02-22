
# **Automating FED Rate Data Extraction from State Bank Pakistan Website**  

## **📌 The Problem**  

The Fed rate called Karachi Interbank Offered Rate (KIBOR), set by the State Bank of Pakistan (SBP), is a crucial benchmark for financial markets. It influences lending rates, stock market behavior, and economic policy decisions. However, SBP publishes this data as **scanned PDFs** on its website, making automated extraction difficult.  

This manual format is inefficient for financial analysts, traders, and researchers who need **structured, timely, and historical rate data**.  

### **The Solution: Automated Scraping & Processing**  

I built a fully **automated scraper** that:  
✔️ **Navigates SBP’s website** dynamically  
✔️ **Identifies new PDFs**, avoiding redundant downloads  
✔️ **Extracts tabular data** from PDFs using `pdfplumber`  
✔️ **Stores structured data** in JSON format  
✔️ **Runs on a schedule** via **GitHub Actions**, ensuring up-to-date data  

---

## **🔍 Approach**  

### **1. Navigating & Identifying New Data**  

- The script launches a headless browser using Playwright.  
- It selects year & month dropdowns dynamically to locate PDFs.  
- Extracted PDF links are compared against existing data to avoid redundant processing.  

### **2. Downloading & Extracting PDF Data**  

- Once new PDFs are identified, they are downloaded and parsed using `pdfplumber`.  
- Since SBP occasionally changes its PDF format, the extraction logic accounts for inconsistencies.  
- The extracted tabular data is structured into a clean JSON format.  

### **3. Incremental Updates & Parallel Processing**  

- The script only fetches new data rather than scraping everything each time.  
- Multi-threading (`ThreadPoolExecutor`) has been added to the code so that the first run of the script that scrapes hundreds of pdfs can be distributed among multiple processor threads to ensure fast processing.  

### **4. Productionalization via GitHub Actions**  

- The scraper runs on a defined daily schedule using GitHub Actions.  
- Logs are maintained for debugging and monitoring failures.  
- New data is automatically committed to the repository for immediate downstream use.  

---

## 🚀 **Scaling the Project: Data Cleaning & Usability**  

During the scraping process, **inconsistent PDF formats over time** resulted in **dirty data**. Some files had missing headers, different column structures, or OCR-related issues.  

### **Next Steps: Building a Data Cleaning Pipeline**  
- **Standardizing historical data formats**  
- **Handling missing or malformed entries**  
- **Transforming JSON into a structured database** for **easy querying & visualization**  

This will be part of a separate project, making the dataset truly **ready for financial modeling, dashboarding, or machine learning** applications.  

---

## **🛠️ Tech Stack**  

| **Category**  | **Technology** |
|--------------|--------------|
| Web Scraping | `Playwright`, `BeautifulSoup` |
| PDF Parsing  | `pdfplumber` |
| Automation   | `GitHub Actions` |
| Concurrency  | `ThreadPoolExecutor` |
| Data Storage | `JSON` |
| Logging      | `logging` |


---

## **⏩Next Steps**

This project showcases **end-to-end automation**, from **scraping to scheduling**, making real-world financial data **usable for downstream analytics**.  

As the next step in this project, I will integrate a data-cleaning pipeline to ensure historical consistency.  


