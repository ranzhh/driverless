#include <opencv2/opencv.hpp>
#include "../include/detection.hpp"

#ifndef TRACK_HPP
#define TRACK_HPP

cv::Mat connectCones(const cv::Mat &image, std::vector<Cone> &cones, cv::Scalar lineColor, int maxDistance = 50);

#endif // TRACK_HPP