import supabase from './supabase_client.js';

// Function to get all competitions
export async function getAllCompetitions() {
  try {
    const { data, error } = await supabase
      .from('competition')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching competitions:', error);
    throw error;
  }
}

// Function to get competition table structure (first few records)
export async function getCompetitionStructure() {
  try {
    const { data, error } = await supabase
      .from('competition')
      .select('*')
      .limit(5);
    
    if (error) {
      throw error;
    }
    
    console.log('Competition table structure (first 5 records):');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Error fetching competition structure:', error);
    throw error;
  }
}

// Function to create a new competition
export async function createCompetition(competitionData) {
  try {
    const { data, error } = await supabase
      .from('competition')
      .insert(competitionData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating competition:', error);
    throw error;
  }
}

// Function to update a competition
export async function updateCompetition(id, updates) {
  try {
    const { data, error } = await supabase
      .from('competition')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error updating competition:', error);
    throw error;
  }
}

// Function to delete a competition
export async function deleteCompetition(id) {
  try {
    const { error } = await supabase
      .from('competition')
      .delete()
      .eq('id', id);
    
    if (error) {
      throw error;
    }
    
    return true;
  } catch (error) {
    console.error('Error deleting competition:', error);
    throw error;
  }
}

// Function to get competition by name_key
export async function getCompetitionByNameKey(nameKey) {
  try {
    const { data, error } = await supabase
      .from('competition')
      .select('*')
      .eq('name_key', nameKey)
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching competition by name_key:', error);
    throw error;
  }
} 