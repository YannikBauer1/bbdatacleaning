import fs from "fs";
import { parse } from "csv-parse/sync";
import { stringify } from "csv-stringify/sync";

// Read the input file
const inputFile = fs.readFileSync("all/musclememory_raw.csv", "utf-8");

// Parse the CSV
const records = parse(inputFile, {
  columns: true,
  skip_empty_lines: true,
});

// Transform the data
const transformedRecords = [];
let currentRecord = null;

for (let i = 0; i < records.length; i++) {
  const record = records[i];

  // Skip if this is a country continuation line (starts with space and parentheses)
  if (record.Competition && record.Competition.trim().startsWith("(")) {
    if (currentRecord) {
      // Extract country from the continuation line
      const countryMatch = record.Competition.match(/\(([^)]+)\)/);
      const country = countryMatch ? countryMatch[1] : "";
      currentRecord.Country = country;
      transformedRecords.push(currentRecord);
      currentRecord = null;
    }
    continue;
  }

  // Extract year from the Year field
  const year = record.Year;

  // Create a date string (using January 1st as default since we don't have specific dates)
  const date = `${year}-01-01`;

  // Determine competition type based on Gender and Category
  let competitionType = "Unknown";
  if (record.Gender === "female") {
    if (record.Category) {
      competitionType = `Female - ${record.Category}`;
    } else {
      competitionType = "Female";
    }
  } else if (record.Gender === "male") {
    if (record.Category) {
      competitionType = `Male - ${record.Category}`;
    } else {
      competitionType = "Male";
    }
  }

  // Create the transformed record
  currentRecord = {
    Competition: record.Competition,
    Location: "", // No location data in source
    Date: date,
    "Competitor Name": record.Name,
    Country: "", // Will be filled in if there's a continuation line
    Judging: "", // No judging scores in source
    Finals: "", // No finals scores in source
    "Round 2": "", // No round 2 scores in source
    "Round 3": "", // No round 3 scores in source
    Routine: "", // No routine scores in source
    Total: record.Score || "", // Use Score if available
    Place: record.Place,
    "Competition Type": competitionType,
  };

  // If there's no next line or next line doesn't contain country info, add the record now
  if (!records[i + 1] || !records[i + 1].Competition?.trim().startsWith("(")) {
    transformedRecords.push(currentRecord);
    currentRecord = null;
  }
}

// Convert to CSV
const output = stringify(transformedRecords, {
  header: true,
  columns: [
    "Competition",
    "Location",
    "Date",
    "Competitor Name",
    "Country",
    "Judging",
    "Finals",
    "Round 2",
    "Round 3",
    "Routine",
    "Total",
    "Place",
    "Competition Type",
  ],
});

// Write to output file
fs.writeFileSync("all/output/musclememory_transformed.csv", output);
