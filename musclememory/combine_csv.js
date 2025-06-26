const fs = require('fs');
const path = require('path');

// Directory containing the CSV files
const inputDir = path.join(__dirname, 'output');
const outputFile = path.join(__dirname, 'combined_competitions.csv');

// Function to clean competition name
function cleanCompetitionName(name) {
    return name.replace(' - IFBB', '');
}

// Function to extract year and gender from filename
function extractInfoFromFilename(filename) {
    const match = filename.match(/ifbb_competitions_(male|female)_(\d{4})\.csv/);
    if (match) {
        return {
            gender: match[1],
            year: match[2]
        };
    }
    return null;
}

// Main function to combine CSV files
function combineCSVFiles() {
    try {
        // Get all CSV files
        const files = fs.readdirSync(inputDir)
            .filter(file => file.endsWith('.csv') && file.startsWith('ifbb_competitions_'));

        if (files.length === 0) {
            console.log('No CSV files found in the output directory.');
            return;
        }

        console.log(`Found ${files.length} CSV files to combine.`);

        // Create header for combined CSV
        const header = ['Year', 'Gender', 'Competition', 'Category', 'Place', 'Name', 'Score'].join(',');

        // Process each file
        const allRows = [];
        files.forEach(file => {
            const filePath = path.join(inputDir, file);
            const info = extractInfoFromFilename(file);
            
            if (!info) {
                console.log(`Skipping file with invalid format: ${file}`);
                return;
            }

            console.log(`Processing ${file}...`);
            
            // Read and process the CSV file
            const content = fs.readFileSync(filePath, 'utf8');
            const rows = content.split('\n').slice(1); // Skip header row
            
            rows.forEach(row => {
                if (row.trim()) {
                    const [competition, category, place, name, score] = row.split(',');
                    const cleanedCompetition = cleanCompetitionName(competition);
                    
                    allRows.push([
                        info.year,
                        info.gender,
                        cleanedCompetition,
                        category,
                        place,
                        name,
                        score
                    ].join(','));
                }
            });
        });

        // Write combined CSV
        const combinedContent = [header, ...allRows].join('\n');
        fs.writeFileSync(outputFile, combinedContent);
        
        console.log(`Successfully combined ${files.length} files into ${outputFile}`);
        console.log(`Total rows: ${allRows.length}`);
    } catch (error) {
        console.error('Error combining CSV files:', error);
    }
}

// Run the script
combineCSVFiles(); 