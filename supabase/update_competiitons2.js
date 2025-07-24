import supabase from './supabase_client.js';

// Function to convert all strings in name_values array to lowercase
export async function updateCompetitionNameValuesToLowercase() {
  try {
    console.log('Fetching all competitions...');
    
    let allCompetitions = [];
    let from = 0;
    const range = 1000; // Fetch 1000 records at a time
    
    while (true) {
      const { data: competitions, error } = await supabase
        .from('competition')
        .select('id, name, name_values')
        .range(from, from + range - 1);
      
      if (error) {
        throw error;
      }
      
      if (!competitions || competitions.length === 0) {
        break; // No more records
      }
      
      allCompetitions = allCompetitions.concat(competitions);
      console.log(`Fetched ${competitions.length} competitions (total: ${allCompetitions.length})`);
      
      if (competitions.length < range) {
        break; // Last batch
      }
      
      from += range;
    }
    
    console.log(`Found ${allCompetitions.length} total competitions to process`);
    
    let totalUpdated = 0;
    let totalSkipped = 0;
    let totalErrors = 0;
    
    // Process each competition
    for (const competition of allCompetitions) {
      try {
        // Skip if name_values is null or empty
        if (!competition.name_values || !Array.isArray(competition.name_values) || competition.name_values.length === 0) {
          console.log(`Skipping competition ${competition.id} (${competition.name}) - no name_values to update`);
          totalSkipped++;
          continue;
        }
        
        // Convert all strings in name_values array to lowercase
        const updatedNameValues = competition.name_values.map(value => {
          if (typeof value === 'string') {
            return value.toLowerCase();
          }
          return value; // Keep non-string values as-is
        });
        
        // Check if any changes were made
        const hasChanges = updatedNameValues.some((value, index) => {
          const original = competition.name_values[index];
          return typeof value === 'string' && typeof original === 'string' && value !== original;
        });
        
        if (!hasChanges) {
          console.log(`Skipping competition ${competition.id} (${competition.name}) - no changes needed`);
          totalSkipped++;
          continue;
        }
        
        // Update the competition with lowercase name_values
        const { error: updateError } = await supabase
          .from('competition')
          .update({ name_values: updatedNameValues })
          .eq('id', competition.id);
        
        if (updateError) {
          console.error(`Error updating competition ${competition.id} (${competition.name}):`, updateError);
          totalErrors++;
        } else {
          console.log(`Updated competition ${competition.id} (${competition.name}) - converted ${competition.name_values.length} name_values to lowercase`);
          totalUpdated++;
        }
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing competition ${competition.id} (${competition.name}):`, error);
        totalErrors++;
      }
    }
    
    console.log(`\nUpdate complete!`);
    console.log(`Total competitions updated: ${totalUpdated}`);
    console.log(`Total competitions skipped: ${totalSkipped}`);
    console.log(`Total errors: ${totalErrors}`);
    
    return { totalUpdated, totalSkipped, totalErrors };
    
  } catch (error) {
    console.error('Error in updateCompetitionNameValuesToLowercase:', error);
    throw error;
  }
}

// Function to preview what changes would be made (without actually updating)
export async function previewCompetitionNameValuesChanges() {
  try {
    console.log('Fetching all competitions to preview changes...');
    
    let allCompetitions = [];
    let from = 0;
    const range = 1000; // Fetch 1000 records at a time
    
    while (true) {
      const { data: competitions, error } = await supabase
        .from('competition')
        .select('id, name, name_values')
        .range(from, from + range - 1);
      
      if (error) {
        throw error;
      }
      
      if (!competitions || competitions.length === 0) {
        break; // No more records
      }
      
      allCompetitions = allCompetitions.concat(competitions);
      console.log(`Fetched ${competitions.length} competitions (total: ${allCompetitions.length})`);
      
      if (competitions.length < range) {
        break; // Last batch
      }
      
      from += range;
    }
    
    console.log(`Found ${allCompetitions.length} total competitions to preview`);
    
    let totalWouldUpdate = 0;
    let totalWouldSkip = 0;
    
    for (const competition of allCompetitions) {
      if (!competition.name_values || !Array.isArray(competition.name_values) || competition.name_values.length === 0) {
        console.log(`Would skip: ${competition.id} (${competition.name}) - no name_values`);
        totalWouldSkip++;
        continue;
      }
      
      const updatedNameValues = competition.name_values.map(value => {
        if (typeof value === 'string') {
          return value.toLowerCase();
        }
        return value;
      });
      
      const hasChanges = updatedNameValues.some((value, index) => {
        const original = competition.name_values[index];
        return typeof value === 'string' && typeof original === 'string' && value !== original;
      });
      
      if (hasChanges) {
        console.log(`Would update: ${competition.id} (${competition.name})`);
        console.log(`  Original: ${JSON.stringify(competition.name_values)}`);
        console.log(`  Updated:  ${JSON.stringify(updatedNameValues)}`);
        console.log('');
        totalWouldUpdate++;
      } else {
        console.log(`Would skip: ${competition.id} (${competition.name}) - no changes needed`);
        totalWouldSkip++;
      }
    }
    
    console.log(`\nPreview complete!`);
    console.log(`Would update: ${totalWouldUpdate} competitions`);
    console.log(`Would skip: ${totalWouldSkip} competitions`);
    
    return { totalWouldUpdate, totalWouldSkip };
    
  } catch (error) {
    console.error('Error in previewCompetitionNameValuesChanges:', error);
    throw error;
  }
}

// Main execution function
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--preview') || args.includes('-p')) {
    console.log('Running preview mode...');
    await previewCompetitionNameValuesChanges();
  } else {
    console.log('Running update mode...');
    await updateCompetitionNameValuesToLowercase();
  }
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
