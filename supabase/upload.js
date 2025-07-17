import { getAllathlete } from './athletes.js';
import { uploadNewAthletesOnly, uploadAthletesFromCSV } from './upload_athletes.js';
import { uploadNewCompetitionsOnly, uploadCompetitionsFromCSV } from './upload_competitions.js';
import { uploadNewEventsOnly, uploadEventsFromCSV } from './upload_events.js';
import { uploadNewResultsOnly, uploadResultsFromCSV } from './upload_results.js';
import { uploadNewSchedule2025Only, uploadSchedule2025FromCSV } from './upload_schedule2025.js';
import { fileURLToPath } from 'node:url';

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

// Function to upload athletes from CSV (new functionality)
export async function uploadAthletesFromCSVFile() {
  try {
    console.log('Uploading athletes from CSV...');
    const result = await uploadNewAthletesOnly();
    return result;
  } catch (error) {
    console.error('Error uploading athletes from CSV:', error);
    throw error;
  }
}

// Function to upload all athletes from CSV (including duplicates)
export async function uploadAllAthletesFromCSV() {
  try {
    console.log('Uploading all athletes from CSV...');
    const result = await uploadAthletesFromCSV();
    return result;
  } catch (error) {
    console.error('Error uploading all athletes from CSV:', error);
    throw error;
  }
}

// Function to upload competitions from CSV (new functionality)
export async function uploadCompetitionsFromCSVFile() {
  try {
    console.log('Uploading competitions from CSV...');
    const result = await uploadNewCompetitionsOnly();
    return result;
  } catch (error) {
    console.error('Error uploading competitions from CSV:', error);
    throw error;
  }
}

// Function to upload all competitions from CSV (including duplicates)
export async function uploadAllCompetitionsFromCSV() {
  try {
    console.log('Uploading all competitions from CSV...');
    const result = await uploadCompetitionsFromCSV();
    return result;
  } catch (error) {
    console.error('Error uploading all competitions from CSV:', error);
    throw error;
  }
}

// Function to upload events from CSV (new functionality)
export async function uploadEventsFromCSVFile() {
  try {
    console.log('Uploading events from CSV...');
    const result = await uploadNewEventsOnly();
    return result;
  } catch (error) {
    console.error('Error uploading events from CSV:', error);
    throw error;
  }
}

// Function to upload all events from CSV (including duplicates)
export async function uploadAllEventsFromCSV() {
  try {
    console.log('Uploading all events from CSV...');
    const result = await uploadEventsFromCSV();
    return result;
  } catch (error) {
    console.error('Error uploading all events from CSV:', error);
    throw error;
  }
}

// Function to upload results from CSV (new functionality)
export async function uploadResultsFromCSVFile() {
  try {
    console.log('Uploading results from CSV...');
    const result = await uploadNewResultsOnly();
    return result;
  } catch (error) {
    console.error('Error uploading results from CSV:', error);
    throw error;
  }
}

// Function to upload all results from CSV (including duplicates)
export async function uploadAllResultsFromCSV() {
  try {
    console.log('Uploading all results from CSV...');
    const result = await uploadResultsFromCSV();
    return result;
  } catch (error) {
    console.error('Error uploading all results from CSV:', error);
    throw error;
  }
}

// Function to upload schedule2025 from CSV (new functionality)
export async function uploadSchedule2025FromCSVFile() {
  try {
    console.log('Uploading schedule2025 from CSV...');
    const result = await uploadNewSchedule2025Only();
    return result;
  } catch (error) {
    console.error('Error uploading schedule2025 from CSV:', error);
    throw error;
  }
}

// Function to upload all schedule2025 from CSV (including duplicates)
export async function uploadAllSchedule2025FromCSV() {
  try {
    console.log('Uploading all schedule2025 from CSV...');
    const result = await uploadSchedule2025FromCSV();
    return result;
  } catch (error) {
    console.error('Error uploading all schedule2025 from CSV:', error);
    throw error;
  }
}

// Example usage
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const mode = args[0] || 'fetch'; // 'fetch', 'upload', 'upload-all', 'competitions', 'competitions-all', 'events', 'events-all', 'results', 'results-all', 'schedule2025', 'schedule2025-all'
  
  switch (mode) {
    case 'upload':
      uploadAthletesFromCSVFile()
        .then(() => console.log('Athletes CSV upload completed successfully'))
        .catch(error => console.error('Athletes CSV upload failed:', error));
      break;
    case 'upload-all':
      uploadAllAthletesFromCSV()
        .then(() => console.log('All athletes CSV upload completed successfully'))
        .catch(error => console.error('All athletes CSV upload failed:', error));
      break;
    case 'competitions':
      uploadCompetitionsFromCSVFile()
        .then(() => console.log('Competitions CSV upload completed successfully'))
        .catch(error => console.error('Competitions CSV upload failed:', error));
      break;
    case 'competitions-all':
      uploadAllCompetitionsFromCSV()
        .then(() => console.log('All competitions CSV upload completed successfully'))
        .catch(error => console.error('All competitions CSV upload failed:', error));
      break;
    case 'events':
      uploadEventsFromCSVFile()
        .then(() => console.log('Events CSV upload completed successfully'))
        .catch(error => console.error('Events CSV upload failed:', error));
      break;
    case 'events-all':
      uploadAllEventsFromCSV()
        .then(() => console.log('All events CSV upload completed successfully'))
        .catch(error => console.error('All events CSV upload failed:', error));
      break;
    case 'results':
      uploadResultsFromCSVFile()
        .then(() => console.log('Results CSV upload completed successfully'))
        .catch(error => console.error('Results CSV upload failed:', error));
      break;
    case 'results-all':
      uploadAllResultsFromCSV()
        .then(() => console.log('All results CSV upload completed successfully'))
        .catch(error => console.error('All results CSV upload failed:', error));
      break;
    case 'schedule2025':
      uploadSchedule2025FromCSVFile()
        .then(() => console.log('Schedule2025 CSV upload completed successfully'))
        .catch(error => console.error('Schedule2025 CSV upload failed:', error));
      break;
    case 'schedule2025-all':
      uploadAllSchedule2025FromCSV()
        .then(() => console.log('All schedule2025 CSV upload completed successfully'))
        .catch(error => console.error('All schedule2025 CSV upload failed:', error));
      break;
    default:
      uploadAthletes()
        .then(() => console.log('Fetch completed successfully'))
        .catch(error => console.error('Fetch failed:', error));
  }
}
