import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';

// Function to map division names from CSV to existing category_type name_keys
function mapDivisionToCategoryType(divisionName) {
  if (!divisionName) return null;
  
  const divisionMap = {
    "Men's Bodybuilding": "mensbb",
    "Women's Bodybuilding": "womensbb",
    "Men's Physique": "mensphysique",
    "Women's Physique": "womensphysique",
    "Men's Classic Physique": "classic",
    "Women's Classic Physique": "classic",
    "Women's Bikini": "bikini",
    "Men's Bikini": "bikini",
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

// Function to get event by competition name_key and year
async function getEventByCompetitionAndYear(competitionNameKey, year) {
  try {
    const { data, error } = await supabase
      .from('event')
      .select(`
        id,
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

// Function to create a new division
async function createDivision(divisionData) {
  try {
    const { data, error } = await supabase
      .from('division')
      .insert(divisionData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating division:', error);
    throw error;
  }
}

// Function to check if division already exists
async function checkDivisionExists(eventId, categoryId) {
  try {
    const { data, error } = await supabase
      .from('division')
      .select('id')
      .eq('event_id', eventId)
      .eq('category_id', categoryId)
      .single();
    
    if (error) {
      return false; // Division doesn't exist
    }
    
    return true; // Division exists
  } catch (error) {
    return false; // Division doesn't exist
  }
}

export async function createMissingDivisions(csvFilePath = 'data/clean/schedule2025.csv') {
  try {
    console.log('Starting to create missing divisions from CSV...');
    
    // Read and parse CSV file
    const csvContent = readFileSync(csvFilePath, 'utf-8');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} schedule entries to process`);
    
    let successCount = 0;
    let errorCount = 0;
    let skippedCount = 0;
    let totalDivisionsCreated = 0;
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      console.log(`Processing ${i + 1}/${records.length}: ${record.name} (${record.competition_key})`);
      
      try {
        // Get the existing event
        const event = await getEventByCompetitionAndYear(record.competition_key, 2025);
        
        if (!event) {
          console.warn(`Event not found for competition ${record.competition_key} year 2025`);
          errorCount++;
          continue;
        }
        
        // Parse divisions from the CSV
        const divisions = parseDivisions(record.division);
        
        if (divisions.length === 0) {
          console.warn(`No divisions found for ${record.name}`);
          skippedCount++;
          continue;
        }
        
        console.log(`  Found ${divisions.length} divisions: ${divisions.join(', ')}`);
        
        // Process each division
        for (const divisionName of divisions) {
          try {
            // Determine category weight
            const categoryWeight = getCategoryWeightFromDivisionType(divisionName);
            
            // Get existing category
            const category = await getExistingCategory(divisionName, categoryWeight);
            
            if (!category) {
              console.warn(`  Skipping division ${divisionName} - category not found`);
              continue;
            }
            
            // Check if division already exists
            const divisionExists = await checkDivisionExists(event.id, category.id);
            
            if (divisionExists) {
              console.log(`  Division ${divisionName} already exists for this event`);
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
            console.log(`  ✅ Created division: ${divisionName} (${categoryWeight})`);
            totalDivisionsCreated++;
            
          } catch (error) {
            console.error(`  Error processing division ${divisionName}:`, error);
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
    
    console.log(`\nDivision creation completed!`);
    console.log(`Successfully processed: ${successCount} events`);
    console.log(`Total divisions created: ${totalDivisionsCreated}`);
    console.log(`Skipped: ${skippedCount} entries`);
    console.log(`Errors: ${errorCount} entries`);
    
    return { successCount, totalDivisionsCreated, skippedCount, errorCount };
    
  } catch (error) {
    console.error('Error in createMissingDivisions:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  createMissingDivisions()
    .then(() => console.log('Missing divisions creation completed successfully'))
    .catch(error => console.error('Missing divisions creation failed:', error));
} 