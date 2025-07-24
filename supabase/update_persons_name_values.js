import supabase from './supabase_client.js';

// Function to convert all strings in name_values array to lowercase for persons
export async function updatePersonNameValuesToLowercase() {
  try {
    console.log('Fetching all persons...');
    
    let allPersons = [];
    let from = 0;
    const range = 1000; // Fetch 1000 records at a time
    
    while (true) {
      const { data: persons, error } = await supabase
        .from('person')
        .select('id, name, name_values')
        .range(from, from + range - 1);
      
      if (error) {
        throw error;
      }
      
      if (!persons || persons.length === 0) {
        break; // No more records
      }
      
      allPersons = allPersons.concat(persons);
      console.log(`Fetched ${persons.length} persons (total: ${allPersons.length})`);
      
      if (persons.length < range) {
        break; // Last batch
      }
      
      from += range;
    }
    
    console.log(`Found ${allPersons.length} total persons to process`);
    
    let totalUpdated = 0;
    let totalSkipped = 0;
    let totalErrors = 0;
    
    // Process each person
    for (const person of allPersons) {
      try {
        // Skip if name_values is null or empty
        if (!person.name_values || !Array.isArray(person.name_values) || person.name_values.length === 0) {
          console.log(`Skipping person ${person.id} (${person.name}) - no name_values to update`);
          totalSkipped++;
          continue;
        }
        
        // Convert all strings in name_values array to lowercase
        const updatedNameValues = person.name_values.map(value => {
          if (typeof value === 'string') {
            return value.toLowerCase();
          }
          return value; // Keep non-string values as-is
        });
        
        // Check if any changes were made
        const hasChanges = updatedNameValues.some((value, index) => {
          const original = person.name_values[index];
          return typeof value === 'string' && typeof original === 'string' && value !== original;
        });
        
        if (!hasChanges) {
          console.log(`Skipping person ${person.id} (${person.name}) - no changes needed`);
          totalSkipped++;
          continue;
        }
        
        // Update the person with lowercase name_values
        const { error: updateError } = await supabase
          .from('person')
          .update({ name_values: updatedNameValues })
          .eq('id', person.id);
        
        if (updateError) {
          console.error(`Error updating person ${person.id} (${person.name}):`, updateError);
          totalErrors++;
        } else {
          console.log(`Updated person ${person.id} (${person.name}) - converted ${person.name_values.length} name_values to lowercase`);
          totalUpdated++;
        }
        
        // Add a small delay to avoid overwhelming the database
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing person ${person.id} (${person.name}):`, error);
        totalErrors++;
      }
    }
    
    console.log(`\nUpdate complete!`);
    console.log(`Total persons updated: ${totalUpdated}`);
    console.log(`Total persons skipped: ${totalSkipped}`);
    console.log(`Total errors: ${totalErrors}`);
    
    return { totalUpdated, totalSkipped, totalErrors };
    
  } catch (error) {
    console.error('Error in updatePersonNameValuesToLowercase:', error);
    throw error;
  }
}

// Function to preview what changes would be made (without actually updating)
export async function previewPersonNameValuesChanges() {
  try {
    console.log('Fetching all persons to preview changes...');
    
    let allPersons = [];
    let from = 0;
    const range = 1000; // Fetch 1000 records at a time
    
    while (true) {
      const { data: persons, error } = await supabase
        .from('person')
        .select('id, name, name_values')
        .range(from, from + range - 1);
      
      if (error) {
        throw error;
      }
      
      if (!persons || persons.length === 0) {
        break; // No more records
      }
      
      allPersons = allPersons.concat(persons);
      console.log(`Fetched ${persons.length} persons (total: ${allPersons.length})`);
      
      if (persons.length < range) {
        break; // Last batch
      }
      
      from += range;
    }
    
    console.log(`Found ${allPersons.length} total persons to preview`);
    
    let totalWouldUpdate = 0;
    let totalWouldSkip = 0;
    
    for (const person of allPersons) {
      if (!person.name_values || !Array.isArray(person.name_values) || person.name_values.length === 0) {
        console.log(`Would skip: ${person.id} (${person.name}) - no name_values`);
        totalWouldSkip++;
        continue;
      }
      
      const updatedNameValues = person.name_values.map(value => {
        if (typeof value === 'string') {
          return value.toLowerCase();
        }
        return value;
      });
      
      const hasChanges = updatedNameValues.some((value, index) => {
        const original = person.name_values[index];
        return typeof value === 'string' && typeof original === 'string' && value !== original;
      });
      
      if (hasChanges) {
        console.log(`Would update: ${person.id} (${person.name})`);
        console.log(`  Original: ${JSON.stringify(person.name_values)}`);
        console.log(`  Updated:  ${JSON.stringify(updatedNameValues)}`);
        console.log('');
        totalWouldUpdate++;
      } else {
        console.log(`Would skip: ${person.id} (${person.name}) - no changes needed`);
        totalWouldSkip++;
      }
    }
    
    console.log(`\nPreview complete!`);
    console.log(`Would update: ${totalWouldUpdate} persons`);
    console.log(`Would skip: ${totalWouldSkip} persons`);
    
    return { totalWouldUpdate, totalWouldSkip };
    
  } catch (error) {
    console.error('Error in previewPersonNameValuesChanges:', error);
    throw error;
  }
}

// Main execution function
async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--preview') || args.includes('-p')) {
    console.log('Running preview mode...');
    await previewPersonNameValuesChanges();
  } else {
    console.log('Running update mode...');
    await updatePersonNameValuesToLowercase();
  }
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
} 