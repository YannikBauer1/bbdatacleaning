const fs = require('fs');
const path = require('path');

function processCSV() {
    // Read the CSV file
    const csvPath = path.join(__dirname, 'data_raw', 'sidebar', '2025.csv');
    const csvContent = fs.readFileSync(csvPath, 'utf8');

    // Split the content into lines and remove empty lines
    const lines = csvContent.split('\n').filter(line => line.trim() !== '');

    // Get the header from the first line
    const headerLine = lines[0];

    // Create a map to store unique competitions with their divisions
    const uniqueCompetitions = new Map();

    // Process each line (skip the header)
    lines.slice(1).forEach(line => {
        // Split the line by comma, but preserve quoted fields
        const columns = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (char === '"') {
                inQuotes = !inQuotes;
                current += char;
            } else if (char === ',' && !inQuotes) {
                columns.push(current);
                current = '';
            } else {
                current += char;
            }
        }
        columns.push(current);
        
        // Extract the competition name from the URL
        const url = columns[3];
        const competitionName = url.split('/').filter(part => part.includes('2025-'))[0] || '';
        
        // Create a unique key based on competition name and date
        const key = `${competitionName}|${columns[1]}|${columns[2]}`;
        
        const division = columns[6]; // divisions column
        
        if (!uniqueCompetitions.has(key)) {
            // If this is a new competition, store all its information
            uniqueCompetitions.set(key, {
                start_date: columns[1],
                end_date: columns[2],
                url: columns[3],
                location: columns[4], // Keep location exactly as is
                comp_type: columns[5],
                divisions: new Set([division]),
                division_type: columns[7],
                promoter: columns[8],
                promoter_website: columns[9]
            });
        } else {
            // If we've seen this competition before, just add the new division
            uniqueCompetitions.get(key).divisions.add(division);
        }
    });

    // Create the output content
    const outputLines = Array.from(uniqueCompetitions.entries()).map(([key, data], index) => {
        // Convert the divisions Set to an array and stringify it
        const divisionsArray = Array.from(data.divisions);
        const jsonString = JSON.stringify(divisionsArray).replace(/"/g, '""');
        
        // Create the output line with all fields, maintaining original format
        return [
            index.toString(),
            data.start_date,
            data.end_date,
            data.url,
            data.location, // Keep location exactly as is
            data.comp_type,
            `"${jsonString}"`,
            data.division_type,
            data.promoter,
            data.promoter_website
        ].join(',');
    });

    // Combine header with the rest of the lines
    const outputContent = [headerLine, ...outputLines].join('\n');

    // Write the output to a new file
    const outputPath = path.join(__dirname, 'data_raw', 'sidebar', '2025_unique.csv');
    fs.writeFileSync(outputPath, outputContent);

    console.log(`Processed ${lines.length - 1} rows (excluding header)`);
    console.log(`Found ${uniqueCompetitions.size} unique competitions`);
    console.log(`Removed ${lines.length - 1 - uniqueCompetitions.size} duplicates`);
    console.log(`Output written to: ${outputPath}`);
}

// Run the processing
processCSV(); 