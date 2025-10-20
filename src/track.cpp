#include "../include/track.hpp"
#include "../include/detection.hpp"

cv::Mat connectCones(const cv::Mat &image, std::vector<Cone> &cones, cv::Scalar lineColor, int maxDistance)
{
    cv::Mat output;
    image.copyTo(output);

    // Start from the bottom cone closest to the middle of the image
    // Copy the cones so we can modify the list; this whole thing can probably be optimized if we have memory/performance issues
    auto remainingCones = cones;
    std::sort(remainingCones.begin(), remainingCones.end(), [image](const Cone &a, const Cone &b)
              { return (a.center.y > b.center.y) ||
                       (a.center.y == b.center.y && std::abs(a.center.x - image.cols / 2) < std::abs(b.center.x - image.cols / 2)); });

    auto firstCone = remainingCones.front();

    cv::rectangle(output, firstCone.boundingBox, cv::Scalar(0, 255, 0), 2);
    cv::circle(output, firstCone.center, 3, lineColor, -1);

    cv::Point previousPoint = firstCone.center;

    std::vector<Cone> trackEdgeCones;

    // Will obviously need tuning
    float VERTICAL_PENALTY_FACTOR = 3.5f;

    while (!remainingCones.empty())
    {
        // Find the next closest cone
        auto it = std::min_element(remainingCones.begin(), remainingCones.end(), [previousPoint, VERTICAL_PENALTY_FACTOR](const Cone &a, const Cone &b)
                                   {
                                    // Use a combination of Euclidean distance and vertical distance
                                    // Penalizing vertical distance helps with eliminating wrong detections
                                    // This helps avoid zigzag when there's a curve on the track
                                    // Main issue with this is if we ever have a view where subsequent cones are very different in vertical distance somehow
                                       double distA = cv::norm(a.center - previousPoint) + std::abs(a.center.y - previousPoint.y) * VERTICAL_PENALTY_FACTOR;
                                       double distB = cv::norm(b.center - previousPoint) + std::abs(b.center.y - previousPoint.y) * VERTICAL_PENALTY_FACTOR;
                                       return distA < distB; });

        // If it's too far, stop
        double distance = cv::norm(it->center - previousPoint) + std::abs(it->center.y - previousPoint.y) * VERTICAL_PENALTY_FACTOR;
        if (distance > maxDistance)
            break;

        if (it == remainingCones.end())
            break;

        // Draw line to the next cone
        cv::line(output, previousPoint, it->center, lineColor, 2);
        cv::rectangle(output, it->boundingBox, cv::Scalar(0, 255, 0), 2);
        cv::circle(output, it->center, 3, lineColor, -1);

        // Add to the track cones
        trackEdgeCones.push_back(*it);

        previousPoint = it->center;
        remainingCones.erase(it);
    }

    // This also helps clean up the wrongly detected cones, as they don't fit the chain.
    cones = trackEdgeCones;

    return output;
}
