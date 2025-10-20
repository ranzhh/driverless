#include "../include/detection.hpp"

#define SHOW_COLOUR_MASKS
#define SHOW_DETECTED_CONES

cv::Mat detectColour(const cv::Mat &image, ColourMaskConfig cfg, const cv::Mat &negMask, bool dilate, bool erode)
{
    cv::Mat retMask = cv::Mat::zeros(image.size(), CV_8UC1);

    for (const auto &colourRange : cfg.colourRanges)
    {
        // Threshold
        cv::Mat mask;
        cv::inRange(image, colourRange.lowerBound, colourRange.upperBound, mask);
        cv::bitwise_or(retMask, mask, retMask);
    }

    // Remove the car area from the mask
    cv::bitwise_and(retMask, ~negMask, retMask);

    if (erode)
        cv::erode(retMask, retMask, cv::Mat(), cv::Point(-1, -1), 1);

    if (dilate)
        cv::dilate(retMask, retMask, cv::Mat(), cv::Point(-1, -1), 2);

    // Morphological operations to clean up the mask
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(2, 2));

    cv::morphologyEx(retMask, retMask, cv::MORPH_CLOSE, kernel);
    cv::morphologyEx(retMask, retMask, cv::MORPH_OPEN, kernel);

    return retMask;
}

std::vector<Cone> identifyCones(const cv::Mat &mask, const cv::Mat &image, int vThreshold, int hThreshold, int maxArea)
{
    std::vector<Cone> detectedParts;
    auto img = image.clone();
    // Find contours
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    for (const auto &contour : contours)
    {
        cv::Rect boundingBox = cv::boundingRect(contour);

        // If the bounding box is too small or big, skip
        if (boundingBox.area() < 20 || boundingBox.area() > maxArea)
        {
            std::cout << "\tDiscarding contour with area: " << boundingBox.area() << std::endl;
            continue;
        }

        // Calculate and draw center
        cv::Moments M = cv::moments(contour);
        if (M.m00 != 0)
        {
            int cX = static_cast<int>(M.m10 / M.m00);
            int cY = static_cast<int>(M.m01 / M.m00);

            detectedParts.push_back({boundingBox, cv::Point(cX, cY)});
            cv::rectangle(img, boundingBox, cv::Scalar(255, 0, 0), 1);
            cv::circle(img, cv::Point(cX, cY), 2, cv::Scalar(0, 0, 255), -1);
        }
    }

    // Filter out duplicates based on proximity, keep the lowest (base)
    std::sort(detectedParts.begin(), detectedParts.end(), [](const Cone &a, const Cone &b)
              { return a.center.y < b.center.y; });

    std::vector<Cone> cones;

    // Start from the top cones and merge downwards
    for (const auto &part : detectedParts)
    {
        bool merged = false;
        for (int i = 0; i < cones.size(); ++i)
        {
            const auto &cone = cones[i];
            {
                if (std::abs(part.center.x - cone.center.x) < hThreshold &&
                    std::abs(part.center.y - cone.center.y) < vThreshold)
                {
                    // Merge the bounding boxes to include both parts
                    cones[i].boundingBox |= part.boundingBox;
                    cones[i].center.x = (cones[i].center.x + part.center.x) / 2;
                    cones[i].center.y = (cones[i].center.y + part.center.y) / 2;
                    merged = true;
                }
            }
        }
        if (!merged)
            cones.push_back(part);
    }

    // Draw bounding boxes for visualization
    for (const auto &cone : cones)
    {
        cv::rectangle(img, cone.boundingBox, cv::Scalar(0, 255, 0), 1);
        cv::circle(img, cone.center, 2, cv::Scalar(255, 0, 0), -1);
    }

    return cones;
}
