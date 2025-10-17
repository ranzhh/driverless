#ifndef UTILS_HPP
#define UTILS_HPP

#include <opencv2/opencv.hpp>

struct ColourRange
{
    cv::Scalar lowerBound;
    cv::Scalar upperBound;
};

struct ColourMaskConfig
{
    std::string name;
    std::vector<ColourRange> colourRanges;
};

struct ColourMaskingResult
{
    cv::Mat mask;
    std::string name;
};

enum Colours
{
    ORANGE,
    BLUE,
    YELLOW
};

cv::Mat createCarMask(const cv::Mat &image);
ColourMaskConfig getColourMask(Colours colour);

#endif // UTILS_HPP
