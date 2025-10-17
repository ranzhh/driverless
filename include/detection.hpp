#include <opencv2/opencv.hpp>
#include "utils.hpp"

#ifndef DETECTION_HPP
#define DETECTION_HPP

struct Cone
{
    cv::Rect boundingBox;
    cv::Point center;
};

cv::Mat detectColour(const cv::Mat &image, ColourMaskConfig cfg, const cv::Mat &negMask, bool dilate = false, bool erode = false);
std::vector<Cone> identifyCones(const cv::Mat &mask, const cv::Mat &image, int vThreshold = 20, int hThreshold = 4, int maxArea = 1000);

#endif // DETECTION_HPP