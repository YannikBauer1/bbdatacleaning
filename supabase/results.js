import supabase from './supabase_client.js';

// Function to get all results
export async function getAllResults() {
  try {
    const { data, error } = await supabase
      .from('result')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching results:', error);
    throw error;
  }
}

// Function to get result table structure (first few records)
export async function getResultStructure() {
  try {
    const { data, error } = await supabase
      .from('result')
      .select('*')
      .limit(5);
    
    if (error) {
      throw error;
    }
    
    console.log('Result table structure (first 5 records):');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Error fetching result structure:', error);
    throw error;
  }
}

// Function to create a new result
export async function createResult(resultData) {
  try {
    const { data, error } = await supabase
      .from('result')
      .insert(resultData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating result:', error);
    throw error;
  }
}

// Function to update a result
export async function updateResult(id, updates) {
  try {
    const { data, error } = await supabase
      .from('result')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error updating result:', error);
    throw error;
  }
}

// Function to delete a result
export async function deleteResult(id) {
  try {
    const { error } = await supabase
      .from('result')
      .delete()
      .eq('id', id);
    
    if (error) {
      throw error;
    }
    
    return true;
  } catch (error) {
    console.error('Error deleting result:', error);
    throw error;
  }
}

// Function to get athlete by person name_key
export async function getAthleteByPersonNameKey(nameKey) {
  try {
    const { data, error } = await supabase
      .from('person')
      .select(`
        id,
        athlete!inner(id)
      `)
      .eq('name_key', nameKey)
      .single();
    
    if (error) {
      throw error;
    }
    
    return data.athlete[0];
  } catch (error) {
    console.error('Error fetching athlete by person name_key:', error);
    throw error;
  }
}

// Function to get category by division name and subtype
export async function getCategoryByDivisionAndSubtype(divisionName, divisionSubtype) {
  try {
    // First get category_type_id by division name
    const { data: categoryType, error: typeError } = await supabase
      .from('category_type')
      .select('id')
      .eq('name_key', divisionName)
      .single();
    
    if (typeError) {
      throw typeError;
    }
    
    // Then get category_weight_id by division subtype
    const { data: categoryWeight, error: weightError } = await supabase
      .from('category_weight')
      .select('id')
      .eq('name', divisionSubtype)
      .single();
    
    if (weightError) {
      throw weightError;
    }
    
    // Finally get category by both IDs
    const { data: category, error: categoryError } = await supabase
      .from('category')
      .select('id')
      .eq('category_type_id', categoryType.id)
      .eq('category_weight_id', categoryWeight.id)
      .single();
    
    if (categoryError) {
      throw categoryError;
    }
    
    return category;
  } catch (error) {
    console.error('Error fetching category by division and subtype:', error);
    throw error;
  }
}

// Function to get event by competition name_key and year
export async function getEventByCompetitionAndYear(competitionNameKey, year) {
  try {
    const { data, error } = await supabase
      .from('event')
      .select(`
        id,
        competition!inner(id, name_key)
      `)
      .eq('competition.name_key', competitionNameKey)
      .eq('year', year)
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching event by competition and year:', error);
    throw error;
  }
}

// Function to create a new division
export async function createDivision(divisionData) {
  try {
    const { data, error } = await supabase
      .from('division')
      .insert(divisionData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating division:', error);
    throw error;
  }
}

// Function to get division by event_id and category_id
export async function getDivisionByEventAndCategory(eventId, categoryId) {
  try {
    const { data, error } = await supabase
      .from('division')
      .select('id')
      .eq('event_id', eventId)
      .eq('category_id', categoryId)
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching division by event and category:', error);
    throw error;
  }
} 