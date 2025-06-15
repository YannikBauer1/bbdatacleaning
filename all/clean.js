import fs from "fs";
import { parse } from "csv-parse/sync";
import { stringify } from "csv-stringify/sync";

// Read the input file
const inputFile = fs.readFileSync("all/everything_raw.csv", "utf-8");

// Parse the CSV
const records = parse(inputFile, {
  columns: true,
  skip_empty_lines: true,
});

// TODO: Make changes to records here
const cleanedRecords = records.map(record => {
  // Example: return record unchanged
  return record;
});

// Convert to CSV
const output = stringify(cleanedRecords, {
  header: true,
  columns: Object.keys(cleanedRecords[0] || {}),
});

// Write to output file
fs.writeFileSync("all/everything_clean.csv", output);

console.log("Cleaned data written to all/everything_clean.csv");
