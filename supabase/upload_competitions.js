import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { createCompetition } from './competition.js';

// Function to create a competition record
async function createCompetitionRecord(competitionData) {
  try {
    const { data, error } = await supabase
      .from('competition')
      .insert(competitionData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating competition:', error);
    throw error;
  }
}

// Main function to process and upload competitions from CSV
export async function uploadCompetitionsFromCSV(csvFilePath = 'data/clean/competitions.csv') {
  try {
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} competitions to process`);
    
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      
      try {
        console.log(`Processing competition ${i + 1}/${records.length}: ${record.name_long}`);
        
        // Create competition data
        const competitionData = {
          name_key: record.name_key,
          name: record.name,
          name_short: record.name_short,
          organization: 'IFBB Pro', // Set to "IFBB Pro" for every competition
          socials: null, // Not known
          image_url: null // Not known
        };
        
        // Create competition record
        const competition = await createCompetitionRecord(competitionData);
        console.log(`Created competition with ID: ${competition.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing competition ${record.name_long}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} competitions`);
    console.log(`Errors: ${errorCount} competitions`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadCompetitionsFromCSV:', error);
    throw error;
  }
}

// Function to check if competitions already exist to avoid duplicates
export async function checkExistingCompetitions() {
  try {
    const { data: competitions, error: competitionError } = await supabase
      .from('competition')
      .select('id, name_key');
    
    if (competitionError) throw competitionError;
    
    console.log(`Found ${competitions.length} existing competitions`);
    
    return {
      competitionIds: competitions.map(c => c.id),
      existingNameKeys: competitions.map(c => c.name_key)
    };
  } catch (error) {
    console.error('Error checking existing competitions:', error);
    throw error;
  }
}

// Function to upload only new competitions (avoiding duplicates)
export async function uploadNewCompetitionsOnly(csvFilePath = 'data/clean/competitions.csv') {
  try {
    console.log('Checking existing competitions...');
    const existing = await checkExistingCompetitions();
    
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    // Filter out existing competitions
    const newRecords = records.filter(record => 
      !existing.existingNameKeys.includes(record.name_key)
    );
    
    console.log(`Found ${newRecords.length} new competitions out of ${records.length} total`);
    
    if (newRecords.length === 0) {
      console.log('No new competitions to upload');
      return { successCount: 0, errorCount: 0 };
    }
    
    // Process only new records
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < newRecords.length; i++) {
      const record = newRecords[i];
      
      try {
        console.log(`Processing new competition ${i + 1}/${newRecords.length}: ${record.name_long}`);
        
        // Create competition data
        const competitionData = {
          name_key: record.name_key,
          name: record.name,
          name_short: record.name_short,
          organization: 'IFBB Pro', // Set to "IFBB Pro" for every competition
          socials: null, // Not known
          image_url: null // Not known
        };
        
        // Create competition record
        const competition = await createCompetitionRecord(competitionData);
        console.log(`Created competition with ID: ${competition.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing competition ${record.name_long}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} new competitions`);
    console.log(`Errors: ${errorCount} competitions`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadNewCompetitionsOnly:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  const args = process.argv.slice(2);
  const mode = args[0] || 'new'; // 'all' or 'new'
  
  if (mode === 'all') {
    uploadCompetitionsFromCSV()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  } else {
    uploadNewCompetitionsOnly()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  }
} 