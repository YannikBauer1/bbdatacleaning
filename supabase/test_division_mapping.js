import { readFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import supabase from './supabase_client.js';

// Function to map division names from CSV to existing category_type name_keys
function mapDivisionToCategoryType(divisionName) {
  if (!divisionName) return null;
  
  const divisionMap = {
    "Men's Bodybuilding": "mensbb",
    "Women's Bodybuilding": "womensbb",
    "Men's Physique": "mensphysique",
    "Women's Physique": "womensphysique",
    "Men's Classic Physique": "classic",
    "Women's Classic Physique": "classic", // Note: This might need adjustment
    "Women's Bikini": "bikini",
    "Men's Bikini": "bikini", // Note: This might need adjustment
    "Figure": "figure",
    "Women's Figure": "figure",
    "Fitness": "fitness",
    "Women's Fitness": "fitness",
    "Wellness": "wellness",
    "Women's Wellness": "wellness",
    "212": "202_212",
    "212 Bodybuilding": "202_212",
    "Men's 212 Bodybuilding": "202_212",
    "Wheelchair": "wheelchair",
    "Men's Wheelchair": "wheelchair"
  };
  
  return divisionMap[divisionName] || null;
}

// Function to get existing category by division name and weight
async function getExistingCategory(divisionName, weightName = 'Open') {
  try {
    // Map division name to category_type name_key
    const categoryTypeKey = mapDivisionToCategoryType(divisionName);
    
    if (!categoryTypeKey) {
      console.warn(`No mapping found for division: ${divisionName}`);
      return null;
    }
    
    // Get category_type by name_key
    const { data: categoryType, error: typeError } = await supabase
      .from('category_type')
      .select('id, name_key, name')
      .eq('name_key', categoryTypeKey)
      .single();
    
    if (typeError) {
      console.warn(`Category type not found for key: ${categoryTypeKey}`);
      return null;
    }
    
    // Get category_weight by name
    const { data: categoryWeight, error: weightError } = await supabase
      .from('category_weight')
      .select('id, name')
      .eq('name', weightName)
      .single();
    
    if (weightError) {
      console.warn(`Category weight not found for: ${weightName}`);
      return null;
    }
    
    // Get category by both IDs
    const { data: category, error: categoryError } = await supabase
      .from('category')
      .select(`
        id,
        category_type:category_type_id(id, name_key, name),
        category_weight:category_weight_id(id, name)
      `)
      .eq('category_type_id', categoryType.id)
      .eq('category_weight_id', categoryWeight.id)
      .single();
    
    if (categoryError) {
      console.warn(`Category not found for type: ${categoryTypeKey} and weight: ${weightName}`);
      return null;
    }
    
    return category;
    
  } catch (error) {
    console.error('Error getting existing category:', error);
    return null;
  }
}

// Function to parse comma-separated divisions
function parseDivisions(divisionsString) {
  if (!divisionsString) return [];
  
  return divisionsString
    .split(',')
    .map(div => div.trim())
    .filter(div => div.length > 0);
}

// Function to determine category weight from division type
function getCategoryWeightFromDivisionType(divisionType) {
  if (!divisionType) return 'Open';
  
  const divisionTypeStr = divisionType.toUpperCase();
  
  if (divisionTypeStr.includes('212')) {
    return '212';
  }
  
  return 'Open';
}

async function testDivisionMapping() {
  try {
    console.log('Testing division mapping with actual CSV data...\n');
    
    // Read and parse CSV file
    const csvContent = readFileSync('data/clean/schedule2025.csv', 'utf-8');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    console.log(`Found ${records.length} schedule entries to test\n`);
    
    // Track unique divisions found
    const uniqueDivisions = new Set();
    const divisionResults = new Map();
    
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      const divisions = parseDivisions(record.division);
      
      for (const divisionName of divisions) {
        uniqueDivisions.add(divisionName);
        
        if (!divisionResults.has(divisionName)) {
          const categoryWeight = getCategoryWeightFromDivisionType(record.division);
          const category = await getExistingCategory(divisionName, categoryWeight);
          
          divisionResults.set(divisionName, {
            mappedKey: mapDivisionToCategoryType(divisionName),
            category: category,
            weight: categoryWeight
          });
        }
      }
    }
    
    // Display results
    console.log('=== DIVISION MAPPING RESULTS ===\n');
    
    for (const [divisionName, result] of divisionResults) {
      console.log(`Division: "${divisionName}"`);
      console.log(`  Mapped to category_type key: "${result.mappedKey}"`);
      console.log(`  Weight: "${result.weight}"`);
      
      if (result.category) {
        console.log(`  ✅ Found category: ID ${result.category.id}`);
        console.log(`     Type: ${result.category.category_type?.name_key} (${result.category.category_type?.name})`);
        console.log(`     Weight: ${result.category.category_weight?.name}`);
      } else {
        console.log(`  ❌ No category found`);
      }
      console.log('');
    }
    
    // Summary
    const foundCount = Array.from(divisionResults.values()).filter(r => r.category).length;
    const totalCount = divisionResults.size;
    
    console.log('=== SUMMARY ===');
    console.log(`Total unique divisions: ${totalCount}`);
    console.log(`Successfully mapped: ${foundCount}`);
    console.log(`Failed to map: ${totalCount - foundCount}`);
    
    // List unmapped divisions
    const unmapped = Array.from(divisionResults.entries())
      .filter(([_, result]) => !result.category)
      .map(([divisionName, _]) => divisionName);
    
    if (unmapped.length > 0) {
      console.log('\nUnmapped divisions:');
      unmapped.forEach(div => console.log(`  - "${div}"`));
    }
    
  } catch (error) {
    console.error('Error testing division mapping:', error);
  }
}

// Run the test
testDivisionMapping(); 