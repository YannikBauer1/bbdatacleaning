import supabase from './supabase_client.js';

// Function to get all category types
async function getCategoryTypes() {
  try {
    const { data, error } = await supabase
      .from('category_type')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    console.log('\n=== CATEGORY TYPES ===');
    console.log(`Found ${data.length} category types:`);
    data.forEach(cat => {
      console.log(`- ID: ${cat.id}, name_key: "${cat.name_key}", name: "${cat.name}"`);
    });
    
    return data;
  } catch (error) {
    console.error('Error fetching category types:', error);
    throw error;
  }
}

// Function to get all category weights
async function getCategoryWeights() {
  try {
    const { data, error } = await supabase
      .from('category_weight')
      .select('*');
    
    if (error) {
      throw error;
    }
    
    console.log('\n=== CATEGORY WEIGHTS ===');
    console.log(`Found ${data.length} category weights:`);
    data.forEach(weight => {
      console.log(`- ID: ${weight.id}, name: "${weight.name}"`);
    });
    
    return data;
  } catch (error) {
    console.error('Error fetching category weights:', error);
    throw error;
  }
}

// Function to get all categories
async function getCategories() {
  try {
    const { data, error } = await supabase
      .from('category')
      .select(`
        *,
        category_type:category_type_id(*),
        category_weight:category_weight_id(*)
      `);
    
    if (error) {
      throw error;
    }
    
    console.log('\n=== CATEGORIES ===');
    console.log(`Found ${data.length} categories:`);
    data.forEach(cat => {
      console.log(`- ID: ${cat.id}, type: "${cat.category_type?.name_key}" (${cat.category_type?.name}), weight: "${cat.category_weight?.name}"`);
    });
    
    return data;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
}

// Function to get all divisions
async function getDivisions() {
  try {
    const { data, error } = await supabase
      .from('division')
      .select(`
        *,
        event:event_id(*),
        category:category_id(
          *,
          category_type:category_type_id(*),
          category_weight:category_weight_id(*)
        )
      `);
    
    if (error) {
      throw error;
    }
    
    console.log('\n=== DIVISIONS ===');
    console.log(`Found ${data.length} divisions:`);
    data.forEach(div => {
      console.log(`- ID: ${div.id}, event: ${div.event?.year} ${div.event?.competition?.name_key}, category: ${div.category?.category_type?.name_key} ${div.category?.category_weight?.name}`);
    });
    
    return data;
  } catch (error) {
    console.error('Error fetching divisions:', error);
    throw error;
  }
}

// Function to test specific division lookup
async function testDivisionLookup(divisionName, divisionSubtype) {
  try {
    console.log(`\n=== TESTING DIVISION LOOKUP ===`);
    console.log(`Looking for division: "${divisionName}", subtype: "${divisionSubtype}"`);
    
    // First get category_type_id by division name
    const { data: categoryType, error: typeError } = await supabase
      .from('category_type')
      .select('id, name_key, name')
      .eq('name_key', divisionName);
    
    if (typeError) {
      console.error('Error finding category type:', typeError);
      return;
    }
    
    console.log(`Category types found: ${categoryType.length}`);
    categoryType.forEach(ct => {
      console.log(`- ID: ${ct.id}, name_key: "${ct.name_key}", name: "${ct.name}"`);
    });
    
    if (categoryType.length === 0) {
      console.log(`No category type found for name_key: "${divisionName}"`);
      return;
    }
    
    // Then get category_weight_id by division subtype
    const { data: categoryWeight, error: weightError } = await supabase
      .from('category_weight')
      .select('id, name')
      .eq('name', divisionSubtype);
    
    if (weightError) {
      console.error('Error finding category weight:', weightError);
      return;
    }
    
    console.log(`Category weights found: ${categoryWeight.length}`);
    categoryWeight.forEach(cw => {
      console.log(`- ID: ${cw.id}, name: "${cw.name}"`);
    });
    
    if (categoryWeight.length === 0) {
      console.log(`No category weight found for name: "${divisionSubtype}"`);
      return;
    }
    
    // Finally get category by both IDs
    const { data: category, error: categoryError } = await supabase
      .from('category')
      .select(`
        id,
        category_type:category_type_id(*),
        category_weight:category_weight_id(*)
      `)
      .eq('category_type_id', categoryType[0].id)
      .eq('category_weight_id', categoryWeight[0].id);
    
    if (categoryError) {
      console.error('Error finding category:', categoryError);
      return;
    }
    
    console.log(`Categories found: ${category.length}`);
    category.forEach(cat => {
      console.log(`- ID: ${cat.id}, type: "${cat.category_type?.name_key}", weight: "${cat.category_weight?.name}"`);
    });
    
    return category;
  } catch (error) {
    console.error('Error in testDivisionLookup:', error);
  }
}

// Function to test specific CSV data parsing
async function testCSVParsing() {
  try {
    console.log('\n=== TESTING CSV PARSING ===');
    
    // Test data from your CSV
    const testRecords = [
      { 'Division': '202_212', 'Division Subtype': '202', 'Division Level': 'pro' },
      { 'Division': '212', 'Division Subtype': 'open', 'Division Level': 'pro' },
      { 'Division': 'mp', 'Division Subtype': 'open', 'Division Level': 'pro' }
    ];
    
    testRecords.forEach((record, index) => {
      console.log(`\nTest record ${index + 1}:`, record);
      
      const divisionFull = record['Division'];
      let divisionName, divisionSubtype;
      
      if (divisionFull.includes('_')) {
        const parts = divisionFull.split('_');
        divisionSubtype = parts[0]; // e.g., "202"
        divisionName = parts[1]; // e.g., "212"
      } else {
        divisionName = divisionFull; // e.g., "212"
        divisionSubtype = record['Division Subtype'] || null;
      }
      
      // Convert to lowercase for database lookup
      divisionName = divisionName.toLowerCase();
      
      console.log(`Parsed: divisionName="${divisionName}", divisionSubtype="${divisionSubtype}"`);
    });
  } catch (error) {
    console.error('Error in testCSVParsing:', error);
  }
}

// Main function to run all tests
async function runAllTests() {
  try {
    console.log('Starting category table exploration...\n');
    
    await getCategoryTypes();
    await getCategoryWeights();
    await getCategories();
    await getDivisions();
    await testCSVParsing();
    
    // Test specific problematic divisions
    await testDivisionLookup('212', '202');
    await testDivisionLookup('212', 'open');
    await testDivisionLookup('mp', 'open');
    
    console.log('\n=== TEST COMPLETED ===');
  } catch (error) {
    console.error('Error running tests:', error);
  }
}

// Run tests if this file is executed directly
if (process.argv[1] === new URL(import.meta.url).pathname) {
  runAllTests()
    .then(() => {
      console.log('Tests completed successfully');
      process.exit(0);
    })
    .catch(error => {
      console.error('Tests failed:', error);
      process.exit(1);
    });
}

export {
  getCategoryTypes,
  getCategoryWeights,
  getCategories,
  getDivisions,
  testDivisionLookup,
  testCSVParsing,
  runAllTests
}; 