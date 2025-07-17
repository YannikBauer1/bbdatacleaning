import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';

// Function to parse dates from CSV format
function parseDates(datesString) {
  if (!datesString) return { start_date: null, end_date: null };
  
  const dates = datesString.split(',').map(d => d.trim());
  
  if (dates.length === 1) {
    return { start_date: dates[0], end_date: dates[0] };
  } else if (dates.length === 2) {
    return { start_date: dates[0], end_date: dates[1] };
  }
  
  return { start_date: null, end_date: null };
}

// Function to get event by competition name_key and year
async function getEventByCompetitionAndYear(competitionNameKey, year) {
  try {
    const { data, error } = await supabase
      .from('event')
      .select(`
        id,
        start_date,
        end_date,
        competition!inner(id, name_key)
      `)
      .eq('competition.name_key', competitionNameKey)
      .eq('year', year)
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error(`Error fetching event for competition ${competitionNameKey} year ${year}:`, error);
    return null;
  }
}

// Function to update event dates
async function updateEventDates(eventId, startDate, endDate) {
  try {
    const { data, error } = await supabase
      .from('event')
      .update({
        start_date: startDate,
        end_date: endDate
      })
      .eq('id', eventId)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error(`Error updating event ${eventId}:`, error);
    throw error;
  }
}

export async function updateEventDatesFromCSV(csvFilePath = 'data/clean/schedule2025.csv') {
  try {
    console.log('Starting event dates update from CSV...');
    
    // Read and parse CSV file
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} schedule entries to process`);
    
    let successCount = 0;
    let errorCount = 0;
    let notFoundCount = 0;
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      console.log(`Processing ${i + 1}/${records.length}: ${record.name} (${record.competition_key})`);
      
      try {
        // Get dates directly from the CSV columns
        const start_date = record.start_date;
        const end_date = record.end_date;
        
        if (!start_date || !end_date) {
          console.warn(`Skipping ${record.name} - no valid dates found`);
          continue;
        }
        
        // Get the existing event
        const event = await getEventByCompetitionAndYear(record.competition_key, 2025);
        
        if (!event) {
          console.warn(`Event not found for competition ${record.competition_key} year 2025`);
          notFoundCount++;
          continue;
        }
        
        // Check if dates are already set
        if (event.start_date && event.end_date) {
          console.log(`Event ${event.id} already has dates: ${event.start_date} to ${event.end_date}`);
          continue;
        }
        
        // Update the event with the dates
        const updatedEvent = await updateEventDates(event.id, start_date, end_date);
        console.log(`Updated event ${event.id} with dates: ${start_date} to ${end_date}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing schedule entry ${record.name}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpdate completed!`);
    console.log(`Successfully updated: ${successCount} events`);
    console.log(`Events not found: ${notFoundCount} entries`);
    console.log(`Errors: ${errorCount} entries`);
    
    return { successCount, notFoundCount, errorCount };
    
  } catch (error) {
    console.error('Error in updateEventDatesFromCSV:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  updateEventDatesFromCSV()
    .then(() => console.log('Event dates update completed successfully'))
    .catch(error => console.error('Event dates update failed:', error));
} 