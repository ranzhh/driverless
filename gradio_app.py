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
CONFIG_FILE = Path("config/default_params.json")

# Default parameters
DEFAULT_PARAMS = {
    "version": "1.0",
    "description": "Driverless pipeline parameters - default configuration",
    "colorDetection": {"erosionIterations": 1, "dilationIterations": 2, "morphKernelSize": 2},
    "coneDetection": {
        "minBoundingBoxArea": 20,
        "maxBoundingBoxArea": 4000,
        "verticalMergeThreshold": 20,
        "horizontalMergeThreshold": 10,
        "orange": {
            "maxBoundingBoxArea": 4000,
            "verticalMergeThreshold": 100,
            "horizontalMergeThreshold": 10,
            "keepClosestN": 2,
        },
        "blue": {"verticalMergeThreshold": 20},
        "yellow": {"verticalMergeThreshold": 20},
    },
    "roadMask": {"hsvLower": [0, 0, 0], "hsvUpper": [179, 70, 190]},
    "trackDrawing": {"maxConeDistance": 150, "verticalPenaltyFactor": 3.5},
    "odometry": {
        "cameraIntrinsics": {
            "fx": 387.3502807617188,
            "fy": 387.3502807617188,
            "cx": 317.7719116210938,
            "cy": 242.4875946044922,
        },
        "ransacConfidence": 0.999,
        "ransacThreshold": 1.0,
        "matchDistanceMultiplier": 2.0,
        "matchDistanceMinimum": 30.0,
    },
}


def load_params():
    """Load parameters from JSON config file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_params(params_dict):
    """Save parameters to JSON config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(params_dict, f, indent=2)
    return "✅ Parameters saved successfully!"


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


def restore_defaults():
    """Restore default parameters."""
    save_params(DEFAULT_PARAMS)
    # Return all default values for the UI
    return [
        # Color detection
        DEFAULT_PARAMS["colorDetection"]["erosionIterations"],
        DEFAULT_PARAMS["colorDetection"]["dilationIterations"],
        DEFAULT_PARAMS["colorDetection"]["morphKernelSize"],
        # Cone identification
        DEFAULT_PARAMS["coneDetection"]["minBoundingBoxArea"],
        DEFAULT_PARAMS["coneDetection"]["maxBoundingBoxArea"],
        DEFAULT_PARAMS["coneDetection"]["verticalMergeThreshold"],
        DEFAULT_PARAMS["coneDetection"]["horizontalMergeThreshold"],
        # Orange cone specific
        DEFAULT_PARAMS["coneDetection"]["orange"]["maxBoundingBoxArea"],
        DEFAULT_PARAMS["coneDetection"]["orange"]["verticalMergeThreshold"],
        DEFAULT_PARAMS["coneDetection"]["orange"]["horizontalMergeThreshold"],
        DEFAULT_PARAMS["coneDetection"]["orange"]["keepClosestN"],
        # Blue cone specific
        DEFAULT_PARAMS["coneDetection"]["blue"]["verticalMergeThreshold"],
        # Yellow cone specific
        DEFAULT_PARAMS["coneDetection"]["yellow"]["verticalMergeThreshold"],
        # Road mask
        DEFAULT_PARAMS["roadMask"]["hsvLower"][0],
        DEFAULT_PARAMS["roadMask"]["hsvLower"][1],
        DEFAULT_PARAMS["roadMask"]["hsvLower"][2],
        DEFAULT_PARAMS["roadMask"]["hsvUpper"][0],
        DEFAULT_PARAMS["roadMask"]["hsvUpper"][1],
        DEFAULT_PARAMS["roadMask"]["hsvUpper"][2],
        # Track drawing
        DEFAULT_PARAMS["trackDrawing"]["maxConeDistance"],
        DEFAULT_PARAMS["trackDrawing"]["verticalPenaltyFactor"],
        # Odometry
        DEFAULT_PARAMS["odometry"]["cameraIntrinsics"]["fx"],
        DEFAULT_PARAMS["odometry"]["cameraIntrinsics"]["fy"],
        DEFAULT_PARAMS["odometry"]["cameraIntrinsics"]["cx"],
        DEFAULT_PARAMS["odometry"]["cameraIntrinsics"]["cy"],
        DEFAULT_PARAMS["odometry"]["ransacConfidence"],
        DEFAULT_PARAMS["odometry"]["ransacThreshold"],
        DEFAULT_PARAMS["odometry"]["matchDistanceMultiplier"],
        DEFAULT_PARAMS["odometry"]["matchDistanceMinimum"],
        "✅ Parameters restored to defaults!",
    ]


def update_params(
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
    """Update parameters from Gradio inputs."""
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

    return save_params(params)


# Build the Gradio interface
with gr.Blocks(title="Driverless Pipeline Controller", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🏎️ Driverless Vision Pipeline")
    gr.Markdown(
        "Interactive parameter tuning and visualization for cone detection, tracking, and odometry"
    )

    with gr.Tabs():
        # Pipeline execution tab
        with gr.Tab("🚀 Run Pipeline"):
            gr.Markdown("### Execute Pipeline Steps")

            with gr.Row():
                step_choice = gr.Radio(
                    choices=["all", "1", "2", "3"],
                    value="all",
                    label="Select Step",
                    info="1: Detect Cones | 2: Draw Tracks | 3: Calculate Odometry",
                )
                run_btn = gr.Button("▶️ Run Pipeline", variant="primary", size="lg")

            output_text = gr.Textbox(label="Pipeline Output", lines=6, max_lines=10)

            gr.Markdown("### Results")
            with gr.Row():
                cones_image = gr.Image(
                    label="🔵 Cone Detection + Track Lines", type="pil", height=400
                )
                odometry_image = gr.Image(label="🎯 Odometry Matches", type="pil", height=400)

            with gr.Row():
                json_download = gr.File(
                    label="📥 Download Detected Cones (JSON)", interactive=False
                )

            run_btn.click(
                fn=run_pipeline,
                inputs=[step_choice],
                outputs=[output_text, cones_image, odometry_image, json_download],
            )

        # Parameter configuration tab
        with gr.Tab("⚙️ Configure Parameters"):
            params = load_params()

            gr.Markdown("### Color Detection Parameters")
            with gr.Row():
                erosion_iter = gr.Slider(
                    0,
                    5,
                    value=params.get("colorDetection", {}).get("erosionIterations", 1),
                    step=1,
                    label="Erosion Iterations",
                )
                dilation_iter = gr.Slider(
                    0,
                    5,
                    value=params.get("colorDetection", {}).get("dilationIterations", 2),
                    step=1,
                    label="Dilation Iterations",
                )
                morph_kernel = gr.Slider(
                    1,
                    7,
                    value=params.get("colorDetection", {}).get("morphKernelSize", 2),
                    step=1,
                    label="Morphological Kernel Size",
                )

            gr.Markdown("### Cone Identification Parameters")
            with gr.Row():
                min_area = gr.Slider(
                    0,
                    100,
                    value=params.get("coneDetection", {}).get("minBoundingBoxArea", 20),
                    step=1,
                    label="Min Bounding Box Area",
                )
                max_area = gr.Slider(
                    100,
                    10000,
                    value=params.get("coneDetection", {}).get("maxBoundingBoxArea", 4000),
                    step=100,
                    label="Max Bounding Box Area",
                )
            with gr.Row():
                v_threshold = gr.Slider(
                    0,
                    100,
                    value=params.get("coneDetection", {}).get("verticalMergeThreshold", 20),
                    step=1,
                    label="Vertical Merge Threshold",
                )
                h_threshold = gr.Slider(
                    0,
                    50,
                    value=params.get("coneDetection", {}).get("horizontalMergeThreshold", 10),
                    step=1,
                    label="Horizontal Merge Threshold",
                )

            gr.Markdown("#### Orange Cone Specific")
            with gr.Row():
                orange_max_area = gr.Slider(
                    100,
                    10000,
                    value=params.get("coneDetection", {})
                    .get("orange", {})
                    .get("maxBoundingBoxArea", 4000),
                    step=100,
                    label="Max Area",
                )
                orange_v_threshold = gr.Slider(
                    0,
                    200,
                    value=params.get("coneDetection", {})
                    .get("orange", {})
                    .get("verticalMergeThreshold", 100),
                    step=5,
                    label="Vertical Threshold",
                )
                orange_h_threshold = gr.Slider(
                    0,
                    50,
                    value=params.get("coneDetection", {})
                    .get("orange", {})
                    .get("horizontalMergeThreshold", 10),
                    step=1,
                    label="Horizontal Threshold",
                )
                orange_keep_n = gr.Slider(
                    1,
                    10,
                    value=params.get("coneDetection", {}).get("orange", {}).get("keepClosestN", 2),
                    step=1,
                    label="Keep Closest N",
                )

            gr.Markdown("#### Blue/Yellow Cone Specific")
            with gr.Row():
                blue_v_threshold = gr.Slider(
                    0,
                    100,
                    value=params.get("coneDetection", {})
                    .get("blue", {})
                    .get("verticalMergeThreshold", 20),
                    step=1,
                    label="Blue Vertical Threshold",
                )
                yellow_v_threshold = gr.Slider(
                    0,
                    100,
                    value=params.get("coneDetection", {})
                    .get("yellow", {})
                    .get("verticalMergeThreshold", 20),
                    step=1,
                    label="Yellow Vertical Threshold",
                )

            gr.Markdown("### Road Mask (HSV Range)")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Lower Bounds**")
                    road_h_lower = gr.Slider(
                        0,
                        179,
                        value=params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[0],
                        step=1,
                        label="H Lower",
                    )
                    road_s_lower = gr.Slider(
                        0,
                        255,
                        value=params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[1],
                        step=1,
                        label="S Lower",
                    )
                    road_v_lower = gr.Slider(
                        0,
                        255,
                        value=params.get("roadMask", {}).get("hsvLower", [0, 0, 0])[2],
                        step=1,
                        label="V Lower",
                    )
                with gr.Column():
                    gr.Markdown("**Upper Bounds**")
                    road_h_upper = gr.Slider(
                        0,
                        179,
                        value=params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[0],
                        step=1,
                        label="H Upper",
                    )
                    road_s_upper = gr.Slider(
                        0,
                        255,
                        value=params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[1],
                        step=1,
                        label="S Upper",
                    )
                    road_v_upper = gr.Slider(
                        0,
                        255,
                        value=params.get("roadMask", {}).get("hsvUpper", [179, 70, 190])[2],
                        step=1,
                        label="V Upper",
                    )

            gr.Markdown("### Track Drawing Parameters")
            with gr.Row():
                max_cone_dist = gr.Slider(
                    50,
                    500,
                    value=params.get("trackDrawing", {}).get("maxConeDistance", 150),
                    step=10,
                    label="Max Cone Distance",
                )
                vertical_penalty = gr.Slider(
                    1.0,
                    10.0,
                    value=params.get("trackDrawing", {}).get("verticalPenaltyFactor", 3.5),
                    step=0.1,
                    label="Vertical Penalty Factor",
                )

            gr.Markdown("### Odometry Parameters")
            gr.Markdown("#### Camera Intrinsics")
            with gr.Row():
                fx = gr.Number(
                    value=params.get("odometry", {}).get("cameraIntrinsics", {}).get("fx", 387.35),
                    label="Focal Length X (fx)",
                )
                fy = gr.Number(
                    value=params.get("odometry", {}).get("cameraIntrinsics", {}).get("fy", 387.35),
                    label="Focal Length Y (fy)",
                )
                cx = gr.Number(
                    value=params.get("odometry", {}).get("cameraIntrinsics", {}).get("cx", 317.77),
                    label="Principal Point X (cx)",
                )
                cy = gr.Number(
                    value=params.get("odometry", {}).get("cameraIntrinsics", {}).get("cy", 242.49),
                    label="Principal Point Y (cy)",
                )

            gr.Markdown("#### RANSAC Parameters")
            with gr.Row():
                ransac_conf = gr.Slider(
                    0.9,
                    0.9999,
                    value=params.get("odometry", {}).get("ransacConfidence", 0.999),
                    step=0.0001,
                    label="RANSAC Confidence",
                )
                ransac_thresh = gr.Slider(
                    0.1,
                    5.0,
                    value=params.get("odometry", {}).get("ransacThreshold", 1.0),
                    step=0.1,
                    label="RANSAC Threshold",
                )

            gr.Markdown("#### Feature Matching")
            with gr.Row():
                match_dist_mult = gr.Slider(
                    1.0,
                    5.0,
                    value=params.get("odometry", {}).get("matchDistanceMultiplier", 2.0),
                    step=0.1,
                    label="Match Distance Multiplier",
                )
                match_dist_min = gr.Slider(
                    10.0,
                    100.0,
                    value=params.get("odometry", {}).get("matchDistanceMinimum", 30.0),
                    step=1.0,
                    label="Match Distance Minimum",
                )

            gr.Markdown("---")
            with gr.Row():
                save_btn = gr.Button("💾 Save Parameters", variant="primary", size="lg")
                restore_btn = gr.Button("🔄 Restore Defaults", variant="secondary", size="lg")
            save_status = gr.Textbox(label="Status")

            # Save button handler
            save_btn.click(
                fn=update_params,
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
                outputs=[save_status],
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
                    save_status,
                ],
            )

        # Documentation tab
        with gr.Tab("📖 Documentation"):
            gr.Markdown("""
            ## Driverless Vision Pipeline
            
            This interface provides interactive control over a modular computer vision pipeline for autonomous vehicles.
            
            ### Pipeline Steps
            
            1. **Detect Cones**: Identifies orange, blue, and yellow cones using color masking
            2. **Draw Tracks**: Connects detected cones to visualize the track boundaries
            3. **Calculate Odometry**: Computes rotation and translation between consecutive frames
            
            ### Using the Interface
            
            1. **Run Pipeline Tab**: Execute individual steps or the complete pipeline
            2. **Configure Parameters Tab**: Adjust detection, tracking, and odometry parameters
            3. Save parameters and re-run the pipeline to see the effects
            
            ### Parameter Guide
            
            - **Color Detection**: Controls morphological operations for noise reduction
            - **Cone Identification**: Defines area thresholds and merging behavior
            - **Road Mask**: HSV color range to filter road pixels
            - **Track Drawing**: Controls how cones are connected
            - **Odometry**: Camera calibration and feature matching parameters
            
            ### Tips
            
            - Start with small parameter changes and observe the results
            - Use Step 1 alone to tune cone detection
            - Orange cones have special handling (typically fewer, used as markers)
            - Camera intrinsics should match your camera's calibration
            """)

if __name__ == "__main__":
    import os

    # Get server configuration from environment or use defaults
    server_name = os.environ.get("GRADIO_SERVER_NAME", "127.0.0.1")
    server_port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))

    print("🚀 Starting Driverless Pipeline Gradio Interface...")
    print(f"📊 Open your browser to http://{server_name}:{server_port}")

    app.launch(server_name=server_name, server_port=server_port, share=False)
