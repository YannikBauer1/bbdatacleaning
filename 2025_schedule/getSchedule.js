import fs from 'fs';
import axios from 'axios';
import * as cheerio from 'cheerio';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Function to extract divisions from competition name and description
function extractDivisions(competitionName, description) {
    const divisions = [];
    const nameLower = competitionName.toLowerCase();
    const descLower = description.toLowerCase();
    
    // Define division keywords and their corresponding full names
    const divisionMap = {
        'men\'s bodybuilding': 'Men\'s Bodybuilding',
        'men\'s 212 bodybuilding': 'Men\'s 212 Bodybuilding',
        'men\'s classic physique': 'Men\'s Classic Physique',
        'men\'s physique': 'Men\'s Physique',
        'men\'s wheelchair': 'Men\'s Wheelchair',
        'women\'s bodybuilding': 'Women\'s Bodybuilding',
        'women\'s fitness': 'Women\'s Fitness',
        'women\'s figure': 'Women\'s Figure',
        'women\'s bikini': 'Women\'s Bikini',
        'women\'s physique': 'Women\'s Physique',
        'women\'s wellness': 'Women\'s Wellness',
        'bikini': 'Women\'s Bikini',
        'figure': 'Women\'s Figure',
        'fitness': 'Women\'s Fitness',
        'wellness': 'Women\'s Wellness',
        'bodybuilding': 'Men\'s Bodybuilding',
        'classic physique': 'Men\'s Classic Physique',
        'physique': 'Men\'s Physique',
        '212': 'Men\'s 212 Bodybuilding',
        'wheelchair': 'Men\'s Wheelchair'
    };
    
    // Check competition name for division indicators
    for (const [keyword, division] of Object.entries(divisionMap)) {
        if (nameLower.includes(keyword)) {
            divisions.push(division);
        }
    }
    
    // Check description for division indicators
    for (const [keyword, division] of Object.entries(divisionMap)) {
        if (descLower.includes(keyword)) {
            divisions.push(division);
        }
    }
    
    // If no specific divisions found, add common divisions based on competition type
    if (divisions.length === 0) {
        if (nameLower.includes('natural')) {
            // Natural competitions typically have all divisions
            divisions.push('Men\'s Bodybuilding', 'Men\'s Classic Physique', 'Men\'s Physique', 
                         'Women\'s Bodybuilding', 'Women\'s Figure', 'Women\'s Bikini', 'Women\'s Wellness');
        } else if (nameLower.includes('masters')) {
            // Masters competitions typically have all divisions
            divisions.push('Men\'s Bodybuilding', 'Men\'s Classic Physique', 'Men\'s Physique', 
                         'Women\'s Bodybuilding', 'Women\'s Figure', 'Women\'s Bikini', 'Women\'s Wellness');
        } else {
            // Standard IFBB Pro competitions typically have all divisions
            divisions.push('Men\'s Bodybuilding', 'Men\'s 212 Bodybuilding', 'Men\'s Classic Physique', 'Men\'s Physique', 
                         'Women\'s Bodybuilding', 'Women\'s Figure', 'Women\'s Bikini', 'Women\'s Wellness');
        }
    }
    
    // Remove duplicates and return
    return [...new Set(divisions)].join(', ');
}

// Function to clean competition name and extract description
function cleanCompetitionName(competitionName) {
    // Remove common suffixes and move them to description
    const suffixes = [
        'OPEN',
        'MASTERS 40/50/60/70',
        'MASTERS 40/45/50/55/60',
        'MASTERS 35/40/45/50/55/60/70',
        'MASTERS 40/50',
        'MASTERS 40',
        'NATURAL OPEN',
        'NATURAL OPEN + NATURAL MASTERS 35/40/45/50/60/70',
        'NATURAL OPEN + MASTERS 40',
        'OPEN + MASTERS 40',
        'OPEN + MASTERS 40/45/50/55/60',
        'OPEN + MASTERS 35/40/50',
        'OPEN + MASTERS 40/50/60/70',
        'OPEN + MASTERS 35/40/45/50/55/60',
        'OPEN + MASTERS 40/50',
        'OPEN + MASTERS 35/40/45/50/55/60/70'
    ];
    
    let cleanName = competitionName;
    let description = '';
    
    // Find and remove suffixes
    for (const suffix of suffixes) {
        if (competitionName.includes(suffix)) {
            cleanName = competitionName.replace(suffix, '').trim();
            description = suffix;
            break;
        }
    }
    
    return { cleanName, description };
}

// Function to extract divisions from competition page using table headers
async function extractDivisionsFromPage(competitionUrl) {
    if (!competitionUrl) return '';
    
    try {
        const response = await axios.get(competitionUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout: 10000
        });
        
        const $ = cheerio.load(response.data);
        const divisions = [];
        
        // Look for division information in h3 elements with table-title class
        $('h3.table-title').each((i, elem) => {
            const text = $(elem).text().trim();
            if (text) {
                // Clean up the division name
                let division = text.replace(/&#8217;/g, "'"); // Fix HTML entities
                division = division.replace(/&#8211;/g, "-"); // Fix HTML entities
                
                // Map common variations to standard names
                const divisionMap = {
                    'MEN\'S BODYBUILDING': 'Men\'s Bodybuilding',
                    'MEN\'S 212 BODYBUILDING': 'Men\'s 212 Bodybuilding',
                    'MEN\'S CLASSIC PHYSIQUE': 'Men\'s Classic Physique',
                    'MEN\'S PHYSIQUE': 'Men\'s Physique',
                    'MEN\'S WHEELCHAIR': 'Men\'s Wheelchair',
                    'WOMEN\'S BODYBUILDING': 'Women\'s Bodybuilding',
                    'WOMEN\'S FITNESS': 'Women\'s Fitness',
                    'WOMEN\'S FIGURE': 'Women\'s Figure',
                    'WOMEN\'S BIKINI': 'Women\'s Bikini',
                    'WOMEN\'S PHYSIQUE': 'Women\'s Physique',
                    'WOMEN\'S WELLNESS': 'Women\'s Wellness'
                };
                
                if (divisionMap[division]) {
                    divisions.push(divisionMap[division]);
                } else if (division && !divisions.includes(division)) {
                    // If not in map but looks like a division, add it
                    if (division.includes('BODYBUILDING') || division.includes('PHYSIQUE') || 
                        division.includes('FITNESS') || division.includes('FIGURE') || 
                        division.includes('BIKINI') || division.includes('WELLNESS') ||
                        division.includes('WHEELCHAIR')) {
                        divisions.push(division);
                    }
                }
            }
        });
        
        // Also look for division information in table headers (className cells) as fallback
        $('.className').each((i, elem) => {
            const text = $(elem).text().trim();
            if (text) {
                // Extract division from text like "MEN'S BODYBUILDING – OPEN"
                const divisionMatch = text.match(/^([^–]+)/);
                if (divisionMatch) {
                    let division = divisionMatch[1].trim();
                    
                    // Clean up the division name
                    division = division.replace(/&#8217;/g, "'"); // Fix HTML entities
                    division = division.replace(/&#8211;/g, "-"); // Fix HTML entities
                    
                    // Map common variations to standard names
                    const divisionMap = {
                        'MEN\'S BODYBUILDING': 'Men\'s Bodybuilding',
                        'MEN\'S 212 BODYBUILDING': 'Men\'s 212 Bodybuilding',
                        'MEN\'S CLASSIC PHYSIQUE': 'Men\'s Classic Physique',
                        'MEN\'S PHYSIQUE': 'Men\'s Physique',
                        'MEN\'S WHEELCHAIR': 'Men\'s Wheelchair',
                        'WOMEN\'S BODYBUILDING': 'Women\'s Bodybuilding',
                        'WOMEN\'S FITNESS': 'Women\'s Fitness',
                        'WOMEN\'S FIGURE': 'Women\'s Figure',
                        'WOMEN\'S BIKINI': 'Women\'s Bikini',
                        'WOMEN\'S PHYSIQUE': 'Women\'s Physique',
                        'WOMEN\'S WELLNESS': 'Women\'s Wellness'
                    };
                    
                    if (divisionMap[division] && !divisions.includes(divisionMap[division])) {
                        divisions.push(divisionMap[division]);
                    } else if (division && !divisions.includes(division)) {
                        // If not in map but looks like a division, add it
                        if (division.includes('BODYBUILDING') || division.includes('PHYSIQUE') || 
                            division.includes('FITNESS') || division.includes('FIGURE') || 
                            division.includes('BIKINI') || division.includes('WELLNESS') ||
                            division.includes('WHEELCHAIR')) {
                            divisions.push(division);
                        }
                    }
                }
            }
        });
        
        // Also look for division information in other common patterns as additional fallback
        $('h1, h2, h3, h4, h5, h6, p, li').each((i, elem) => {
            const text = $(elem).text().toLowerCase();
            const divisionKeywords = [
                'men\'s bodybuilding',
                'men\'s 212 bodybuilding', 
                'men\'s classic physique',
                'men\'s physique',
                'men\'s wheelchair',
                'women\'s bodybuilding',
                'women\'s fitness',
                'women\'s figure',
                'women\'s bikini',
                'women\'s physique',
                'women\'s wellness'
            ];
            
            const divisionMap = {
                'men\'s bodybuilding': 'Men\'s Bodybuilding',
                'men\'s 212 bodybuilding': 'Men\'s 212 Bodybuilding',
                'men\'s classic physique': 'Men\'s Classic Physique',
                'men\'s physique': 'Men\'s Physique',
                'men\'s wheelchair': 'Men\'s Wheelchair',
                'women\'s bodybuilding': 'Women\'s Bodybuilding',
                'women\'s fitness': 'Women\'s Fitness',
                'women\'s figure': 'Women\'s Figure',
                'women\'s bikini': 'Women\'s Bikini',
                'women\'s physique': 'Women\'s Physique',
                'women\'s wellness': 'Women\'s Wellness'
            };
            
            divisionKeywords.forEach(keyword => {
                if (text.includes(keyword) && !divisions.includes(divisionMap[keyword])) {
                    divisions.push(divisionMap[keyword]);
                }
            });
        });
        
        return [...new Set(divisions)].join(', ');
        
    } catch (error) {
        console.log(`Error fetching divisions from ${competitionUrl}: ${error.message}`);
        return '';
    }
}

async function scrapeIFBBSchedule() {
    try {
        console.log('Fetching IFBB Pro schedule page...');
        
        const response = await axios.get('https://www.ifbbpro.com/schedule/', {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });
        
        const $ = cheerio.load(response.data);
        const competitions = [];
        
        console.log('Extracting competition data...');
        
        // Find all tables on the page
        $('table').each((tableIndex, table) => {
            const $table = $(table);
            
            $table.find('tr').each((rowIndex, row) => {
                // Skip header rows
                if (rowIndex === 0) return;
                
                const $row = $(row);
                const cells = $row.find('td');
                
                if (cells.length >= 4) {
                    const originalCompetitionName = $(cells[0]).text().trim();
                    const date = $(cells[1]).text().trim();
                    const venue = $(cells[2]).text().trim();
                    const promoter = $(cells[3]).text().trim();
                    
                    // Extract competition URL if available
                    const competitionLink = $(cells[0]).find('a').attr('href') || '';
                    
                    if (originalCompetitionName && date) {
                        // Clean competition name and extract description
                        const { cleanName, description } = cleanCompetitionName(originalCompetitionName);
                        
                        // Parse date range
                        let startDate = '';
                        let endDate = '';
                        
                        if (date.includes('-')) {
                            const dateParts = date.split('-').map(d => d.trim());
                            startDate = dateParts[0] || '';
                            endDate = dateParts[1] || '';
                        } else {
                            startDate = date;
                            endDate = '';
                        }
                        
                        // Parse venue (city, state, country)
                        let locationCity = '';
                        let locationState = '';
                        let locationCountry = '';
                        
                        if (venue) {
                            const venueParts = venue.split(',').map(v => v.trim());
                            if (venueParts.length >= 3) {
                                locationCity = venueParts[0] || '';
                                locationState = venueParts[1] || '';
                                locationCountry = venueParts[2] || '';
                            } else if (venueParts.length === 2) {
                                locationCity = venueParts[0] || '';
                                locationState = venueParts[1] || '';
                            } else {
                                locationCity = venue;
                            }
                        }
                        
                        // Extract promoter email if available
                        const promoterEmail = $(cells[3]).find('a[href^="mailto:"]').attr('href')?.replace('mailto:', '') || '';
                        
                        // Determine division type from competition name
                        let divisionType = '';
                        let competitionLevel = 'IFBB Pro';
                        
                        // Check for division indicators in the name
                        const nameLower = cleanName.toLowerCase();
                        if (nameLower.includes('natural')) {
                            divisionType = 'Natural';
                        } else if (nameLower.includes('masters')) {
                            divisionType = 'Masters';
                        } else {
                            divisionType = 'Open';
                        }
                        
                        competitions.push({
                            'Competition Name': cleanName,
                            'Start Date': startDate,
                            'End Date': endDate,
                            'Location City': locationCity,
                            'Location State': locationState,
                            'Location Country': locationCountry,
                            'Divisions': '',
                            'Division Type': divisionType,
                            'Competition Level': competitionLevel,
                            'Promoter Name': promoter,
                            'Promoter Email': promoterEmail,
                            'Promoter Website': '',
                            'Description': description,
                            'Competition URL': competitionLink,
                            'Source': 'IFBB Pro Schedule'
                        });
                    }
                }
            });
        });
        
        console.log(`Found ${competitions.length} competitions`);
        console.log('Extracting division information from individual competition pages...');
        
        // Extract divisions from individual competition pages
        for (let i = 0; i < competitions.length; i++) {
            const competition = competitions[i];
            console.log(`Processing ${i + 1}/${competitions.length}: ${competition['Competition Name']}`);
            
            const divisions = await extractDivisionsFromPage(competition['Competition URL']);
            competition['Divisions'] = divisions;
            
            // Add a small delay to be respectful to the server
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // Convert to CSV
        const csvHeader = 'Competition Name,Start Date,End Date,Location City,Location State,Location Country,Divisions,Division Type,Competition Level,Promoter Name,Promoter Email,Promoter Website,Description,Competition URL,Source\n';
        
        const csvContent = competitions.map(comp => {
            return [
                `"${comp['Competition Name']}"`,
                `"${comp['Start Date']}"`,
                `"${comp['End Date']}"`,
                `"${comp['Location City']}"`,
                `"${comp['Location State']}"`,
                `"${comp['Location Country']}"`,
                `"${comp['Divisions']}"`,
                `"${comp['Division Type']}"`,
                `"${comp['Competition Level']}"`,
                `"${comp['Promoter Name']}"`,
                `"${comp['Promoter Email']}"`,
                `"${comp['Promoter Website']}"`,
                `"${comp['Description']}"`,
                `"${comp['Competition URL']}"`,
                `"${comp['Source']}"`
            ].join(',');
        }).join('\n');
        
        const fullCsv = csvHeader + csvContent;
        
        // Write to file
        const outputPath = path.join(__dirname, 'ifbb_pro_competitions_2025_schedule.csv');
        fs.writeFileSync(outputPath, fullCsv);
        
        console.log(`Data saved to ${outputPath}`);
        console.log(`Total competitions scraped: ${competitions.length}`);
        
        return competitions;
        
    } catch (error) {
        console.error('Error scraping data:', error);
        throw error;
    }
}

// Run the scraper
scrapeIFBBSchedule()
    .then(() => {
        console.log('Scraping completed successfully!');
        process.exit(0);
    })
    .catch(error => {
        console.error('Scraping failed:', error);
        process.exit(1);
    });
