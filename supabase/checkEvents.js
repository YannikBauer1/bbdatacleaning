import supabase from './supabase_client.js';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// Helper function to fetch all event records with pagination
async function fetchAllEvents() {
  const allEvents = [];
  let from = 0;
  const pageSize = 1000; // Supabase default limit
  
  while (true) {
    const { data: events, error: fetchError } = await supabase
      .from('event')
      .select('id, location')
      .range(from, from + pageSize - 1);
    
    if (fetchError) {
      throw new Error(`Error fetching events: ${fetchError.message}`);
    }
    
    if (!events || events.length === 0) {
      break; // No more records
    }
    
    allEvents.push(...events);
    console.log(`Fetched ${events.length} events (total so far: ${allEvents.length})`);
    
    if (events.length < pageSize) {
      break; // Last page
    }
    
    from += pageSize;
  }
  
  return allEvents;
}

// Helper function to normalize location name for image search
function normalizeLocationName(locationName) {
  if (!locationName || typeof locationName !== 'string') return '';
  
  return locationName
    .toLowerCase()
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/[^\w\-]/g, '') // Remove special characters except hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
    .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
}

// Helper function to check if location image exists in background bucket
async function checkLocationImage(locationName) {
  try {
    if (!locationName) return false;
    
    const normalizedName = normalizeLocationName(locationName);
    
    // Check if location image exists in the locations folder
    const { data, error } = await supabase.storage
      .from('background')
      .list('locations', {
        search: normalizedName
      });
    
    if (error) {
      console.error(`Error checking location image for ${locationName}:`, error);
      return false;
    }
    
    // Check if any file matches the location name
    const hasImage = data.some(file => {
      const fileName = file.name.toLowerCase();
      return fileName.includes(normalizedName) ||
             fileName.includes(normalizedName.replace('-', '_')) ||
             fileName.includes(normalizedName.replace('-', ''));
    });
    
    return hasImage;
  } catch (error) {
    console.error(`Error checking location image for ${locationName}:`, error);
    return false;
  }
}

// Helper function to parse location JSON
function parseLocation(locationData) {
  if (!locationData) return null;
  
  try {
    // If it's already an object, return it
    if (typeof locationData === 'object') {
      return locationData;
    }
    
    // If it's a string, try to parse it as JSON
    if (typeof locationData === 'string') {
      return JSON.parse(locationData);
    }
    
    return null;
  } catch (error) {
    console.warn('Error parsing location data:', error);
    return null;
  }
}

// Helper function to write missing locations JSON files
function writeMissingLocationsJson(missingLocationsData, completeFailuresData) {
  try {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);
    
    // Write simple list of all missing location names
    const simpleListPath = join(__dirname, '..', 'all', 'jsons', 'missing_location_names.json');
    const simpleList = {
      totalMissingLocations: missingLocationsData.locations.length,
      timestamp: new Date().toISOString(),
      locationNames: missingLocationsData.locations.map(loc => loc.locationName)
    };
    writeFileSync(simpleListPath, JSON.stringify(simpleList, null, 2), 'utf8');
    console.log(`Simple missing locations list written to: ${simpleListPath}`);
    
    // Write complete failures (no image at any level)
    const completeFailuresPath = join(__dirname, '..', 'all', 'jsons', 'complete_location_failures.json');
    writeFileSync(completeFailuresPath, JSON.stringify(completeFailuresData, null, 2), 'utf8');
    console.log(`Complete location failures written to: ${completeFailuresPath}`);
    
  } catch (error) {
    console.error('Error writing missing locations JSON:', error);
  }
}

// Main function to check event locations and find missing images
export async function checkEventLocations() {
  try {
    console.log('Starting event location image checking...');
    
    // Fetch all event records with pagination
    const events = await fetchAllEvents();
    
    console.log(`Found ${events.length} event records to process`);
    
    const results = {
      processed: 0,
      eventsWithLocation: 0,
      eventsWithoutLocation: 0,
      missingImages: [],
      missingImagesWithEventIds: {},
      completeFailures: [], // Events with no image at any level
      locationTypes: {
        city: 0,
        state: 0,
        country: 0,
        noLocation: 0
      }
    };
    
    // Process each event
    for (const event of events) {
      try {
        results.processed++;
        
        // Parse location data
        const location = parseLocation(event.location);
        
        if (!location) {
          results.eventsWithoutLocation++;
          results.locationTypes.noLocation++;
          console.log(`Event ${event.id}: No location data`);
          continue;
        }
        
        results.eventsWithLocation++;
        
        let locationName = null;
        let locationType = null;
        let hasImage = false;
        let checkedLevels = [];
        let hasAnyImage = false;
        
        // Check all available levels and track what we checked
        if (location.city && location.city.trim()) {
          const cityName = location.city.trim();
          const cityHasImage = await checkLocationImage(cityName);
          checkedLevels.push({ name: cityName, type: 'city', hasImage: cityHasImage });
          
          if (cityHasImage) {
            locationName = cityName;
            locationType = 'city';
            hasImage = true;
            hasAnyImage = true;
            results.locationTypes.city++;
          }
        }
        
        if (location.state && location.state.trim()) {
          const stateName = location.state.trim();
          const stateHasImage = await checkLocationImage(stateName);
          checkedLevels.push({ name: stateName, type: 'state', hasImage: stateHasImage });
          
          if (!hasImage && stateHasImage) {
            locationName = stateName;
            locationType = 'state';
            hasImage = true;
            hasAnyImage = true;
            results.locationTypes.state++;
          } else if (stateHasImage) {
            hasAnyImage = true;
          }
        }
        
        if (location.country && location.country.trim()) {
          const countryName = location.country.trim();
          const countryHasImage = await checkLocationImage(countryName);
          checkedLevels.push({ name: countryName, type: 'country', hasImage: countryHasImage });
          
          if (!hasImage && countryHasImage) {
            locationName = countryName;
            locationType = 'country';
            hasImage = true;
            hasAnyImage = true;
            results.locationTypes.country++;
          } else if (countryHasImage) {
            hasAnyImage = true;
          }
        }
        
        // If no location data at all
        if (checkedLevels.length === 0) {
          results.locationTypes.noLocation++;
          console.log(`Event ${event.id}: No valid location data`);
          continue;
        }
        
        // If we found an image at any level, use the best one
        if (hasImage) {
          console.log(`Event ${event.id}: Found image for ${locationType} "${locationName}"`);
        } else {
          // No image found at any level - this is a complete failure
          results.completeFailures.push({
            eventId: event.id,
            fullLocation: location,
            checkedLevels: checkedLevels
          });
          
          // Also track individual missing locations for the simple list
          for (const level of checkedLevels) {
            if (!level.hasImage) {
              results.missingImages.push({
                eventId: event.id,
                locationName: level.name,
                locationType: level.type,
                fullLocation: location
              });
              
              // Track by location name for JSON output
              if (!results.missingImagesWithEventIds[level.name]) {
                results.missingImagesWithEventIds[level.name] = {
                  locationName: level.name,
                  locationType: level.type,
                  eventIds: [],
                  count: 0
                };
              }
              results.missingImagesWithEventIds[level.name].eventIds.push(event.id);
              results.missingImagesWithEventIds[level.name].count++;
            }
          }
          
          console.log(`Event ${event.id}: No image found for any level - complete failure`);
        }
        
      } catch (error) {
        console.error(`Error processing event ${event.id}:`, error);
      }
    }
    
    // Write missing locations data to JSON files
    if (results.missingImages.length > 0) {
      const missingLocationsData = {
        totalMissingImages: results.missingImages.length,
        timestamp: new Date().toISOString(),
        locationTypes: results.locationTypes,
        locations: Object.values(results.missingImagesWithEventIds)
          .sort((a, b) => b.count - a.count) // Sort by count descending
      };
      
      const completeFailuresData = {
        totalCompleteFailures: results.completeFailures.length,
        timestamp: new Date().toISOString(),
        events: results.completeFailures
      };
      
      writeMissingLocationsJson(missingLocationsData, completeFailuresData);
    }
    
    // Print summary
    console.log('\n=== EVENT LOCATION IMAGE CHECKING SUMMARY ===');
    console.log(`Total events processed: ${results.processed}`);
    console.log(`Events with location data: ${results.eventsWithLocation}`);
    console.log(`Events without location data: ${results.eventsWithoutLocation}`);
    console.log(`Missing images found: ${results.missingImages.length}`);
    console.log(`Complete failures (no image at any level): ${results.completeFailures.length}`);
    console.log('\nLocation types breakdown:');
    console.log(`  - City locations: ${results.locationTypes.city}`);
    console.log(`  - State locations: ${results.locationTypes.state}`);
    console.log(`  - Country locations: ${results.locationTypes.country}`);
    console.log(`  - No location data: ${results.locationTypes.noLocation}`);
    
    if (results.missingImages.length > 0) {
      console.log('\nTop 10 missing location images:');
      const topMissing = Object.values(results.missingImagesWithEventIds)
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);
      
      topMissing.forEach(location => {
        console.log(`  - ${location.locationName} (${location.locationType}): ${location.count} events`);
      });
    }
    
    if (results.completeFailures.length > 0) {
      console.log('\nSample complete failures (no image at any level):');
      results.completeFailures.slice(0, 5).forEach(failure => {
        console.log(`  - Event ${failure.eventId}: ${JSON.stringify(failure.fullLocation)}`);
      });
    }
    
    return results;
    
  } catch (error) {
    console.error('Error in checkEventLocations:', error);
    throw error;
  }
}

// Function to get statistics about event locations
export async function getEventLocationStats() {
  try {
    const events = await fetchAllEvents();
    
    const stats = {
      totalEvents: events.length,
      eventsWithLocation: 0,
      eventsWithoutLocation: 0,
      locationTypes: {
        city: 0,
        state: 0,
        country: 0,
        noLocation: 0
      },
      uniqueLocations: new Set(),
      locationCounts: {}
    };
    
    for (const event of events) {
      const location = parseLocation(event.location);
      
      if (!location) {
        stats.eventsWithoutLocation++;
        stats.locationTypes.noLocation++;
        continue;
      }
      
      stats.eventsWithLocation++;
      
      let locationName = null;
      let locationType = null;
      
      if (location.city && location.city.trim()) {
        locationName = location.city.trim();
        locationType = 'city';
        stats.locationTypes.city++;
      } else if (location.state && location.state.trim()) {
        locationName = location.state.trim();
        locationType = 'state';
        stats.locationTypes.state++;
      } else if (location.country && location.country.trim()) {
        locationName = location.country.trim();
        locationType = 'country';
        stats.locationTypes.country++;
      } else {
        stats.locationTypes.noLocation++;
        continue;
      }
      
      if (locationName) {
        stats.uniqueLocations.add(locationName);
        const key = `${locationName} (${locationType})`;
        stats.locationCounts[key] = (stats.locationCounts[key] || 0) + 1;
      }
    }
    
    console.log('\n=== EVENT LOCATION STATISTICS ===');
    console.log(`Total events: ${stats.totalEvents}`);
    console.log(`Events with location: ${stats.eventsWithLocation}`);
    console.log(`Events without location: ${stats.eventsWithoutLocation}`);
    console.log(`Unique locations: ${stats.uniqueLocations.size}`);
    console.log('\nLocation types breakdown:');
    console.log(`  - City locations: ${stats.locationTypes.city}`);
    console.log(`  - State locations: ${stats.locationTypes.state}`);
    console.log(`  - Country locations: ${stats.locationTypes.country}`);
    console.log(`  - No location data: ${stats.locationTypes.noLocation}`);
    
    console.log('\nTop 10 most common locations:');
    const topLocations = Object.entries(stats.locationCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
    
    topLocations.forEach(([location, count]) => {
      console.log(`  - ${location}: ${count} events`);
    });
    
    return stats;
    
  } catch (error) {
    console.error('Error getting event location stats:', error);
    throw error;
  }
}

// Run the checking function if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('Running event location image checking...');
  
  // First get stats
  await getEventLocationStats();
  
  // Then check for missing images
  await checkEventLocations();
  
  console.log('Event location image checking completed!');
}
