const fs = require('fs');
const path = require('path');

function processCSV() {
    // Read the CSV file
    const csvPath = path.join(__dirname, 'data_raw', 'sidebar', 'pro_schedule_2025.csv');
    const csvContent = fs.readFileSync(csvPath, 'utf8');

    // Split the content into lines and remove empty lines
    const lines = csvContent.split('\n').filter(line => line.trim() !== '');

    // Get the header from the first line and modify it
    const headerLine = lines[0];
    const headerColumns = headerLine.split(',').map(col => col.trim());
    headerColumns[headerColumns.length - 1] = 'competition_type'; // Replace the last column header
    const modifiedHeader = headerColumns.join(',');

    // Create a map to store unique competitions with their types
    const uniqueCompetitions = new Map();

    // Process each line (skip the header)
    lines.slice(1).forEach(line => {
        // Split the line by comma, but be careful with commas inside quotes
        const columns = line.split(',').map(col => col.trim());
        
        // Extract relevant information
        const competitionName = columns[1];
        const competitionSubtype = columns[5] || ''; // competition_subtype column
        const competitionType = columns[columns.length - 1]; // Last column is the competition type

        // Apply filters
        // 1. Skip if has MASTERS in subtype but no OPEN
        if (competitionSubtype.includes('MASTERS') && !competitionSubtype.includes('OPEN')) {
            return;
        }
        
        // 2. Skip if has NATURAL in name
        if (competitionName.toUpperCase().includes('NATURAL')) {
            return;
        }
        
        if (!uniqueCompetitions.has(competitionName)) {
            // If this is a new competition, store all its information
            uniqueCompetitions.set(competitionName, {
                line: line,
                types: new Set([competitionType])
            });
        } else {
            // If we've seen this competition before, just add the new type
            uniqueCompetitions.get(competitionName).types.add(competitionType);
        }
    });

    // Create the output content
    const outputLines = Array.from(uniqueCompetitions.entries()).map(([name, data], index) => {
        // Get the base line without the competition type
        const baseColumns = data.line.split(',').map(col => col.trim());
        baseColumns.pop(); // Remove the last column (competition type)
        
        // Reset the index (first column)
        baseColumns[0] = (index + 1).toString();
        
        // Add all competition types as the last column, as a properly escaped stringified array
        const typesArray = Array.from(data.types);
        const jsonString = JSON.stringify(typesArray).replace(/"/g, '""');
        return [...baseColumns, `"${jsonString}"`].join(',');
    });

    // Combine header with the rest of the lines
    const outputContent = [modifiedHeader, ...outputLines].join('\n');

    // Write the output to a new file
    const outputPath = path.join(__dirname, 'data_raw', 'sidebar', 'pro_schedule_2025_unique.csv');
    fs.writeFileSync(outputPath, outputContent);

    console.log(`Processed ${lines.length - 1} rows (excluding header)`);
    console.log(`Found ${uniqueCompetitions.size} unique competitions after filtering`);
    console.log(`Removed ${lines.length - 1 - uniqueCompetitions.size} competitions (duplicates and filtered)`);
    console.log(`Output written to: ${outputPath}`);
}

// Run the processing
processCSV(); 