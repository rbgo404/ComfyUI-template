import base64
import io
import json
import logging
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from io import BytesIO
import time
import requests
from PIL import Image
        

COMFYUI_DIR = f"{os.getenv('NFS_VOLUME')}/ComfyUI"
BASE64_PREAMBLE = "data:image/png;base64,"


def download_tempfile(file_url, filename):
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        filetype = filename.split(".")[-1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{filetype}")
        temp_file.write(response.content)
        return temp_file.name, temp_file
    except Exception as e:
        logging.error("Error downloading and saving image:", e)
        return None



def setup_comfyui():
    try:
        logging.info(f"Attempting to start comfy-ui server at {COMFYUI_DIR}")
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=COMFYUI_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for a short time to see if the process starts successfully
        time.sleep(5)
        
        if process.poll() is None:
            logging.info("ComfyUI server process started successfully.")
            return process
        else:
            stdout, stderr = process.communicate()
            logging.error(f"ComfyUI server failed to start. Stdout: {stdout}, Stderr: {stderr}")
            raise Exception("ComfyUI server failed to start")
    except Exception as e:
        logging.error("Failed to run setup_comfyui:", exc_info=True)
        raise Exception("Error setting up ComfyUI repo") from e

def queue_prompt(prompt, client_id, server_address):
    print("====="*200,"INSIDE THE QUEUE PROMPT")
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type, server_address):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(
        "http://{}/view?{}".format(server_address, url_values)
    ) as response:
        return response.read()


def get_history(prompt_id, server_address):
    with urllib.request.urlopen(
        "http://{}/history/{}".format(server_address, prompt_id)
    ) as response:
        output = json.loads(response.read())
        return output[prompt_id]["outputs"]
        # return json.loads(response.read())


def get_images(ws, prompt, client_id, server_address):
    prompt_id = queue_prompt(prompt, client_id, server_address)["prompt_id"]
    print("====="*200," prompt_id: ",prompt_id)
    logging.info(f"prompt id:  {prompt_id}")
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data

    # history = get_history(prompt_id, server_address)[prompt_id]
    history = get_history(prompt_id, server_address)
    print("====="*200," history: ",history)
    for node_id in history:
        node_output = history[node_id]
        if "gifs" in node_output:
            outputs = []
            for item in node_output["gifs"]:
                outputs.append({"filename": item.get("filename")})
            if not output_images.get(node_id):
                output_images[node_id] = outputs
            else:
                output_images[node_id].extend(outputs)
        if "images" in node_output:
            outputs = []
            for image in node_output["images"]:
                # Image Preview Nodes don't get saved, so this is how to extract the data from previews
                if image.get("type") == "temp":
                    image_data = get_image(
                        image["filename"],
                        image["subfolder"],
                        image["type"],
                        server_address,
                    )
                    outputs.append(
                        {"filename": image.get("filename"), "data": image_data}
                    )
                else:
                    print("saved image: ", image)
                    print("image type: ", image.get("type"))
                    # When the image gets saved
                    outputs.append({"filename": image.get("filename")})
            if not output_images.get(node_id):
                output_images[node_id] = outputs
            else:
                output_images[node_id].extend(outputs)

    return output_images


def fill_template(workflow, template_values):
    if isinstance(workflow, dict):
        # If it's a dictionary, recursively process its keys and values
        for key, value in workflow.items():
            workflow[key] = fill_template(value, template_values)
        return workflow
    elif isinstance(workflow, list):
        # If it's a list, recursively process its elements
        return [fill_template(item, template_values) for item in workflow]
    elif (
        isinstance(workflow, str)
        and workflow.startswith("{{")
        and workflow.endswith("}}")
    ):
        # If it's a placeholder, replace it with the corresponding value
        placeholder = workflow[2:-2]
        if placeholder in template_values:
            return template_values[placeholder]
        else:
            return workflow  # Placeholder not found in values
    else:
        # If it's neither a dictionary, list, nor a placeholder, leave it unchanged
        return workflow


def convert_request_file_url_to_path(template_values):
    tempfiles = []
    new_template_values = template_values.copy()
    for key, value in template_values.items():
        if isinstance(value, str) and (
            value.startswith("https://") or value.startswith("http://")
        ):
            if value[-1] == "/":
                value = value[:-1]
            filename = value.split("/")[-1]

            file_destination_path, file_object = download_tempfile(
                file_url=value, filename=filename
            )
            tempfiles.append(file_object)
            new_template_values[key] = file_destination_path

        elif isinstance(value, dict):
            if value.get("type") == "image":
                data = value.get("data")
                image = b64_to_pil(data)

                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False
                ) as temp_file:
                    file_destination_path = temp_file.name
                    image.save(file_destination_path)

                    tempfiles.append(temp_file)
                    new_template_values[key] = file_destination_path

    return new_template_values, tempfiles

"""
This is the relevant output from ComfyUI

"outputs": {
    "12": {
    "gifs": [
        {
        "filename": "output_video_00001.mp4",
        "subfolder": "",
        "type": "temp",
        "format": "video/h264-mp4",
        "frame_rate": 30.0
        }
    ]
}

"""

# I don't convert to base64 - I directly feed the video path so model.py can take it and push to S3 
def convert_outputs_to_base64(node_id, file_name, file_data=None):
    if not file_data:
        # this means the file_name is in mp4
        file_type = file_name.split(".")[-1]
        file_type = file_type.lower()
        filepath = os.path.join("ComfyUI", "output", file_name)
        if file_type == "gif":
            return {
                "node_id": node_id,
                "data": filepath,
                "format": file_type,
            }
        elif file_type == "mp4":
            return {
                "node_id": node_id,
                # "data": mp4_to_base64(filepath),
                "data": filepath,
                "format": file_type,
            }
        elif file_type in {"png", "jpeg", "jpg"}:
            image = Image.open(filepath)
            return {"node_id": node_id, "data": filepath, "format": file_type}
    else:
        image = Image.open(io.BytesIO(file_data))
        b64_img = pil_to_b64(image)
        return {"node_id": node_id, "data": filepath, "format": "png"}


def gif_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")


def mp4_to_base64(file_path: str):
    with open(file_path, "rb") as mp4_file:
        binary_data = mp4_file.read()
        base64_data = base64.b64encode(binary_data)
        base64_string = base64_data.decode("utf-8")

    return base64_string


def b64_to_pil(b64_str):
    return Image.open(BytesIO(base64.b64decode(b64_str.replace(BASE64_PREAMBLE, ""))))


def pil_to_b64(pil_img):
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str
