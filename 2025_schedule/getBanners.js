import axios from 'axios';
import * as cheerio from 'cheerio';
import { createObjectCsvWriter } from 'csv-writer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class IFBBProScraper {
    constructor() {
        this.baseUrl = 'https://www.ifbbpro.com/contest-banners';
        this.competitions = [];
    }

    async getTotalPages() {
        try {
            console.log('Getting total pages...');
            const response = await axios.get(this.baseUrl);
            const $ = cheerio.load(response.data);
            
            // Look for pagination to determine total pages
            const pagination = $('.pagination');
            if (pagination.length > 0) {
                const links = pagination.find('a');
                const pageNumbers = [];
                links.each((i, link) => {
                    const text = $(link).text().trim();
                    if (/^\d+$/.test(text)) {
                        pageNumbers.push(parseInt(text));
                    }
                });
                const maxPage = Math.max(...pageNumbers);
                console.log(`Found ${maxPage} pages of contest banners`);
                return maxPage;
            }
            
            console.log('No pagination found, defaulting to 1 page');
            return 1;
        } catch (error) {
            console.error('Error getting total pages:', error.message);
            return 1;
        }
    }

    async scrapeBannerLinks(pageNum = 1) {
        const url = pageNum === 1 ? this.baseUrl : `${this.baseUrl}/page/${pageNum}/`;
        
        try {
            console.log(`Scraping page ${pageNum}: ${url}`);
            const response = await axios.get(url);
            const $ = cheerio.load(response.data);
            
            // Extract all contest banner links
            const bannerLinks = [];
            $('h2').each((i, heading) => {
                const link = $(heading).find('a');
                if (link.length > 0) {
                    bannerLinks.push({
                        title: $(heading).text().trim(),
                        url: link.attr('href')
                    });
                }
            });
            
            console.log(`Found ${bannerLinks.length} contest banners on page ${pageNum}`);
            return bannerLinks;
            
        } catch (error) {
            console.error(`Error scraping page ${pageNum}:`, error.message);
            return [];
        }
    }

    async scrapeContestDetails(contestUrl, contestTitle) {
        try {
            console.log(`Scraping contest details: ${contestTitle}`);
            const response = await axios.get(contestUrl);
            const $ = cheerio.load(response.data);
            
            const contestData = {
                competition_name: contestTitle,
                start_date: '',
                end_date: '',
                competition_level: 'IFBB Pro',
                divisions: '',
                division_types: '',
                division_extra: '',
                promoter: '',
                promoter_email: '',
                promoter_website: '',
                location: ''
            };
            
            // Extract content from the page
            const content = $('.entry-content');
            if (content.length > 0) {
                const text = content.text();
                
                // Extract dates (look for common date patterns)
                const datePatterns = [
                    /(\w+ \d{1,2},? \d{4})/g,
                    /(\d{1,2}\/\d{1,2}\/\d{4})/g,
                    /(\d{1,2}-\d{1,2}-\d{4})/g,
                    /(\w+ \d{1,2}-\d{1,2},? \d{4})/g
                ];
                
                for (const pattern of datePatterns) {
                    const matches = text.match(pattern);
                    if (matches) {
                        if (matches.length >= 2) {
                            contestData.start_date = matches[0];
                            contestData.end_date = matches[1];
                        } else {
                            contestData.start_date = matches[0];
                        }
                        break;
                    }
                }
                
                // Extract location (look for common location patterns)
                const locationPatterns = [
                    /(?:in|at|location:?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/gi,
                    /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*[A-Z]{2}/g
                ];
                
                for (const pattern of locationPatterns) {
                    const matches = text.match(pattern);
                    if (matches && matches.length > 0) {
                        contestData.location = matches[0].replace(/^(?:in|at|location:?)\s+/i, '');
                        break;
                    }
                }
                
                // Extract divisions
                const divisionKeywords = [
                    'Men\'s Open Bodybuilding', 'Men\'s 212 Bodybuilding', 'Men\'s Classic Physique',
                    'Men\'s Physique', 'Men\'s Wheelchair', 'Women\'s Bodybuilding', 'Women\'s Fitness',
                    'Women\'s Figure', 'Women\'s Bikini', 'Women\'s Physique', 'Women\'s Wellness',
                    'Masters', 'Figure', 'Bikini', 'Physique', 'Bodybuilding', 'Fitness', 'Wellness'
                ];
                
                const foundDivisions = [];
                for (const keyword of divisionKeywords) {
                    if (text.toLowerCase().includes(keyword.toLowerCase())) {
                        foundDivisions.push(keyword);
                    }
                }
                
                if (foundDivisions.length > 0) {
                    contestData.divisions = foundDivisions.join(', ');
                    contestData.division_types = foundDivisions.join(', ');
                }
                
                // Extract promoter information
                const promoterPatterns = [
                    /promoter:?\s*([^\n\r]+)/gi,
                    /contact:?\s*([^\n\r]+)/gi,
                    /organizer:?\s*([^\n\r]+)/gi
                ];
                
                for (const pattern of promoterPatterns) {
                    const matches = text.match(pattern);
                    if (matches && matches.length > 0) {
                        contestData.promoter = matches[0].replace(/^(?:promoter|contact|organizer):?\s*/i, '');
                        break;
                    }
                }
                
                // Extract email
                const emailPattern = /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
                const emailMatches = text.match(emailPattern);
                if (emailMatches && emailMatches.length > 0) {
                    contestData.promoter_email = emailMatches[0];
                }
                
                // Extract website
                const websitePattern = /(https?:\/\/[^\s]+)/g;
                const websiteMatches = text.match(websitePattern);
                if (websiteMatches && websiteMatches.length > 0) {
                    contestData.promoter_website = websiteMatches[0];
                }
                
                // Extract division extra (Masters categories)
                const mastersPattern = /(Masters\s+(?:Figure|Bikini|Physique|Bodybuilding)\s+\d+(?:\/\d+)*)/gi;
                const mastersMatches = text.match(mastersPattern);
                if (mastersMatches && mastersMatches.length > 0) {
                    contestData.division_extra = mastersMatches.join(', ');
                }
            }
            
            return contestData;
            
        } catch (error) {
            console.error(`Error scraping contest details for ${contestTitle}:`, error.message);
            return {
                competition_name: contestTitle,
                start_date: '',
                end_date: '',
                competition_level: 'IFBB Pro',
                divisions: '',
                division_types: '',
                division_extra: '',
                promoter: '',
                promoter_email: '',
                promoter_website: '',
                location: ''
            };
        }
    }

    async scrapeAllContests() {
        try {
            const totalPages = await this.getTotalPages();
            const allBannerLinks = [];
            
            // Scrape all pages to get banner links
            for (let page = 1; page <= totalPages; page++) {
                const bannerLinks = await this.scrapeBannerLinks(page);
                allBannerLinks.push(...bannerLinks);
                
                // Add delay between pages
                if (page < totalPages) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
            
            console.log(`Total contest banners found: ${allBannerLinks.length}`);
            
            // Scrape details for each contest
            for (let i = 0; i < allBannerLinks.length; i++) {
                const banner = allBannerLinks[i];
                const contestData = await this.scrapeContestDetails(banner.url, banner.title);
                this.competitions.push(contestData);
                
                console.log(`Processed ${i + 1}/${allBannerLinks.length}: ${banner.title}`);
                
                // Add delay between requests
                if (i < allBannerLinks.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 1500));
                }
            }
            
        } catch (error) {
            console.error('Error during scraping:', error);
        }
    }

    saveToCSV() {
        const csvWriter = createObjectCsvWriter({
            path: path.join(__dirname, 'ifbb_pro_contests.csv'),
            header: [
                { id: 'competition_name', title: 'competition_name' },
                { id: 'start_date', title: 'start_date' },
                { id: 'end_date', title: 'end_date' },
                { id: 'competition_level', title: 'competition_level' },
                { id: 'divisions', title: 'divisions' },
                { id: 'division_types', title: 'division_types' },
                { id: 'division_extra', title: 'division_extra' },
                { id: 'promoter', title: 'promoter' },
                { id: 'promoter_email', title: 'promoter_email' },
                { id: 'promoter_website', title: 'promoter_website' },
                { id: 'location', title: 'location' }
            ]
        });

        csvWriter.writeRecords(this.competitions)
            .then(() => {
                console.log(`CSV file saved to: ${path.join(__dirname, 'ifbb_pro_contests.csv')}`);
                console.log(`Total competitions processed: ${this.competitions.length}`);
            })
            .catch(error => {
                console.error('Error saving CSV:', error);
            });
    }
}

// Main execution
async function main() {
    const scraper = new IFBBProScraper();
    
    console.log('Starting IFBB Pro contest banner scraping...');
    console.log('This may take several minutes depending on the number of contests...');
    
    await scraper.scrapeAllContests();
    scraper.saveToCSV();
    
    console.log('Scraping completed!');
}

// Run the script
main().catch(console.error);
