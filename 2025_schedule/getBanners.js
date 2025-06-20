import fs from 'fs';
import https from 'https';
import csvWriter from 'csv-writer';
import * as cheerio from 'cheerio';
import axios from 'axios';

// Function to make HTTPS request
function makeRequest(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve(jsonData);
                } catch (error) {
                    reject(error);
                }
            });
        }).on('error', (error) => {
            reject(error);
        });
    });
}

// Function to extract divisions from title and categories
function extractDivisions(event) {
    const title = event.title.toLowerCase();
    const categories = event.categories || [];
    
    let divisions = [];
    let divisionType = '';
    let divisionsExtra = '';
    
    // Common division keywords
    const divisionKeywords = {
        'men': ['men', 'male', 'mp', 'mens physique', "men's physique"],
        'women': ['women', 'female', 'wp', 'womens physique', "women's physique"],
        'bikini': ['bikini', 'bik'],
        'figure': ['figure', 'fig'],
        'wellness': ['wellness', 'well'],
        'classic': ['classic', 'classic physique', 'cp'],
        'bodybuilding': ['bodybuilding', 'bb'],
        'fitness': ['fitness', 'fit'],
        'masters': ['masters', 'master', '40+', '50+', '60+'],
        'natural': ['natural', 'nat'],
        'open': ['open'],
        'amateur': ['amateur', 'am'],
        'pro': ['pro', 'professional']
    };
    
    // Extract divisions from title
    for (const [division, keywords] of Object.entries(divisionKeywords)) {
        for (const keyword of keywords) {
            if (title.includes(keyword)) {
                if (!divisions.includes(division)) {
                    divisions.push(division);
                }
            }
        }
    }
    
    // Extract from categories
    for (const category of categories) {
        const catName = category.name.toLowerCase();
        for (const [division, keywords] of Object.entries(divisionKeywords)) {
            for (const keyword of keywords) {
                if (catName.includes(keyword)) {
                    if (!divisions.includes(division)) {
                        divisions.push(division);
                    }
                }
            }
        }
    }
    
    // Determine division type
    if (divisions.includes('masters')) {
        divisionType = 'masters';
        // Extract age groups
        const ageMatches = title.match(/(\d{2}\+)/g);
        if (ageMatches) {
            divisionsExtra = ageMatches.join(', ');
        }
    } else if (divisions.includes('natural')) {
        divisionType = 'natural';
    } else if (divisions.includes('open')) {
        divisionType = 'open';
    } else {
        divisionType = 'open'; // default
    }
    
    return {
        divisions: divisions.join(', '),
        divisionType,
        divisionsExtra
    };
}

// Function to determine competition level
function getCompetitionLevel(event) {
    const categories = event.categories || [];
    if (categories.length > 0) {
        const catName = categories[0].name.toLowerCase();
        if (catName.includes('pro')) return 'pro';
        if (catName.includes('qualifier')) return 'qualifier';
        if (catName.includes('regional')) return 'regional';
    }
    return 'unknown';
}

// Function to fetch all events from all years
async function fetchAllEvents() {
    const baseUrl = 'https://www.ifbbpro.com/wp-json/tribe/events/v1/events/';
    const allEvents = [];
    const seenIds = new Set();
    const startYear = 2015;
    const endYear = 2026;
    
    console.log('Fetching events from IFBB Pro API for all years...');
    
    for (let year = startYear; year <= endYear; year++) {
        let page = 1;
        let hasMorePages = true;
        while (hasMorePages) {
            try {
                const start_date = `${year}-01-01`;
                const end_date = `${year}-12-31`;
                const url = `${baseUrl}?page=${page}&per_page=100&start_date=${start_date}&end_date=${end_date}`;
                console.log(`Fetching year ${year}, page ${page}...`);
                const data = await makeRequest(url);
                if (data.events && data.events.length > 0) {
                    let newEvents = 0;
                    for (const event of data.events) {
                        if (!seenIds.has(event.id)) {
                            allEvents.push(event);
                            seenIds.add(event.id);
                            newEvents++;
                        }
                    }
                    console.log(`Found ${data.events.length} events on year ${year}, page ${page} (${newEvents} new)`);
                    if (data.next_rest_url) {
                        page++;
                    } else {
                        hasMorePages = false;
                    }
                } else {
                    hasMorePages = false;
                }
            } catch (error) {
                console.error(`Error fetching year ${year}, page ${page}:`, error.message);
                hasMorePages = false;
            }
        }
    }
    console.log(`Total unique events fetched: ${allEvents.length}`);
    return allEvents;
}

// Function to fetch and parse divisions from event web page
async function fetchDivisionsFromPage(eventUrl) {
    try {
        console.log(`Fetching divisions from: ${eventUrl}`);
        const { data: html } = await axios.get(eventUrl, { 
            timeout: 15000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });
        const $ = cheerio.load(html);
        
        let divisions = [];
        
        // Specifically target the .tribe-events-event-division class
        $('.tribe-events-event-division a').each((i, elem) => {
            const divisionText = $(elem).text().trim();
            if (divisionText && !divisions.includes(divisionText)) {
                divisions.push(divisionText);
            }
        });
        
        // If no divisions found in the specific class, try alternative selectors
        if (divisions.length === 0) {
            // Look for division information in various common locations
            const selectors = [
                '.tribe-events-single-event-description',
                '.entry-content',
                '.event-description',
                '.competition-details',
                '.divisions',
                '.categories',
                'ul li',
                'table td',
                'p',
                'div'
            ];
            
            // Common division keywords to look for
            const divisionKeywords = [
                'bikini', 'figure', 'wellness', 'physique', 'bodybuilding', 'fitness',
                'men', 'women', 'male', 'female', 'masters', 'classic', 'open',
                'pro', 'amateur', 'natural'
            ];
            
            for (const selector of selectors) {
                $(selector).each((i, elem) => {
                    const text = $(elem).text().toLowerCase();
                    
                    // Check if this element contains division-related content
                    const hasDivisionContent = divisionKeywords.some(keyword => 
                        text.includes(keyword)
                    );
                    
                    if (hasDivisionContent) {
                        // Split text into lines and look for division patterns
                        const lines = text.split(/\n|\r|\.|,|;|\(|\)/).map(line => line.trim());
                        
                        for (const line of lines) {
                            if (line.length > 2 && line.length < 100) { // Reasonable length for division names
                                // Look for patterns like "Bikini Division", "Men's Physique", etc.
                                const divisionMatch = line.match(/(bikini|figure|wellness|physique|bodybuilding|fitness|men|women|male|female|masters|classic|open|pro|amateur|natural)(\s+(division|class|category|competition|open|pro|amateur|masters|physique|bodybuilding|fitness|bikini|figure|wellness))?/i);
                                
                                if (divisionMatch) {
                                    const division = divisionMatch[0].trim();
                                    if (!divisions.includes(division)) {
                                        divisions.push(division);
                                    }
                                }
                            }
                        }
                    }
                });
            }
            
            // Also look for specific patterns in the entire page
            const fullText = $.text().toLowerCase();
            
            // Look for patterns like "Divisions: Bikini, Figure, Wellness"
            const divisionPatterns = [
                /divisions?[:\s]+([^.\n]+)/gi,
                /categories?[:\s]+([^.\n]+)/gi,
                /classes?[:\s]+([^.\n]+)/gi,
                /events?[:\s]+([^.\n]+)/gi
            ];
            
            for (const pattern of divisionPatterns) {
                const matches = fullText.match(pattern);
                if (matches) {
                    for (const match of matches) {
                        const divisionList = match.replace(/divisions?[:\s]+|categories?[:\s]+|classes?[:\s]+|events?[:\s]+/gi, '');
                        const divisionItems = divisionList.split(/[,&]/).map(item => item.trim());
                        
                        for (const item of divisionItems) {
                            if (divisionKeywords.some(keyword => item.includes(keyword))) {
                                if (!divisions.includes(item)) {
                                    divisions.push(item);
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Clean up and format divisions
        divisions = divisions
            .map(div => div.replace(/[^\w\s]/g, '').trim())
            .filter(div => div.length > 0)
            .map(div => div.charAt(0).toUpperCase() + div.slice(1).toLowerCase());
        
        // Remove duplicates
        divisions = [...new Set(divisions)];
        
        console.log(`Found divisions: ${divisions.join(', ')}`);
        return divisions.join(', ');
        
    } catch (error) {
        console.error(`Error fetching/parsing event page: ${eventUrl}`, error.message);
        return '';
    }
}

// Update processEvents to fetch divisions from the event page
async function processEvents(events) {
    const processed = [];
    let processedCount = 0;
    
    for (const event of events) {
        processedCount++;
        console.log(`Processing event ${processedCount}/${events.length}: ${event.title}`);
        
        const divisionInfo = extractDivisions(event); // fallback
        const competitionLevel = getCompetitionLevel(event);
        
        // Extract promoter information
        const organizer = event.organizer && event.organizer.length > 0 ? event.organizer[0] : {};
        
        // Format dates as date-only (YYYY-MM-DD)
        const formatDate = (dateString) => {
            if (!dateString) return '';
            return dateString.split(' ')[0];
        };
        
        // Fetch divisions from event page (primary source)
        let divisions = '';
        if (event.url) {
            divisions = await fetchDivisionsFromPage(event.url);
            // Add a small delay to be respectful to the server
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // Use page divisions if found, otherwise fall back to extracted divisions
        const finalDivisions = divisions || divisionInfo.divisions;
        
        processed.push({
            competition_name: event.title || '',
            venue_city: event.venue?.city || '',
            venue_country: event.venue?.country || '',
            divisions: finalDivisions,
            division_type: divisionInfo.divisionType,
            divisions_extra: divisionInfo.divisionsExtra,
            competition_level: competitionLevel,
            start_date: formatDate(event.start_date),
            end_date: formatDate(event.end_date),
            promoter_name: organizer.organizer || '',
            promoter_email: organizer.email || '',
            promoter_website: organizer.website || '',
            ifbbwebsite_link: event.url || ''
        });
    }
    return processed;
}

// Function to save data to CSV
function saveToCSV(data, filename) {
    const writer = csvWriter.createObjectCsvWriter({
        path: filename,
        header: [
            { id: 'competition_name', title: 'competition_name' },
            { id: 'venue_city', title: 'venue_city' },
            { id: 'venue_country', title: 'venue_country' },
            { id: 'divisions', title: 'divisions' },
            { id: 'division_type', title: 'division_type' },
            { id: 'divisions_extra', title: 'divisions_extra' },
            { id: 'competition_level', title: 'competition_level' },
            { id: 'start_date', title: 'start_date' },
            { id: 'end_date', title: 'end_date' },
            { id: 'promoter_name', title: 'promoter_name' },
            { id: 'promoter_email', title: 'promoter_email' },
            { id: 'promoter_website', title: 'promoter_website' },
            { id: 'ifbbwebsite_link', title: 'ifbbwebsite_link' }
        ]
    });
    
    return writer.writeRecords(data).then(() => {
        console.log(`Data saved to ${filename}`);
    });
}

// Function to test different API parameters
async function testAPI() {
    const baseUrl = 'https://www.ifbbpro.com/wp-json/tribe/events/v1/events/';
    
    console.log('Testing different API parameters...');
    
    // Test 1: Default (current behavior)
    try {
        const data1 = await makeRequest(`${baseUrl}?per_page=5`);
        console.log(`Test 1 (default): ${data1.events?.length || 0} events`);
        if (data1.events && data1.events.length > 0) {
            console.log('Sample event dates:', data1.events.map(e => e.start_date).slice(0, 3));
        }
    } catch (error) {
        console.log('Test 1 failed:', error.message);
    }
    
    // Test 2: With past date range
    try {
        const data2 = await makeRequest(`${baseUrl}?per_page=5&start_date=2020-01-01&end_date=2024-12-31`);
        console.log(`Test 2 (past dates): ${data2.events?.length || 0} events`);
        if (data2.events && data2.events.length > 0) {
            console.log('Sample event dates:', data2.events.map(e => e.start_date).slice(0, 3));
        }
    } catch (error) {
        console.log('Test 2 failed:', error.message);
    }
    
    // Test 3: With status=all
    try {
        const data3 = await makeRequest(`${baseUrl}?per_page=5&status=all`);
        console.log(`Test 3 (status=all): ${data3.events?.length || 0} events`);
        if (data3.events && data3.events.length > 0) {
            console.log('Sample event dates:', data3.events.map(e => e.start_date).slice(0, 3));
        }
    } catch (error) {
        console.log('Test 3 failed:', error.message);
    }
    
    // Test 4: With no status filter
    try {
        const data4 = await makeRequest(`${baseUrl}?per_page=5&status=`);
        console.log(`Test 4 (no status): ${data4.events?.length || 0} events`);
        if (data4.events && data4.events.length > 0) {
            console.log('Sample event dates:', data4.events.map(e => e.start_date).slice(0, 3));
        }
    } catch (error) {
        console.log('Test 4 failed:', error.message);
    }
}

// Function to examine API response structure
async function examineAPIStructure() {
    const baseUrl = 'https://www.ifbbpro.com/wp-json/tribe/events/v1/events/';
    
    console.log('Examining API response structure...');
    
    try {
        const data = await makeRequest(`${baseUrl}?per_page=1`);
        
        if (data.events && data.events.length > 0) {
            const event = data.events[0];
            console.log('\n=== EVENT STRUCTURE ===');
            console.log('Event ID:', event.id);
            console.log('Title:', event.title);
            console.log('Categories:', JSON.stringify(event.categories, null, 2));
            console.log('Tags:', JSON.stringify(event.tags, null, 2));
            console.log('All event keys:', Object.keys(event));
            
            // Check if there are any division-related fields
            const divisionRelatedKeys = Object.keys(event).filter(key => 
                key.toLowerCase().includes('division') || 
                key.toLowerCase().includes('category') ||
                key.toLowerCase().includes('class') ||
                key.toLowerCase().includes('type')
            );
            console.log('Division-related keys:', divisionRelatedKeys);
            
            // Check for any additional API endpoints
            if (event.rest_url) {
                console.log('Individual event URL:', event.rest_url);
                try {
                    const individualEvent = await makeRequest(event.rest_url);
                    console.log('Individual event structure:', Object.keys(individualEvent));
                    if (individualEvent.categories) {
                        console.log('Individual event categories:', JSON.stringify(individualEvent.categories, null, 2));
                    }
                } catch (error) {
                    console.log('Could not fetch individual event:', error.message);
                }
            }
        }
    } catch (error) {
        console.error('Error examining API structure:', error.message);
    }
}

// Function to examine categories endpoint
async function examineCategories() {
    console.log('\n=== EXAMINING CATEGORIES ENDPOINT ===');
    
    try {
        const categoriesUrl = 'https://www.ifbbpro.com/wp-json/tribe/events/v1/categories';
        const categories = await makeRequest(categoriesUrl);
        console.log('Available categories:', categories.categories?.map(cat => ({
            name: cat.name,
            slug: cat.slug,
            description: cat.description
        })) || 'No categories found');
    } catch (error) {
        console.log('Error fetching categories:', error.message);
    }
}

// Function to examine multiple events for better division data
async function examineMultipleEvents() {
    console.log('\n=== EXAMINING MULTIPLE EVENTS ===');
    
    try {
        const data = await makeRequest('https://www.ifbbpro.com/wp-json/tribe/events/v1/events/?per_page=5');
        
        if (data.events && data.events.length > 0) {
            for (let i = 0; i < Math.min(3, data.events.length); i++) {
                const event = data.events[i];
                console.log(`\nEvent ${i + 1}: ${event.title}`);
                console.log('Categories:', event.categories?.map(c => c.name).join(', ') || 'None');
                console.log('Tags:', event.tags?.map(t => t.name).join(', ') || 'None');
                
                // Check if there's more detailed info in the individual event
                try {
                    const individualEvent = await makeRequest(event.rest_url);
                    console.log('Individual event categories:', individualEvent.categories?.map(c => c.name).join(', ') || 'None');
                    console.log('Individual event tags:', individualEvent.tags?.map(t => t.name).join(', ') || 'None');
                    
                    // Check if there are any custom fields that might contain division info
                    if (individualEvent.custom_fields) {
                        console.log('Custom fields:', Object.keys(individualEvent.custom_fields));
                    }
                } catch (error) {
                    console.log('Could not fetch individual event details');
                }
            }
        }
    } catch (error) {
        console.log('Error examining multiple events:', error.message);
    }
}

// Main function
async function main() {
    try {
        // First examine the API structure to understand the data
        await examineAPIStructure();
        await examineCategories();
        await examineMultipleEvents();
        
        console.log('\n--- Starting main data fetch ---\n');
        
        // Fetch all events
        const events = await fetchAllEvents();
        console.log(`Fetched events: ${events.length}`);

        // Check for duplicate event IDs
        const ids = events.map(e => e.id);
        const uniqueIds = new Set(ids);
        if (uniqueIds.size !== ids.length) {
            console.log(`Duplicate event IDs found: ${ids.length - uniqueIds.size}`);
        } else {
            console.log('No duplicate event IDs found.');
        }

        // Process events
        const processedData = await processEvents(events);
        console.log(`Processed events: ${processedData.length}`);

        // Check for duplicate competition names in processed data
        const compNames = processedData.map(e => e.competition_name);
        const uniqueCompNames = new Set(compNames);
        if (uniqueCompNames.size !== compNames.length) {
            console.log(`Duplicate competition names in processed data: ${compNames.length - uniqueCompNames.size}`);
        } else {
            console.log('No duplicate competition names in processed data.');
        }

        // Save to CSV
        const filename = 'ifbb_events_2025.csv';
        await saveToCSV(processedData, filename);

        // Count lines in CSV (excluding header)
        const csvLines = fs.readFileSync(filename, 'utf-8').split('\n').filter(Boolean);
        console.log(`Written to CSV: ${csvLines.length - 1}`);

        console.log(`Successfully processed ${processedData.length} events`);
        console.log(`CSV file created: ${filename}`);

    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Run the script
main();
