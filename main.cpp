#include <opencv2/opencv.hpp>
#include <iostream>
#include "include/utils.hpp"
#include "include/detection.hpp"
#include "include/track.hpp"
#include "include/odometry.hpp"

int main()
{
    // Task 1: Load and display an image
    std::cout << "Task 1: Loading and displaying an image..." << std::endl;

    cv::Mat img1 = cv::imread("data/frame_1.png");
    cv::Mat img2 = cv::imread("data/frame_2.png");
    if (img1.empty())
        return -1;

    cv::imwrite("output/original_image.png", img1);
    std::cout << "Saved: output/original_image.png" << std::endl;

    // Task 2: Detect the cones in the image
    std::cout << "Task 2 (and 3): Detecting cones (and their colour) in the image..." << std::endl;

    // Convert to HSV color space
    cv::Mat hsvImage;
    cv::cvtColor(img1, hsvImage, cv::COLOR_BGR2HSV);

    cv::Mat carMask = createCarMask(img1);
    cv::Mat roadMask = detectColour(hsvImage, {"Road", {{cv::Scalar(0, 0, 0), cv::Scalar(179, 70, 190)}}}, carMask, false, true);

    cv::Mat orangeMask = detectColour(hsvImage, getColourMask(ORANGE), carMask | roadMask, true);
    cv::Mat blueMask = detectColour(hsvImage, getColourMask(BLUE), carMask | roadMask, true);
    cv::Mat yellowMask = detectColour(hsvImage, getColourMask(YELLOW), carMask | roadMask, true);

    // The vertical threshold should really be calculated based on the spacing of the cones in the real world and the camera parameters...
    // For now these seem to work ok
    auto orangeCones = identifyCones(orangeMask, img1, 100, 10, 4000);
    auto blueCones = identifyCones(blueMask, img1, 20);
    auto yellowCones = identifyCones(yellowMask, img1, 20);

    // Small refinement, there's no reason to have too many orange if there are any lying around
    // The orange cones should only be 2 and close to the car when we're starting; in a real world scenario we'd ignore them after starting.
    std::sort(orangeCones.begin(), orangeCones.end(), [](const Cone &a, const Cone &b)
              { return a.center.y > b.center.y; });

    if (orangeCones.size() > 2)
        orangeCones.resize(2);

    // Task 4: Find the track boundaries by connecting the cones
    std::cout << "Task 4: Connecting the detected cones to form track boundaries..." << std::endl;

    // Connect the cones
    cv::Mat outputImage;
    img1.copyTo(outputImage);
    outputImage = connectCones(outputImage, blueCones, cv::Scalar(255, 0, 0), 150);
    outputImage = connectCones(outputImage, yellowCones, cv::Scalar(0, 255, 255), 150);

    cv::imwrite("output/detected_cones.png", outputImage);
    std::cout << "Saved: output/detected_cones.png" << std::endl;

    cv::Mat odometryResult = calcOdometry(img1, img2, carMask);
    cv::imwrite("output/odometry_matches.png", odometryResult);
    std::cout << "Saved: output/odometry_matches.png" << std::endl;

    std::cout << "\nAll results saved to output/ directory" << std::endl;
    std::cout << "View them at: http://localhost:8080" << std::endl;

    return 0;
}
