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