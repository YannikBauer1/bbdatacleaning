import axios from 'axios';
import * as cheerio from 'cheerio';
import { createObjectCsvWriter } from 'csv-writer';
import fs from 'fs';

const baseUrl = 'https://contests.npcnewsonline.com/contests';
const years = Array.from({ length: 14 }, (_, i) => 2011 + i); // 2011 to 2024

const csvWriter = createObjectCsvWriter({
    path: 'npcnews/all_clean.csv',
    header: [
        { id: 'startDate', title: 'Start Date' },
        { id: 'endDate', title: 'End Date' },
        { id: 'competition', title: 'Competition' },
        { id: 'location', title: 'Location' },
        { id: 'competitorName', title: 'Competitor Name' },
        { id: 'country', title: 'Country' },
        { id: 'judging', title: 'Judging' },
        { id: 'finals', title: 'Finals' },
        { id: 'round2', title: 'Round 2' },
        { id: 'round3', title: 'Round 3' },
        { id: 'routine', title: 'Routine' },
        { id: 'total', title: 'Total' },
        { id: 'place', title: 'Place' },
        { id: 'competitionType', title: 'Competition Type' },
        { id: 'date', title: 'Date' }
    ]
});

async function fetchContestData(year) {
    try {
        const url = `${baseUrl}/${year}/ifbb`;
        console.log(`Fetching data from ${url}`);
        
        const response = await axios.get(url);
        const $ = cheerio.load(response.data);
        
        const contests = [];
        
        // Find all contest entries
        $('.contest-entry').each((i, element) => {
            const contest = {
                startDate: $(element).find('.start-date').text().trim(),
                endDate: $(element).find('.end-date').text().trim(),
                competition: $(element).find('.competition-name').text().trim(),
                location: $(element).find('.location').text().trim(),
                competitorName: $(element).find('.competitor-name').text().trim(),
                country: $(element).find('.country').text().trim(),
                judging: $(element).find('.judging').text().trim(),
                finals: $(element).find('.finals').text().trim(),
                round2: $(element).find('.round2').text().trim(),
                round3: $(element).find('.round3').text().trim(),
                routine: $(element).find('.routine').text().trim(),
                total: $(element).find('.total').text().trim(),
                place: $(element).find('.place').text().trim(),
                competitionType: $(element).find('.competition-type').text().trim(),
                date: $(element).find('.date').text().trim()
            };
            
            contests.push(contest);
        });
        
        return contests;
    } catch (error) {
        console.error(`Error fetching data for year ${year}:`, error.message);
        return [];
    }
}

// Get all contest URLs for a given year
async function getContestUrlsForYear(year) {
    const url = `${baseUrl}/${year}/ifbb`;
    console.log(`Fetching contest list from ${url}`);
    const response = await axios.get(url);
    console.log(`Response status: ${response.status}`);
    console.log(`Response length: ${response.data.length}`);
    const $ = cheerio.load(response.data);
    const contestUrls = [];
    // Only select <a> tags inside .contest-listing and match URLs containing the year and 'ifbb_'
    $('.contest-listing a').each((i, el) => {
        const href = $(el).attr('href');
        console.log(`Found contest link: ${href}`);
        if (href && href.includes(`/contests/${year}/`)) {
            contestUrls.push(href);
        }
    });
    console.log(`Found ${contestUrls.length} contest URLs for year ${year}`);
    // Remove duplicates
    return [...new Set(contestUrls)];
}

// Extract results from a contest page
async function extractResultsFromContest(url, year) {
    console.log(`Fetching contest results from ${url}`);
    const response = await axios.get(url);
    const $ = cheerio.load(response.data);
    
    // Get contest name and date
    const contestName = $('.entry-title').first().text().trim();
    const contestDate = $('.entry-date').first().text().trim();
    
    const results = [];
    
    // Process each division in the contest table
    $('.contest_table td').each((i, divisionCell) => {
        const division = $(divisionCell).find('.division-title').text().trim();
        
        // Find all competitor classes in this division
        const classes = [];
        $(divisionCell).find('.competitor-class').each((j, classEl) => {
            const classText = $(classEl).text().trim();
            classes.push({
                name: classText,
                element: classEl
            });
        });
        
        // Process each class
        classes.forEach((classInfo, classIndex) => {
            const nextClass = classes[classIndex + 1];
            const startElement = classInfo.element;
            const endElement = nextClass ? nextClass.element : null;
            
            // Get all competitors between this class and the next class
            let currentElement = $(startElement).next();
            while (currentElement.length && (!endElement || currentElement[0] !== endElement)) {
                if (currentElement.is('a[data-parent="open"], a[data-parent="wheelchair"], a[data-parent*="masters"]')) {
                    const place = currentElement.find('span').first().text().trim();
                    const fullText = currentElement.text().trim();
                    const competitorName = fullText.replace(/^\d+\s+/, '').trim();
                    
                    // Skip if it's a comparison link or no valid place
                    if (!competitorName.includes('Comparisons') && place && !place.includes('disqualified')) {
                        results.push({
                            year,
                            contestName,
                            contestDate,
                            division: `${division} - ${classInfo.name}`,
                            place: parseInt(place),
                            competitorName,
                            contestUrl: url
                        });
                    }
                }
                currentElement = currentElement.next();
            }
        });
    });
    
    return results;
}

// Update main
async function main() {
    // Initialize CSV writer
    const csvWriter = createObjectCsvWriter({
        path: 'npcnews/all_clean.csv',
        header: [
            { id: 'year', title: 'Year' },
            { id: 'contestName', title: 'Contest Name' },
            { id: 'contestDate', title: 'Contest Date' },
            { id: 'division', title: 'Division' },
            { id: 'place', title: 'Place' },
            { id: 'competitorName', title: 'Competitor Name' },
            { id: 'contestUrl', title: 'Contest URL' }
        ]
    });

    // Create or clear the CSV file
    await csvWriter.writeRecords([]);

    for (const year of years) {
        let contestUrls = [];
        try {
            contestUrls = await getContestUrlsForYear(year);
            console.log(`Found ${contestUrls.length} contest URLs for year ${year}`);
        } catch (e) {
            console.error(`Failed to get contest URLs for year ${year}:`, e.message);
            continue;
        }

        for (const contestUrl of contestUrls) {
            try {
                const results = await extractResultsFromContest(contestUrl, year);
                if (results.length > 0) {
                    // Write results for this contest immediately
                    await csvWriter.writeRecords(results);
                    console.log(`Wrote ${results.length} results for ${results[0].contestName}`);
                }
                await new Promise(resolve => setTimeout(resolve, 1000));
            } catch (e) {
                console.error(`Failed to extract results from ${contestUrl}:`, e.message);
            }
        }
    }
    console.log('All contest results written to npcnews/all_clean.csv');
}

main().catch(console.error);
