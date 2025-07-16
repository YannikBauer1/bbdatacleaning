import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';

// Helper function to normalize country names for nationality
function normalizeCountry(country) {
  if (!country) return '';
  return country.toLowerCase().replace(/\s+/g, '-');
}

// Helper function to extract unique countries from location data
function extractNationalities(locationData) {
  if (!locationData) return [];
  
  try {
    const locations = JSON.parse(locationData);
    const countries = locations
      .map(loc => loc.country)
      .filter(country => country && country.trim() !== '');
    
    // Get unique countries and normalize them
    const uniqueCountries = [...new Set(countries)];
    return uniqueCountries.map(normalizeCountry);
  } catch (error) {
    console.warn('Error parsing location data:', error);
    return [];
  }
}

// Helper function to transform location data for the 'from' field
function transformLocationData(locationData) {
  if (!locationData) return [];
  
  try {
    const locations = JSON.parse(locationData);
    return locations.map(loc => ({
      city: loc.city || '',
      state: loc.state || '',
      country: loc.country || ''
    }));
  } catch (error) {
    console.warn('Error parsing location data:', error);
    return [];
  }
}

// Function to create a person record
async function createPerson(personData) {
  try {
    const { data, error } = await supabase
      .from('person')
      .insert(personData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating person:', error);
    throw error;
  }
}

// Function to create an athlete record
async function createAthlete(athleteData) {
  try {
    const { data, error } = await supabase
      .from('athlete')
      .insert(athleteData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating athlete:', error);
    throw error;
  }
}

// Main function to process and upload athletes from CSV
export async function uploadAthletesFromCSV(csvFilePath = 'data/clean/athletes.csv') {
  try {
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} athletes to process`);
    
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      
      try {
        console.log(`Processing athlete ${i + 1}/${records.length}: ${record.name_long}`);
        
        // Extract nationalities from location data
        const nationalities = extractNationalities(record.location);
        
        // Transform location data for 'from' field
        const fromLocations = transformLocationData(record.location);
        
        // Create person data
        const personData = {
          name: record.name_long,
          image_url: null, // Not known
          socials: null, // Not known
          nationality: nationalities,
          sex: record.sex || null, // Will be added to CSV
          name_key: record.name_key,
          name_short: record.name_short,
          from: fromLocations
        };
        
        // Create person record
        const person = await createPerson(personData);
        console.log(`Created person with ID: ${person.id}`);
        
        // Create athlete data
        const athleteData = {
          active: record.active || true, // Will be added to CSV, default to true
          nickname: record.nickname || null,
          height: null, // Not known
          weight: null, // Not known
          person_id: person.id
        };
        
        // Create athlete record
        const athlete = await createAthlete(athleteData);
        console.log(`Created athlete with ID: ${athlete.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing athlete ${record.name_long}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} athletes`);
    console.log(`Errors: ${errorCount} athletes`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadAthletesFromCSV:', error);
    throw error;
  }
}

// Function to check if athletes already exist to avoid duplicates
export async function checkExistingAthletes() {
  try {
    const { data: athletes, error: athleteError } = await supabase
      .from('athlete')
      .select('id, person_id');
    
    if (athleteError) throw athleteError;
    
    const { data: persons, error: personError } = await supabase
      .from('person')
      .select('id, name_key');
    
    if (personError) throw personError;
    
    console.log(`Found ${athletes.length} existing athletes`);
    console.log(`Found ${persons.length} existing persons`);
    
    return {
      athleteIds: athletes.map(a => a.id),
      personIds: persons.map(p => p.id),
      existingNameKeys: persons.map(p => p.name_key)
    };
  } catch (error) {
    console.error('Error checking existing athletes:', error);
    throw error;
  }
}

// Function to upload only new athletes (avoiding duplicates)
export async function uploadNewAthletesOnly(csvFilePath = 'data/clean/athletes.csv') {
  try {
    console.log('Checking existing athletes...');
    const existing = await checkExistingAthletes();
    
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    // Filter out existing athletes
    const newRecords = records.filter(record => 
      !existing.existingNameKeys.includes(record.name_key)
    );
    
    console.log(`Found ${newRecords.length} new athletes out of ${records.length} total`);
    
    if (newRecords.length === 0) {
      console.log('No new athletes to upload');
      return { successCount: 0, errorCount: 0 };
    }
    
    // Process only new records
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < newRecords.length; i++) {
      const record = newRecords[i];
      
      try {
        console.log(`Processing new athlete ${i + 1}/${newRecords.length}: ${record.name_long}`);
        
        // Extract nationalities from location data
        const nationalities = extractNationalities(record.location);
        
        // Transform location data for 'from' field
        const fromLocations = transformLocationData(record.location);
        
        // Create person data
        const personData = {
          name: record.name_long,
          image_url: null,
          socials: null,
          nationality: nationalities,
          sex: record.sex || null,
          name_key: record.name_key,
          name_short: record.name_short,
          from: fromLocations
        };
        
        // Create person record
        const person = await createPerson(personData);
        console.log(`Created person with ID: ${person.id}`);
        
        // Create athlete data
        const athleteData = {
          active: record.active || true,
          nickname: record.nickname || null,
          height: null,
          weight: null,
          person_id: person.id
        };
        
        // Create athlete record
        const athlete = await createAthlete(athleteData);
        console.log(`Created athlete with ID: ${athlete.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing athlete ${record.name_long}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} new athletes`);
    console.log(`Errors: ${errorCount} athletes`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadNewAthletesOnly:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  const args = Deno.args;
  const mode = args[0] || 'new'; // 'all' or 'new'
  
  if (mode === 'all') {
    uploadAthletesFromCSV()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  } else {
    uploadNewAthletesOnly()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  }
} 