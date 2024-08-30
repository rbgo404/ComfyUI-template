import copy
import os
import time
import uuid
from multiprocessing import Process
import subprocess
from typing import Dict
import threading
import logging
import time
import json
import boto3
import os
from botocore.exceptions import NoCredentialsError
import websocket
from helpers import (
    convert_outputs_to_base64,
    convert_request_file_url_to_path,
    fill_template,
    get_images,
    setup_comfyui,
)


def run_comfyui_in_background():
    def run_server():
        process = setup_comfyui()
        if process:
            stdout, stderr = process.communicate()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    logging.info("ComfyUI server thread started")

class InferlessPythonModel:
    def initialize(self):
        self.directory_path = os.getenv('NFS_VOLUME')
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.bucket_region = os.getenv('BUCKET_REGION')        
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if not os.path.exists(self.directory_path+"/ComfyUI"):
            subprocess.run(["wget", "https://github.com/rbgo404/Files/raw/main/build.sh"])
            subprocess.run(["bash", "build.sh"], check=True)
        
        self._data_dir = self.directory_path+"/data"
        self._model = None
        self.ws = None
        self.json_workflow = None
        self.server_address = "127.0.0.1:8188"
        self.client_id = str(uuid.uuid4())
        
        run_comfyui_in_background()

        with open(
            os.path.join(self._data_dir,"comfy_ui_workflow.json"), "rb"
        ) as json_file:
            self.json_workflow = json.load(json_file)
        socket_connected = False
        while not socket_connected:
            try:
                self.ws = websocket.WebSocket()
                self.ws.connect(
                    "ws://{}/ws?clientId={}".format(self.server_address, self.client_id)
                )
                socket_connected = True
            except Exception as e:
                print("Could not connect to comfyUI server. Trying again...")
                time.sleep(5)

        print("Successfully connected to the ComfyUI server!")


    def _patch_headers(self, request, **kwargs):
        # Remove the 'Expect' header to avoid the connection error
        request.headers.pop('Expect', None)

    def infer(self, inputs):
        project_id = inputs.pop("project_id")
        inputs["hires_upscale"] = float(inputs["hires_upscale"])
        inputs["hires_denoise"] = float(inputs["hires_denoise"])
        inputs["frame_load_cap"] = int(inputs["frame_load_cap"])
        inputs["input_width"] = int(inputs["input_width"])
        inputs["input_height"] = int(inputs["input_height"])
        inputs["output_width"] = int(inputs["output_width"])
        inputs["output_height"] = int(inputs["output_height"])
        inputs["hires_steps"] = int(inputs["hires_steps"])
        inputs["seed"] = int(inputs["seed"])
        
        template_values, tempfiles = convert_request_file_url_to_path(inputs)
        json_workflow = copy.deepcopy(self.json_workflow)
        json_workflow = fill_template(json_workflow, template_values)

        try:
            outputs = get_images(
                self.ws, json_workflow, self.client_id, self.server_address
            )

        except Exception as e:
            print("Error occurred while running Comfy workflow: ", e)

        for file in tempfiles:
            file.close()

        result = []
        for node_id in outputs:
            for item in outputs[node_id]:
                file_name = self.directory_path+item.get("filename")
                file_data = item.get("data")
                print('file_name, file_data', file_name, file_data)
                output = convert_outputs_to_base64(
                    node_id=node_id, file_name=file_name, file_data=file_data
                )
                result.append(output)
        
        local_file_path = result[0]['data']
        file_extension = os.path.splitext(local_file_path)[-1].lower()

        if file_extension in ['.mp4', '.jpg', '.png', '.gif']:
            s3_file_name = f'{project_id}.{file_extension}'
            s3_client = boto3.client('s3',region_name = self.bucket_region,aws_access_key_id = self.aws_access_key_id,
                                     aws_secret_access_key=self.aws_secret_access_key)
            s3_client.meta.events.register('before-send.s3.*', self._patch_headers)
            s3_client.upload_file(local_file_path, self.bucket_name, s3_file_name)
            s3_file_path = f'https://{self.bucket_name}.s3.amazonaws.com/{s3_file_name}'

            return {"s3_file_path":s3_file_path}

        else:
            return {"error":"File type is not supported"}
