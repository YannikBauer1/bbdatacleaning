import supabase from './supabase_client.js';

// Function to get all events
export async function getAllEvents() {
  try {
    const { data, error } = await supabase
      .from('event')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching events:', error);
    throw error;
  }
}

// Function to get event table structure (first few records)
export async function getEventStructure() {
  try {
    const { data, error } = await supabase
      .from('event')
      .select('*')
      .limit(5);
    
    if (error) {
      throw error;
    }
    
    console.log('Event table structure (first 5 records):');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Error fetching event structure:', error);
    throw error;
  }
}

// Function to create a new event
export async function createEvent(eventData) {
  try {
    const { data, error } = await supabase
      .from('event')
      .insert(eventData)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error creating event:', error);
    throw error;
  }
}

// Function to update an event
export async function updateEvent(id, updates) {
  try {
    const { data, error } = await supabase
      .from('event')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error updating event:', error);
    throw error;
  }
}

// Function to delete an event
export async function deleteEvent(id) {
  try {
    const { error } = await supabase
      .from('event')
      .delete()
      .eq('id', id);
    
    if (error) {
      throw error;
    }
    
    return true;
  } catch (error) {
    console.error('Error deleting event:', error);
    throw error;
  }
}

// Function to get competition by name_key
export async function getCompetitionByNameKey(nameKey) {
  try {
    const { data, error } = await supabase
      .from('competition')
      .select('id')
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