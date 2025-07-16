import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { 
  createResult, 
  getAthleteByPersonNameKey, 
  getCategoryByDivisionAndSubtype,
  getEventByCompetitionAndYear,
  createDivision,
  getDivisionByEventAndCategory
} from './results.js';

// Function to create a result record
async function createResultRecord(resultData) {
  try {
    const { data, error } = await supabase
      .from('result')
      .insert(resultData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating result:', error);
    throw error;
  }
}

// Helper function to format division subtype
function formatDivisionSubtype(subtype) {
  if (!subtype) return null;
  
  // Convert to title case and capitalize letters after "-"
  return subtype
    .split('-')
    .map(part => part.trim().toLowerCase().replace(/\b\w/g, l => l.toUpperCase()))
    .join('-');
}

// Helper function to extract year from date
function extractYearFromDate(dateString) {
  if (!dateString) return null;
  
  try {
    const date = new Date(dateString);
    return date.getFullYear();
  } catch (error) {
    console.warn('Error parsing date:', dateString);
    return null;
  }
}

// Main function to process and upload results from CSV
export async function uploadResultsFromCSV(csvFilePath = 'data/clean/results.csv') {
  try {
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} results to process`);
    
    let successCount = 0;
    let errorCount = 0;
    let divisionCache = new Map(); // Cache divisions to avoid duplicates
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      
      try {
        console.log(`Processing result ${i + 1}/${records.length}: ${record['athlete_name_key']} in ${record['competition_name_key']}`);
        
        // Get athlete by person name_key
        const athleteNameKey = record['athlete_name_key'];
        if (!athleteNameKey) {
          console.warn(`No valid athlete name key for: ${record['athlete_name_key']}`);
          errorCount++;
          continue;
        }
        
        let athlete;
        try {
          athlete = await getAthleteByPersonNameKey(athleteNameKey);
        } catch (error) {
          console.warn(`Athlete not found for name_key: ${athleteNameKey}`);
          errorCount++;
          continue;
        }
        
        // Get event by competition name and year
        const competitionNameKey = record['competition_name_key'];
        const year = parseInt(record['year']) || new Date().getFullYear();
        
        if (!competitionNameKey) {
          console.warn(`No valid competition name key for: ${record['competition_name_key']}`);
          errorCount++;
          continue;
        }
        
        let event;
        try {
          event = await getEventByCompetitionAndYear(competitionNameKey, year);
        } catch (error) {
          console.warn(`Event not found for competition: ${competitionNameKey} and year: ${year}`);
          errorCount++;
          continue;
        }
        
        // Get category by division and subtype
        const divisionName = record['Division']?.toLowerCase(); // Use as-is, e.g., '202_212'
        const divisionSubtype = formatDivisionSubtype(record['Division Subtype']);
                
        if (!divisionName) {
          console.warn(`No valid division name for: ${record['Division']}`);
          errorCount++;
          continue;
        }
        
        let category;
        try {
          category = await getCategoryByDivisionAndSubtype(divisionName, divisionSubtype);
        } catch (error) {
          console.warn(`Category not found for division: ${divisionName} and subtype: ${divisionSubtype}`);
          errorCount++;
          continue;
        }
        
        // Get or create division
        const divisionKey = `${event.id}_${category.id}`;
        let division;
        
        if (divisionCache.has(divisionKey)) {
          division = divisionCache.get(divisionKey);
        } else {
          try {
            division = await getDivisionByEventAndCategory(event.id, category.id);
            divisionCache.set(divisionKey, division);
          } catch (error) {
            // Division doesn't exist, create it
            const divisionData = {
              event_id: event.id,
              category_id: category.id,
              start_time: null, // Not known
              end_time: null, // Not known
              order: null, // Not known
              description: null, // Not known
              timezone: null // Not known
            };
            
            division = await createDivision(divisionData);
            divisionCache.set(divisionKey, division);
            console.log(`Created division with ID: ${division.id}`);
          }
        }
        
        // Create result data
        const resultData = {
          judging_1: record['Judging 1'] ? parseFloat(record['Judging 1']) : null,
          judging_2: record['Judging 2'] ? parseFloat(record['Judging 2']) : null,
          judging_3: record['Judging 3'] ? parseFloat(record['Judging 3']) : null,
          judging_4: record['Judging 4'] ? parseFloat(record['Judging 4']) : null,
          routine: record['Routine'] ? parseFloat(record['Routine']) : null,
          total: record['Total'] ? parseFloat(record['Total']) : null,
          place: record['Place'] ? parseInt(record['Place']) : null,
          athlete_id: athlete.id,
          division_id: division.id
        };
        
        // Create result record
        const result = await createResultRecord(resultData);
        console.log(`Created result with ID: ${result.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing result for ${record['athlete_name_key']}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} results`);
    console.log(`Errors: ${errorCount} results`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadResultsFromCSV:', error);
    throw error;
  }
}

// Function to check if results already exist to avoid duplicates
export async function checkExistingResults() {
  try {
    const { data: results, error: resultError } = await supabase
      .from('result')
      .select('id, athlete_id, division_id');
    
    if (resultError) throw resultError;
    
    console.log(`Found ${results.length} existing results`);
    
    return {
      resultIds: results.map(r => r.id),
      existingResultKeys: results.map(r => `${r.athlete_id}_${r.division_id}`)
    };
  } catch (error) {
    console.error('Error checking existing results:', error);
    throw error;
  }
}

// Function to upload only new results (avoiding duplicates)
export async function uploadNewResultsOnly(csvFilePath = 'data/clean/results.csv') {
  try {
    console.log('Checking existing results...');
    const existing = await checkExistingResults();
    
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} results to process`);
    
    let successCount = 0;
    let errorCount = 0;
    let divisionCache = new Map(); // Cache divisions to avoid duplicates
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      
      try {
        console.log(`Processing result ${i + 1}/${records.length}: ${record['athlete_name_key']} in ${record['competition_name_key']}`);
        
        // Get athlete by person name_key
        const athleteNameKey = record['athlete_name_key'];
        if (!athleteNameKey) {
          console.warn(`No valid athlete name key for: ${record['athlete_name_key']}`);
          errorCount++;
          continue;
        }
        
        let athlete;
        try {
          athlete = await getAthleteByPersonNameKey(athleteNameKey);
        } catch (error) {
          console.warn(`Athlete not found for name_key: ${athleteNameKey}`);
          errorCount++;
          continue;
        }
        
        // Get event by competition name and year
        const competitionNameKey = record['competition_name_key'];
        const year = parseInt(record['year']) || new Date().getFullYear();
        
        if (!competitionNameKey) {
          console.warn(`No valid competition name key for: ${record['competition_name_key']}`);
          errorCount++;
          continue;
        }
        
        let event;
        try {
          event = await getEventByCompetitionAndYear(competitionNameKey, year);
        } catch (error) {
          console.warn(`Event not found for competition: ${competitionNameKey} and year: ${year}`);
          errorCount++;
          continue;
        }
        
        // Get category by division and subtype
        const divisionName = record['Division']?.toLowerCase(); // Use as-is, e.g., '202_212'
        const divisionSubtype = record['Division Subtype'] ? formatDivisionSubtype(record['Division Subtype']) : null;
        
        if (!divisionName) {
          console.warn(`No valid division name for: ${record['Division']}`);
          errorCount++;
          continue;
        }
        
        let category;
        try {
          category = await getCategoryByDivisionAndSubtype(divisionName, divisionSubtype);
        } catch (error) {
          console.warn(`Category not found for division: ${divisionName} and subtype: ${divisionSubtype}`);
          errorCount++;
          continue;
        }
        
        // Get or create division
        const divisionKey = `${event.id}_${category.id}`;
        let division;
        
        if (divisionCache.has(divisionKey)) {
          division = divisionCache.get(divisionKey);
        } else {
          try {
            division = await getDivisionByEventAndCategory(event.id, category.id);
            divisionCache.set(divisionKey, division);
          } catch (error) {
            // Division doesn't exist, create it
            const divisionData = {
              event_id: event.id,
              category_id: category.id,
              start_time: null, // Not known
              end_time: null, // Not known
              order: null, // Not known
              description: null, // Not known
              timezone: null // Not known
            };
            
            division = await createDivision(divisionData);
            divisionCache.set(divisionKey, division);
            console.log(`Created division with ID: ${division.id}`);
          }
        }
        
        // Check if result already exists
        const resultKey = `${athlete.id}_${division.id}`;
        if (existing.existingResultKeys.includes(resultKey)) {
          console.log(`Result already exists for athlete ${athlete.id} and division ${division.id}, skipping`);
          continue;
        }
        
        // Create result data
        const resultData = {
          judging_1: record['Judging 1'] ? parseFloat(record['Judging 1']) : null,
          judging_2: record['Judging 2'] ? parseFloat(record['Judging 2']) : null,
          judging_3: record['Judging 3'] ? parseFloat(record['Judging 3']) : null,
          judging_4: record['Judging 4'] ? parseFloat(record['Judging 4']) : null,
          routine: record['Routine'] ? parseFloat(record['Routine']) : null,
          total: record['Total'] ? parseFloat(record['Total']) : null,
          place: record['Place'] ? parseInt(record['Place']) : null,
          athlete_id: athlete.id,
          division_id: division.id
        };
        
        // Create result record
        const result = await createResultRecord(resultData);
        console.log(`Created result with ID: ${result.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing result for ${record['athlete_name_key']}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} new results`);
    console.log(`Errors: ${errorCount} results`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadNewResultsOnly:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  const args = process.argv.slice(2);
  const mode = args[0] || 'new'; // 'all' or 'new'
  
  if (mode === 'all') {
    uploadResultsFromCSV()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  } else {
    uploadNewResultsOnly()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  }
} 