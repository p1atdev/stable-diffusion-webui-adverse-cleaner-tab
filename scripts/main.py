import numpy as np
import cv2
from PIL import Image
from pathlib import Path
import os

from cv2.ximgproc import guidedFilter

import gradio as gr
import launch
from modules import script_callbacks


def clean_image(
    input_image: Image,
    diameter: float = 5,
    sigma_color: float = 8,
    sigma_space: float = 8,
    radius: float = 4,
    eps: float = 16,
) -> Image:

    img = np.array(input_image).astype(np.float32)
    y = img.copy()

    for _ in range(64):
        y = cv2.bilateralFilter(y, diameter, sigma_color, sigma_space)

    for _ in range(4):
        y = guidedFilter(img, y, radius, eps)

    output_image = Image.fromarray(y.clip(0, 255).astype(np.uint8))
    return [input_image, output_image]

def batch_process(
        input_dir: str,
        output_dir: str,
        diameter: float = 5,
        sigma_color: float = 8,
        sigma_space: float = 8,
        radius: float = 4,
        eps: float = 16,
    ):
        print("Batch cleaning started")
        try:
            input_dir = Path(input_dir)
            output_dir = Path(output_dir)
            image_paths = [
                p
                for p in input_dir.iterdir()
                if (p.is_file and p.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"])
            ]

            print(f"Found {len(image_paths)} images")

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for i, f in enumerate(image_paths):
                if f.is_dir():
                    continue

                img = Image.open(f)

                _, cleaned_image = clean_image(
                    img,
                    diameter,
                    sigma_color,
                    sigma_space,
                    radius,
                    eps
                )

                caption_output_path = output_dir / f.name

                if caption_output_path.exists():
                    print(f"File already exists: {caption_output_path}. Skipped.")
                    continue

                # save img 
                cleaned_image.save(caption_output_path)

                print(
                    f"{f.name} has benn cleaned. Saved to {caption_output_path}."
                )

            print("All done!")
            return "Done!"
        except Exception as e:
            return f"Error: {e}"

def send_to_input(output):
    return output

def clear_output():
    return [None, None]

def on_ui_tabs():
    with gr.Blocks() as app:
        with gr.Tabs():
            with gr.TabItem(label="Single"):
                with gr.Row ():  
                    with gr.Column():
                        input_image = gr.Image(type="pil", label="Input Image")
                        start_btn = gr.Button(value="Start", variant="primary")

                    with gr.Column():
                        with gr.Row ():  
                            input_preview = gr.Image(
                                type="pil", 
                                label="Input Preview",
                                interactive=False
                            )
                            output_image = gr.Image(
                                type="pil", label="Output Image", interactive=False
                            )
                        send_to_input_btn = gr.Button(value="Use as input", variant="secondary")
                        clear_output_btn = gr.Button(value="Clear output", variant="secondary")

                gr.Markdown(
                    "The lllyasviel's original repo is [here](https://github.com/lllyasviel/AdverseCleaner/tree/main)."
                )

            with gr.TabItem(label="Batch"): 
                with gr.Row().style(equal_height=False):
                    with gr.Column():
                        input_dir_input = gr.Textbox(
                            label="Image Directory",
                            placeholder="path/to/caption",
                            type="text",
                        )
                        output_dir_input = gr.Textbox(
                            label="Output Directory",
                            placeholder="path/to/output",
                            type="text",
                        )

                        gr.Markdown("")

                        batch_start_btn = gr.Button(
                            value="Interrogate", variant="primary"
                        )

                    with gr.Column():
                        status_block = gr.Label(label="Status", value="Idle")     

            with gr.Row ():  
                with gr.Column():
                    with gr.Accordion("Advanced Config", open=True):
                            # ref: https://github.com/gogodr/AdverseCleanerExtension
                            gr.Markdown("#### Bilateral Filter")
                            diameter_slider = gr.Slider(
                                minimum=1,
                                maximum=30,
                                step=1,
                                value=5,
                                label="Diameter (default = 5)",
                                interactive=True,
                            )
                            sigma_color_slider = gr.Slider(
                                minimum=1,
                                maximum=30,
                                step=1,
                                value=8,
                                label="SigmaColor (default = 8)",
                                interactive=True,
                            )
                            sigma_space_slider = gr.Slider(
                                minimum=1,
                                maximum=30,
                                step=1,
                                value=8,
                                label="SigmaSpace (default = 8)",
                                interactive=True,
                            )

                            gr.Markdown("#### Guided Filter")
                            radius_slider = gr.Slider(
                                minimum=1,
                                maximum=30,
                                step=1,
                                value=4,
                                label="Radius (default = 4)",
                                interactive=True,
                            )
                            eps_slider = gr.Slider(
                                minimum=1,
                                maximum=30,
                                step=1,
                                value=16,
                                label="Accuracy (default = 16)",
                                interactive=True,
                            )                                            

                gr.Column()

        start_btn.click(
            fn=clean_image,
            inputs=[
                input_image,
                diameter_slider,
                sigma_color_slider,
                sigma_space_slider,
                radius_slider,
                eps_slider,
            ],
            outputs=[input_preview, output_image],
        )
        batch_start_btn.click(
            fn=batch_process,
            inputs=[
                input_dir_input,
                output_dir_input,
                diameter_slider,
                sigma_color_slider,
                sigma_space_slider,
                radius_slider,
                eps_slider,
            ],
            outputs=[status_block],
        )
        send_to_input_btn.click(
            fn=send_to_input, inputs=[output_image], outputs=[input_image]
        )
        clear_output_btn.click(fn=clear_output, outputs=[input_preview, output_image])

    return [(app, "Adverse Cleaner", "adverse_cleaner_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)

