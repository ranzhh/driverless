#include "../include/utils.hpp"

ColourMaskConfig getColourMask(Colours colour)
{
    switch (colour)
    {
    case ORANGE:
        return {"Orange", {{cv::Scalar(0, 160, 160), cv::Scalar(10, 255, 255)}, {cv::Scalar(160, 160, 160), cv::Scalar(179, 255, 255)}}};
    case BLUE:
        return {"Blue", {{cv::Scalar(100, 60, 105), cv::Scalar(115, 255, 255)}}};
    case YELLOW:
        return {"Yellow", {{cv::Scalar(10, 82, 200), cv::Scalar(20, 255, 255)}}};

    default:
        return {"", {}};
    }
}

cv::Mat createCarMask(const cv::Mat &image)
{
    // The car is approximated as this polygon in the lower half of the image;
    // If I were to do this for real, I'd probably use a more sophisticated polygon and we'd require a stable camera mount
    cv::Mat mask = cv::Mat::zeros(image.size(), CV_8UC1);
    cv::Point pts[8] = {
        cv::Point(image.cols * 0.05, image.rows),
        cv::Point(image.cols * 0.1, image.rows * 0.9),
        cv::Point(image.cols * 0.28, image.rows * 0.9),
        cv::Point(image.cols * 0.38, image.rows * 0.68),
        cv::Point(image.cols * 0.62, image.rows * 0.68),
        cv::Point(image.cols * 0.72, image.rows * 0.9),
        cv::Point(image.cols * 0.9, image.rows * 0.9),
        cv::Point(image.cols * 0.95, image.rows)};
    cv::fillConvexPoly(mask, pts, 8, cv::Scalar(255));
    return mask;
}
