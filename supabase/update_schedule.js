import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';

// Function to get event by competition name_key and year
async function getEventByCompetitionAndYear(competitionNameKey, year) {
  try {
    const { data, error } = await supabase
      .from('event')
      .select(`
        id,
        ifbb_url,
        competition!inner(id, name)
      `)
      .eq('competition.name', competitionNameKey)
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

// Function to update event URL
async function updateEventUrl(eventId, newUrl) {
  try {
    const { data, error } = await supabase
      .from('event')
      .update({ ifbb_url: newUrl })
      .eq('id', eventId)
      .select('id, ifbb_url')
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error(`Error updating URL for event ${eventId}:`, error);
    throw error;
  }
}

// Main function to update schedule URLs from JSON file
export async function updateScheduleUrls(jsonFilePath = 'data/clean/schedule2025.json') {
  try {
    console.log('Reading schedule JSON file...');
    const scheduleData = JSON.parse(readFileSync(jsonFilePath, 'utf-8'));
    
    console.log(`Found ${Object.keys(scheduleData).length} schedule entries to process`);
    
    let successCount = 0;
    let errorCount = 0;
    let notFoundCount = 0;
    let noUrlCount = 0;
    
    for (const [competitionKey, scheduleEntry] of Object.entries(scheduleData)) {
      try {
        console.log(`Processing: ${competitionKey} (${scheduleEntry.name})`);
        
        // Skip if no URL in schedule entry
        if (!scheduleEntry.url || scheduleEntry.url.trim() === '') {
          console.log(`  No URL provided for ${competitionKey}`);
          noUrlCount++;
          continue;
        }
        
        // Get the year from the schedule entry
        const year = parseInt(scheduleEntry.year);
        if (!year) {
          console.log(`  Invalid year for ${competitionKey}: ${scheduleEntry.year}`);
          errorCount++;
          continue;
        }
        
        // Find the event by competition name key and year
        const event = await getEventByCompetitionAndYear(competitionKey, year);
        
        if (!event) {
          console.log(`  Event not found for ${competitionKey} year ${year}`);
          notFoundCount++;
          continue;
        }
        
        // Update the event URL
        const updatedEvent = await updateEventUrl(event.id, scheduleEntry.url);
        console.log(`  Updated URL for ${competitionKey}: ${updatedEvent.url}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`  Error processing ${competitionKey}:`, error);
        errorCount++;
      }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('UPDATE SCHEDULE URLS SUMMARY:');
    console.log(`Total schedule entries: ${Object.keys(scheduleData).length}`);
    console.log(`Successfully updated: ${successCount} events`);
    console.log(`Events not found: ${notFoundCount} events`);
    console.log(`Entries with no URL: ${noUrlCount} entries`);
    console.log(`Errors: ${errorCount} events`);
    
    return {
      totalEntries: Object.keys(scheduleData).length,
      successCount,
      notFoundCount,
      noUrlCount,
      errorCount
    };
    
  } catch (error) {
    console.error('Error in updateScheduleUrls:', error);
    throw error;
  }
}

// Function to update URLs for specific competitions only
export async function updateSpecificCompetitionUrls(competitionKeys, jsonFilePath = 'data/clean/schedule2025.json') {
  try {
    console.log('Reading schedule JSON file...');
    const scheduleData = JSON.parse(readFileSync(jsonFilePath, 'utf-8'));
    
    console.log(`Processing ${competitionKeys.length} specific competitions...`);
    
    let successCount = 0;
    let errorCount = 0;
    let notFoundCount = 0;
    let noUrlCount = 0;
    
    for (const competitionKey of competitionKeys) {
      try {
        const scheduleEntry = scheduleData[competitionKey];
        if (!scheduleEntry) {
          console.log(`  Schedule entry not found for ${competitionKey}`);
          errorCount++;
          continue;
        }
        
        console.log(`Processing: ${competitionKey} (${scheduleEntry.name})`);
        
        // Skip if no URL in schedule entry
        if (!scheduleEntry.url || scheduleEntry.url.trim() === '') {
          console.log(`  No URL provided for ${competitionKey}`);
          noUrlCount++;
          continue;
        }
        
        // Get the year from the schedule entry
        const year = parseInt(scheduleEntry.year);
        if (!year) {
          console.log(`  Invalid year for ${competitionKey}: ${scheduleEntry.year}`);
          errorCount++;
          continue;
        }
        
        // Find the event by competition name key and year
        const event = await getEventByCompetitionAndYear(competitionKey, year);
        
        if (!event) {
          console.log(`  Event not found for ${competitionKey} year ${year}`);
          notFoundCount++;
          continue;
        }
      
        
        // Update the event URL
        const updatedEvent = await updateEventUrl(event.id, scheduleEntry.url);
        console.log(`  Updated URL for ${competitionKey}: ${updatedEvent.ifbb_url}`);
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`  Error processing ${competitionKey}:`, error);
        errorCount++;
      }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('UPDATE SPECIFIC COMPETITION URLS SUMMARY:');
    console.log(`Total competitions to process: ${competitionKeys.length}`);
    console.log(`Successfully updated: ${successCount} events`);
    console.log(`Events not found: ${notFoundCount} events`);
    console.log(`Entries with no URL: ${noUrlCount} entries`);
    console.log(`Errors: ${errorCount} events`);
    
    return {
      totalCompetitions: competitionKeys.length,
      successCount,
      notFoundCount,
      noUrlCount,
      errorCount
    };
    
  } catch (error) {
    console.error('Error in updateSpecificCompetitionUrls:', error);
    throw error;
  }
}

// Function to check which competitions have URLs in schedule but not in events
export async function checkMissingUrls(jsonFilePath = 'data/clean/schedule2025.json') {
  try {
    console.log('Reading schedule JSON file...');
    const scheduleData = JSON.parse(readFileSync(jsonFilePath, 'utf-8'));
    
    console.log(`Checking ${Object.keys(scheduleData).length} schedule entries for missing URLs...`);
    
    const missingUrls = [];
    const alreadyHaveUrls = [];
    const noScheduleUrl = [];
    
    for (const [competitionKey, scheduleEntry] of Object.entries(scheduleData)) {
      try {
        // Skip if no URL in schedule entry
        if (!scheduleEntry.url || scheduleEntry.url.trim() === '') {
          noScheduleUrl.push(competitionKey);
          continue;
        }
        
        const year = parseInt(scheduleEntry.year);
        if (!year) {
          console.log(`  Invalid year for ${competitionKey}: ${scheduleEntry.year}`);
          continue;
        }
        
        // Find the event by competition name key and year
        const event = await getEventByCompetitionAndYear(competitionKey, year);
        
        if (!event) {
          missingUrls.push({
            competitionKey,
            name: scheduleEntry.name,
            year,
            scheduleUrl: scheduleEntry.url
          });
          continue;
        }
        
        // Check if event already has a URL
        if (event.ifbb_url && event.ifbb_url.trim() !== '') {
          alreadyHaveUrls.push({
            competitionKey,
            name: scheduleEntry.name,
            year,
            eventUrl: event.ifbb_url,
            scheduleUrl: scheduleEntry.url,
            needsUpdate: event.ifbb_url !== scheduleEntry.url
          });
        } else {
          missingUrls.push({
            competitionKey,
            name: scheduleEntry.name,
            year,
            scheduleUrl: scheduleEntry.url
          });
        }
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 50));
        
      } catch (error) {
        console.error(`  Error checking ${competitionKey}:`, error);
      }
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('MISSING URLS ANALYSIS:');
    console.log(`Total schedule entries: ${Object.keys(scheduleData).length}`);
    console.log(`Events missing URLs: ${missingUrls.length}`);
    console.log(`Events already have URLs: ${alreadyHaveUrls.length}`);
    console.log(`Schedule entries with no URL: ${noScheduleUrl.length}`);
    
    if (missingUrls.length > 0) {
      console.log('\nEvents missing URLs:');
      missingUrls.forEach(item => {
        console.log(`  ${item.competitionKey} (${item.name}) - ${item.year}`);
      });
    }
    
    const needsUpdate = alreadyHaveUrls.filter(item => item.needsUpdate);
    if (needsUpdate.length > 0) {
      console.log('\nEvents that need URL updates:');
      needsUpdate.forEach(item => {
        console.log(`  ${item.competitionKey} (${item.name}) - ${item.year}`);
        console.log(`    Current: ${item.eventUrl}`);
        console.log(`    Schedule: ${item.scheduleUrl}`);
      });
    }
    
    return {
      totalEntries: Object.keys(scheduleData).length,
      missingUrls,
      alreadyHaveUrls,
      noScheduleUrl,
      needsUpdate
    };
    
  } catch (error) {
    console.error('Error in checkMissingUrls:', error);
    throw error;
  }
}

// Example usage:
await updateScheduleUrls();
// await updateSpecificCompetitionUrls(['arnold_classic', 'olympia']);
// await checkMissingUrls();
