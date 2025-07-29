import supabase from './supabase_client.js';

/**
 * Check for missing competition entries based on logo images in the bucket
 * Lists all images in the 'logos' bucket under 'competitions' folder
 * and checks if there's a corresponding entry in the competition table
 */
export async function checkMissingCompetitionLogos() {
  try {
    console.log('🔍 Checking for missing competition entries based on logo images...\n');

    // 1. Get all images from the logos bucket in competitions folder
    console.log('📁 Fetching images from logos bucket (competitions folder)...');
    
    let allImageFiles = [];
    let offset = 0;
    const limit = 1000; // Use a larger limit to get more files per request
    
    while (true) {
      const { data: imageFiles, error: listError } = await supabase.storage
        .from('logos')
        .list('competitions', {
          limit: limit,
          offset: offset
        });

      if (listError) {
        throw new Error(`Failed to list images: ${listError.message}`);
      }

      if (!imageFiles || imageFiles.length === 0) {
        break; // No more files to fetch
      }

      allImageFiles = allImageFiles.concat(imageFiles);
      console.log(`📁 Fetched ${imageFiles.length} images (total so far: ${allImageFiles.length})`);
      
      if (imageFiles.length < limit) {
        break; // This was the last batch
      }
      
      offset += limit;
    }

    if (allImageFiles.length === 0) {
      console.log('❌ No images found in logos/competitions folder');
      return;
    }

    console.log(`📊 Found ${allImageFiles.length} total images in logos/competitions folder\n`);

    // 2. Process each image file
    const missingCompetitions = [];
    const foundCompetitions = [];

    console.log(`\n🔍 Processing ${allImageFiles.length} image files...`);
    
    for (const imageFile of allImageFiles) {
      console.log(`\n📄 Processing file: ${imageFile.name}`);
      
      // Skip non-image files
      if (!imageFile.name.match(/\.(png|jpg|jpeg|gif|webp)$/i)) {
        console.log(`⏭️ Skipping non-image file: ${imageFile.name}`);
        continue;
      }

      // Extract competition name from filename (remove extension)
      const fileName = imageFile.name;
      const competitionName = fileName.replace(/\.(png|jpg|jpeg|gif|webp)$/i, '');
      
      console.log(`🔍 Checking: ${fileName} → "${competitionName}"`);

      // Check if competition exists in database
      const { data: competition, error } = await supabase
        .from('competition')
        .select('name')
        .eq('name', competitionName)
        .single();

      if (error && error.code !== 'PGRST116') { // PGRST116 is "not found"
        console.error(`❌ Error checking competition "${competitionName}":`, error);
        continue;
      }

      if (competition) {
        console.log(`✅ Found: "${competitionName}"`);
        foundCompetitions.push({
          fileName,
          name: competitionName
        });
      } else {
        console.log(`❌ Missing: "${competitionName}"`);
        missingCompetitions.push({
          fileName,
          name: competitionName
        });
      }
    }

    // 3. Display results
    console.log('\n📋 RESULTS SUMMARY:');
    console.log(`✅ Found competitions: ${foundCompetitions.length}`);
    console.log(`❌ Missing competitions: ${missingCompetitions.length}\n`);

    if (missingCompetitions.length > 0) {
      console.log('❌ MISSING COMPETITION ENTRIES:');
      console.log('These logo images exist but have no corresponding competition entry:');
      console.log('─'.repeat(80));
      
      missingCompetitions.forEach((item, index) => {
        console.log(`${index + 1}. ${item.fileName} → name: "${item.name}"`);
      });
      
      console.log('\n💡 SUGGESTION: You may want to create competition entries for these missing items.');
    }

    if (foundCompetitions.length > 0) {
      console.log('\n✅ FOUND COMPETITION ENTRIES:');
      console.log('These logo images have corresponding competition entries:');
      console.log('─'.repeat(80));
      
      foundCompetitions.slice(0, 10).forEach((item, index) => {
        console.log(`${index + 1}. ${item.fileName} → "${item.name}"`);
      });
      
      if (foundCompetitions.length > 10) {
        console.log(`... and ${foundCompetitions.length - 10} more`);
      }
    }

    return {
      totalImages: allImageFiles.length,
      foundCompetitions: foundCompetitions.length,
      missingCompetitions: missingCompetitions.length,
      missingList: missingCompetitions,
      foundList: foundCompetitions
    };

  } catch (error) {
    console.error('❌ Error checking competition logos:', error);
    throw error;
  }
}

/**
 * Get detailed information about a specific missing competition
 */
export async function getMissingCompetitionDetails(nameKey) {
  try {
    console.log(`🔍 Getting details for missing competition: ${nameKey}`);
    
    // Check if it exists in the database
    const { data: competition, error } = await supabase
      .from('competition')
      .select('*')
      .eq('name', nameKey)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 is "not found"
      throw error;
    }

    if (competition) {
      console.log(`✅ Competition "${nameKey}" exists in database:`);
      console.log(competition);
      return { exists: true, data: competition };
    } else {
      console.log(`❌ Competition "${nameKey}" does not exist in database`);
      
      // Check if the logo file exists
      const { data: fileExists, error: fileError } = await supabase.storage
        .from('logos')
        .list('competitions', {
          search: nameKey
        });

      if (fileError) {
        console.error('Error checking file existence:', fileError);
      } else {
        console.log(`📁 Logo files found for "${nameKey}":`, fileExists);
      }

      return { exists: false, logoFiles: fileExists };
    }

  } catch (error) {
    console.error('Error getting competition details:', error);
    throw error;
  }
}

// Run the check if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  checkMissingCompetitionLogos()
    .then(result => {
      console.log('\n✅ Check completed successfully!');
      process.exit(0);
    })
    .catch(error => {
      console.error('❌ Check failed:', error);
      process.exit(1);
    });
}
