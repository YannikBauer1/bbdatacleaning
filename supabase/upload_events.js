import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { createEvent, getCompetitionByNameKey } from './events.js';

// Function to create an event record
async function createEventRecord(eventData) {
  try {
    const { data, error } = await supabase
      .from('event')
      .insert(eventData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating event:', error);
    throw error;
  }
}

// Helper function to build location object
function buildLocationObject(city, state, country) {
  const location = {};
  
  if (city && city.trim() !== '') {
    location.city = city.trim();
  }
  
  if (state && state.trim() !== '') {
    location.state = state.trim();
  }
  
  if (country && country.trim() !== '') {
    location.country = country.trim();
  }
  
  return Object.keys(location).length > 0 ? location : null;
}

// Main function to process and upload events from CSV
export async function uploadEventsFromCSV(csvFilePath = 'data/clean/events.csv') {
  try {
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} events to process`);
    
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      
      try {
        console.log(`Processing event ${i + 1}/${records.length}: ${record.competition_key} ${record.year}`);
        
        // Get competition ID by name_key
        const competition = await getCompetitionByNameKey(record.competition_key);
        if (!competition) {
          console.warn(`Competition not found for key: ${record.competition_key}`);
          errorCount++;
          continue;
        }
        
        // Build location object
        const location = buildLocationObject(
          record.event_city,
          record.event_state,
          record.event_country
        );
        
        // Create event data
        const eventData = {
          end_date: record.end_date || null,
          start_date: record.start_date || null,
          location: location,
          year: parseInt(record.year) || null,
          competition_id: competition.id,
          photos: null, // Not known
          promoter: null, // Not known
          stream: null, // Not known
          edition: null // Not known
        };
        
        // Create event record
        const event = await createEventRecord(eventData);
        console.log(`Created event with ID: ${event.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing event ${record.competition_key} ${record.year}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} events`);
    console.log(`Errors: ${errorCount} events`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadEventsFromCSV:', error);
    throw error;
  }
}

// Function to check if events already exist to avoid duplicates
export async function checkExistingEvents() {
  try {
    const { data: events, error: eventError } = await supabase
      .from('event')
      .select('id, competition_id, year');
    
    if (eventError) throw eventError;
    
    console.log(`Found ${events.length} existing events`);
    
    return {
      eventIds: events.map(e => e.id),
      existingEventKeys: events.map(e => `${e.competition_id}_${e.year}`)
    };
  } catch (error) {
    console.error('Error checking existing events:', error);
    throw error;
  }
}

// Function to upload only new events (avoiding duplicates)
export async function uploadNewEventsOnly(csvFilePath = 'data/clean/events.csv') {
  try {
    console.log('Checking existing events...');
    const existing = await checkExistingEvents();
    
    console.log('Reading CSV file...');
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    
    console.log('Parsing CSV data...');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    // Get all competitions for lookup
    const { data: competitions, error: compError } = await supabase
      .from('competition')
      .select('id, name_key');
    
    if (compError) throw compError;
    
    const competitionMap = {};
    competitions.forEach(comp => {
      competitionMap[comp.name_key] = comp.id;
    });
    
    // Filter out existing events
    const newRecords = records.filter(record => {
      const competitionId = competitionMap[record.competition_key];
      if (!competitionId) return false; // Skip if competition not found
      
      const eventKey = `${competitionId}_${record.year}`;
      return !existing.existingEventKeys.includes(eventKey);
    });
    
    console.log(`Found ${newRecords.length} new events out of ${records.length} total`);
    
    if (newRecords.length === 0) {
      console.log('No new events to upload');
      return { successCount: 0, errorCount: 0 };
    }
    
    // Process only new records
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < newRecords.length; i++) {
      const record = newRecords[i];
      
      try {
        console.log(`Processing new event ${i + 1}/${newRecords.length}: ${record.competition_key} ${record.year}`);
        
        // Get competition ID by name_key
        const competition = await getCompetitionByNameKey(record.competition_key);
        if (!competition) {
          console.warn(`Competition not found for key: ${record.competition_key}`);
          errorCount++;
          continue;
        }
        
        // Build location object
        const location = buildLocationObject(
          record.event_city,
          record.event_state,
          record.event_country
        );
        
        // Create event data
        const eventData = {
          end_date: record.end_date || null,
          start_date: record.start_date || null,
          location: location,
          year: parseInt(record.year) || null,
          competition_id: competition.id,
          photos: null, // Not known
          promoter: null, // Not known
          stream: null, // Not known
          edition: null // Not known
        };
        
        // Create event record
        const event = await createEventRecord(eventData);
        console.log(`Created event with ID: ${event.id}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing event ${record.competition_key} ${record.year}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} new events`);
    console.log(`Errors: ${errorCount} events`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadNewEventsOnly:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  const args = process.argv.slice(2);
  const mode = args[0] || 'new'; // 'all' or 'new'
  
  if (mode === 'all') {
    uploadEventsFromCSV()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  } else {
    uploadNewEventsOnly()
      .then(() => console.log('Upload completed successfully'))
      .catch(error => console.error('Upload failed:', error));
  }
} 