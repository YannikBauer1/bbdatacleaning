const fs = require('fs');
const path = require('path');

// File paths
const inputFile = path.join(__dirname, 'combined_competitions.csv');
const outputFile = path.join(__dirname, 'pro_competitions.csv');

// Function to filter out amateur competitions and empty names
function filterProCompetitions() {
    try {
        // Read the combined CSV file
        const content = fs.readFileSync(inputFile, 'utf8');
        const rows = content.split('\n');
        
        if (rows.length === 0) {
            console.log('No data found in the combined CSV file.');
            return;
        }

        // Keep the header row and add Category_Subtype column
        const header = rows[0] + ',Category_Subtype';
        const filteredRows = [header];

        // Track the last sequential place number
        let lastSequentialPlace = 0;
        let currentCompetition = '';
        let currentCategory = '';

        // Process each row (skip header)
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i].trim();
            if (!row) continue;

            // Split the row and check the competition name and athlete name
            const columns = row.split(',');
            const year = parseInt(columns[0]); // Year is in the 1st column
            const gender = columns[1]; // Gender is in the 2nd column
            const competitionName = columns[2]; // Competition name is in the 3rd column
            const category = columns[3]; // Category is in the 4th column
            const place = columns[4]; // Place is in the 5th column
            const athleteName = columns[5]; // Athlete name is in the 6th column

            // Only keep rows where:
            // 1. Year is 1965 or later
            // 2. Competition name doesn't contain "Amateur"
            // 3. Athlete name is not empty
            // 4. Category doesn't contain "Masters" or "Junior" or "Teen"
            // 5. Competition is not "North American Championships"
            // 6. Competition is not "French Championships"
            // 7. Competition is not "South East Asian Games"
            // 8. Competition is not "German Championships"
            // 9. Competition is not "British Championships"
            // 10. Competition is not "Australian Championships"
            // 11. Competition doesn't contain "Australasia"
            // 12. Competition is not "American and Caribbean Championships"
            // 13. Competition doesn't contain "Elite Tour"
            // 14. Competition is not "Mexican Championships"
            // 15. Competition doesn't contain "Diamond Cup"
            // 16. Competition doesn't contain "UK Nationals"
            // 17. Competition doesn't contain "Olympia - Masters"
            // 18. Competition doesn't contain "Dunes Classic"
            if (year >= 1965 &&
                !competitionName.toLowerCase().includes('amateur') && 
                athleteName && athleteName.trim() !== '' &&
                !category.toLowerCase().includes('masters') &&
                !category.toLowerCase().includes('junior') &&
                !category.toLowerCase().includes('teen') &&
                !competitionName.includes('North American Championships') &&
                !competitionName.includes('French Championships') &&
                !competitionName.includes('South East Asian Games') &&
                !competitionName.includes('German Championships') &&
                !competitionName.includes('British Championships') &&
                !competitionName.includes('Australian Championships') &&
                !competitionName.includes('Australasia') &&
                !competitionName.includes('American and Caribbean Championships') &&
                !competitionName.includes('Elite Tour') &&
                !competitionName.includes('Mexican Championships') &&
                !competitionName.includes('Diamond Cup') &&
                !competitionName.includes('UK Nationals') &&
                !competitionName.includes('Olympia - Masters') &&
                /*!competitionName.includes('Mr International') &&
                !competitionName.includes('Mr Belgium') &&*/
                category.toLowerCase() !== 'amateur' &&
                category.toLowerCase() !== 'most muscular' &&
                !category.toLowerCase().includes('figure ') &&
                !competitionName.includes('Dunes Classic') &&
                !competitionName.includes('Junior Mr America')) {
                
                // Initialize category subtype
                let categorySubtype = '';

                // Store original category before any modifications
                const originalCategory = category;

                // Replace LightWeight category with 202 or 212 based on year (only for males)
                let isLightweightCategory = false;
                if (gender === 'male') {
                    const lowerCategory = originalCategory.toLowerCase();
                    if (lowerCategory.includes('light') && lowerCategory.includes('weight')) {
                        isLightweightCategory = true;
                        if (year >= 2007 && year <= 2011) {
                            columns[3] = '202'; // Replace LightWeight with 202 for 2007-2011
                        } else if (year >= 2012) {
                            columns[3] = '212'; // Replace LightWeight with 212 for 2012 and later
                        }
                    }
                }
                
                // Replace Open, empty, or bodybuilding category with mensbb for male competitors
                if (gender === 'male' && (
                    originalCategory.toLowerCase() === 'open' || 
                    !originalCategory || 
                    originalCategory.trim() === '' ||
                    originalCategory.toLowerCase() === 'bodybuilding'
                )) {
                    columns[3] = 'mensbb';
                }
                
                // Replace empty or bodybuilding category with womensbb for female competitors
                if (gender === 'female' && (
                    !originalCategory || 
                    originalCategory.trim() === '' ||
                    originalCategory.toLowerCase() === 'bodybuilding'
                )) {
                    columns[3] = 'womensbb';
                }
                
                // Replace bodybuilding category with womensbb for female competitors
                if (gender === 'female' && originalCategory.toLowerCase() === 'bodybuilding') {
                    columns[3] = 'womensbb';
                }
                
                // Replace Physique category with mensphysique for male competitors
                if (gender === 'male' && originalCategory.toLowerCase() === 'physique') {
                    columns[3] = 'mensphysique';
                }

                // Replace Physique category with womensphysique for female competitors
                if (gender === 'female' && originalCategory.toLowerCase() === 'physique') {
                    columns[3] = 'womensphysique';
                }
                
                // Convert all categories to lowercase
                columns[3] = columns[3].toLowerCase();

                // Handle female weight classes (only if not lightweight category)
                if (gender === 'female' && !isLightweightCategory) {
                    const lowerCategory = originalCategory.toLowerCase();
                    if (lowerCategory === 'heavyweight' || lowerCategory === 'lightweight' || lowerCategory === 'middleweight') {
                        categorySubtype = originalCategory;
                        columns[3] = 'womensbb';
                    }
                }

                // Handle male weight classes and categories (only if not lightweight category)
                if (gender === 'male' && !isLightweightCategory) {
                    const lowerCategory = originalCategory.toLowerCase();
                    if (lowerCategory === 'heavyweight' || 
                        lowerCategory === 'light-heavyweight' || 
                        lowerCategory === 'lightweight' || 
                        lowerCategory === 'medium' || 
                        lowerCategory === 'middleweight' || 
                        lowerCategory === 'professional' || 
                        lowerCategory === 'short' || 
                        lowerCategory === 'tall') {
                        categorySubtype = originalCategory;
                        columns[3] = 'mensbb';
                    }
                }
                
                // Remove text in parentheses from athlete names
                columns[5] = columns[5].replace(/\s*\([^)]*\)\s*/g, '').trim();

                // Check if we're in a new competition/category
                if (competitionName !== currentCompetition || columns[3] !== currentCategory) {
                    currentCompetition = competitionName;
                    currentCategory = columns[3];
                    lastSequentialPlace = 0;
                }

                // Update place number if needed
                if (place === '-' || (place !== '-' && parseInt(place) > lastSequentialPlace)) {
                    columns[4] = (lastSequentialPlace + 1).toString();
                }

                // Update last sequential place if this is a valid number
                if (place !== '-' && !isNaN(parseInt(place))) {
                    const placeNum = parseInt(place);
                    if (placeNum === lastSequentialPlace + 1) {
                        lastSequentialPlace = placeNum;
                    }
                }

                // Add the category subtype to the row
                filteredRows.push(columns.join(',') + ',' + categorySubtype);
            }
        }

        // Write filtered data to new CSV
        fs.writeFileSync(outputFile, filteredRows.join('\n'));
        
        console.log(`Successfully filtered competitions.`);
        console.log(`Original rows: ${rows.length - 1}`);
        console.log(`Filtered rows: ${filteredRows.length - 1}`);
        console.log(`Removed rows: ${rows.length - filteredRows.length}`);
    } catch (error) {
        console.error('Error filtering competitions:', error);
    }
}

// Run the script
filterProCompetitions();