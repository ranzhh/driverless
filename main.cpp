#include <opencv2/opencv.hpp>
#include <iostream>
#include "include/utils.hpp"
#include "include/detection.hpp"
#include "include/track.hpp"

int main()
{
    // Task 1: Load and display an image
    std::cout << "Task 1: Loading and displaying an image..." << std::endl;

    cv::Mat img = cv::imread("data/frame_1.png");
    if (img.empty())
        return -1;

    cv::imshow("Original image", img);
    cv::waitKey(0);

    // Task 2: Detect the cones in the image
    std::cout << "Task 2: Detecting cones in the image..." << std::endl;

    // Convert to HSV color space
    cv::Mat hsvImage;
    cv::cvtColor(img, hsvImage, cv::COLOR_BGR2HSV);

    cv::Mat carMask = createCarMask(img);
    cv::Mat roadMask = detectColour(hsvImage, {"Road", {{cv::Scalar(0, 0, 0), cv::Scalar(179, 70, 190)}}}, carMask, false, true);

    cv::Mat orangeMask = detectColour(hsvImage, getColourMask(ORANGE), carMask | roadMask, true);
    cv::Mat blueMask = detectColour(hsvImage, getColourMask(BLUE), carMask | roadMask, true);
    cv::Mat yellowMask = detectColour(hsvImage, getColourMask(YELLOW), carMask | roadMask, true);

    // The vertical threshold should really be calculated based on the spacing of the cones in the real world and the camera parameters...
    // For now these seem to work ok
    auto orangeCones = identifyCones(orangeMask, img, 100, 10, 4000);
    auto blueCones = identifyCones(blueMask, img, 20);
    auto yellowCones = identifyCones(yellowMask, img, 20);

    // Small refinement, there's no reason to have too many orange if there are any lying around
    // The orange cones should only be 2 and close to the car when we're starting; in a real world scenario we'd ignore them after starting.
    std::sort(orangeCones.begin(), orangeCones.end(), [](const Cone &a, const Cone &b)
              { return a.center.y > b.center.y; });

    if (orangeCones.size() > 2)
        orangeCones.resize(2);

    // Connect the cones
    cv::Mat outputImage;
    img.copyTo(outputImage);
    outputImage = connectCones(outputImage, blueCones, cv::Scalar(255, 0, 0), 150);
    outputImage = connectCones(outputImage, yellowCones, cv::Scalar(0, 255, 255), 150);

    return 0;
}
