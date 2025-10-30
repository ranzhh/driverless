#pragma once

#include <string>
#include <opencv2/opencv.hpp>
#include "json.hpp"
#include <fstream>
#include <iostream>

using json = nlohmann::json;

// Parameter structures matching the JSON configuration

struct ColorDetectionParams
{
    int erosionIterations = 1;
    int dilationIterations = 2;
    int morphKernelSize = 2;
};

struct ConeColorParams
{
    int maxBoundingBoxArea = 4000;
    int verticalMergeThreshold = 20;
    int horizontalMergeThreshold = 10;
    int keepClosestN = -1; // -1 means no limit
};

struct ConeDetectionParams
{
    int minBoundingBoxArea = 20;
    int maxBoundingBoxArea = 4000;
    int verticalMergeThreshold = 20;
    int horizontalMergeThreshold = 10;

    ConeColorParams orange;
    ConeColorParams blue;
    ConeColorParams yellow;
};

struct RoadMaskParams
{
    cv::Scalar hsvLower = cv::Scalar(0, 0, 0);
    cv::Scalar hsvUpper = cv::Scalar(179, 70, 190);
};

struct TrackDrawingParams
{
    int maxConeDistance = 150;
    float verticalPenaltyFactor = 3.5f;
};

struct CameraIntrinsics
{
    double fx = 387.3502807617188;
    double fy = 387.3502807617188;
    double cx = 317.7719116210938;
    double cy = 242.4875946044922;

    cv::Mat toMat() const
    {
        return (cv::Mat_<double>(3, 3) << fx, 0, cx, 0, fy, cy, 0, 0, 1);
    }
};

struct OdometryParams
{
    CameraIntrinsics cameraIntrinsics;
    double ransacConfidence = 0.999;
    double ransacThreshold = 1.0;
    double matchDistanceMultiplier = 2.0;
    double matchDistanceMinimum = 30.0;
};

// Main configuration structure
struct PipelineParams
{
    std::string version = "1.0";
    std::string description;

    ColorDetectionParams colorDetection;
    ConeDetectionParams coneDetection;
    RoadMaskParams roadMask;
    TrackDrawingParams trackDrawing;
    OdometryParams odometry;

    // Load from JSON file
    static PipelineParams loadFromFile(const std::string &filepath)
    {
        PipelineParams params;

        try
        {
            std::ifstream file(filepath);
            if (!file.is_open())
            {
                std::cerr << "Warning: Could not open config file: " << filepath << std::endl;
                std::cerr << "Using default parameters" << std::endl;
                return params;
            }

            json j;
            file >> j;

            // Parse color detection
            if (j.contains("colorDetection"))
            {
                auto &cd = j["colorDetection"];
                if (cd.contains("erosionIterations"))
                    params.colorDetection.erosionIterations = cd["erosionIterations"];
                if (cd.contains("dilationIterations"))
                    params.colorDetection.dilationIterations = cd["dilationIterations"];
                if (cd.contains("morphKernelSize"))
                    params.colorDetection.morphKernelSize = cd["morphKernelSize"];
            }

            // Parse cone detection
            if (j.contains("coneDetection"))
            {
                auto &cone = j["coneDetection"];
                if (cone.contains("minBoundingBoxArea"))
                    params.coneDetection.minBoundingBoxArea = cone["minBoundingBoxArea"];
                if (cone.contains("maxBoundingBoxArea"))
                    params.coneDetection.maxBoundingBoxArea = cone["maxBoundingBoxArea"];
                if (cone.contains("verticalMergeThreshold"))
                    params.coneDetection.verticalMergeThreshold = cone["verticalMergeThreshold"];
                if (cone.contains("horizontalMergeThreshold"))
                    params.coneDetection.horizontalMergeThreshold = cone["horizontalMergeThreshold"];

                // Orange cones
                if (cone.contains("orange"))
                {
                    auto &orange = cone["orange"];
                    if (orange.contains("maxBoundingBoxArea"))
                        params.coneDetection.orange.maxBoundingBoxArea = orange["maxBoundingBoxArea"];
                    if (orange.contains("verticalMergeThreshold"))
                        params.coneDetection.orange.verticalMergeThreshold = orange["verticalMergeThreshold"];
                    if (orange.contains("horizontalMergeThreshold"))
                        params.coneDetection.orange.horizontalMergeThreshold = orange["horizontalMergeThreshold"];
                    if (orange.contains("keepClosestN"))
                        params.coneDetection.orange.keepClosestN = orange["keepClosestN"];
                }

                // Blue cones
                if (cone.contains("blue"))
                {
                    auto &blue = cone["blue"];
                    if (blue.contains("verticalMergeThreshold"))
                        params.coneDetection.blue.verticalMergeThreshold = blue["verticalMergeThreshold"];
                }

                // Yellow cones
                if (cone.contains("yellow"))
                {
                    auto &yellow = cone["yellow"];
                    if (yellow.contains("verticalMergeThreshold"))
                        params.coneDetection.yellow.verticalMergeThreshold = yellow["verticalMergeThreshold"];
                }
            }

            // Parse road mask
            if (j.contains("roadMask"))
            {
                auto &road = j["roadMask"];
                if (road.contains("hsvLower") && road["hsvLower"].is_array() && road["hsvLower"].size() == 3)
                {
                    params.roadMask.hsvLower = cv::Scalar(
                        road["hsvLower"][0].get<int>(),
                        road["hsvLower"][1].get<int>(),
                        road["hsvLower"][2].get<int>());
                }
                if (road.contains("hsvUpper") && road["hsvUpper"].is_array() && road["hsvUpper"].size() == 3)
                {
                    params.roadMask.hsvUpper = cv::Scalar(
                        road["hsvUpper"][0].get<int>(),
                        road["hsvUpper"][1].get<int>(),
                        road["hsvUpper"][2].get<int>());
                }
            }

            // Parse track drawing
            if (j.contains("trackDrawing"))
            {
                auto &track = j["trackDrawing"];
                if (track.contains("maxConeDistance"))
                    params.trackDrawing.maxConeDistance = track["maxConeDistance"];
                if (track.contains("verticalPenaltyFactor"))
                    params.trackDrawing.verticalPenaltyFactor = track["verticalPenaltyFactor"];
            }

            // Parse odometry
            if (j.contains("odometry"))
            {
                auto &odom = j["odometry"];

                if (odom.contains("cameraIntrinsics"))
                {
                    auto &intr = odom["cameraIntrinsics"];
                    if (intr.contains("fx"))
                        params.odometry.cameraIntrinsics.fx = intr["fx"];
                    if (intr.contains("fy"))
                        params.odometry.cameraIntrinsics.fy = intr["fy"];
                    if (intr.contains("cx"))
                        params.odometry.cameraIntrinsics.cx = intr["cx"];
                    if (intr.contains("cy"))
                        params.odometry.cameraIntrinsics.cy = intr["cy"];
                }

                if (odom.contains("ransacConfidence"))
                    params.odometry.ransacConfidence = odom["ransacConfidence"];
                if (odom.contains("ransacThreshold"))
                    params.odometry.ransacThreshold = odom["ransacThreshold"];
                if (odom.contains("matchDistanceMultiplier"))
                    params.odometry.matchDistanceMultiplier = odom["matchDistanceMultiplier"];
                if (odom.contains("matchDistanceMinimum"))
                    params.odometry.matchDistanceMinimum = odom["matchDistanceMinimum"];
            }

            std::cout << "Loaded parameters from: " << filepath << std::endl;
        }
        catch (const std::exception &e)
        {
            std::cerr << "Error parsing config file: " << e.what() << std::endl;
            std::cerr << "Using default parameters" << std::endl;
        }

        return params;
    }

    // Save to JSON file
    void saveToFile(const std::string &filepath) const
    {
        json j;

        j["version"] = version;
        j["description"] = description;

        // Color detection
        j["colorDetection"]["erosionIterations"] = colorDetection.erosionIterations;
        j["colorDetection"]["dilationIterations"] = colorDetection.dilationIterations;
        j["colorDetection"]["morphKernelSize"] = colorDetection.morphKernelSize;

        // Cone detection
        j["coneDetection"]["minBoundingBoxArea"] = coneDetection.minBoundingBoxArea;
        j["coneDetection"]["maxBoundingBoxArea"] = coneDetection.maxBoundingBoxArea;
        j["coneDetection"]["verticalMergeThreshold"] = coneDetection.verticalMergeThreshold;
        j["coneDetection"]["horizontalMergeThreshold"] = coneDetection.horizontalMergeThreshold;

        j["coneDetection"]["orange"]["maxBoundingBoxArea"] = coneDetection.orange.maxBoundingBoxArea;
        j["coneDetection"]["orange"]["verticalMergeThreshold"] = coneDetection.orange.verticalMergeThreshold;
        j["coneDetection"]["orange"]["horizontalMergeThreshold"] = coneDetection.orange.horizontalMergeThreshold;
        j["coneDetection"]["orange"]["keepClosestN"] = coneDetection.orange.keepClosestN;

        j["coneDetection"]["blue"]["verticalMergeThreshold"] = coneDetection.blue.verticalMergeThreshold;
        j["coneDetection"]["yellow"]["verticalMergeThreshold"] = coneDetection.yellow.verticalMergeThreshold;

        // Road mask
        j["roadMask"]["hsvLower"] = {
            (int)roadMask.hsvLower[0],
            (int)roadMask.hsvLower[1],
            (int)roadMask.hsvLower[2]};
        j["roadMask"]["hsvUpper"] = {
            (int)roadMask.hsvUpper[0],
            (int)roadMask.hsvUpper[1],
            (int)roadMask.hsvUpper[2]};

        // Track drawing
        j["trackDrawing"]["maxConeDistance"] = trackDrawing.maxConeDistance;
        j["trackDrawing"]["verticalPenaltyFactor"] = trackDrawing.verticalPenaltyFactor;

        // Odometry
        j["odometry"]["cameraIntrinsics"]["fx"] = odometry.cameraIntrinsics.fx;
        j["odometry"]["cameraIntrinsics"]["fy"] = odometry.cameraIntrinsics.fy;
        j["odometry"]["cameraIntrinsics"]["cx"] = odometry.cameraIntrinsics.cx;
        j["odometry"]["cameraIntrinsics"]["cy"] = odometry.cameraIntrinsics.cy;

        j["odometry"]["ransacConfidence"] = odometry.ransacConfidence;
        j["odometry"]["ransacThreshold"] = odometry.ransacThreshold;
        j["odometry"]["matchDistanceMultiplier"] = odometry.matchDistanceMultiplier;
        j["odometry"]["matchDistanceMinimum"] = odometry.matchDistanceMinimum;

        std::ofstream file(filepath);
        file << j.dump(4); // Pretty print with 4 spaces
        file.close();

        std::cout << "Saved parameters to: " << filepath << std::endl;
    }
};
