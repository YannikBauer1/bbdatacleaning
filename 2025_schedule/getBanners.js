import fs from 'fs';
import https from 'https';
import csvWriter from 'csv-writer';
import * as cheerio from 'cheerio';
import axios from 'axios';

// Load configuration from JSON file
const config = JSON.parse(fs.readFileSync('./base_url.json', 'utf8'));
const BANNER_URL = config.banner_url;
const RESULTS_URL = config.results_url;

// Function to parse date range
function parseDateRange(dateText) {
    if (!dateText) return { start_date: null, end_date: null };
    
    // Remove extra whitespace and normalize
    dateText = dateText.trim();
    
    // Check if it's a date range (contains dash or hyphen)
    if (dateText.includes('-') || dateText.includes('–')) {
        const parts = dateText.split(/[-–]/).map(part => part.trim());
        if (parts.length === 2) {
            return {
                start_date: parts[0],
                end_date: parts[1]
            };
        }
    }
    
    // Single date
    return {
        start_date: dateText,
        end_date: dateText
    };
}

// Function to extract location information
function parseLocation(locationText) {
    if (!locationText) return { city: null, state: null, country: null };
    
    locationText = locationText.trim();
    
    // Split by comma and clean up
    const parts = locationText.split(',').map(part => part.trim());
    
    if (parts.length === 1) {
        // Single location - could be city, state, or country
        return { city: parts[0], state: null, country: null };
    } else if (parts.length === 2) {
        // City, State/Country
        return { city: parts[0], state: parts[1], country: null };
    } else if (parts.length >= 3) {
        // City, State, Country
        return { 
            city: parts[0], 
            state: parts[1], 
            country: parts.slice(2).join(', ')
        };
    }
    
    return { city: null, state: null, country: null };
}

// Function to extract divisions from HTML
function extractDivisions($) {
    const divisions = [];
    $('.tribe-events-event-division a').each((index, element) => {
        const divisionText = $(element).text().trim();
        if (divisionText) {
            divisions.push(divisionText);
        }
    });
    return divisions;
}

// Function to extract division type from HTML
function extractDivisionType($) {
    const divisionTypeElement = $('.tribe-events-event-division-type a');
    if (divisionTypeElement.length > 0) {
        return divisionTypeElement.text().trim();
    }
    return null;
}

// Function to extract competition level from HTML
function extractCompetitionLevel($) {
    const categoryElement = $('.tribe-events-event-categories a');
    if (categoryElement.length > 0) {
        return categoryElement.text().trim();
    }
    return null;
}

// Function to extract promoter information
function extractPromoterInfo($) {
    let promoterName = null;
    let promoterEmail = null;
    let promoterWebsite = null;
    
    // Extract promoter name from .tribe-organizer
    const promoterElement = $('.tribe-organizer');
    if (promoterElement.length > 0) {
        promoterName = promoterElement.text().trim();
    }
    
    // Extract promoter email from .tribe-organizer-email
    const emailElement = $('.tribe-organizer-email');
    if (emailElement.length > 0) {
        promoterEmail = emailElement.text().trim();
    }
    
    // Extract promoter website from .tribe-organizer-url a
    const websiteElement = $('.tribe-organizer-url a');
    if (websiteElement.length > 0) {
        promoterWebsite = websiteElement.attr('href');
    }
    
    // Fallback: Look for website in various possible locations
    if (!promoterWebsite) {
        $('p, div, span').each((index, element) => {
            const text = $(element).text().trim();
            const lowerText = text.toLowerCase();
            
            // Look for website
            if ((lowerText.includes('www.') || lowerText.includes('http')) && !promoterWebsite) {
                const urlMatch = text.match(/(https?:\/\/[^\s]+|www\.[^\s]+)/i);
                if (urlMatch) {
                    promoterWebsite = urlMatch[0];
                }
            }
        });
    }
    
    return { promoterName, promoterEmail, promoterWebsite };
}

// Function to extract date information from HTML
function extractDateInfo($) {
    let startDate = null;
    let endDate = null;
    
    // Extract start date from .tribe-events-start-date
    const startDateElement = $('.tribe-events-start-date');
    if (startDateElement.length > 0) {
        startDate = startDateElement.text().trim();
    }
    
    // Extract end date from .tribe-events-end-date
    const endDateElement = $('.tribe-events-end-date');
    if (endDateElement.length > 0) {
        endDate = endDateElement.text().trim();
        // If end date is the same as start date, set it to null to avoid duplication
        if (endDate === startDate) {
            endDate = null;
        }
    }
    
    return { startDate, endDate };
}

// Function to extract location information from HTML
function extractLocationInfo($) {
    let locationCity = null;
    let locationState = null;
    let locationCountry = null;
    
    // Extract from structured HTML elements
    const localityElement = $('.tribe-locality');
    if (localityElement.length > 0) {
        locationCity = localityElement.text().trim();
    }
    
    const regionElement = $('.tribe-region');
    if (regionElement.length > 0) {
        locationState = regionElement.text().trim();
    }
    
    const countryElement = $('.tribe-country-name');
    if (countryElement.length > 0) {
        locationCountry = countryElement.text().trim();
    }
    
    // Fallback: Extract venue name from .tribe-venue if city not found
    if (!locationCity) {
        const venueElement = $('.tribe-venue');
        if (venueElement.length > 0) {
            locationCity = venueElement.text().trim();
        }
    }
    
    // Fallback: Extract full address from .tribe-address if structured elements not found
    if (!locationCity || !locationState || !locationCountry) {
        const addressElement = $('.tribe-address');
        if (addressElement.length > 0) {
            const addressText = addressElement.text().trim();
            const locationInfo = parseLocation(addressText);
            locationCity = locationInfo.city || locationCity;
            locationState = locationInfo.state || locationState;
            locationCountry = locationInfo.country || locationCountry;
        }
    }
    
    return { locationCity, locationState, locationCountry };
}

// Function to extract description from HTML
function extractDescription($) {
    // Look for #Compdescription
    const descElement = $('#Compdescription');
    if (descElement.length > 0) {
        // Get all text inside, including table cells
        return descElement.text().replace(/\s+/g, ' ').trim();
    }
    return null;
}

// Function to scrape contest banners (existing function with source added)
async function scrapeCompetitionPage(url, competitionName) {
    try {
        console.log(`Scraping contest banner details for: ${competitionName}`);
        
        const response = await axios.get(url);
        const $ = cheerio.load(response.data);
        
        // Extract divisions
        const divisions = extractDivisions($);
        
        // Extract division type
        const divisionType = extractDivisionType($);
        
        // Extract competition level
        const competitionLevel = extractCompetitionLevel($);
        
        // Extract promoter information
        const promoterInfo = extractPromoterInfo($);
        
        // Extract date information
        const dateInfo = extractDateInfo($);
        
        // Extract location information
        const locationInfo = extractLocationInfo($);
        
        // Extract description
        const description = extractDescription($);
        
        return {
            competition_name: competitionName,
            start_date: dateInfo.startDate,
            end_date: dateInfo.endDate,
            location_city: locationInfo.locationCity,
            location_state: locationInfo.locationState,
            location_country: locationInfo.locationCountry,
            divisions: divisions,
            division_type: divisionType,
            competition_level: competitionLevel,
            promoter_name: promoterInfo.promoterName,
            promoter_email: promoterInfo.promoterEmail,
            promoter_website: promoterInfo.promoterWebsite,
            description: description,
            competition_url: url,
            source: 'contest_banners'
        };
        
    } catch (error) {
        console.error(`Error scraping competition page ${url}:`, error.message);
        // Return basic info if detailed scraping fails
        return {
            competition_name: competitionName,
            start_date: null,
            end_date: null,
            location_city: null,
            location_state: null,
            location_country: null,
            divisions: ['All Divisions'],
            division_type: null,
            competition_level: null,
            promoter_name: null,
            promoter_email: null,
            promoter_website: null,
            description: null,
            competition_url: url,
            source: 'contest_banners'
        };
    }
}

// Function to scrape results page (different structure from contest banners)
async function scrapeResultsPage(url, competitionName) {
    try {
        console.log(`Scraping results details for: ${competitionName}`);
        
        const response = await axios.get(url);
        const $ = cheerio.load(response.data);
        
        // Extract the same detailed information as contest banners
        // Extract divisions
        const divisions = extractDivisions($);
        
        // Extract division type
        const divisionType = extractDivisionType($);
        
        // Extract competition level
        const competitionLevel = extractCompetitionLevel($);
        
        // Extract promoter information
        const promoterInfo = extractPromoterInfo($);
        
        // Extract date information
        const dateInfo = extractDateInfo($);
        
        // Extract location information
        const locationInfo = extractLocationInfo($);
        
        // Extract description
        const description = extractDescription($);
        
        return {
            competition_name: competitionName,
            start_date: dateInfo.startDate,
            end_date: dateInfo.endDate,
            location_city: locationInfo.locationCity,
            location_state: locationInfo.locationState,
            location_country: locationInfo.locationCountry,
            divisions: divisions,
            division_type: divisionType,
            competition_level: competitionLevel,
            promoter_name: promoterInfo.promoterName,
            promoter_email: promoterInfo.promoterEmail,
            promoter_website: promoterInfo.promoterWebsite,
            description: description,
            competition_url: url,
            source: 'results'
        };
        
    } catch (error) {
        console.error(`Error scraping results page ${url}:`, error.message);
        // Return basic info if detailed scraping fails
        return {
            competition_name: competitionName,
            start_date: null,
            end_date: null,
            location_city: null,
            location_state: null,
            location_country: null,
            divisions: ['All Divisions'],
            division_type: null,
            competition_level: 'Pro',
            promoter_name: null,
            promoter_email: null,
            promoter_website: null,
            description: null,
            competition_url: url,
            source: 'results'
        };
    }
}

// Function to scrape results pages
async function scrapeResultsPages() {
    try {
        console.log('Starting to scrape IFBB Pro results pages...');
        
        const competitions = [];
        const competitionLinks = [];
        let pageNum = 1;
        let hasMorePages = true;
        
        // Loop through all results pages
        while (hasMorePages) {
            const url = pageNum === 1 
                ? RESULTS_URL
                : `${RESULTS_URL}page/${pageNum}/`;
            
            console.log(`Scraping results page ${pageNum}: ${url}`);
            
            try {
                const response = await axios.get(url);
                const $ = cheerio.load(response.data);
                
                let pageCompetitions = 0;
                
                // Find all competition cards on this page - similar structure to contest banners
                $('li.event-container-main-large').each((index, element) => {
                    const card = $(element);
                    // Competition link
                    const link = card.find('a.fusion-column-anchor').attr('href');
                    // Competition name
                    const name = card.find('h2.fusion-title-heading').text().trim();
                    // Dates
                    const startDate = card.find('.tribe-event-date-start').text().trim();
                    const endDate = card.find('.tribe-event-date-end').text().trim() || startDate;
                    // Location (might be in different elements)
                    const locationCity = card.find('.event-location, .fusion-meta-tb').text().trim();
                    // Competition level
                    const competitionLevel = card.find('.fusion-tb-categories a').text().trim();

                    if (link && name) {
                        competitionLinks.push({
                            name,
                            url: link,
                            startDate,
                            endDate,
                            locationCity,
                            competitionLevel
                        });
                        pageCompetitions++;
                        console.log(`Found results competition: ${name} -> ${link}`);
                    }
                });
                
                // Also try alternative selectors for results page structure
                $('li.fusion-layout-column a.fusion-column-anchor').each((index, element) => {
                    const link = $(element).attr('href');
                    const name = $(element).closest('li').find('h2.fusion-title-heading').text().trim();
                    
                    if (link && name && link.includes('ifbbpro.com') && name.length > 5) {
                        // Check if we already have this competition
                        const exists = competitionLinks.some(comp => comp.name === name || comp.url === link);
                        if (!exists) {
                            const card = $(element).closest('li');
                            const startDate = card.find('.tribe-event-date-start').text().trim();
                            const endDate = card.find('.tribe-event-date-end').text().trim() || startDate;
                            const locationCity = card.find('.event-location, .fusion-meta-tb').text().trim();
                            const competitionLevel = card.find('.fusion-tb-categories a').text().trim();
                            
                            competitionLinks.push({
                                name,
                                url: link,
                                startDate,
                                endDate,
                                locationCity,
                                competitionLevel
                            });
                            pageCompetitions++;
                            console.log(`Found results competition (alternative): ${name} -> ${link}`);
                        }
                    }
                });
                
                console.log(`Results page ${pageNum}: Found ${pageCompetitions} competitions`);
                
                // If no competitions found on this page, we've reached the end
                if (pageCompetitions === 0) {
                    hasMorePages = false;
                    console.log(`No more results competitions found. Stopping at page ${pageNum - 1}`);
                } else {
                    pageNum++;
                    // Add delay between pages to be respectful to the server
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
                
            } catch (error) {
                console.error(`Error scraping results page ${pageNum}:`, error.message);
                hasMorePages = false;
            }
        }
        
        console.log(`\nTotal results found: ${competitionLinks.length} competition links across ${pageNum - 1} pages`);
        
        // Now scrape each individual results page
        for (let i = 0; i < competitionLinks.length; i++) {
            const { name, url, startDate, endDate, locationCity, competitionLevel } = competitionLinks[i];
            console.log(`Processing results ${i + 1}/${competitionLinks.length}: ${name}`);
            
            // Add delay to be respectful to the server
            if (i > 0) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            const competitionDetails = await scrapeResultsPage(url, name);
            // Overwrite with info from the card if not found on detail page
            competitionDetails.start_date = competitionDetails.start_date || startDate;
            competitionDetails.end_date = competitionDetails.end_date || (endDate !== startDate ? endDate : null);
            competitionDetails.location_city = competitionDetails.location_city || locationCity;
            competitionDetails.competition_level = competitionDetails.competition_level || competitionLevel;
            competitions.push(competitionDetails);
        }
        
        return competitions;
        
    } catch (error) {
        console.error('Error scraping results pages:', error);
        throw error;
    }
}

// Function to scrape contest banners pages
async function scrapeContestBannersWithDetails() {
    try {
        console.log('Starting to scrape IFBB Pro contest banners with detailed information...');
        
        const competitions = [];
        const competitionLinks = [];
        let pageNum = 1;
        let hasMorePages = true;
        
        // Loop through all contest banner pages
        while (hasMorePages) {
            const url = pageNum === 1 
                ? BANNER_URL
                : `${BANNER_URL}page/${pageNum}/`;
            
            console.log(`Scraping contest banner page ${pageNum}: ${url}`);
            
            try {
                const response = await axios.get(url);
                const $ = cheerio.load(response.data);
                
                let pageCompetitions = 0;
                
                // Find all competition cards on this page
                $('li.contest-card-container').each((index, element) => {
                    const card = $(element);
                    // Competition link
                    const link = card.find('a.fusion-column-anchor').attr('href');
                    // Competition name
                    const name = card.find('h2.fusion-title-heading').text().trim();
                    // Dates
                    const startDate = card.find('.tribe-event-date-start').text().trim();
                    const endDate = card.find('.tribe-event-date-end').text().trim() || startDate;
                    // Location
                    const locationCity = card.find('.event-location').text().trim();
                    // Competition level
                    const competitionLevel = card.find('.fusion-tb-categories a').text().trim();

                    if (link && name) {
                        competitionLinks.push({
                            name,
                            url: link,
                            startDate,
                            endDate,
                            locationCity,
                            competitionLevel
                        });
                        pageCompetitions++;
                        console.log(`Found contest banner competition: ${name} -> ${link}`);
                    }
                });
                
                console.log(`Contest banner page ${pageNum}: Found ${pageCompetitions} competitions`);
                
                // If no competitions found on this page, we've reached the end
                if (pageCompetitions === 0) {
                    hasMorePages = false;
                    console.log(`No more contest banner competitions found. Stopping at page ${pageNum - 1}`);
                } else {
                    pageNum++;
                    // Add delay between pages to be respectful to the server
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
                
            } catch (error) {
                console.error(`Error scraping contest banner page ${pageNum}:`, error.message);
                hasMorePages = false;
            }
        }
        
        console.log(`\nTotal contest banners found: ${competitionLinks.length} competition links across ${pageNum - 1} pages`);
        
        // Now scrape each individual competition page
        for (let i = 0; i < competitionLinks.length; i++) {
            const { name, url, startDate, endDate, locationCity, competitionLevel } = competitionLinks[i];
            console.log(`Processing contest banner ${i + 1}/${competitionLinks.length}: ${name}`);
            
            // Add delay to be respectful to the server
            if (i > 0) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            // Pass the scraped info as defaults to the detail scraper
            const competitionDetails = await scrapeCompetitionPage(url, name);
            // Overwrite with info from the card if not found on detail page
            competitionDetails.start_date = competitionDetails.start_date || startDate;
            competitionDetails.end_date = competitionDetails.end_date || (endDate !== startDate ? endDate : null);
            competitionDetails.location_city = competitionDetails.location_city || locationCity;
            competitionDetails.competition_level = competitionDetails.competition_level || competitionLevel;
            competitions.push(competitionDetails);
        }
        
        return competitions;
        
    } catch (error) {
        console.error('Error scraping contest banners:', error);
        throw error;
    }
}

// Main scraping function that gets competition links from both sources
async function scrapeAllCompetitionsWithDetails() {
    try {
        console.log('Starting to scrape IFBB Pro competitions from both sources...');
        
        const allCompetitions = [];
        
        // 1. Scrape contest banners
        console.log('\n=== SCRAPING CONTEST BANNERS ===');
        const bannerCompetitions = await scrapeContestBannersWithDetails();
        allCompetitions.push(...bannerCompetitions);
        
        // 2. Scrape results pages
        console.log('\n=== SCRAPING RESULTS PAGES ===');
        const resultsCompetitions = await scrapeResultsPages();
        allCompetitions.push(...resultsCompetitions);
        
        console.log(`\nTotal competitions from both sources: ${allCompetitions.length}`);
        console.log(`- Contest banners: ${bannerCompetitions.length}`);
        console.log(`- Results pages: ${resultsCompetitions.length}`);
        
        // Create CSV writer
        const createCsvWriter = csvWriter.createObjectCsvWriter;
        const csvWriterInstance = createCsvWriter({
            path: 'ifbb_pro_competitions_2025_combined.csv',
            header: [
                { id: 'competition_name', title: 'Competition Name' },
                { id: 'start_date', title: 'Start Date' },
                { id: 'end_date', title: 'End Date' },
                { id: 'location_city', title: 'Location City' },
                { id: 'location_state', title: 'Location State' },
                { id: 'location_country', title: 'Location Country' },
                { id: 'divisions', title: 'Divisions' },
                { id: 'division_type', title: 'Division Type' },
                { id: 'competition_level', title: 'Competition Level' },
                { id: 'promoter_name', title: 'Promoter Name' },
                { id: 'promoter_email', title: 'Promoter Email' },
                { id: 'promoter_website', title: 'Promoter Website' },
                { id: 'description', title: 'Description' },
                { id: 'competition_url', title: 'Competition URL' },
                { id: 'source', title: 'Source' }
            ]
        });
        
        // Write to CSV
        await csvWriterInstance.writeRecords(allCompetitions);
        console.log('Data saved to ifbb_pro_competitions_2025_combined.csv');
        
        // Print summary
        console.log('\nCompetitions found with details:');
        allCompetitions.forEach((comp, index) => {
            console.log(`${index + 1}. ${comp.competition_name} [${comp.source}]`);
            console.log(`   Date: ${comp.start_date}${comp.end_date !== comp.start_date ? ` - ${comp.end_date}` : ''}`);
            console.log(`   Location: ${comp.location_city}${comp.location_state ? `, ${comp.location_state}` : ''}${comp.location_country ? `, ${comp.location_country}` : ''}`);
            console.log(`   Divisions: ${comp.divisions.join(', ')}`);
            console.log(`   Type: ${comp.division_type} | Level: ${comp.competition_level}`);
            if (comp.promoter_name) {
                console.log(`   Promoter: ${comp.promoter_name}`);
            }
            console.log('');
        });
        
        return allCompetitions;
        
    } catch (error) {
        console.error('Error scraping all competitions:', error);
        throw error;
    }
}

// Run the scraper
async function main() {
    try {
        console.log('Starting IFBB Pro competition scraping from both sources...\n');
        
        // Scrape all pages with detailed information from both sources
        const results = await scrapeAllCompetitionsWithDetails();
        
        console.log('\nScraping completed successfully!');
        console.log(`Total competitions found: ${results.length}`);
        
    } catch (error) {
        console.error('Failed to scrape competitions:', error);
    }
}

// Export functions for potential reuse
export { scrapeAllCompetitionsWithDetails, main };

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

