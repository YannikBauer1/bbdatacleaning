# MuscleMemory IFBB Competition Scraper

This script scrapes IFBB competition data from musclememory.com and saves it to CSV files.

## Setup

1. Make sure you have Node.js installed on your system
2. Install the required dependencies:
   ```bash
   npm install
   ```

## Usage

Run the scraper with:
```bash
npm start
```

The script will:
1. Create an `output` directory
2. Scrape all IFBB competitions from musclememory.com
3. Create separate CSV files for each year in the `output` directory

## Output Format

Each CSV file will contain the following columns:
- Competition: Name of the competition
- Place: Placement in the competition
- Name: Name of the competitor
- Score: Score (if available)

## Notes

- The script includes a 1-second delay between requests to be respectful to the server
- Only IFBB competitions are scraped
- Data is saved in yearly CSV files for easier organization 