import supabase from './supabase_client.js';

// Function to update person priorities based on their achievements
async function updatePersonPriorities() {
  console.log('Starting person priority updates...');
  
  try {
    // Get total count of persons
    const { count: totalPersons } = await supabase
      .from('person')
      .select('*', { count: 'exact', head: true });
    
    console.log(`Total persons to process: ${totalPersons}`);
    
    const batchSize = 100;
    let processed = 0;
    
    while (processed < totalPersons) {
      console.log(`Processing persons ${processed + 1} to ${Math.min(processed + batchSize, totalPersons)}...`);
      
      // Get batch of persons
      const { data: persons, error: fetchError } = await supabase
        .from('person')
        .select('id, name')
        .range(processed, processed + batchSize - 1);
      
      if (fetchError) {
        console.error('Error fetching persons:', fetchError);
        break;
      }
      
      // Process each person in the batch
      for (const person of persons) {
        const priority = await calculatePersonPriority(person.id);
        
        // Update person priority
        const { error: updateError } = await supabase
          .from('person')
          .update({ priority })
          .eq('id', person.id);
        
        if (updateError) {
          console.error(`Error updating person ${person.id}:`, updateError);
        }
      }
      
      processed += batchSize;
      console.log(`Processed ${Math.min(processed, totalPersons)} persons`);
    }
    
    console.log('Person priority updates completed!');
  } catch (error) {
    console.error('Error updating person priorities:', error);
  }
}

// Function to calculate priority for a person based on their achievements
async function calculatePersonPriority(personId) {
  try {
    // Get all results for this person through athlete table
    const { data: results, error } = await supabase
      .from('result')
      .select(`
        place,
        division:division_id(
          event:event_id(
            competition:competition_id(name)
          )
        )
      `)
      .eq('athlete_id', (await supabase
        .from('athlete')
        .select('id')
        .eq('person_id', personId)
        .single()
      ).data.id);
    
    if (error) {
      console.error(`Error fetching results for person ${personId}:`, error);
      return 9; // Default priority
    }
    
    if (!results || results.length === 0) {
      return 9; // No results, lowest priority
    }
    
    let hasOlympiaWin = false;
    let hasArnoldWin = false;
    let hasOlympiaTop3 = false;
    let hasArnoldTop3 = false;
    let hasOlympiaTop10 = false;
    let hasArnoldTop5 = false;
    let hasOlympiaOrArnold = false;
    let hasProWin = false;
    let hasProTop3 = false;
    let hasProTop5 = false;
    let hasProTop10 = false;
    
    for (const result of results) {
      const competitionKey = result.division?.event?.competition?.name;
      const place = result.place;
      
      if (!competitionKey || !place) continue;
      
      // Check for Olympia and Arnold Classic results
      if (competitionKey === 'olympia' || competitionKey === 'olympia_europe') {
        hasOlympiaOrArnold = true;
        if (place === 1) hasOlympiaWin = true;
        else if (place <= 3) hasOlympiaTop3 = true;
        else if (place <= 10) hasOlympiaTop10 = true;
      } else if (competitionKey === 'arnold_classic' || competitionKey.startsWith('arnold_classic_')) {
        hasOlympiaOrArnold = true;
        if (place === 1) hasArnoldWin = true;
        else if (place <= 3) hasArnoldTop3 = true;
        else if (place <= 5) hasArnoldTop5 = true;
      } else {
        // Pro show (not Olympia or Arnold)
        if (place === 1) hasProWin = true;
        else if (place <= 3) hasProTop3 = true;
        else if (place <= 5) hasProTop5 = true;
        else if (place <= 10) hasProTop10 = true;
      }
    }
    
    // Determine priority based on achievements
    if (hasOlympiaWin || hasArnoldWin) return 1;
    if (hasOlympiaTop3 || hasArnoldTop3) return 2;
    if (hasOlympiaTop10 || hasArnoldTop5) return 3;
    if (hasOlympiaOrArnold) return 4;
    if (hasProWin) return 5;
    if (hasProTop3) return 6;
    if (hasProTop5) return 7;
    if (hasProTop10) return 8;
    
    return 9; // Default priority
  } catch (error) {
    console.error(`Error calculating priority for person ${personId}:`, error);
    return 9;
  }
}

// Function to update competition priorities based on category count
async function updateCompetitionPriorities() {
  console.log('Starting competition priority updates...');
  
  try {
    // Get total count of competitions
    const { count: totalCompetitions } = await supabase
      .from('competition')
      .select('*', { count: 'exact', head: true });
    
    console.log(`Total competitions to process: ${totalCompetitions}`);
    
    const batchSize = 100;
    let processed = 0;
    
    while (processed < totalCompetitions) {
      console.log(`Processing competitions ${processed + 1} to ${Math.min(processed + batchSize, totalCompetitions)}...`);
      
      // Get batch of competitions
      const { data: competitions, error: fetchError } = await supabase
        .from('competition')
        .select('id, name')
        .range(processed, processed + batchSize - 1);
      
      if (fetchError) {
        console.error('Error fetching competitions:', fetchError);
        break;
      }
      
      // Process each competition in the batch
      for (const competition of competitions) {
        const priority = await calculateCompetitionPriority(competition.id, competition.name);
        
        // Update competition priority
        const { error: updateError } = await supabase
          .from('competition')
          .update({ priority })
          .eq('id', competition.id);
        
        if (updateError) {
          console.error(`Error updating competition ${competition.id}:`, updateError);
        }
      }
      
      processed += batchSize;
      console.log(`Processed ${Math.min(processed, totalCompetitions)} competitions`);
    }
    
    console.log('Competition priority updates completed!');
  } catch (error) {
    console.error('Error updating competition priorities:', error);
  }
}

// Function to calculate priority for a competition based on category count
async function calculateCompetitionPriority(competitionId, name) {
  try {
    // Special cases for Olympia and Arnold Classic variations
    if (name === 'olympia' || name === 'olympia_europe' || 
        name === 'arnold_classic' || name.startsWith('arnold_classic_')) {
      return 1;
    }
    
    // Count categories for this competition
    const { count: categoryCount, error } = await supabase
      .from('event')
      .select('*', { count: 'exact', head: true })
      .eq('competition_id', competitionId);
    
    if (error) {
      console.error(`Error counting categories for competition ${competitionId}:`, error);
      return 5; // Default priority
    }
    
    // Determine priority based on category count
    if (categoryCount >= 8) return 2;
    if (categoryCount >= 5) return 3;
    if (categoryCount >= 2) return 4;
    return 5; // 1-2 categories
  } catch (error) {
    console.error(`Error calculating priority for competition ${competitionId}:`, error);
    return 5;
  }
}

// Main function to update all priorities
async function updateAllPriorities() {
  console.log('Starting priority updates for all tables...');
  
  try {
    // Update person priorities first
    await updatePersonPriorities();
    
    // Update competition priorities
    await updateCompetitionPriorities();
    
    console.log('All priority updates completed successfully!');
  } catch (error) {
    console.error('Error in priority update process:', error);
  }
}

// Export functions for individual use
export {
  updatePersonPriorities,
  updateCompetitionPriorities,
  updateAllPriorities,
  calculatePersonPriority,
  calculateCompetitionPriority
};

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  updateAllPriorities();
}
