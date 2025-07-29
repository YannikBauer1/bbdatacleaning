import supabase from './supabase_client.js';
import sharp from 'sharp';
import { Readable } from 'stream';

/**
 * Converts non-PNG images in the locations folder to PNG format
 * Downloads the image, converts it to PNG, uploads the new version, and deletes the old one
 */
async function convertLocationImagesToPNG() {
  try {
    console.log('Starting image conversion process...');
    
    // List all files in the locations folder with pagination
    let allFiles = [];
    let offset = 0;
    const limit = 1000; // Use a larger limit to get more files per request
    
    while (true) {
      const { data: files, error: listError } = await supabase.storage
        .from('background')
        .list('locations', {
          limit: limit,
          offset: offset
        });
      
      if (listError) {
        throw new Error(`Error listing files: ${listError.message}`);
      }
      
      if (!files || files.length === 0) {
        break; // No more files to fetch
      }
      
      allFiles = allFiles.concat(files);
      console.log(`📁 Fetched ${files.length} files (total so far: ${allFiles.length})`);
      
      if (files.length < limit) {
        break; // This was the last batch
      }
      
      offset += limit;
    }
    
    if (allFiles.length === 0) {
      console.log('No files found in locations folder');
      return;
    }
    
    console.log(`Found ${allFiles.length} total files in locations folder`);
    
    // Filter for non-PNG images
    const nonPngImages = allFiles.filter(file => {
      const extension = file.name.toLowerCase().split('.').pop();
      return extension !== 'png' && ['jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff', 'tif'].includes(extension);
    });
    
    if (nonPngImages.length === 0) {
      console.log('No non-PNG images found to convert');
      return;
    }
    
    console.log(`Found ${nonPngImages.length} non-PNG images to convert`);
    
    let convertedCount = 0;
    let errorCount = 0;
    
    // Process each non-PNG image
    for (const image of nonPngImages) {
      try {
        console.log(`Processing: ${image.name}`);
        
        // Download the original image
        const { data: imageData, error: downloadError } = await supabase.storage
          .from('background')
          .download(`locations/${image.name}`);
        
        if (downloadError) {
          console.error(`Error downloading ${image.name}:`, downloadError.message);
          errorCount++;
          continue;
        }
        
        // Convert image to PNG using sharp
        const pngBuffer = await sharp(await imageData.arrayBuffer())
          .png()
          .toBuffer();
        
        // Create new filename with .png extension
        const nameWithoutExtension = image.name.split('.').slice(0, -1).join('.');
        const newFileName = `${nameWithoutExtension}.png`;
        
        // Upload the converted PNG image
        const { error: uploadError } = await supabase.storage
          .from('background')
          .upload(`locations/${newFileName}`, pngBuffer, {
            contentType: 'image/png',
            upsert: true // Overwrite if file already exists
          });
        
        if (uploadError) {
          console.error(`Error uploading converted ${newFileName}:`, uploadError.message);
          errorCount++;
          continue;
        }
        
        // Delete the original non-PNG image
        const { error: deleteError } = await supabase.storage
          .from('background')
          .remove([`locations/${image.name}`]);
        
        if (deleteError) {
          console.error(`Error deleting original ${image.name}:`, deleteError.message);
          // Don't increment error count here as the conversion was successful
          console.warn(`Warning: Original file ${image.name} could not be deleted, but PNG version was uploaded`);
        }
        
        console.log(`✓ Successfully converted ${image.name} to ${newFileName}`);
        convertedCount++;
        
      } catch (error) {
        console.error(`Error processing ${image.name}:`, error.message);
        errorCount++;
      }
    }
    
    console.log('\n=== CONVERSION SUMMARY ===');
    console.log(`Total non-PNG images found: ${nonPngImages.length}`);
    console.log(`Successfully converted: ${convertedCount}`);
    console.log(`Errors: ${errorCount}`);
    
    if (convertedCount > 0) {
      console.log('\nConversion process completed successfully!');
    } else {
      console.log('\nNo images were converted due to errors.');
    }
    
  } catch (error) {
    console.error('Fatal error in conversion process:', error.message);
    throw error;
  }
}

/**
 * Helper function to check the current state of images in the locations folder
 */
async function checkLocationImagesStatus() {
  try {
    console.log('Checking current status of location images...');
    
    // List all files with pagination
    let allFiles = [];
    let offset = 0;
    const limit = 1000;
    
    while (true) {
      const { data: files, error } = await supabase.storage
        .from('background')
        .list('locations', {
          limit: limit,
          offset: offset
        });
      
      if (error) {
        throw new Error(`Error listing files: ${error.message}`);
      }
      
      if (!files || files.length === 0) {
        break; // No more files to fetch
      }
      
      allFiles = allFiles.concat(files);
      console.log(`📁 Fetched ${files.length} files (total so far: ${allFiles.length})`);
      
      if (files.length < limit) {
        break; // This was the last batch
      }
      
      offset += limit;
    }
    
    if (allFiles.length === 0) {
      console.log('No files found in locations folder');
      return;
    }
    
    // Group files by extension
    const fileTypes = {};
    allFiles.forEach(file => {
      const extension = file.name.toLowerCase().split('.').pop();
      if (!fileTypes[extension]) {
        fileTypes[extension] = [];
      }
      fileTypes[extension].push(file.name);
    });
    
    console.log('\n=== LOCATION IMAGES STATUS ===');
    console.log(`Total files: ${allFiles.length}`);
    console.log('\nFiles by type:');
    
    Object.entries(fileTypes).forEach(([extension, fileList]) => {
      console.log(`${extension.toUpperCase()}: ${fileList.length} files`);
    });
    
    const nonPngCount = Object.entries(fileTypes)
      .filter(([ext]) => ext !== 'png')
      .reduce((sum, [, files]) => sum + files.length, 0);
    
    if (nonPngCount > 0) {
      console.log(`\n⚠️  Found ${nonPngCount} non-PNG images that can be converted`);
    } else {
      console.log('\n✅ All images are already in PNG format');
    }
    
  } catch (error) {
    console.error('Error checking image status:', error.message);
  }
}

// Export functions for use in other modules
export { convertLocationImagesToPNG, checkLocationImagesStatus };

// Run the conversion if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  
  if (command === 'check') {
    checkLocationImagesStatus();
  } else if (command === 'convert') {
    convertLocationImagesToPNG();
  } else {
    console.log('Usage:');
    console.log('  node convertFlagsImages.js check    - Check current status of images');
    console.log('  node convertFlagsImages.js convert  - Convert non-PNG images to PNG');
  }
}
