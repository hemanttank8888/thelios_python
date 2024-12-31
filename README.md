# Scrapy Project: mauijim Data Scraper

## Overview
This project is built using the **Scrapy** library and is designed to scrape data from the thelios website. The scraped data is stored in a MySQL database for further processing and analysis.


## Features
- Scrapes product data from the thelios website.
- Cleans and validates data to ensure accuracy and consistency.
- Efficiently handles large datasets with Scrapy's asynchronous framework.
- Stores scraped data in a MySQL database.

## Requirements
- Python 3.13.0
- Scrapy library
- MySQL database

## Installation
- Clone this repository:
   ```bash
   git clone https://github.com/hemanttank8888/thelios_python.git
   cd thelios_python
   ```
- Install the required dependencies
  ```bash
  pip install -r requirements.txt
  ```

## Configuration

```Python
MYSQL_HOST = 'your-database-host'
MYSQL_USER = 'your-database-username'
MYSQL_PASSWORD = 'your-database-password'
MYSQL_DATABASE = 'your-database-name'
```

## Usage
- Run the Scrapy spider to start scraping:

```bash
scrapy crawl <spider-name>

```
