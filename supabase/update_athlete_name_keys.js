import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// Get the directory of the current file
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load athletes.json file
function loadAthletesData() {
  try {
    const athletesPath = join(__dirname, '..', 'keys', 'athletes.json');
    const athletesContent = readFileSync(athletesPath, 'utf8');
    return JSON.parse(athletesContent);
  } catch (error) {
    console.error('Error loading athletes.json:', error);
    throw error;
  }
}

// Function to find persons with matching names and update their name_values
export async function updateAthleteNameKeys() {
  try {
    console.log('Loading athletes data...');
    const athletesData = loadAthletesData();
    
    console.log(`Found ${Object.keys(athletesData).length} athlete keys to process`);
    
    let totalUpdated = 0;
    let totalSkipped = 0;
    
    // Process each athlete key
    for (const [key, nameVariations] of Object.entries(athletesData)) {
      //console.log(`Processing key: ${key} with ${nameVariations.length} name variations`);
      
      // Find the person whose name matches any of the variations
      const { data: matchingPerson, error } = await supabase
        .from('person')
        .select('id, name, name_values')
        .eq('name', key)
        .single();
      
      if (error) {
        if (error.code === 'PGRST116') {
          // No rows returned
          console.log(`No person found for key: ${key}`);
          totalSkipped++;
        } else {
          console.error(`Error finding person for key ${key}:`, error);
        }
        continue;
      }
      
      if (!matchingPerson) {
        console.log(`No person found for key: ${key}`);
        totalSkipped++;
        continue;
      }
      
      //console.log(`Found person for key: ${key} - ID: ${matchingPerson.id}, Name: ${matchingPerson.name}`);
      
      // Update the person's name_values
      const { error: updateError } = await supabase
        .from('person')
        .update({ name_values: nameVariations })
        .eq('id', matchingPerson.id);
      
      if (updateError) {
        console.error(`Error updating person ${matchingPerson.id} for key ${key}:`, updateError);
      } else {
        //console.log(`Updated person ${matchingPerson.id} (${matchingPerson.name}) with name_values for key: ${key}`);
        totalUpdated++;
      }
    }
    
    console.log(`\nUpdate complete!`);
    console.log(`Total persons updated: ${totalUpdated}`);
    console.log(`Total keys skipped (no matches): ${totalSkipped}`);
    
    return { totalUpdated, totalSkipped };
    
  } catch (error) {
    console.error('Error in updateAthleteNameKeys:', error);
    throw error;
  }
}

// Main execution function
async function main() {
  console.log('Running athlete name keys update...');
  await updateAthleteNameKeys();
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
