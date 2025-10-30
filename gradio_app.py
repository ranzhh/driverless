#!/usr/bin/env python3
"""
Gradio interface for the driverless vision pipeline.
Provides interactive parameter tuning and visualization.
"""

import json
import subprocess
from pathlib import Path

import gradio as gr
from PIL import Image

# Configuration
OUTPUT_DIR = Path("output")
DEFAULT_PARAMS_FILE = Path("config/default_params.json")
CURRENT_PARAMS_FILE = Path("config/current_params.json")


def load_default_params():
    """Load default parameters from JSON config file."""
    if DEFAULT_PARAMS_FILE.exists():
        with open(DEFAULT_PARAMS_FILE, "r") as f:
            return json.load(f)
    return {}


def load_current_params():
    """Load current parameters from JSON config file."""
    if CURRENT_PARAMS_FILE.exists():
        with open(CURRENT_PARAMS_FILE, "r") as f:
            return json.load(f)
    # If no current params exist, use defaults
    return load_default_params()


def save_current_params(params_dict):
    """Save current parameters to JSON config file."""
    with open(CURRENT_PARAMS_FILE, "w") as f:
        json.dump(params_dict, f, indent=2)
    return "✅ Parameters saved successfully!"


def save_as_config(params_dict):
    """Save parameters to the config file used by the C++ pipeline."""
    with open(DEFAULT_PARAMS_FILE, "w") as f:
        json.dump(params_dict, f, indent=2)


def run_pipeline(step="all"):
    """Run the C++ pipeline with specified step."""
    try:
        cmd = ["./build/driverless"]
        if step != "all":
            cmd.append(step)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Load output images
            cones_img = None
            odometry_img = None
            json_file = None

            if (OUTPUT_DIR / "detected_cones.png").exists():
                cones_img = Image.open(OUTPUT_DIR / "detected_cones.png")

            if (OUTPUT_DIR / "odometry_matches.png").exists():
                odometry_img = Image.open(OUTPUT_DIR / "odometry_matches.png")

            if (OUTPUT_DIR / "detected_cones.json").exists():
                json_file = str(OUTPUT_DIR / "detected_cones.json")

            return (
                f"✅ Pipeline step '{step}' completed successfully!\n\n{result.stdout}",
                cones_img,
                odometry_img,
                json_file,
            )
        else:
            return (
                f"❌ Pipeline failed with code {result.returncode}\n\n{result.stderr}",
                None,
                None,
                None,
            )
    except subprocess.TimeoutExpired:
        return "❌ Pipeline execution timeout (30s)", None, None, None
    except Exception as e:
        return f"❌ Error: {str(e)}", None, None, None


def compare_with_defaults(current_value, default_value):
    """Compare current value with default to determine if it's modified."""
    return current_value != default_value


def get_slider_elem_classes(current_value, default_value):
    """Return CSS classes for slider based on whether value differs from default."""
    if compare_with_defaults(current_value, default_value):
        return "modified-param"
    return ""


def restore_defaults():
    """Restore default parameters."""
    defaults = load_default_params()
    save_current_params(defaults)

    # Return all default values for the UI
    return [
        # Color detection
        defaults["colorDetection"]["erosionIterations"],
        defaults["colorDetection"]["dilationIterations"],
        defaults["colorDetection"]["morphKernelSize"],
        # Cone identification
        defaults["coneDetection"]["minBoundingBoxArea"],
        defaults["coneDetection"]["maxBoundingBoxArea"],
        defaults["coneDetection"]["verticalMergeThreshold"],
        defaults["coneDetection"]["horizontalMergeThreshold"],
        # Orange cone specific
        defaults["coneDetection"]["orange"]["maxBoundingBoxArea"],
        defaults["coneDetection"]["orange"]["verticalMergeThreshold"],
        defaults["coneDetection"]["orange"]["horizontalMergeThreshold"],
        defaults["coneDetection"]["orange"]["keepClosestN"],
        # Blue cone specific
        defaults["coneDetection"]["blue"]["verticalMergeThreshold"],
        # Yellow cone specific
        defaults["coneDetection"]["yellow"]["verticalMergeThreshold"],
        # Road mask
        defaults["roadMask"]["hsvLower"][0],
        defaults["roadMask"]["hsvLower"][1],
        defaults["roadMask"]["hsvLower"][2],
        defaults["roadMask"]["hsvUpper"][0],
        defaults["roadMask"]["hsvUpper"][1],
        defaults["roadMask"]["hsvUpper"][2],
        # Track drawing
        defaults["trackDrawing"]["maxConeDistance"],
        defaults["trackDrawing"]["verticalPenaltyFactor"],
        # Odometry
        defaults["odometry"]["cameraIntrinsics"]["fx"],
        defaults["odometry"]["cameraIntrinsics"]["fy"],
        defaults["odometry"]["cameraIntrinsics"]["cx"],
        defaults["odometry"]["cameraIntrinsics"]["cy"],
        defaults["odometry"]["ransacConfidence"],
        defaults["odometry"]["ransacThreshold"],
        defaults["odometry"]["matchDistanceMultiplier"],
        defaults["odometry"]["matchDistanceMinimum"],
        "✅ Parameters restored to defaults!",
    ]


def save_and_run_pipeline(
    # Color detection
    erosion_iter,
    dilation_iter,
    morph_kernel,
    # Cone identification
    min_area,
    max_area,
    v_threshold,
    h_threshold,
    # Orange cone specific
    orange_max_area,
    orange_v_threshold,
    orange_h_threshold,
    orange_keep_n,
    # Blue cone specific
    blue_v_threshold,
    # Yellow cone specific
    yellow_v_threshold,
    # Road mask
    road_h_lower,
    road_s_lower,
    road_v_lower,
    road_h_upper,
    road_s_upper,
    road_v_upper,
    # Track drawing
    max_cone_dist,
    vertical_penalty,
    # Odometry
    fx,
    fy,
    cx,
    cy,
    ransac_conf,
    ransac_thresh,
    match_dist_mult,
    match_dist_min,
):
    """Save parameters and run the pipeline."""
    # Build parameters dict
    params = {
        "version": "1.0",
        "description": "Driverless pipeline parameters - updated via Gradio",
        "colorDetection": {
            "erosionIterations": int(erosion_iter),
            "dilationIterations": int(dilation_iter),
            "morphKernelSize": int(morph_kernel),
        },
        "coneDetection": {
            "minBoundingBoxArea": int(min_area),
            "maxBoundingBoxArea": int(max_area),
            "verticalMergeThreshold": int(v_threshold),
            "horizontalMergeThreshold": int(h_threshold),
            "orange": {
                "maxBoundingBoxArea": int(orange_max_area),
                "verticalMergeThreshold": int(orange_v_threshold),
                "horizontalMergeThreshold": int(orange_h_threshold),
                "keepClosestN": int(orange_keep_n),
            },
            "blue": {"verticalMergeThreshold": int(blue_v_threshold)},
            "yellow": {"verticalMergeThreshold": int(yellow_v_threshold)},
        },
        "roadMask": {
            "hsvLower": [int(road_h_lower), int(road_s_lower), int(road_v_lower)],
            "hsvUpper": [int(road_h_upper), int(road_s_upper), int(road_v_upper)],
        },
        "trackDrawing": {
            "maxConeDistance": int(max_cone_dist),
            "verticalPenaltyFactor": float(vertical_penalty),
        },
        "odometry": {
            "cameraIntrinsics": {
                "fx": float(fx),
                "fy": float(fy),
                "cx": float(cx),
                "cy": float(cy),
            },
            "ransacConfidence": float(ransac_conf),
            "ransacThreshold": float(ransac_thresh),
            "matchDistanceMultiplier": float(match_dist_mult),
            "matchDistanceMinimum": float(match_dist_min),
        },
    }

    # Save to current params
    save_current_params(params)

    # Save to config file used by C++ pipeline
    save_as_config(params)

    # Run the pipeline
    output, cones_img, odometry_img, json_file = run_pipeline("all")

    # Return all outputs for display + show results page
    return (
        output,
        cones_img,
        odometry_img,
        json_file,
        gr.update(visible=False),  # Hide config page
        gr.update(visible=True),  # Show results page
    )


# Build the Gradio interface
with gr.Blocks(
    title="Driverless Pipeline Controller",
    theme=gr.themes.Soft(),
    css="""
    .modified-param label {
        color: #ff8800 !important;
        font-weight: bold !important;
    }
    .modified-param input[type="range"] {
        accent-color: #ff8800 !important;
    }
    .modified-param input[type="number"] {
        border-color: #ff8800 !important;
    }
""",
) as app:
    gr.Markdown("# 🏎️ Driverless Vision Pipeline")
    gr.Markdown(
        "Interactive parameter tuning and visualization for cone detection, tracking, and odometry"
    )

    # Landing page with start button
    with gr.Column(visible=True) as landing_page:
        gr.Markdown("### Ready to run the vision pipeline")
        gr.Markdown("Click below to configure parameters and execute the pipeline")
        start_btn = gr.Button("▶️ Start Pipeline", variant="primary", size="lg")

    # Parameter configuration page
    with gr.Column(visible=False) as config_page:
        gr.Markdown("### Configure Pipeline Parameters")
        gr.Markdown("*Parameters shown in orange are different from default values*")

        with gr.Row():
            run_pipeline_btn = gr.Button("▶️ Run", variant="primary", size="lg")
            restore_btn = gr.Button("🔄 Restore Defaults", variant="secondary", size="lg")

        status_msg = gr.Textbox(label="Status", lines=1, visible=False)

        gr.Markdown("---")
        gr.Markdown("### Parameters")

        # Load current and default params
        current_params = load_current_params()
        default_params = load_default_params()

        gr.Markdown("#### Color Detection")
        with gr.Row():
            erosion_iter = gr.Slider(
                0,
                5,
                value=current_params.get("colorDetection", {}).get("erosionIterations", 1),
                step=1,
                label="Erosion Iterations",
                elem_classes=get_slider_elem_classes(
                    current_params.get("colorDetection", {}).get("erosionIterations", 1),
                    default_params.get("colorDetection", {}).get("erosionIterations", 1),
                ),
            )
            dilation_iter = gr.Slider(
                0,
                5,
                value=current_params.get("colorDetection", {}).get("dilationIterations", 2),
                step=1,
                label="Dilation Iterations",
                elem_classes=get_slider_elem_classes(
                    current_params.get("colorDetection", {}).get("dilationIterations", 2),
                    default_params.get("colorDetection", {}).get("dilationIterations", 2),
                ),
            )
            morph_kernel = gr.Slider(
                1,
                7,
                value=current_params.get("colorDetection", {}).get("morphKernelSize", 2),
                step=1,
                label="Morphological Kernel Size",
                elem_classes=get_slider_elem_classes(
                    current_params.get("colorDetection", {}).get("morphKernelSize", 2),
                    default_params.get("colorDetection", {}).get("morphKernelSize", 2),
                ),
            )

        gr.Markdown("#### Cone Identification")
        with gr.Row():
            min_area = gr.Slider(
                0,
                100,
                value=current_params.get("coneDetection", {}).get("minBoundingBoxArea", 20),
                step=1,
                label="Min Bounding Box Area",
                elem_classes=get_slider_elem_classes(
                    current_params.get("coneDetection", {}).get("minBoundingBoxArea", 20),
                    default_params.get("coneDetection", {}).get("minBoundingBoxArea", 20),
                ),
            )
            max_area = gr.Slider(
                100,
                10000,
                value=current_params.get("coneDetection", {}).get("maxBoundingBoxArea", 4000),
                step=100,
                label="Max Bounding Box Area",
                elem_classes=get_slider_elem_classes(
                    current_params.get("coneDetection", {}).get("maxBoundingBoxArea", 4000),
                    default_params.get("coneDetection", {}).get("maxBoundingBoxArea", 4000),
                ),
            )
        with gr.Row():
            v_threshold = gr.Slider(
                0,
                100,
                value=current_params.get("coneDetection", {}).get("verticalMergeThreshold", 20),
                step=1,
                label="Vertical Merge Threshold",
                elem_classes=get_slider_elem_classes(
                    current_params.get("coneDetection", {}).get("verticalMergeThreshold", 20),
                    default_params.get("coneDetection", {}).get("verticalMergeThreshold", 20),
                ),
            )
            h_threshold = gr.Slider(
                0,
                50,
                value=current_params.get("coneDetection", {}).get("horizontalMergeThreshold", 10),
                step=1,
                label="Horizontal Merge Threshold",
                elem_classes=get_slider_elem_classes(
                    current_params.get("coneDetection", {}).get("horizontalMergeThreshold", 10),
                    default_params.get("coneDetection", {}).get("horizontalMergeThreshold", 10),
                ),
            )

        with gr.Accordion("Orange Cone Specific", open=False):
            with gr.Row():
                orange_max_area = gr.Slider(
                    100,
                    10000,
                    value=current_params.get("coneDetection", {})
                    .get("orange", {})
                    .get("maxBoundingBoxArea", 4000),
                    step=100,
                    label="Max Area",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("maxBoundingBoxArea", 4000),
                        default_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("maxBoundingBoxArea", 4000),
                    ),
                )
                orange_v_threshold = gr.Slider(
                    0,
                    200,
                    value=current_params.get("coneDetection", {})
                    .get("orange", {})
                    .get("verticalMergeThreshold", 100),
                    step=5,
                    label="Vertical Threshold",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("verticalMergeThreshold", 100),
                        default_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("verticalMergeThreshold", 100),
                    ),
                )
            with gr.Row():
                orange_h_threshold = gr.Slider(
                    0,
                    50,
                    value=current_params.get("coneDetection", {})
                    .get("orange", {})
                    .get("horizontalMergeThreshold", 10),
                    step=1,
                    label="Horizontal Threshold",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("horizontalMergeThreshold", 10),
                        default_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("horizontalMergeThreshold", 10),
                    ),
                )
                orange_keep_n = gr.Slider(
                    1,
                    10,
                    value=current_params.get("coneDetection", {})
                    .get("orange", {})
                    .get("keepClosestN", 2),
                    step=1,
                    label="Keep Closest N",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("keepClosestN", 2),
                        default_params.get("coneDetection", {})
                        .get("orange", {})
                        .get("keepClosestN", 2),
                    ),
                )

        with gr.Accordion("Blue/Yellow Cone Specific", open=False):
            with gr.Row():
                blue_v_threshold = gr.Slider(
                    0,
                    100,
                    value=current_params.get("coneDetection", {})
                    .get("blue", {})
                    .get("verticalMergeThreshold", 20),
                    step=1,
                    label="Blue Vertical Threshold",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("coneDetection", {})
                        .get("blue", {})
                        .get("verticalMergeThreshold", 20),
                        default_params.get("coneDetection", {})
                        .get("blue", {})
                        .get("verticalMergeThreshold", 20),
                    ),
                )
                yellow_v_threshold = gr.Slider(
                    0,
                    100,
                    value=current_params.get("coneDetection", {})
                    .get("yellow", {})
                    .get("verticalMergeThreshold", 20),
                    step=1,
                    label="Yellow Vertical Threshold",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("coneDetection", {})
                        .get("yellow", {})
                        .get("verticalMergeThreshold", 20),
                        default_params.get("coneDetection", {})
                        .get("yellow", {})
                        .get("verticalMergeThreshold", 20),
                    ),
                )

        with gr.Accordion("Road Mask (HSV Range)", open=False):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Lower Bounds**")
                    road_h_lower = gr.Slider(
                        0,
                        179,
                        value=current_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[0],
                        step=1,
                        label="H Lower",
                        elem_classes=get_slider_elem_classes(
                            current_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[0],
                            default_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[0],
                        ),
                    )
                    road_s_lower = gr.Slider(
                        0,
                        255,
                        value=current_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[1],
                        step=1,
                        label="S Lower",
                        elem_classes=get_slider_elem_classes(
                            current_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[1],
                            default_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[1],
                        ),
                    )
                    road_v_lower = gr.Slider(
                        0,
                        255,
                        value=current_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[2],
                        step=1,
                        label="V Lower",
                        elem_classes=get_slider_elem_classes(
                            current_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[2],
                            default_params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[2],
                        ),
                    )
                with gr.Column():
                    gr.Markdown("**Upper Bounds**")
                    road_h_upper = gr.Slider(
                        0,
                        179,
                        value=current_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[
                            0
                        ],
                        step=1,
                        label="H Upper",
                        elem_classes=get_slider_elem_classes(
                            current_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[0],
                            default_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[0],
                        ),
                    )
                    road_s_upper = gr.Slider(
                        0,
                        255,
                        value=current_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[
                            1
                        ],
                        step=1,
                        label="S Upper",
                        elem_classes=get_slider_elem_classes(
                            current_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[1],
                            default_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[1],
                        ),
                    )
                    road_v_upper = gr.Slider(
                        0,
                        255,
                        value=current_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[
                            2
                        ],
                        step=1,
                        label="V Upper",
                        elem_classes=get_slider_elem_classes(
                            current_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[2],
                            default_params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[2],
                        ),
                    )

        with gr.Accordion("Track Drawing Parameters", open=False):
            with gr.Row():
                max_cone_dist = gr.Slider(
                    50,
                    500,
                    value=current_params.get("trackDrawing", {}).get("maxConeDistance", 150),
                    step=10,
                    label="Max Cone Distance",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("trackDrawing", {}).get("maxConeDistance", 150),
                        default_params.get("trackDrawing", {}).get("maxConeDistance", 150),
                    ),
                )
                vertical_penalty = gr.Slider(
                    1.0,
                    10.0,
                    value=current_params.get("trackDrawing", {}).get("verticalPenaltyFactor", 3.5),
                    step=0.1,
                    label="Vertical Penalty Factor",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("trackDrawing", {}).get("verticalPenaltyFactor", 3.5),
                        default_params.get("trackDrawing", {}).get("verticalPenaltyFactor", 3.5),
                    ),
                )

        with gr.Accordion("Odometry Parameters", open=False):
            gr.Markdown("**Camera Intrinsics**")
            with gr.Row():
                fx = gr.Number(
                    value=current_params.get("odometry", {})
                    .get("cameraIntrinsics", {})
                    .get("fx", 387.35),
                    label="Focal Length X (fx)",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("fx", 387.35),
                        default_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("fx", 387.35),
                    ),
                )
                fy = gr.Number(
                    value=current_params.get("odometry", {})
                    .get("cameraIntrinsics", {})
                    .get("fy", 387.35),
                    label="Focal Length Y (fy)",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("fy", 387.35),
                        default_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("fy", 387.35),
                    ),
                )
            with gr.Row():
                cx = gr.Number(
                    value=current_params.get("odometry", {})
                    .get("cameraIntrinsics", {})
                    .get("cx", 317.77),
                    label="Principal Point X (cx)",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("cx", 317.77),
                        default_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("cx", 317.77),
                    ),
                )
                cy = gr.Number(
                    value=current_params.get("odometry", {})
                    .get("cameraIntrinsics", {})
                    .get("cy", 242.49),
                    label="Principal Point Y (cy)",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("cy", 242.49),
                        default_params.get("odometry", {})
                        .get("cameraIntrinsics", {})
                        .get("cy", 242.49),
                    ),
                )

            gr.Markdown("**RANSAC Parameters**")
            with gr.Row():
                ransac_conf = gr.Slider(
                    0.9,
                    0.9999,
                    value=current_params.get("odometry", {}).get("ransacConfidence", 0.999),
                    step=0.0001,
                    label="RANSAC Confidence",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {}).get("ransacConfidence", 0.999),
                        default_params.get("odometry", {}).get("ransacConfidence", 0.999),
                    ),
                )
                ransac_thresh = gr.Slider(
                    0.1,
                    5.0,
                    value=current_params.get("odometry", {}).get("ransacThreshold", 1.0),
                    step=0.1,
                    label="RANSAC Threshold",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {}).get("ransacThreshold", 1.0),
                        default_params.get("odometry", {}).get("ransacThreshold", 1.0),
                    ),
                )

            gr.Markdown("**Feature Matching**")
            with gr.Row():
                match_dist_mult = gr.Slider(
                    1.0,
                    5.0,
                    value=current_params.get("odometry", {}).get("matchDistanceMultiplier", 2.0),
                    step=0.1,
                    label="Match Distance Multiplier",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {}).get("matchDistanceMultiplier", 2.0),
                        default_params.get("odometry", {}).get("matchDistanceMultiplier", 2.0),
                    ),
                )
                match_dist_min = gr.Slider(
                    10.0,
                    100.0,
                    value=current_params.get("odometry", {}).get("matchDistanceMinimum", 30.0),
                    step=1.0,
                    label="Match Distance Minimum",
                    elem_classes=get_slider_elem_classes(
                        current_params.get("odometry", {}).get("matchDistanceMinimum", 30.0),
                        default_params.get("odometry", {}).get("matchDistanceMinimum", 30.0),
                    ),
                )

    # Results page
    with gr.Column(visible=False) as results_page:
        gr.Markdown("### Pipeline Results")

        pipeline_output = gr.Textbox(label="Pipeline Output", lines=6)
        with gr.Row():
            result_cones_img = gr.Image(
                label="🔵 Cone Detection + Track Lines", type="pil", height=350
            )
            result_odometry_img = gr.Image(label="🎯 Odometry Matches", type="pil", height=350)
        result_json = gr.File(label="📥 Download Detected Cones (JSON)", interactive=False)

        gr.Markdown("---")
        restart_btn = gr.Button("▶️ Start Pipeline", variant="primary", size="lg")

    # Navigation handlers
    def show_config_page():
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

    def show_landing_page():
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    start_btn.click(
        fn=show_config_page,
        outputs=[landing_page, config_page, results_page],
    )

    restart_btn.click(
        fn=show_config_page,
        outputs=[landing_page, config_page, results_page],
    )

    # Run pipeline button handler
    run_pipeline_btn.click(
        fn=save_and_run_pipeline,
        inputs=[
            erosion_iter,
            dilation_iter,
            morph_kernel,
            min_area,
            max_area,
            v_threshold,
            h_threshold,
            orange_max_area,
            orange_v_threshold,
            orange_h_threshold,
            orange_keep_n,
            blue_v_threshold,
            yellow_v_threshold,
            road_h_lower,
            road_s_lower,
            road_v_lower,
            road_h_upper,
            road_s_upper,
            road_v_upper,
            max_cone_dist,
            vertical_penalty,
            fx,
            fy,
            cx,
            cy,
            ransac_conf,
            ransac_thresh,
            match_dist_mult,
            match_dist_min,
        ],
        outputs=[
            pipeline_output,
            result_cones_img,
            result_odometry_img,
            result_json,
            config_page,
            results_page,
        ],
    )

    # Restore defaults button handler
    restore_btn.click(
        fn=restore_defaults,
        outputs=[
            erosion_iter,
            dilation_iter,
            morph_kernel,
            min_area,
            max_area,
            v_threshold,
            h_threshold,
            orange_max_area,
            orange_v_threshold,
            orange_h_threshold,
            orange_keep_n,
            blue_v_threshold,
            yellow_v_threshold,
            road_h_lower,
            road_s_lower,
            road_v_lower,
            road_h_upper,
            road_s_upper,
            road_v_upper,
            max_cone_dist,
            vertical_penalty,
            fx,
            fy,
            cx,
            cy,
            ransac_conf,
            ransac_thresh,
            match_dist_mult,
            match_dist_min,
            status_msg,
        ],
    )

if __name__ == "__main__":
    import os

    # Get server configuration from environment or use defaults
    server_name = os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1")
    server_port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))

    print("🚀 Starting Driverless Pipeline Gradio Interface...")
    print(f"📊 Open your browser to http://{server_name}:{server_port}")

    app.launch(server_name=server_name, server_port=server_port, share=False)
