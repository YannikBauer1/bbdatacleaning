import { supabase } from './supabase.js';
import { createObjectCsvWriter } from 'csv-writer';
import fs from 'fs';
import path from 'path';

async function downloadAndProcessYear(year) {
    try {
        console.log(`\nAttempting to list files for year ${year}...`);
        
        // List all files in the year folder
        const { data: files, error } = await supabase
            .storage
            .from('pipeline')
            .list(`jsons-clean/${year}`, {
                limit: 1000,
                offset: 0,
                sortBy: { column: 'name', order: 'asc' }
            });

        if (error) {
            console.error(`Error listing files for year ${year}:`, error);
            return;
        }

        //console.log('Raw files response:', files);

        if (!files || files.length === 0) {
            console.log(`No files found for year ${year}`);
            return;
        }

        // Filter out empty files and placeholder files
        const validFiles = files.filter(file => 
            file.name !== '.emptyFolderPlaceholder' && 
            file.metadata?.size > 0
        );

        console.log(`Found ${validFiles.length} valid files for year ${year}`);
        if (validFiles.length > 0) {
            //console.log('First few files:', validFiles.slice(0, 3));
        }

        // Create a temporary directory for the year
        const tempDir = path.join(process.cwd(), 'temp', year);
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }

        // Download and process each JSON file
        const allData = [];
        for (const file of validFiles) {
            //console.log(`\nProcessing file: ${file.name}`);
            
            const { data: fileData, error: downloadError } = await supabase
                .storage
                .from('pipeline')
                .download(`jsons-clean/${year}/${file.name}`);

            if (downloadError) {
                console.error(`Error downloading file ${file.name}:`, downloadError);
                continue;
            }

            if (!fileData) {
                console.error(`No data received for file ${file.name}`);
                continue;
            }

            const jsonText = await fileData.text();
            if (jsonText.length === 0) {
                console.log(`Skipping empty file: ${file.name}`);
                continue;
            }
            
            //console.log(`File content length: ${jsonText.length} characters`);
            
            let jsonData;
            try {
                jsonData = JSON.parse(jsonText);
            } catch (parseError) {
                console.error(`Error parsing JSON for file ${file.name}:`, parseError);
                continue;
            }

            // Check if the JSON has the expected structure
            if (!jsonData.competition || !Array.isArray(jsonData.competition)) {
                console.log('JSON structure:', JSON.stringify(jsonData, null, 2));
                console.error(`Invalid JSON structure in file ${file.name}`);
                continue;
            }

            // Convert the array-based JSON to an array of objects
            const rows = [];
            for (let i = 0; i < jsonData.competition.length; i++) {
                const row = {
                    competition: jsonData.competition[i] || '',
                    location: jsonData.location?.[i] || '',
                    date: jsonData.date?.[i] || '',
                    competitors_name: jsonData.competitors_name?.[i] || '',
                    country: jsonData.country?.[i] || '',
                    judging: jsonData.judging?.[i] || '',
                    finals: jsonData.finals?.[i] || '',
                    round2: jsonData.round2?.[i] || '',
                    round3: jsonData.round3?.[i] || '',
                    routine: jsonData.routine?.[i] || '',
                    total: jsonData.total?.[i] || '',
                    place: jsonData.place?.[i] || '',
                    competition_type: jsonData.competition_type?.[i] || ''
                };
                rows.push(row);
            }

            allData.push(...rows);
            //console.log(`Processed ${rows.length} rows from ${file.name}`);
        }

        if (allData.length === 0) {
            console.log(`No data collected for year ${year}`);
            return;
        }

        // Create output directory if it doesn't exist
        const outputDir = path.join(process.cwd(), 'all/output');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Write to CSV
        const csvWriter = createObjectCsvWriter({
            path: path.join(outputDir, `${year}_data.csv`),
            header: [
                { id: 'competition', title: 'Competition' },
                { id: 'location', title: 'Location' },
                { id: 'date', title: 'Date' },
                { id: 'competitors_name', title: 'Competitor Name' },
                { id: 'country', title: 'Country' },
                { id: 'judging', title: 'Judging' },
                { id: 'finals', title: 'Finals' },
                { id: 'round2', title: 'Round 2' },
                { id: 'round3', title: 'Round 3' },
                { id: 'routine', title: 'Routine' },
                { id: 'total', title: 'Total' },
                { id: 'place', title: 'Place' },
                { id: 'competition_type', title: 'Competition Type' }
            ]
        });

        await csvWriter.writeRecords(allData);
        //console.log(`Successfully wrote ${allData.length} rows to ${year}_data.csv`);

        // Clean up temporary directory
        fs.rmSync(tempDir, { recursive: true, force: true });
    } catch (error) {
        console.error(`Error processing year ${year}:`, error);
    }
}

async function main() {
    // Test Supabase connection first
    try {
        const { data, error } = await supabase.storage.getBucket('pipeline');
        if (error) {
            console.error('Error connecting to Supabase:', error);
            return;
        }
        console.log('Successfully connected to Supabase');
        console.log('Bucket info:', data);
    } catch (error) {
        console.error('Failed to connect to Supabase:', error);
        return;
    }

    // Process years from 2007 to 2023
    const years = Array.from({ length: 17 }, (_, i) => (2007 + i).toString());
    
    for (const year of years) {
        console.log(`\nProcessing year ${year}...`);
        await downloadAndProcessYear(year);
    }
}

main().catch(console.error);

