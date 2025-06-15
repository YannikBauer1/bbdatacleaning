const fs = require('fs');
const path = require('path');
const axios = require('axios');

/**
 * Downloads images from a list of URLs
 * @param {string} downloadPath - Path where images should be saved
 * @param {string[]} urlList - List of image URLs to download
 * @param {string} retryFilePath - Path to save failed downloads for retry
 */
async function downloadImage(downloadPath, urlList, retryFilePath) {
    // Create directory if it doesn't exist
    if (!fs.existsSync(downloadPath)) {
        fs.mkdirSync(downloadPath, { recursive: true });
    }

    // Get list of files already in the directory
    const existingFiles = fs.readdirSync(downloadPath);
    
    // Filter for score/result images and those not already downloaded
    const urlsToDownload = urlList.filter(url => {
        // Extract the filename from the URL, preserving the extension
        const urlParts = url.split('/');
        const lastPart = urlParts[urlParts.length - 1];
        const secondLastPart = urlParts[urlParts.length - 2];
        const filename = `${secondLastPart}_${lastPart}`;
        
        // Check if filename contains 'score' (case insensitive)
        const isScore = true //filename.toLowerCase().includes('score');
        
        // Check if file already exists
        const fileExists = existingFiles.includes(filename);
        if (fileExists) {
            console.log(`Skipping ${filename} - already downloaded`);
        }
        
        return isScore && !fileExists;
    });

    console.log(`Found ${urlsToDownload.length} new images to download out of ${urlList.length} total URLs`);

    // Load existing retry URLs
    let retryUrls = [];
    if (fs.existsSync(retryFilePath)) {
        retryUrls = JSON.parse(fs.readFileSync(retryFilePath, 'utf8'));
    }

    // Download each image
    for (const url of urlsToDownload) {
        try {
            // Extract the filename from the URL, preserving the extension
            const urlParts = url.split('/');
            const lastPart = urlParts[urlParts.length - 1];
            const secondLastPart = urlParts[urlParts.length - 2];
            const filename = `${secondLastPart}_${lastPart}`;
            const outPath = path.join(downloadPath, filename);
            
            // Try different URL formats
            const urlFormats = [
                url.replace('/http', '/if_/http'),  // Try with if_ prefix
                url.replace('/http', '/im_/http'),  // Try with im_ prefix
                url.replace('/http', '/id_/http'),  // Try with id_ prefix
                url.replace('/http', '/js_/http'),  // Try with js_ prefix
                url.replace('/http', '/cs_/http'),  // Try with cs_ prefix
                url.replace('/http', '/http')       // Try without any prefix
            ];

            let success = false;
            for (const newUrl of urlFormats) {
                try {
                    // Download the image using axios with responseType as 'arraybuffer'
                    const response = await axios.get(newUrl, {
                        responseType: 'arraybuffer',
                        headers: {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.9',
                        },
                        timeout: 30000 // 30 second timeout
                    });

                    // Write the image data to file
                    fs.writeFileSync(outPath, response.data);
                    console.log(`Downloaded: ${filename}`);
                    success = true;
                    break;
                } catch (error) {
                    if (error.response && error.response.status === 404) {
                        continue; // Try next URL format
                    }
                    if (error.code === 'ECONNABORTED') {
                        // Add to retry list if timeout
                        if (!retryUrls.includes(url)) {
                            retryUrls.push(url);
                        }
                        console.log(`Timeout for ${filename}, added to retry list`);
                        break;
                    }
                    throw error; // Re-throw other errors
                }
            }

            if (!success) {
                console.error(`Failed to download ${filename} after trying all URL formats`);
                // Add to retry list if all formats failed
                if (!retryUrls.includes(url)) {
                    retryUrls.push(url);
                }
            }
            
        } catch (error) {
            console.error(`Error processing ${url}:`, error.message);
            // Add to retry list if there was an error
            if (!retryUrls.includes(url)) {
                retryUrls.push(url);
            }
            continue;
        }
    }

    // Save retry URLs to file
    fs.writeFileSync(retryFilePath, JSON.stringify(retryUrls, null, 2));
}

/**
 * Calls the Wayback Machine API to get image URLs for a specific year
 * @param {number} year - The year to get images for
 * @param {string} [callUrl] - Optional custom URL pattern
 * @returns {Promise<string[]>} - List of image URLs
 */
async function callWaybackMachineAPI(year, callUrl = null) {
    try {
        // Define the base API URL
        const apiUrl = "http://web.archive.org/cdx/search/cdx";

        // Construct the URL pattern based on the year
        let targetUrl;
        if (callUrl === null) {
            if (year <= 2015) {
                targetUrl = `http://www.ifbbpro.com/wp-content/uploads/image/${year}/results/*`;
            } else {
                targetUrl = `http://www.ifbbpro.com/wp-content/uploads/${year}/*`;
            }
        } else {
            targetUrl = `${callUrl}/${year}*`;
        }

        console.log(targetUrl);

        // Parameters for the API request
        const params = {
            url: targetUrl,  // Target URL
            output: 'json',  // Request JSON output
            limit: 2000,     // Limit the number of results
            filter: 'statuscode:200'  // Filter only valid HTTP 200 responses
        };

        // Make the API request
        const response = await axios.get(apiUrl, { params });
        
        if (response.status === 200) {
            // Parse the JSON response
            const data = response.data;
            
            // The first entry is a header; skip it
            const snapshots = data.slice(1);
            
            // Extract and print snapshot details
            const allUrls = snapshots.map(snapshot => {
                const timestamp = snapshot[1];  // Timestamp of the snapshot
                return `http://web.archive.org/web/${timestamp}/${snapshot[2]}`;  // Archived URL
            });
            
            console.log("Retrieved urls from Wayback Machine API");
            return allUrls;
        } else {
            console.error(`Failed to retrieve data. Status code: ${response.status}`);
            return null;
        }
    } catch (error) {
        console.error(`Error calling Wayback Machine API for year ${year}:`, error.message);
        return null;
    }
}

/**
 * Main function to process years and download images
 * @param {number[]} yearsList - List of years to process
 * @param {string} downloadPath - Base path for downloads
 */
async function main(yearsList, downloadPath) {
    const retryFilePath = path.join(downloadPath, 'retry_urls.json');
    
    for (const year of yearsList) {
        console.log(`Processing year: ${year}`);
        try {
            const allUrls = await callWaybackMachineAPI(year);
            
            if (allUrls && allUrls.length > 0) {
                const yearPath = path.join(downloadPath, year.toString());
                await downloadImage(yearPath, allUrls, retryFilePath);
            }
        } catch (error) {
            console.error(`Error processing year ${year}:`, error);
        }
    }
}

// Example usage
const yearsList = [2023];
const baseDownloadPath = './waybackMachine/downloaded_images';

main(yearsList, baseDownloadPath)
    .then(() => console.log('Download process completed'))
    .catch(error => console.error('Error in main process:', error)); 