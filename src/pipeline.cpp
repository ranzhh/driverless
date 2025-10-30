#include "../include/pipeline.hpp"
#include "../include/utils.hpp"
#include "../include/detection.hpp"
#include "../include/track.hpp"
#include "../include/odometry.hpp"
#include <fstream>
#include <sstream>
#include <iostream>

// JSON serialization helpers
void saveConeDetectionToJson(const ConeDetectionResult &result, const std::string &filepath)
{
    std::ofstream file(filepath);
    if (!file.is_open())
    {
        std::cerr << "Error: Could not open file for writing: " << filepath << std::endl;
        return;
    }

    file << "{\n";

    // Save orange cones
    file << "  \"orangeCones\": [\n";
    for (size_t i = 0; i < result.orangeCones.size(); ++i)
    {
        const auto &cone = result.orangeCones[i];
        file << "    {";
        file << "\"x\": " << cone.center.x << ", ";
        file << "\"y\": " << cone.center.y << ", ";
        file << "\"bbox_x\": " << cone.boundingBox.x << ", ";
        file << "\"bbox_y\": " << cone.boundingBox.y << ", ";
        file << "\"bbox_width\": " << cone.boundingBox.width << ", ";
        file << "\"bbox_height\": " << cone.boundingBox.height;
        file << "}";
        if (i < result.orangeCones.size() - 1)
            file << ",";
        file << "\n";
    }
    file << "  ],\n";

    // Save blue cones
    file << "  \"blueCones\": [\n";
    for (size_t i = 0; i < result.blueCones.size(); ++i)
    {
        const auto &cone = result.blueCones[i];
        file << "    {";
        file << "\"x\": " << cone.center.x << ", ";
        file << "\"y\": " << cone.center.y << ", ";
        file << "\"bbox_x\": " << cone.boundingBox.x << ", ";
        file << "\"bbox_y\": " << cone.boundingBox.y << ", ";
        file << "\"bbox_width\": " << cone.boundingBox.width << ", ";
        file << "\"bbox_height\": " << cone.boundingBox.height;
        file << "}";
        if (i < result.blueCones.size() - 1)
            file << ",";
        file << "\n";
    }
    file << "  ],\n";

    // Save yellow cones
    file << "  \"yellowCones\": [\n";
    for (size_t i = 0; i < result.yellowCones.size(); ++i)
    {
        const auto &cone = result.yellowCones[i];
        file << "    {";
        file << "\"x\": " << cone.center.x << ", ";
        file << "\"y\": " << cone.center.y << ", ";
        file << "\"bbox_x\": " << cone.boundingBox.x << ", ";
        file << "\"bbox_y\": " << cone.boundingBox.y << ", ";
        file << "\"bbox_width\": " << cone.boundingBox.width << ", ";
        file << "\"bbox_height\": " << cone.boundingBox.height;
        file << "}";
        if (i < result.yellowCones.size() - 1)
            file << ",";
        file << "\n";
    }
    file << "  ]\n";

    file << "}\n";
    file.close();

    std::cout << "Saved cone detection results to: " << filepath << std::endl;
}

// Simple JSON parser for cone data
ConeDetectionResult loadConeDetectionFromJson(const std::string &filepath)
{
    ConeDetectionResult result;
    std::ifstream file(filepath);

    if (!file.is_open())
    {
        std::cerr << "Error: Could not open file for reading: " << filepath << std::endl;
        return result;
    }

    std::string line;
    std::vector<Cone> *currentCones = nullptr;

    while (std::getline(file, line))
    {
        // Simple parsing - look for cone type arrays
        if (line.find("\"orangeCones\"") != std::string::npos)
        {
            currentCones = &result.orangeCones;
        }
        else if (line.find("\"blueCones\"") != std::string::npos)
        {
            currentCones = &result.blueCones;
        }
        else if (line.find("\"yellowCones\"") != std::string::npos)
        {
            currentCones = &result.yellowCones;
        }
        else if (currentCones && line.find("\"x\":") != std::string::npos)
        {
            // Parse cone data
            Cone cone;
            std::istringstream iss(line);
            std::string token;

            // Extract values using simple string parsing
            size_t pos;

            // Get x
            pos = line.find("\"x\": ");
            if (pos != std::string::npos)
            {
                cone.center.x = std::stoi(line.substr(pos + 5));
            }

            // Get y
            pos = line.find("\"y\": ");
            if (pos != std::string::npos)
            {
                cone.center.y = std::stoi(line.substr(pos + 5));
            }

            // Get bbox_x
            pos = line.find("\"bbox_x\": ");
            if (pos != std::string::npos)
            {
                cone.boundingBox.x = std::stoi(line.substr(pos + 10));
            }

            // Get bbox_y
            pos = line.find("\"bbox_y\": ");
            if (pos != std::string::npos)
            {
                cone.boundingBox.y = std::stoi(line.substr(pos + 10));
            }

            // Get bbox_width
            pos = line.find("\"bbox_width\": ");
            if (pos != std::string::npos)
            {
                cone.boundingBox.width = std::stoi(line.substr(pos + 14));
            }

            // Get bbox_height
            pos = line.find("\"bbox_height\": ");
            if (pos != std::string::npos)
            {
                cone.boundingBox.height = std::stoi(line.substr(pos + 15));
            }

            currentCones->push_back(cone);
        }
    }

    file.close();

    std::cout << "Loaded cone detection results from: " << filepath << std::endl;
    std::cout << "  Orange cones: " << result.orangeCones.size() << std::endl;
    std::cout << "  Blue cones: " << result.blueCones.size() << std::endl;
    std::cout << "  Yellow cones: " << result.yellowCones.size() << std::endl;

    return result;
}

// Step 1: Detect cones from an image
ConeDetectionResult detectConesFromImage(
    const std::string &imagePath,
    const std::string &outputJsonPath)
{
    std::cout << "\n=== STEP 1: DETECTING CONES ===" << std::endl;
    std::cout << "Input image: " << imagePath << std::endl;

    ConeDetectionResult result;

    // Load image
    cv::Mat img = cv::imread(imagePath);
    if (img.empty())
    {
        std::cerr << "Error: Could not load image: " << imagePath << std::endl;
        return result;
    }

    // Convert to HSV color space
    cv::Mat hsvImage;
    cv::cvtColor(img, hsvImage, cv::COLOR_BGR2HSV);

    // Create masks
    cv::Mat carMask = createCarMask(img);
    cv::Mat roadMask = detectColour(hsvImage, {"Road", {{cv::Scalar(0, 0, 0), cv::Scalar(179, 70, 190)}}}, carMask, false, true);

    // Detect different colored cones
    cv::Mat orangeMask = detectColour(hsvImage, getColourMask(ORANGE), carMask | roadMask, true);
    cv::Mat blueMask = detectColour(hsvImage, getColourMask(BLUE), carMask | roadMask, true);
    cv::Mat yellowMask = detectColour(hsvImage, getColourMask(YELLOW), carMask | roadMask, true);

    // Identify cones
    result.orangeCones = identifyCones(orangeMask, img, 100, 10, 4000);
    result.blueCones = identifyCones(blueMask, img, 20);
    result.yellowCones = identifyCones(yellowMask, img, 20);

    // Refine orange cones (keep only closest 2)
    std::sort(result.orangeCones.begin(), result.orangeCones.end(), [](const Cone &a, const Cone &b)
              { return a.center.y > b.center.y; });

    if (result.orangeCones.size() > 2)
        result.orangeCones.resize(2);

    // Save results to JSON
    saveConeDetectionToJson(result, outputJsonPath);

    std::cout << "Detected:" << std::endl;
    std::cout << "  Orange cones: " << result.orangeCones.size() << std::endl;
    std::cout << "  Blue cones: " << result.blueCones.size() << std::endl;
    std::cout << "  Yellow cones: " << result.yellowCones.size() << std::endl;

    return result;
}

// Step 2: Draw track lines using pre-detected cones
cv::Mat drawTrackLinesFromCones(
    const std::string &imagePath,
    const std::string &inputJsonPath,
    const std::string &outputImagePath)
{
    std::cout << "\n=== STEP 2: DRAWING TRACK LINES ===" << std::endl;
    std::cout << "Input image: " << imagePath << std::endl;
    std::cout << "Input cones JSON: " << inputJsonPath << std::endl;

    // Load image
    cv::Mat img = cv::imread(imagePath);
    if (img.empty())
    {
        std::cerr << "Error: Could not load image: " << imagePath << std::endl;
        return cv::Mat();
    }

    // Load cone detection results from JSON
    ConeDetectionResult cones = loadConeDetectionFromJson(inputJsonPath);

    // Draw track lines
    cv::Mat outputImage;
    img.copyTo(outputImage);

    outputImage = connectCones(outputImage, cones.blueCones, cv::Scalar(255, 0, 0), 150);
    outputImage = connectCones(outputImage, cones.yellowCones, cv::Scalar(0, 255, 255), 150);

    // Save output image
    cv::imwrite(outputImagePath, outputImage);
    std::cout << "Saved track lines image to: " << outputImagePath << std::endl;

    return outputImage;
}

// Step 3: Calculate odometry between two frames
cv::Mat calculateOdometry(
    const std::string &image1Path,
    const std::string &image2Path,
    const std::string &outputImagePath)
{
    std::cout << "\n=== STEP 3: CALCULATING ODOMETRY ===" << std::endl;
    std::cout << "Frame 1: " << image1Path << std::endl;
    std::cout << "Frame 2: " << image2Path << std::endl;

    // Load images
    cv::Mat img1 = cv::imread(image1Path);
    cv::Mat img2 = cv::imread(image2Path);

    if (img1.empty() || img2.empty())
    {
        std::cerr << "Error: Could not load one or both images" << std::endl;
        return cv::Mat();
    }

    // Create car mask for the first image
    cv::Mat carMask = createCarMask(img1);

    // Calculate odometry
    cv::Mat odometryResult = calcOdometry(img1, img2, carMask);

    // Save output image
    cv::imwrite(outputImagePath, odometryResult);
    std::cout << "Saved odometry visualization to: " << outputImagePath << std::endl;

    return odometryResult;
}
