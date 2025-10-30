#include <opencv2/opencv.hpp>
#include <iostream>
#include "include/pipeline.hpp"

int main(int argc, char *argv[])
{
    std::cout << "=== MODULAR DRIVERLESS PIPELINE ===" << std::endl;
    std::cout << "This program demonstrates three independent steps:" << std::endl;
    std::cout << "  1. Detect cones and save to JSON" << std::endl;
    std::cout << "  2. Draw track lines from JSON data" << std::endl;
    std::cout << "  3. Calculate odometry between frames" << std::endl;
    std::cout << std::endl;

    // Check if user wants to run specific steps
    bool runStep1 = true;
    bool runStep2 = true;
    bool runStep3 = true;

    if (argc > 1)
    {
        // Parse command line arguments to run specific steps
        runStep1 = false;
        runStep2 = false;
        runStep3 = false;

        for (int i = 1; i < argc; ++i)
        {
            std::string arg = argv[i];
            if (arg == "1" || arg == "detect")
                runStep1 = true;
            else if (arg == "2" || arg == "track")
                runStep2 = true;
            else if (arg == "3" || arg == "odometry")
                runStep3 = true;
            else if (arg == "all")
            {
                runStep1 = true;
                runStep2 = true;
                runStep3 = true;
            }
            else
            {
                std::cout << "Usage: " << argv[0] << " [1|detect] [2|track] [3|odometry] [all]" << std::endl;
                std::cout << "  Run specific steps or all steps (default: all)" << std::endl;
                std::cout << "Examples:" << std::endl;
                std::cout << "  " << argv[0] << "           # Run all steps" << std::endl;
                std::cout << "  " << argv[0] << " 1         # Run only step 1 (detect cones)" << std::endl;
                std::cout << "  " << argv[0] << " 2         # Run only step 2 (draw track lines)" << std::endl;
                std::cout << "  " << argv[0] << " 1 2       # Run steps 1 and 2" << std::endl;
                return 0;
            }
        }
    }

    // Define file paths
    const std::string inputImage = "data/frame_1.png";
    const std::string inputImage2 = "data/frame_2.png";
    const std::string conesJsonPath = "output/detected_cones.json";
    const std::string trackImagePath = "output/detected_cones.png";
    const std::string odometryImagePath = "output/odometry_matches.png";

    // STEP 1: Detect cones from image and save to JSON
    if (runStep1)
    {
        ConeDetectionResult cones = detectConesFromImage(inputImage, conesJsonPath);
    }

    // STEP 2: Draw track lines using detected cones from JSON
    if (runStep2)
    {
        cv::Mat trackImage = drawTrackLinesFromCones(inputImage, conesJsonPath, trackImagePath);
    }

    // STEP 3: Calculate odometry between two frames
    if (runStep3)
    {
        cv::Mat odometryImage = calculateOdometry(inputImage, inputImage2, odometryImagePath);
    }

    std::cout << "\n=== PIPELINE COMPLETE ===" << std::endl;
    std::cout << "Output files:" << std::endl;
    if (runStep1)
        std::cout << "  - Detected cones JSON: " << conesJsonPath << std::endl;
    if (runStep2)
        std::cout << "  - Track lines image: " << trackImagePath << std::endl;
    if (runStep3)
        std::cout << "  - Odometry visualization: " << odometryImagePath << std::endl;
    std::cout << "\nView results at: http://localhost:8080" << std::endl;

    return 0;
}
