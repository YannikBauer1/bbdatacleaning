import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { createCompetition, getCompetitionByNameKey } from './competition.js';
import { createEvent } from './events.js';
import { createDivision, getDivisionByEventAndCategory } from './results.js';

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

// Function to map division names from CSV to existing category_type name_keys
function mapDivisionToCategoryType(divisionName) {
  if (!divisionName) return null;
  
  const divisionMap = {
    "Men's Bodybuilding": "mensbb",
    "Women's Bodybuilding": "womensbb",
    "Men's Physique": "mensphysique",
    "Women's Physique": "womensphysique",
    "Men's Classic Physique": "classic",
    "Women's Classic Physique": "classic", // Note: This might need adjustment
    "Women's Bikini": "bikini",
    "Men's Bikini": "bikini", // Note: This might need adjustment
    "Figure": "figure",
    "Women's Figure": "figure",
    "Fitness": "fitness",
    "Women's Fitness": "fitness",
    "Wellness": "wellness",
    "Women's Wellness": "wellness",
    "212": "202_212",
    "212 Bodybuilding": "202_212",
    "Men's 212 Bodybuilding": "202_212",
    "Wheelchair": "wheelchair",
    "Men's Wheelchair": "wheelchair"
  };
  
  return divisionMap[divisionName] || null;
}

// Function to get existing category by division name and weight
async function getExistingCategory(divisionName, weightName = 'Open') {
  try {
    // Map division name to category_type name_key
    const categoryTypeKey = mapDivisionToCategoryType(divisionName);
    
    if (!categoryTypeKey) {
      console.warn(`No mapping found for division: ${divisionName}`);
      return null;
    }
    
    // Get category_type by name_key
    const { data: categoryType, error: typeError } = await supabase
      .from('category_type')
      .select('id')
      .eq('name_key', categoryTypeKey)
      .single();
    
    if (typeError) {
      console.warn(`Category type not found for key: ${categoryTypeKey}`);
      return null;
    }
    
    // Get category_weight by name
    const { data: categoryWeight, error: weightError } = await supabase
      .from('category_weight')
      .select('id')
      .eq('name', weightName)
      .single();
    
    if (weightError) {
      console.warn(`Category weight not found for: ${weightName}`);
      return null;
    }
    
    // Get category by both IDs
    const { data: category, error: categoryError } = await supabase
      .from('category')
      .select('id')
      .eq('category_type_id', categoryType.id)
      .eq('category_weight_id', categoryWeight.id)
      .single();
    
    if (categoryError) {
      console.warn(`Category not found for type: ${categoryTypeKey} and weight: ${weightName}`);
      return null;
    }
    
    return category;
    
  } catch (error) {
    console.error('Error getting existing category:', error);
    return null;
  }
}

// Function to determine category weight from division type
function getCategoryWeightFromDivisionType(divisionType) {
  if (!divisionType) return 'Open';
  
  const divisionTypeStr = divisionType.toUpperCase();
  
  if (divisionTypeStr.includes('212')) {
    return '212';
  }
  
  return 'Open';
}

// Function to parse comma-separated divisions
function parseDivisions(divisionsString) {
  if (!divisionsString) return [];
  
  return divisionsString
    .split(',')
    .map(div => div.trim())
    .filter(div => div.length > 0);
}

// Function to parse dates
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

export async function uploadSchedule2025FromCSV(csvFilePath = 'data/clean/schedule2025.csv') {
  try {
    console.log('Starting schedule2025 upload from CSV...');
    
    // Read and parse CSV file
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} schedule entries to process`);
    
    // Caches to avoid duplicate database calls
    const competitionCache = new Map();
    const eventCache = new Map();
    const divisionCache = new Map();
    
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      console.log(`Processing ${i + 1}/${records.length}: ${record.name}`);
      
      try {
        // Parse dates
        const { start_date, end_date } = parseDates(record.dates);
        
        // Get or create competition
        let competition;
        const competitionKey = record.competition_key;
        
        if (competitionCache.has(competitionKey)) {
          competition = competitionCache.get(competitionKey);
        } else {
          try {
            competition = await getCompetitionByNameKey(competitionKey);
            competitionCache.set(competitionKey, competition);
          } catch (error) {
            // Competition doesn't exist, create it
            const competitionData = {
              name: record.name,
              name_key: competitionKey,
              name_short: record.name,
              organization: 'IFBB Pro',
              image_url: null,
              socials: null
            };
            
            competition = await createCompetition(competitionData);
            competitionCache.set(competitionKey, competition);
            console.log(`Created competition with ID: ${competition.id}`);
          }
        }
        
        // Build location object
        const location = buildLocationObject(
          record.location_city,
          record.location_state,
          record.location_country
        );
        
        // Create event
        const eventData = {
          competition_id: competition.id,
          year: 2025,
          start_date: start_date,
          end_date: end_date,
          location: location,
          promoter_name: record.promoter_name,
          promoter_email: record.promoter_email,
          promoter_website: record.promoter_website,
          stream: null,
          edition: null,
          photos_title: null,
          photos_all: null
        };
        
        const event = await createEvent(eventData);
        console.log(`Created event with ID: ${event.id}`);
        
        // Parse divisions
        const divisions = parseDivisions(record.divisions);
        const categoryWeight = getCategoryWeightFromDivisionType(record.divisions);
        
        for (const divisionName of divisions) {
          try {
            // Get existing category
            const category = await getExistingCategory(divisionName, categoryWeight);
            
            if (!category) {
              console.warn(`Skipping division ${divisionName} - category not found`);
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
                  start_time: null,
                  end_time: null,
                  order: null,
                  description: null,
                  timezone: null
                };
                
                division = await createDivision(divisionData);
                divisionCache.set(divisionKey, division);
                console.log(`Created division with ID: ${division.id}`);
              }
            }
            
          } catch (error) {
            console.error(`Error processing division ${divisionName}:`, error);
            errorCount++;
          }
        }
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing schedule entry ${record.name}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} schedule entries`);
    console.log(`Errors: ${errorCount} entries`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadSchedule2025FromCSV:', error);
    throw error;
  }
}

export async function uploadNewSchedule2025Only(csvFilePath = 'data/clean/schedule2025.csv') {
  try {
    console.log('Starting new schedule2025 upload (new entries only)...');
    
    // Read and parse CSV file
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} schedule entries to process`);
    
    // Caches to avoid duplicate database calls
    const competitionCache = new Map();
    const eventCache = new Map();
    const divisionCache = new Map();
    
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      console.log(`Processing ${i + 1}/${records.length}: ${record.name}`);
      
      try {
        // Parse dates
        const { start_date, end_date } = parseDates(record.dates);
        
        // Get or create competition
        let competition;
        const competitionKey = record.competition_key;
        
        if (competitionCache.has(competitionKey)) {
          competition = competitionCache.get(competitionKey);
        } else {
          try {
            competition = await getCompetitionByNameKey(competitionKey);
            competitionCache.set(competitionKey, competition);
          } catch (error) {
            // Competition doesn't exist, create it
            const competitionData = {
              name: record.name,
              name_key: competitionKey,
              name_short: record.name,
              organization: 'IFBB Pro',
              image_url: null,
              socials: null
            };
            
            competition = await createCompetition(competitionData);
            competitionCache.set(competitionKey, competition);
            console.log(`Created competition with ID: ${competition.id}`);
          }
        }
        
        // Build location object
        const location = buildLocationObject(
          record.location_city,
          record.location_state,
          record.location_country
        );
        
        // Create event
        const eventData = {
          competition_id: competition.id,
          year: 2025,
          start_date: start_date,
          end_date: end_date,
          location: location,
          promoter_name: record.promoter_name,
          promoter_email: record.promoter_email,
          promoter_website: record.promoter_website,
          stream: null,
          edition: null,
          photos_title: null,
          photos_all: null
        };
        
        const event = await createEvent(eventData);
        console.log(`Created event with ID: ${event.id}`);
        
        // Parse divisions
        const divisions = parseDivisions(record.divisions);
        const categoryWeight = getCategoryWeightFromDivisionType(record.divisions);
        
        for (const divisionName of divisions) {
          try {
            // Get existing category
            const category = await getExistingCategory(divisionName, categoryWeight);
            
            if (!category) {
              console.warn(`Skipping division ${divisionName} - category not found`);
              continue;
            }
            
            // Create division
            const divisionData = {
              event_id: event.id,
              category_id: category.id,
              start_time: null,
              end_time: null,
              order: null,
              description: null,
              timezone: null
            };
            
            const division = await createDivision(divisionData);
            console.log(`Created division with ID: ${division.id}`);
            
          } catch (error) {
            console.error(`Error processing division ${divisionName}:`, error);
            errorCount++;
          }
        }
        
        successCount++;
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing schedule entry ${record.name}:`, error);
        errorCount++;
      }
    }
    
    console.log(`\nUpload completed!`);
    console.log(`Successfully processed: ${successCount} new schedule entries`);
    console.log(`Errors: ${errorCount} entries`);
    
    return { successCount, errorCount };
    
  } catch (error) {
    console.error('Error in uploadNewSchedule2025Only:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  const args = Deno.args;
  const mode = args[0] || 'new'; // 'all' or 'new'
  
  if (mode === 'all') {
    uploadSchedule2025FromCSV()
      .then(() => console.log('Schedule2025 upload completed successfully'))
      .catch(error => console.error('Schedule2025 upload failed:', error));
  } else {
    uploadNewSchedule2025Only()
      .then(() => console.log('Schedule2025 upload completed successfully'))
      .catch(error => console.error('Schedule2025 upload failed:', error));
  }
} 