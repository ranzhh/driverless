#include <opencv2/opencv.hpp>
#include "utils.hpp"
#include "params.hpp"

#ifndef DETECTION_HPP
#define DETECTION_HPP

struct Cone
{
    cv::Rect boundingBox;
    cv::Point center;
};

cv::Mat detectColour(const cv::Mat &image, ColourMaskConfig cfg, const cv::Mat &negMask, bool dilate = false, bool erode = false, const ColorDetectionParams &params = ColorDetectionParams());
std::vector<Cone> identifyCones(const cv::Mat &mask, const cv::Mat &image, int vThreshold = 20, int hThreshold = 4, int maxArea = 1000, int minArea = 20);

#endif // DETECTION_HPP
