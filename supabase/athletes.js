import supabase from './supabase_client.js';

// Example function to get all athlete
export async function getAllathlete() {
  try {
    const { data, error } = await supabase
      .from('athlete')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching athlete:', error);
    throw error;
  }
}

// Example function to get athlete by ID
export async function getAthleteById(id) {
  try {
    const { data, error } = await supabase
      .from('athlete')
      .select('*')
      .eq('id', id)
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching athlete:', error);
    throw error;
  }
}

// Example function to create a new athlete
export async function createAthlete(athleteData) {
  try {
    const { data, error } = await supabase
      .from('athlete')
      .insert(athleteData)
      .select();
    
    if (error) {
      throw error;
    }
    
    return data[0];
  } catch (error) {
    console.error('Error creating athlete:', error);
    throw error;
  }
}

// Example function to update an athlete
export async function updateAthlete(id, updates) {
  try {
    const { data, error } = await supabase
      .from('athlete')
      .update(updates)
      .eq('id', id)
      .select();
    
    if (error) {
      throw error;
    }
    
    return data[0];
  } catch (error) {
    console.error('Error updating athlete:', error);
    throw error;
  }
}

// Example function to delete an athlete
export async function deleteAthlete(id) {
  try {
    const { error } = await supabase
      .from('athlete')
      .delete()
      .eq('id', id);
    
    if (error) {
      throw error;
    }
    
    return true;
  } catch (error) {
    console.error('Error deleting athlete:', error);
    throw error;
  }
}
