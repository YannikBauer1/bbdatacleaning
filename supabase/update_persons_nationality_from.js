import supabase from './supabase_client.js';

// Helper function to clean nationality string by removing ", 7" and similar patterns
function cleanNationality(nationality) {
  if (!nationality || typeof nationality !== 'string') return '';
  
  // Remove patterns like ", 7", ", 5", etc. and trim whitespace
  let cleaned = nationality
    .replace(/,\s*\d+/g, '') // Remove ", 7", ", 5", etc.
    .replace(/,\s*$/g, '') // Remove trailing commas
    .trim(); // Trim whitespace
  
  // Standardize country names
  const countryMappings = {
    'usa': 'United States',
    'us': 'United States',
    'u.s.': 'United States',
    'u.s.a.': 'United States',
    'united states of america': 'United States',
    'uk': 'United Kingdom',
    'u.k.': 'United Kingdom',
    'united kingdom of great britain and northern ireland': 'United Kingdom',
    'great britain': 'United Kingdom',
    'england': 'United Kingdom',
    'scotland': 'United Kingdom',
    'wales': 'United Kingdom',
    'northern ireland': 'United Kingdom',
    'bosnia & herzegovina': 'Bosnia and Herzegovina',
    'bosnia and herzegovina': 'Bosnia and Herzegovina',
    'antigua & barbuda': 'Antigua and Barbuda',
    'antigua and barbuda': 'Antigua and Barbuda',
    'trinidad & tobago': 'Trinidad and Tobago',
    'trinidad and tobago': 'Trinidad and Tobago',
    'st lucia': 'Saint Lucia',
    'st. lucia': 'Saint Lucia',
    'cape verde': 'Cabo Verde',
    'curaçao': 'Curacao',
    'faroe islandss': 'Faroe Islands',
    'germay': 'Germany',
    'north africa': 'Africa',
    'south wales': 'Wales',
    'west roxbury': 'United States',
    'boston west roxbury': 'United States',
    'tahiti': 'French Polynesia',
    'yugoslavia': 'Serbia',
    'rhodesia': 'Zimbabwe',
    'macedonia': 'North Macedonia'
  };
  
  // Check for exact matches in mappings (case-insensitive)
  const lowerCleaned = cleaned.toLowerCase();
  if (countryMappings[lowerCleaned]) {
    return countryMappings[lowerCleaned];
  }
  
  // Handle lowercase entries with hyphens (e.g., "united-states" -> "United States")
  if (cleaned === cleaned.toLowerCase() && cleaned.includes('-')) {
    cleaned = cleaned
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  
  // Handle all lowercase entries (e.g., "vietnam" -> "Vietnam")
  if (cleaned === cleaned.toLowerCase() && !cleaned.includes('-')) {
    cleaned = cleaned
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  
  // Handle mixed case entries that need standardization
  if (cleaned.includes(' And ') || cleaned.includes(' & ')) {
    cleaned = cleaned.replace(/ And /g, ' and ').replace(/ & /g, ' and ');
  }
  
  return cleaned;
}

// Helper function to clean from object entries
function cleanFromEntry(fromEntry) {
  if (!fromEntry || typeof fromEntry !== 'object') return fromEntry;
  
  const cleaned = { ...fromEntry };
  
  // Clean country field if it exists
  if (cleaned.country && typeof cleaned.country === 'string') {
    cleaned.country = cleanNationality(cleaned.country);
  }
  
  // Clean city field if it exists
  if (cleaned.city && typeof cleaned.city === 'string') {
    cleaned.city = cleanNationality(cleaned.city);
  }
  
  // Clean state field if it exists
  if (cleaned.state && typeof cleaned.state === 'string') {
    cleaned.state = cleanNationality(cleaned.state);
  }
  
  return cleaned;
}

// Helper function to deduplicate nationality array
function deduplicateNationalities(nationalities) {
  if (!Array.isArray(nationalities)) return [];
  
  const seen = new Set();
  const deduplicated = [];
  
  for (const nationality of nationalities) {
    const cleaned = cleanNationality(nationality);
    if (cleaned && !seen.has(cleaned.toLowerCase())) {
      seen.add(cleaned.toLowerCase());
      deduplicated.push(cleaned);
    }
  }
  
  return deduplicated;
}

// Helper function to deduplicate from array
function deduplicateFrom(fromArray) {
  if (!Array.isArray(fromArray)) return [];
  
  const seen = new Set();
  const deduplicated = [];
  
  for (const fromEntry of fromArray) {
    const cleaned = cleanFromEntry(fromEntry);
    
    // Create a key for comparison (city, state, country)
    const key = `${cleaned.city || ''}|${cleaned.state || ''}|${cleaned.country || ''}`;
    
    if (!seen.has(key)) {
      seen.add(key);
      deduplicated.push(cleaned);
    }
  }
  
  return deduplicated;
}

// Helper function to fetch all person records with pagination
async function fetchAllPersons() {
  const allPersons = [];
  let from = 0;
  const pageSize = 1000; // Supabase default limit
  
  while (true) {
    const { data: persons, error: fetchError } = await supabase
      .from('person')
      .select('id, nationality, from')
      .range(from, from + pageSize - 1);
    
    if (fetchError) {
      throw new Error(`Error fetching persons: ${fetchError.message}`);
    }
    
    if (!persons || persons.length === 0) {
      break; // No more records
    }
    
    allPersons.push(...persons);
    console.log(`Fetched ${persons.length} persons (total so far: ${allPersons.length})`);
    
    if (persons.length < pageSize) {
      break; // Last page
    }
    
    from += pageSize;
  }
  
  return allPersons;
}

// Main function to clean and update nationality and from entries
export async function cleanAndUpdatePersons() {
  try {
    console.log('Starting nationality and from cleaning and updating...');
    
    // Fetch all person records with pagination
    const persons = await fetchAllPersons();
    
    console.log(`Found ${persons.length} person records to process`);
    
    const results = {
      processed: 0,
      updated: 0,
      errors: 0,
      nationalityCleaned: 0,
      fromCleaned: 0,
      duplicatesRemoved: 0
    };
    
    // Process each person
    for (const person of persons) {
      try {
        results.processed++;
        
        let needsUpdate = false;
        const updateData = {};
        
        // Clean nationality array
        if (person.nationality && Array.isArray(person.nationality)) {
          const originalNationalities = [...person.nationality];
          const cleanedNationalities = deduplicateNationalities(person.nationality);
          
          if (JSON.stringify(originalNationalities) !== JSON.stringify(cleanedNationalities)) {
            updateData.nationality = cleanedNationalities;
            needsUpdate = true;
            results.nationalityCleaned++;
            results.duplicatesRemoved += (originalNationalities.length - cleanedNationalities.length);
            
            console.log(`Person ${person.id}: Cleaned nationality from ${originalNationalities.length} to ${cleanedNationalities.length} entries`);
          }
        }
        
        // Clean from array
        if (person.from && Array.isArray(person.from)) {
          const originalFrom = [...person.from];
          const cleanedFrom = deduplicateFrom(person.from);
          
          if (JSON.stringify(originalFrom) !== JSON.stringify(cleanedFrom)) {
            updateData.from = cleanedFrom;
            needsUpdate = true;
            results.fromCleaned++;
            
            console.log(`Person ${person.id}: Cleaned from from ${originalFrom.length} to ${cleanedFrom.length} entries`);
          }
        }
        
        // Update person if needed
        if (needsUpdate) {
          const { error: updateError } = await supabase
            .from('person')
            .update(updateData)
            .eq('id', person.id);
          
          if (updateError) {
            console.error(`Error updating person ${person.id}:`, updateError);
            results.errors++;
          } else {
            results.updated++;
            console.log(`Successfully updated person ${person.id}`);
          }
        }
        
        // Log progress every 100 persons
        if (results.processed % 100 === 0) {
          console.log(`Processed ${results.processed}/${persons.length} persons...`);
        }
        
      } catch (error) {
        console.error(`Error processing person ${person.id}:`, error);
        results.errors++;
      }
    }
    
    // Print final results
    console.log('\n=== FINAL RESULTS ===');
    console.log(`Total persons processed: ${results.processed}`);
    console.log(`Total persons updated: ${results.updated}`);
    console.log(`Nationality arrays cleaned: ${results.nationalityCleaned}`);
    console.log(`From arrays cleaned: ${results.fromCleaned}`);
    console.log(`Duplicate entries removed: ${results.duplicatesRemoved}`);
    console.log(`Errors encountered: ${results.errors}`);
    
    return results;
    
  } catch (error) {
    console.error('Error in cleanAndUpdatePersons:', error);
    throw error;
  }
}

// Function to run the update process
async function main() {
  try {
    await cleanAndUpdatePersons();
    console.log('Person update process completed successfully!');
  } catch (error) {
    console.error('Person update process failed:', error);
    process.exit(1);
  }
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
