import supabase from './supabase_client.js';

// Function to get division table structure
export async function getDivisionStructure() {
  try {
    const { data, error } = await supabase
      .from('division')
      .select('*')
      .limit(5);
    
    if (error) {
      throw error;
    }
    
    console.log('Division table structure (first 5 records):');
    console.log(data);
    return data;
  } catch (error) {
    console.error('Error fetching division structure:', error);
    throw error;
  }
}

// Run the test
getDivisionStructure(); 