import fs from "fs";
import path from "path";
import { fileURLToPath } from 'url';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const outputDir = path.join(__dirname, "output");
const outputFiles = fs.readdirSync(outputDir)
  .filter(f => f.endsWith('.csv'))
  .sort();

// Column name mappings
const columnMappings = {
  'Competition': 'Competition',
  'Contest Name': 'Competition',
  'competition': 'Competition',
  'Division': 'Division',
  'Competition Type': 'Division',
  'competition_type': 'Division',
  'Date': 'Date',
  'Contest Date': 'Date',
  'date': 'Date',
  'Competitor Name': 'Competitor Name',
  'Name': 'Competitor Name',
  'competitors_name': 'Competitor Name',
  'Country': 'Country',
  'country': 'Country',
  'Place': 'Place',
  'place': 'Place',
  'Total': 'Total',
  'total': 'Total',
  'Judging': 'Judging',
  'judging': 'Judging',
  'Finals': 'Finals',
  'finals': 'Finals',
  'Location': 'Location',
  'location': 'Location',
  'URL': 'URL',
  'url': 'URL',
  'Image URL': 'Image URL',
  'img_url': 'Image URL'
};

// Function to extract competition name from URL
function extractCompetitionFromUrl(url) {
  if (!url) return '';
  try {
    const parts = url.split('/');
    const contestPart = parts[parts.length - 1];
    if (!contestPart) return '';
    
    // Remove year prefix if present
    const namePart = contestPart.replace(/^\d{4}_/, '');
    
    return namePart
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
      .replace(/\b(Ifbb|Pro)\b/g, match => match.toUpperCase());
  } catch (error) {
    console.error('Error processing URL:', url, error);
    return '';
  }
}

// Get all unique columns from all files
let allColumns = new Set();
let allData = [];

for (const file of outputFiles) {
  const filePath = path.join(outputDir, file);
  const data = fs.readFileSync(filePath, 'utf8');
  const records = parse(data, {
    columns: true,
    skip_empty_lines: true
  });

  // Add columns to the set
  if (records.length > 0) {
    Object.keys(records[0]).forEach(col => {
      // Map column name if it exists in mappings
      const mappedCol = columnMappings[col] || col;
      allColumns.add(mappedCol);
    });
  }

  // Determine source based on filename
  let source;
  if (file === 'musclememory_data.csv') {
    source = 'musclememory';
  } else if (file === 'npcnews.csv') {
    source = 'npcnews';
  } else if (file.startsWith('2024_')) {
    source = '2024';
  } else {
    source = 'scorecards';
  }

  // Add source column and fill missing columns
  records.forEach(record => {
    const newRecord = { Source: source };
    allColumns.forEach(col => {
      const originalCol = Object.entries(columnMappings).find(([orig, mapped]) => mapped === col)?.[0];
      if (source === '2024') {
        if (col === 'Competitor Name') {
          newRecord[col] = record['competitors_name'] || '';
        } else if (col === 'Division') {
          newRecord[col] = record['competition_type'] || '';
        } else if (col === 'Competition') {
          newRecord[col] = record['competition'] || '';
        } else if (col === 'Date') {
          newRecord[col] = record['date'] || '';
        } else if (col === 'Location') {
          newRecord[col] = record['location'] || '';
        } else if (col === 'URL') {
          newRecord[col] = record['url'] || '';
        } else if (col === 'Image URL') {
          newRecord[col] = record['img_url'] || '';
        } else if (col === 'Total') {
          newRecord[col] = record['total'] || '';
        } else if (col === 'Place') {
          newRecord[col] = record['place'] || '';
        } else if (col === 'Judging') {
          newRecord[col] = record['judging'] || '';
        } else if (col === 'Finals') {
          newRecord[col] = record['finals'] || '';
        } else if (col === 'Country') {
          newRecord[col] = record['country'] || '';
        } else {
          newRecord[col] = record[originalCol] || record[col] || '';
        }
      } else if (col === 'Competition' && source === 'npcnews') {
        const url = record['Contest URL'] || record['URL'] || record['url'] || '';
        const competitionName = extractCompetitionFromUrl(url);
        newRecord[col] = competitionName;
      } else if (col === 'Date' && source === 'npcnews') {
        newRecord[col] = record['Contest Date'] || record[originalCol] || record[col] || '';
      } else if (col === 'Division' && (source === 'musclememory' || source === 'scorecards')) {
        newRecord[col] = record['Competition Type'] || record[originalCol] || record[col] || '';
      } else if (col === 'Competitor Name') {
        newRecord[col] = record['Name'] || record['competitors_name'] || record[originalCol] || record[col] || '';
      } else {
        newRecord[col] = record[originalCol] || record[col] || '';
      }
    });
    allData.push(newRecord);
  });
}

// Convert Set to Array and ensure Source is first
const columns = ['Source', ...Array.from(allColumns).filter(c => c !== 'Source')];

// Write the combined data
const output = stringify(allData, {
  header: true,
  columns: columns
});

fs.writeFileSync(path.join(__dirname, 'all_years_combined.csv'), output);
console.log('All CSVs combined into all_years_combined.csv');
