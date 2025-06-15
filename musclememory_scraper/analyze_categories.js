const fs = require('fs');
const path = require('path');

// File paths
const inputFile = path.join(__dirname, 'pro_competitions.csv');

function analyzeCategories() {
    try {
        // Read the CSV file
        const content = fs.readFileSync(inputFile, 'utf8');
        const rows = content.split('\n');
        
        if (rows.length === 0) {
            console.log('No data found in the CSV file.');
            return;
        }

        // Skip header row
        const maleCategories = new Set();
        const femaleCategories = new Set();

        // Process each row
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i].trim();
            if (!row) continue;

            const columns = row.split(',');
            const gender = columns[1]; // Gender is in the 2nd column
            const category = columns[3]; // Category is in the 4th column

            // Collect categories based on gender
            if (gender === 'male') {
                maleCategories.add(category);
            } else if (gender === 'female') {
                femaleCategories.add(category);
            }
        }

        // Convert Sets to Arrays and sort alphabetically
        const uniqueMaleCategories = Array.from(maleCategories).sort();
        const uniqueFemaleCategories = Array.from(femaleCategories).sort();

        // Print results
        console.log('Unique Male Categories:');
        console.log('----------------------');
        uniqueMaleCategories.forEach(category => {
            console.log(category);
        });
        console.log('\nTotal number of unique male categories:', uniqueMaleCategories.length);

        console.log('\nUnique Female Categories:');
        console.log('------------------------');
        uniqueFemaleCategories.forEach(category => {
            console.log(category);
        });
        console.log('\nTotal number of unique female categories:', uniqueFemaleCategories.length);

    } catch (error) {
        console.error('Error analyzing categories:', error);
    }
}

// Run the analysis
analyzeCategories();