const fs = require('fs');
const path = require('path');

/**
 * Extracts the base name and size information from a filename
 * @param {string} filename - The filename to analyze
 * @returns {Object} - Object containing base name and size information
 */
function parseFilename(filename) {
    // Remove file extension
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, '');
    
    // Check if filename contains size pattern (e.g., -791x1024)
    const sizeMatch = nameWithoutExt.match(/-(\d+)x(\d+)$/);
    
    if (sizeMatch) {
        const width = parseInt(sizeMatch[1]);
        const height = parseInt(sizeMatch[2]);
        const baseName = nameWithoutExt.replace(/-(\d+)x(\d+)$/, '');
        return {
            baseName,
            hasSize: true,
            width,
            height,
            totalPixels: width * height
        };
    } else {
        return {
            baseName: nameWithoutExt,
            hasSize: false,
            width: 0,
            height: 0,
            totalPixels: 0
        };
    }
}

/**
 * Groups similar images and selects the best quality version
 * @param {string} sourceDir - Directory containing the images
 * @param {string} targetDir - Directory to store unique images
 */
function filterUniqueImages(sourceDir, targetDir) {
    // Create target directory if it doesn't exist
    if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
    }

    // Get all year folders
    const yearFolders = fs.readdirSync(sourceDir)
        .filter(item => fs.statSync(path.join(sourceDir, item)).isDirectory());

    // Process each year folder
    yearFolders.forEach(year => {
        const yearSourceDir = path.join(sourceDir, year);
        const yearTargetDir = path.join(targetDir, year);
        
        // Create year directory in target if it doesn't exist
        if (!fs.existsSync(yearTargetDir)) {
            fs.mkdirSync(yearTargetDir, { recursive: true });
        }

        // Get all files in the year directory
        const files = fs.readdirSync(yearSourceDir);
        
        // Group files by their base name
        const fileGroups = {};
        
        files.forEach(file => {
            const fileInfo = parseFilename(file);
            if (!fileGroups[fileInfo.baseName]) {
                fileGroups[fileInfo.baseName] = [];
            }
            fileGroups[fileInfo.baseName].push({
                filename: file,
                ...fileInfo
            });
        });

        // Process each group and select the best quality image
        Object.entries(fileGroups).forEach(([baseName, group]) => {
            // Sort group by quality preference:
            // 1. Files without size suffix
            // 2. Files with largest total pixels
            group.sort((a, b) => {
                if (a.hasSize && !b.hasSize) return 1;
                if (!a.hasSize && b.hasSize) return -1;
                return b.totalPixels - a.totalPixels;
            });

            // Select the best quality image
            const bestImage = group[0];
            
            // Copy the best image to the target directory
            const sourcePath = path.join(yearSourceDir, bestImage.filename);
            const targetPath = path.join(yearTargetDir, bestImage.filename);
            
            fs.copyFileSync(sourcePath, targetPath);
            console.log(`Copied: ${year}/${bestImage.filename} (${group.length} similar images)`);
        });
    });
}

// Example usage
const sourceDir = './waybackMachine/downloaded_images';
const targetDir = './waybackMachine/unique_images';

filterUniqueImages(sourceDir, targetDir); 