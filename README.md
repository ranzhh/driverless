# Driverless E-Agle TRT
This project aims to complete the tasks assigned for the E-Agle TRT recruitment challenge.

Some brief explanations of the choices made:

#### Why camera instead of LIDAR? We're moving to LIDAR.
Because I haven't used OpenCV in a while and since I'm going to need to pick it up again for other stuff I felt like brushing up on the basics of image processing.

#### Why take this approach to detect the cones?
Normally I'd just train a YOLOvX to detect the cones; this was more of a challenge to me since it requires more explainability and I feel that would be good for the future, rather than "oh it auto extracted some inscrutable features". Additionally, there will probably be processing constraints for the car itself.

#### Your code has a lot of magic numbers floating around, why?
In a production scenario those numbers would be inferred from the environment; even just cloud cover vs clear sky could break this approach, or a piece flying off the car since I'm masking it manually, you name it. This is meant to be a quick demo / example.

#### Your C++ sucks dude, when did you learn it?
Some 15 years ago and I haven't written it since, I'm more of a Python guy nowadays. I actually enjoyed getting back into this though.

#### Did you employ any external assistance for this?
Of course, mostly perplexity to brush up on basics, Claude for some library mangling (let's say OpenCV installed via Brew wasn't where it should've been), and a repo of somebody else for the colour spaces because I didn't have the time for grid search + clicking through 300 images to find the colours that masked the best.

## Tasks
### Task 1: opening the image
Self explanatory.

### Task 2: finding the cones
I opted for colour masking instead of a DL based approach because, as I mentioned earlier, I'm less familiar with thisw way and as such it was a more fun challenge. I'm basically looking for the colour of the cones in the image, masking out both the car and all greyish hues. After that, I'm doing some transformations to make the mask better, but they're all empirically tested - not really scientifically derived.

### Task 3: dividing the cones based on colour
Automatically done in the second task.

### Task 4: Connect the edges
The main challenge here was to ignore the points that were wrongly detected. In a production environment, I'd focus on improving the detection itself to get rid of those outliers. As an example, you could:
- mask out the areas that don't belong to the floor, I'd avoid it since it doesn't scale well
- do edge detection and merge the masks
- look for the opposite stripe colour (black/white) and require the shape to be striped; I tried this approach but couldn't quite get it to work, but in principle it sounds good.

I opted for just ordering the point by distance, then penalising the vertical distance even more; this is a common trick when training models, summing multiple losses, and it seems to have worked pretty well eliminating the outliers. Obviously if there were a "fake" cone standing in the middle of the track it wouldn't work, as I'm not reprojecting the curve and attempting to check that it is a valid shape or anything.

### Task 5: Calculate rotation and translation from frame1 to frame2
Just using ORB as suggested into brute force matching, not much to say here. This is the part that could be improved the most, ideally by working on a better matching logic (will maybe have the time for it this afternoon)

## Parameter Configuration System

The pipeline now supports configurable parameters via JSON configuration files. This allows fine-tuning of detection, tracking, and odometry without recompiling the C++ code.

### Configuration File
Parameters are loaded from `config/default_params.json`. The configuration includes:

- **Color Detection**: Morphological operations (erosion, dilation, kernel size)
- **Cone Identification**: Area thresholds, merge distances for different cone types
- **Road Masking**: HSV color ranges for road detection
- **Track Drawing**: Distance thresholds and penalties
- **Odometry**: Camera intrinsics and RANSAC parameters

### Web API for Parameters

The server provides REST endpoints to manage parameters:

**GET /api/params** - Retrieve current configuration
```bash
curl http://localhost:8080/api/params
```

**POST /api/params** - Update configuration
```bash
curl -X POST http://localhost:8080/api/params \
  -H "Content-Type: application/json" \
  -d '{
    "color_detection": {"erosion_iterations": 2, "dilation_iterations": 3, "morph_kernel_size": 3},
    "cone_identification": {"min_area": 25, "max_area": 5000, "v_threshold": 25, "h_threshold": 12},
    "odometry": {"fx": 387.35, "fy": 387.35, "cx": 317.77, "cy": 242.49, "ransac_confidence": 0.999, "ransac_threshold": 1.0}
  }'
```

After updating parameters, simply re-run the pipeline to see the effects.

## Usage
If you're on Mac, you have various choices, you can build the project, `make serve`, you name it. If you're on any other system, I highly recommend just running `docker compose up -d --build` and saving yourself the hassle. It should work out of the box and serve you a page on localhost:8080 (this was completely vibecoded) allowing you to view the results.
