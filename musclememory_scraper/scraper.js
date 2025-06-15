const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

// Create output directory if it doesn't exist
const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}

// Base URLs for the website
const BASE_URLS = {
    //male: 'https://musclememory.com/male/year.html',
    female: 'https://musclememory.com/female/year.html'
};

// Configure axios with default headers
const axiosInstance = axios.create({
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    timeout: 10000 // 10 second timeout
});

// Function to get all year links
async function getYearLinks(baseUrl) {
    try {
        console.log('Fetching year links from:', baseUrl);
        const response = await axiosInstance.get(baseUrl);
        const $ = cheerio.load(response.data);
        const yearLinks = [];
        
        // Find all year links - handle both formats:
        // 1. show.php?g=1&y=YEAR (female format)
        // 2. show.php?y=YEAR (male format)
        $('a[href*="show.php"]').each((i, element) => {
            const href = $(element).attr('href');
            const year = $(element).text().trim();
            
            // Check if this is a year link
            if (year && href && (href.includes('show.php?y=') || href.includes('show.php?g=1&y='))) {
                // Extract year from href if text is empty
                const yearMatch = href.match(/y=(\d{4})/);
                const extractedYear = yearMatch ? yearMatch[1] : year;
                
                yearLinks.push({
                    year: extractedYear,
                    url: `https://musclememory.com/${href}`
                });
            }
        });
        
        console.log(`Found ${yearLinks.length} year links`);
        return yearLinks;
    } catch (error) {
        console.error('Error fetching year links:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response headers:', error.response.headers);
        }
        return [];
    }
}

// Function to get competition links for a specific year
async function getCompetitionLinks(yearUrl) {
    try {
        console.log('Fetching competition links from:', yearUrl);
        const response = await axiosInstance.get(yearUrl);
        const $ = cheerio.load(response.data);
        const competitionLinks = [];
        
        // Find all competition links in the list table
        $('#list a[href*="show.php?c="]').each((i, element) => {
            const competitionName = $(element).text().trim();
            const href = $(element).attr('href');
            if (competitionName && href) {
                competitionLinks.push({
                    name: competitionName,
                    url: `https://musclememory.com/${href}`
                });
            }
        });
        
        console.log(`Found ${competitionLinks.length} competition links`);
        return competitionLinks;
    } catch (error) {
        console.error('Error fetching competition links:', error.message);
        return [];
    }
}

// Function to get competition data for a specific competition
async function getCompetitionData(competitionUrl) {
    try {
        console.log('Fetching competition data from:', competitionUrl);
        const response = await axiosInstance.get(competitionUrl);
        const $ = cheerio.load(response.data);
        const results = [];
        
        // Find all tables
        $('table').each((i, table) => {
            let currentCategory = '';
            const rows = [];
            
            // Process each row in the table
            $(table).find('tr').each((j, row) => {
                const columns = $(row).find('td');
                
                // Check if this is a category header row (either colspan=2 or bold text)
                if (columns.length === 2 && 
                    (columns.first().attr('colspan') === '2' || 
                     columns.first().find('b').length > 0)) {
                    currentCategory = columns.first().text().trim();
                    return; // Skip to next row
                }
                
                // Also check for category headers in the format "| **Category** |"
                const firstCell = columns.first();
                if (firstCell.find('b').length > 0 && 
                    firstCell.text().trim() !== '' && 
                    !firstCell.text().trim().match(/^\d+$/) && 
                    !firstCell.text().trim().match(/^-$/)) {
                    currentCategory = firstCell.text().trim();
                    return; // Skip to next row
                }
                
                // Process regular result rows
                if (columns.length >= 2) {
                    const place = $(columns[0]).text().trim();
                    const name = $(columns[1]).text().trim();
                    const score = columns.length > 2 ? $(columns[2]).text().trim() : '';
                    
                    if (place && name) {
                        rows.push({
                            place,
                            name,
                            score,
                            category: currentCategory
                        });
                    }
                }
            });
            
            if (rows.length > 0) {
                results.push(...rows);
            }
        });
        
        console.log(`Found ${results.length} results for this competition`);
        return results;
    } catch (error) {
        console.error(`Error fetching data for ${competitionUrl}:`, error.message);
        return [];
    }
}

// Function to save data to CSV
function saveToCSV(data, year, gender) {
    const csvContent = [
        ['Competition', 'Category', 'Place', 'Name', 'Score'].join(','),
        ...data.map(row => [
            row.competition,
            row.category,
            row.place,
            row.name,
            row.score
        ].join(','))
    ].join('\n');

    const filePath = path.join(outputDir, `ifbb_competitions_${gender}_${year}.csv`);
    fs.writeFileSync(filePath, csvContent);
    console.log(`Saved ${data.length} records to ${filePath}`);
}

// Function to process competitions for a specific gender
async function processGender(gender) {
    console.log(`Starting to process ${gender} competitions...`);
    
    // Get all year links
    const yearLinks = await getYearLinks(BASE_URLS[gender]);
    if (yearLinks.length === 0) {
        console.error(`No year links found for ${gender}. Skipping...`);
        return;
    }
    
    console.log(`Found ${yearLinks.length} years to process for ${gender}`);
    
    // Process each year
    for (const { year, url } of yearLinks) {
        console.log(`Processing year ${year} for ${gender}...`);
        
        // Get competition links for the year
        const competitionLinks = await getCompetitionLinks(url);
        
        // Process each competition
        const allCompetitions = [];
        for (const { name, url: competitionUrl } of competitionLinks) {
            // Only process IFBB competitions
            if (name.includes('IFBB')) {
                console.log(`Processing competition: ${name}`);
                const results = await getCompetitionData(competitionUrl);
                
                if (results.length > 0) {
                    // Add competition name to each result
                    const competitionResults = results.map(result => ({
                        ...result,
                        competition: name
                    }));
                    allCompetitions.push(...competitionResults);
                }
                
                // Add a small delay to be respectful to the server
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }
        
        if (allCompetitions.length > 0) {
            // Save to CSV
            saveToCSV(allCompetitions, year, gender);
        }
    }
}

// Main function to run the scraper
async function main() {
    console.log('Starting to scrape musclememory.com...');
    
    // Process both male and female competitions
    await processGender('male');
    await processGender('female');
    
    console.log('Scraping completed!');
}

// Run the main function
main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
}); 