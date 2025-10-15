import supabase from '../supabase/supabase_client.js';
import axios from 'axios';
import * as cheerio from 'cheerio';
import { createWriteStream } from 'fs';
import { mkdir } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { pipeline } from 'stream/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Fetches all events from Supabase for the current year (2025)
 * @returns {Promise<Array>} Array of event objects
 */
async function getEventsForCurrentYear() {
  try {
    const currentYear = 2025;
    
    console.log(`Fetching events for year ${currentYear}...`);
    
    const { data, error } = await supabase
      .from('event')
      .select(`
        *,
        competition:competition_id (*)
      `)
      .eq('year', currentYear)
      .order('start_date', { ascending: true });
    
    if (error) {
      throw error;
    }
    
    console.log(`Found ${data.length} events for ${currentYear}`);
    return data;
    
  } catch (error) {
    console.error('Error fetching events for current year:', error);
    throw error;
  }
}

/**
 * Fetches HTML from a URL
 * @param {string} url - The URL to fetch
 * @returns {Promise<string>} HTML content
 */
async function fetchHTML(url) {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 30000
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching HTML from ${url}:`, error.message);
    throw error;
  }
}

/**
 * Extracts event image URL from IFBB page HTML
 * @param {string} html - HTML content
 * @returns {string|null} Image URL or null if not found
 */
function extractEventImageUrl(html) {
  try {
    const $ = cheerio.load(html);
    
    // Look for the event image in the tribe-events-event-image div
    let imageUrl = $('.tribe-events-event-image img').attr('src') || 
                   $('.tribe-events-event-image img').attr('data-orig-src');
    
    // Fallback: try other common selectors
    if (!imageUrl) {
      imageUrl = $('img.wp-post-image').attr('src') ||
                 $('img.wp-post-image').attr('data-orig-src');
    }
    
    // Make sure we have a valid URL
    if (imageUrl && imageUrl.startsWith('http')) {
      return imageUrl;
    }
    
    return null;
  } catch (error) {
    console.error('Error extracting image URL:', error.message);
    return null;
  }
}

/**
 * Downloads an image from a URL to a file
 * @param {string} imageUrl - URL of the image to download
 * @param {string} outputPath - Path where to save the image
 * @returns {Promise<boolean>} Success status
 */
async function downloadImage(imageUrl, outputPath) {
  try {
    // Create directory if it doesn't exist
    await mkdir(dirname(outputPath), { recursive: true });
    
    const response = await axios({
      method: 'GET',
      url: imageUrl,
      responseType: 'stream',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 30000
    });
    
    await pipeline(response.data, createWriteStream(outputPath));
    return true;
  } catch (error) {
    console.error(`Error downloading image from ${imageUrl}:`, error.message);
    return false;
  }
}

/**
 * Processes a single event: fetches the page, extracts image, and saves it
 * @param {Object} event - Event object from Supabase
 * @param {string} baseOutputDir - Base directory for saving images
 * @returns {Promise<Object>} Result object with success status and details
 */
async function processEvent(event, baseOutputDir) {
  const result = {
    eventId: event.id,
    competitionName: event.competition?.name || 'unknown',
    year: event.year,
    success: false,
    error: null,
    imagePath: null
  };
  
  try {
    // Check if event has an IFBB URL
    if (!event.ifbb_url) {
      result.error = 'No IFBB URL';
      return result;
    }
    
    console.log(`Processing: ${event.competition?.name} ${event.year}`);
    console.log(`  URL: ${event.ifbb_url}`);
    
    // Fetch the HTML
    const html = await fetchHTML(event.ifbb_url);
    
    // Extract image URL
    const imageUrl = extractEventImageUrl(html);
    if (!imageUrl) {
      result.error = 'No image found on page';
      return result;
    }
    
    console.log(`  Found image: ${imageUrl}`);
    
    // Create output path: competition_name_key/event_year/background.png
    const competitionFolder = event.competition?.name || 'unknown';
    const outputPath = join(baseOutputDir, competitionFolder, event.year.toString(), 'background.png');
    
    // Download the image
    const downloaded = await downloadImage(imageUrl, outputPath);
    
    if (downloaded) {
      result.success = true;
      result.imagePath = outputPath;
      console.log(`  ✓ Saved to: ${outputPath}`);
    } else {
      result.error = 'Failed to download image';
    }
    
    return result;
  } catch (error) {
    result.error = error.message;
    console.error(`  ✗ Error processing event:`, error.message);
    return result;
  }
}

/**
 * Processes all events for the current year
 * @param {string} outputDir - Base directory for saving images (default: eventImages/downloads)
 * @returns {Promise<Object>} Summary of results
 */
async function downloadAllEventImages(outputDir = null) {
  try {
    // Default output directory
    const baseOutputDir = outputDir || join(dirname(__dirname), 'eventImages', 'downloads');
    
    console.log('\n=== Starting Event Image Download ===');
    console.log(`Output directory: ${baseOutputDir}\n`);
    
    // Fetch all events
    const events = await getEventsForCurrentYear();
    
    // Filter events that have IFBB URLs
    const eventsWithUrls = events.filter(e => e.ifbb_url);
    console.log(`Found ${eventsWithUrls.length} events with IFBB URLs out of ${events.length} total\n`);
    
    const results = {
      total: eventsWithUrls.length,
      successful: 0,
      failed: 0,
      errors: []
    };
    
    // Process each event
    for (let i = 0; i < eventsWithUrls.length; i++) {
      const event = eventsWithUrls[i];
      console.log(`\n[${i + 1}/${eventsWithUrls.length}]`);
      
      const result = await processEvent(event, baseOutputDir);
      
      if (result.success) {
        results.successful++;
      } else {
        results.failed++;
        results.errors.push({
          event: `${result.competitionName} ${result.year}`,
          error: result.error
        });
      }
      
      // Small delay to be respectful to the server
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Print summary
    console.log('\n\n=== Download Summary ===');
    console.log(`Total events processed: ${results.total}`);
    console.log(`Successful downloads: ${results.successful}`);
    console.log(`Failed downloads: ${results.failed}`);
    
    if (results.errors.length > 0) {
      console.log('\nErrors:');
      results.errors.forEach(err => {
        console.log(`  - ${err.event}: ${err.error}`);
      });
    }
    
    return results;
  } catch (error) {
    console.error('Error in downloadAllEventImages:', error);
    throw error;
  }
}

export { getEventsForCurrentYear, downloadAllEventImages };

// Test execution
if (import.meta.url === `file://${process.argv[1]}`) {
  // Check if user wants to test fetch only or download images
  const args = process.argv.slice(2);
  const mode = args[0] || 'download'; // 'fetch' or 'download'
  
  if (mode === 'fetch') {
    // Test fetching events only
    getEventsForCurrentYear()
      .then(events => {
        console.log('\n=== Events fetched successfully ===');
        console.log(`Total events: ${events.length}\n`);
        
        // Show first few events as sample
        events.slice(0, 3).forEach((event, index) => {
          console.log(`Event ${index + 1}:`);
          console.log(`  Event ID: ${event.id}`);
          console.log(`  Competition: ${event.competition?.name}`);
          console.log(`  Year: ${event.year}`);
          console.log(`  Start Date: ${event.start_date || 'N/A'}`);
          console.log(`  End Date: ${event.end_date || 'N/A'}`);
          console.log(`  IFBB URL: ${event.ifbb_url || 'N/A'}`);
          console.log('');
        });
        
        if (events.length > 3) {
          console.log(`... and ${events.length - 3} more events`);
        }
      })
      .catch(error => {
        console.error('Test failed:', error);
        process.exit(1);
      });
  } else {
    // Download all event images
    downloadAllEventImages()
      .then(results => {
        console.log('\n✓ Image download process completed');
        process.exit(results.failed > 0 ? 1 : 0);
      })
      .catch(error => {
        console.error('Download failed:', error);
        process.exit(1);
      });
  }
}

