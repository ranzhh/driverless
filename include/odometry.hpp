#ifndef ODOMETRY_HPP
#define ODOMETRY_HPP

#include <opencv2/opencv.hpp>
#include "params.hpp"

cv::Mat calcOdometry(const cv::Mat &prevFrame, const cv::Mat &currFrame, cv::Mat negMask, const OdometryParams &params = OdometryParams());

#endif // ODOMETRY_HPP
