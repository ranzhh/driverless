#ifndef PIPELINE_HPP
#define PIPELINE_HPP

#include <opencv2/opencv.hpp>
#include <string>
#include "detection.hpp"

// Structure to hold intermediate cone detection results
struct ConeDetectionResult
{
    std::vector<Cone> orangeCones;
    std::vector<Cone> blueCones;
    std::vector<Cone> yellowCones;
};

// Step 1: Detect cones from an image and save results to JSON
// Returns: ConeDetectionResult containing all detected cones
// Saves: JSON file with cone positions and types
ConeDetectionResult detectConesFromImage(
    const std::string &imagePath,
    const std::string &outputJsonPath);

// Step 2: Draw track lines using pre-detected cones from JSON
// Reads: JSON file with cone positions
// Returns: Output image with track lines drawn
// Saves: Output image file
cv::Mat drawTrackLinesFromCones(
    const std::string &imagePath,
    const std::string &inputJsonPath,
    const std::string &outputImagePath);

// Step 3: Calculate odometry between two frames
// Returns: Image with feature matches visualized
// Saves: Output image file and prints R and t matrices
cv::Mat calculateOdometry(
    const std::string &image1Path,
    const std::string &image2Path,
    const std::string &outputImagePath);

// Utility functions for JSON serialization
void saveConeDetectionToJson(const ConeDetectionResult &result, const std::string &filepath);
ConeDetectionResult loadConeDetectionFromJson(const std::string &filepath);

#endif // PIPELINE_HPP
