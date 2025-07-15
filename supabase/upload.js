import { getAllathlete } from './athletes.js';
import { fileURLToPath } from 'url';

// Function to get all athletes and log them
export async function uploadAthletes() {
  try {
    console.log('Fetching all athletes...');
    const athletes = await getAllathlete();
    
    console.log(`Found ${athletes.length} athletes:`);
    console.log(athletes);
    
    return athletes;
  } catch (error) {
    console.error('Error in uploadAthletes:', error);
    throw error;
  }
}

// Example usage
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  uploadAthletes()
    .then(() => console.log('Upload completed successfully'))
    .catch(error => console.error('Upload failed:', error));
}
