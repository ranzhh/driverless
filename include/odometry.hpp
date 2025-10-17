#ifndef ODOMETRY_HPP
#define ODOMETRY_HPP

#include <opencv2/opencv.hpp>

cv::Mat calcOdometry(const cv::Mat &prevFrame, const cv::Mat &currFrame, cv::Mat negMask);

#endif // ODOMETRY_HPP