import supabase from './supabase_client.js';

// Function to get all athletes
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

// Function to get athlete table structure (first few records)
export async function getAthleteStructure() {
  try {
    const { data, error } = await supabase
      .from('athlete')
      .select('*')
      .limit(5);
    
    if (error) {
      throw error;
    }
    
    console.log('Athlete table structure (first 5 records):');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Error fetching athlete structure:', error);
    throw error;
  }
}

// Function to get person table structure
export async function getPersonStructure() {
  try {
    const { data, error } = await supabase
      .from('person')
      .select('*')
      .limit(5);
    
    if (error) {
      throw error;
    }
    
    console.log('Person table structure (first 5 records):');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Error fetching person structure:', error);
    throw error;
  }
}

// Function to get all persons
export async function getAllPersons() {
  try {
    const { data, error } = await supabase
      .from('person')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching persons:', error);
    throw error;
  }
}

// Function to get athletes with person data joined
export async function getAthletesWithPersonData() {
  try {
    const { data, error } = await supabase
      .from('athlete')
      .select(`
        *,
        person:person_id(*)
      `)
      .limit(5);
    
    if (error) {
      throw error;
    }
    
    console.log('Athletes with person data (first 5 records):');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Error fetching athletes with person data:', error);
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

// Function to create a new person
export async function createPerson(personData) {
  try {
    const { data, error } = await supabase
      .from('person')
      .insert(personData)
      .select();
    
    if (error) {
      throw error;
    }
    
    return data[0];
  } catch (error) {
    console.error('Error creating person:', error);
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
