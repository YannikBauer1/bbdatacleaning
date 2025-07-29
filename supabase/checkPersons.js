import supabase from './supabase_client.js';

// Helper function to clean nationality string
function cleanNationality(nationality) {
  if (!nationality || typeof nationality !== 'string') return '';
  
  // Remove commas, numbers, and trim whitespace
  let cleaned = nationality
    .replace(/[,0-9]/g, '') // Remove commas and numbers
    .trim(); // Trim whitespace
  
  // Handle specific country name mappings
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
    'north africa': 'Africa', // This might need more specific handling
    'south wales': 'Wales', // This might need more specific handling
    'west roxbury': 'United States', // This is a neighborhood in Boston
    'boston west roxbury': 'United States', // This is a neighborhood in Boston
    'tahiti': 'French Polynesia',
    'yugoslavia': 'Serbia', // Yugoslavia no longer exists, defaulting to Serbia
    'rhodesia': 'Zimbabwe', // Rhodesia no longer exists, defaulting to Zimbabwe
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
    // Split by spaces and capitalize each word
    cleaned = cleaned
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  
  // Handle mixed case entries that need standardization
  // (e.g., "Trinidad And Tobago" -> "Trinidad and Tobago")
  if (cleaned.includes(' And ') || cleaned.includes(' & ')) {
    cleaned = cleaned.replace(/ And /g, ' and ').replace(/ & /g, ' and ');
  }
  
  return cleaned;
}

// Helper function to normalize nationality for comparison (lowercase)
function normalizeNationality(nationality) {
  return nationality.toLowerCase();
}

// Helper function to check if flag image exists in background bucket
async function checkFlagImage(countryName) {
  try {
    // Convert country name to lowercase with hyphens for spaces
    const flagName = countryName.toLowerCase().replace(/\s+/g, '-');
    
    // Check if flag image exists in the flags folder
    const { data, error } = await supabase.storage
      .from('background')
      .list('flags', {
        search: flagName
      });
    
    if (error) {
      console.error(`Error checking flag for ${countryName}:`, error);
      return false;
    }
    
    // Check if any file matches the flag name
    const hasFlag = data.some(file => 
      file.name.toLowerCase().includes(flagName) ||
      file.name.toLowerCase().includes(flagName.replace('-', '_'))
    );
    
    return hasFlag;
  } catch (error) {
    console.error(`Error checking flag image for ${countryName}:`, error);
    return false;
  }
}

// Helper function to write JSON file
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

function writeMissingFlagsJson(missingFlagsData) {
  try {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);
    const jsonPath = join(__dirname, '..', 'all', 'jsons', 'missing_flag_countries.json');
    
    writeFileSync(jsonPath, JSON.stringify(missingFlagsData, null, 2), 'utf8');
    console.log(`Missing flags data written to: ${jsonPath}`);
  } catch (error) {
    console.error('Error writing missing flags JSON:', error);
  }
}

// Helper function to fetch all person records with pagination
async function fetchAllPersons() {
  const allPersons = [];
  let from = 0;
  const pageSize = 1000; // Supabase default limit
  
  while (true) {
    const { data: persons, error: fetchError } = await supabase
      .from('person')
      .select('id, nationality')
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

// Main function to clean and validate nationality entries
export async function cleanAndValidateNationalities() {
  try {
    console.log('Starting nationality cleaning and validation...');
    
    // Fetch all person records with pagination
    const persons = await fetchAllPersons();
    
    console.log(`Found ${persons.length} person records to process`);
    
    const results = {
      processed: 0,
      updated: 0,
      errors: 0,
      duplicatesFound: 0,
      missingFlags: [],
      cleanedNationalities: new Set(),
      missingFlagsWithPersonIds: {} // Track person IDs for each missing flag country
    };
    
    // Process each person
    for (const person of persons) {
      try {
        results.processed++;
        
        if (!person.nationality || !Array.isArray(person.nationality)) {
          console.log(`Person ${person.id}: No nationality array found`);
          continue;
        }
        
        const originalNationalities = [...person.nationality];
        const cleanedNationalities = [];
        const seenNormalized = new Set();
        
        // Clean each nationality entry
        for (const nationality of originalNationalities) {
          const cleaned = cleanNationality(nationality);
          
          if (!cleaned) {
            console.log(`Person ${person.id}: Empty nationality after cleaning: "${nationality}"`);
            continue;
          }
          
          const normalized = normalizeNationality(cleaned);
          
          // Check for duplicates (case-insensitive)
          if (seenNormalized.has(normalized)) {
            console.log(`Person ${person.id}: Duplicate nationality found: "${nationality}" -> "${cleaned}"`);
            results.duplicatesFound++;
            continue;
          }
          
                   seenNormalized.add(normalized);
         cleanedNationalities.push(cleaned);
         results.cleanedNationalities.add(cleaned);
         
         // Track this nationality for missing flag checking
         if (!results.missingFlagsWithPersonIds[cleaned]) {
           results.missingFlagsWithPersonIds[cleaned] = [];
         }
         results.missingFlagsWithPersonIds[cleaned].push(person.id);
        }
        
        // Check if nationalities changed
        const hasChanged = originalNationalities.length !== cleanedNationalities.length ||
          originalNationalities.some((orig, index) => orig !== cleanedNationalities[index]);
        
        if (hasChanged) {
          // Update the person record
          const { error: updateError } = await supabase
            .from('person')
            .update({ nationality: cleanedNationalities })
            .eq('id', person.id);
          
          if (updateError) {
            console.error(`Error updating person ${person.id}:`, updateError);
            results.errors++;
          } else {
            console.log(`Person ${person.id}: Updated nationalities from [${originalNationalities.join(', ')}] to [${cleanedNationalities.join(', ')}]`);
            results.updated++;
          }
        }
        
      } catch (error) {
        console.error(`Error processing person ${person.id}:`, error);
        results.errors++;
      }
    }
    
    // Check for flag images
    console.log('\nChecking for flag images...');
    const uniqueNationalities = Array.from(results.cleanedNationalities);
    
    for (const nationality of uniqueNationalities) {
      const hasFlag = await checkFlagImage(nationality);
      if (!hasFlag) {
        results.missingFlags.push(nationality);
        console.log(`Missing flag image for: ${nationality}`);
      } else {
        // Remove from missing flags tracking if flag exists
        delete results.missingFlagsWithPersonIds[nationality];
      }
    }
    
    // Print summary
    console.log('\n=== NATIONALITY CLEANING SUMMARY ===');
    console.log(`Total persons processed: ${results.processed}`);
    console.log(`Persons updated: ${results.updated}`);
    console.log(`Errors encountered: ${results.errors}`);
    console.log(`Duplicate entries found: ${results.duplicatesFound}`);
    console.log(`Unique nationalities after cleaning: ${results.cleanedNationalities.size}`);
    console.log(`Missing flag images: ${results.missingFlags.length}`);
    
    if (results.missingFlags.length > 0) {
      console.log('\nNationalities missing flag images:');
      results.missingFlags.forEach(flag => console.log(`  - ${flag}`));
      
      // Write missing flags data to JSON file
      const missingFlagsData = {
        totalMissingFlags: results.missingFlags.length,
        timestamp: new Date().toISOString(),
        countries: Object.keys(results.missingFlagsWithPersonIds).map(country => ({
          country: country,
          personIds: results.missingFlagsWithPersonIds[country],
          count: results.missingFlagsWithPersonIds[country].length
        })).sort((a, b) => b.count - a.count) // Sort by count descending
      };
      
      writeMissingFlagsJson(missingFlagsData);
    }
    
    return results;
    
  } catch (error) {
    console.error('Error in cleanAndValidateNationalities:', error);
    throw error;
  }
}

// Function to get statistics about nationality entries
export async function getNationalityStats() {
  try {
    // Use the same pagination function to get all persons
    const persons = await fetchAllPersons();
    
    const stats = {
      totalPersons: persons.length,
      personsWithNationality: 0,
      totalNationalityEntries: 0,
      uniqueNationalities: new Set(),
      nationalityCounts: {},
      problematicEntries: []
    };
    
    for (const person of persons) {
      if (person.nationality && Array.isArray(person.nationality)) {
        stats.personsWithNationality++;
        stats.totalNationalityEntries += person.nationality.length;
        
        for (const nationality of person.nationality) {
          if (nationality) {
            stats.uniqueNationalities.add(nationality);
            stats.nationalityCounts[nationality] = (stats.nationalityCounts[nationality] || 0) + 1;
            
            // Check for problematic entries
            if (nationality.includes(',') || /\d/.test(nationality)) {
              stats.problematicEntries.push(nationality);
            }
          }
        }
      }
    }
    
    console.log('\n=== NATIONALITY STATISTICS ===');
    console.log(`Total persons: ${stats.totalPersons}`);
    console.log(`Persons with nationality: ${stats.personsWithNationality}`);
    console.log(`Total nationality entries: ${stats.totalNationalityEntries}`);
    console.log(`Unique nationalities: ${stats.uniqueNationalities.size}`);
    console.log(`Problematic entries found: ${stats.problematicEntries.length}`);
    
    if (stats.problematicEntries.length > 0) {
      console.log('\nSample problematic entries:');
      const uniqueProblematic = [...new Set(stats.problematicEntries)].slice(0, 10);
      uniqueProblematic.forEach(entry => console.log(`  - "${entry}"`));
    }
    
    return stats;
    
  } catch (error) {
    console.error('Error getting nationality stats:', error);
    throw error;
  }
}

// Run the cleaning function if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('Running nationality cleaning and validation...');
  
  // First get stats
  await getNationalityStats();
  
  // Then clean and validate
  await cleanAndValidateNationalities();
  
  console.log('Nationality cleaning and validation completed!');
}
