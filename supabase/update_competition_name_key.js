import supabase from './supabase_client.js';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// Get the directory of the current file
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load competitions.json file
function loadCompetitionsData() {
  try {
    const competitionsPath = join(__dirname, '..', 'keys', 'competitions.json');
    const competitionsContent = readFileSync(competitionsPath, 'utf8');
    return JSON.parse(competitionsContent);
  } catch (error) {
    console.error('Error loading competitions.json:', error);
    throw error;
  }
}

// Flatten the nested competitions structure to get all competition keys
function flattenCompetitions(competitionsData) {
  const flattened = {};
  
  for (const region of Object.values(competitionsData)) {
    for (const country of Object.values(region)) {
      for (const [key, nameVariations] of Object.entries(country)) {
        flattened[key] = nameVariations;
      }
    }
  }
  
  return flattened;
}

// Function to find competitions with matching names and update their name_values
export async function updateCompetitionNameKeys() {
  try {
    console.log('Loading competitions data...');
    const competitionsData = loadCompetitionsData();
    
    // Flatten the nested structure
    const flattenedCompetitions = flattenCompetitions(competitionsData);
    
    console.log(`Found ${Object.keys(flattenedCompetitions).length} competition keys to process`);
    
    let totalUpdated = 0;
    let totalSkipped = 0;
    
    // Process each competition key
    for (const [key, nameVariations] of Object.entries(flattenedCompetitions)) {
      //console.log(`Processing key: ${key} with ${nameVariations.length} name variations`);
      
      // Find the competition whose name matches any of the variations
      const { data: matchingCompetition, error } = await supabase
        .from('competition')
        .select('id, name, name_values')
        .eq('name', key)
        .single();
      
      if (error) {
        if (error.code === 'PGRST116') {
          // No rows returned
          console.log(`No competition found for key: ${key}`);
          totalSkipped++;
        } else {
          console.error(`Error finding competition for key ${key}:`, error);
        }
        continue;
      }
      
      if (!matchingCompetition) {
        console.log(`No competition found for key: ${key}`);
        totalSkipped++;
        continue;
      }
      
      //console.log(`Found competition for key: ${key} - ID: ${matchingCompetition.id}, Name: ${matchingCompetition.name}`);
      
      // Update the competition's name_values
      const { error: updateError } = await supabase
        .from('competition')
        .update({ name_values: nameVariations })
        .eq('id', matchingCompetition.id);
      
      if (updateError) {
        console.error(`Error updating competition ${matchingCompetition.id} for key ${key}:`, updateError);
      } else {
        //console.log(`Updated competition ${matchingCompetition.id} (${matchingCompetition.name}) with name_values for key: ${key}`);
        totalUpdated++;
      }
    }
    
    console.log(`\nUpdate complete!`);
    console.log(`Total competitions updated: ${totalUpdated}`);
    console.log(`Total keys skipped (no matches): ${totalSkipped}`);
    
    return { totalUpdated, totalSkipped };
    
  } catch (error) {
    console.error('Error in updateCompetitionNameKeys:', error);
    throw error;
  }
}

// Main execution function
async function main() {
  console.log('Running competition name keys update...');
  await updateCompetitionNameKeys();
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
