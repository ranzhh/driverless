#include "../include/detection.hpp"

cv::Mat calcOdometry(const cv::Mat &prevFrame, const cv::Mat &currFrame, cv::Mat negMask)
{
    // Detect ORB keypoints and descriptors
    cv::Ptr<cv::ORB> orb = cv::ORB::create();
    std::vector<cv::KeyPoint> keypointsPrev, keypointsCurr;
    cv::Mat descriptorsPrev, descriptorsCurr;

    orb->detectAndCompute(prevFrame, ~negMask, keypointsPrev, descriptorsPrev);
    orb->detectAndCompute(currFrame, ~negMask, keypointsCurr, descriptorsCurr);

    // Brute force matcher with Hamming distance
    cv::BFMatcher matcher(cv::NORM_HAMMING);
    std::vector<cv::DMatch> matches;
    matcher.match(descriptorsPrev, descriptorsCurr, matches);

    // Filter good matches based on distance
    double maxDist = 0;
    double minDist = 100;
    for (int i = 0; i < descriptorsPrev.rows; i++)
    {
        double dist = matches[i].distance;
        if (dist < minDist)
            minDist = dist;
        if (dist > maxDist)
            maxDist = dist;
    }

    std::vector<cv::DMatch> goodMatches;
    for (int i = 0; i < descriptorsPrev.rows; i++)
    {
        if (matches[i].distance <= std::max(2 * minDist, 30.0))
        {
            goodMatches.push_back(matches[i]);
        }
    }

    // Extract location of good matches
    std::vector<cv::Point2f> pointsPrev;
    std::vector<cv::Point2f> pointsCurr;
    for (size_t i = 0; i < goodMatches.size(); i++)
    {
        pointsPrev.push_back(keypointsPrev[goodMatches[i].queryIdx].pt);
        pointsCurr.push_back(keypointsCurr[goodMatches[i].trainIdx].pt);
    }

    // Compute Essential matrix
    cv::Mat intrinsics = (cv::Mat_<double>(3, 3) << 387.3502807617188, 0, 317.7719116210938,
                          0, 387.3502807617188, 242.4875946044922,
                          0, 0, 1);
    cv::Mat essentialMat = cv::findEssentialMat(pointsPrev, pointsCurr, intrinsics, cv::RANSAC, 0.999, 1.0);

    // Recover pose from Essential matrix
    cv::Mat R, t;
    auto inliers = cv::recoverPose(essentialMat, pointsPrev, pointsCurr, intrinsics, R, t);

    std::cout << "Rotation Matrix:\n"
              << R << std::endl;
    std::cout << "Translation Vector:\n"
              << t << std::endl;

    // Draw matches for visualization
    cv::Mat imgMatches;
    cv::drawMatches(prevFrame, keypointsPrev, currFrame, keypointsCurr, goodMatches, imgMatches);

    return imgMatches;
}
