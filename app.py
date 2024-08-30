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
        self.directory_path = "/var/nfs-mount/ComfyUI-VOL"
        
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
            os.path.join(self._data_dir,"comfy_ui_workflow.json"), "r"
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

        template_values = {
                            'input_video_url': 'https://sukuru.s3.amazonaws.com/videos/db76940a-db5f-4578-8f87-9db41af32647.MP4',
                            'frame_load_cap': 60,
                            'input_width': 360,
                            'input_height': 640,
                            'prompt_styler': '(ultra high res:1.4), (masterpiece), (beautiful lighting:1.4) , Bright sunlight illuminates , (mesmerizing:1.5), colorful, vibrant,',
                            'ipadapter_image_url': 'https://sukuru.s3.amazonaws.com/custom_themes_main/Flowers/purple-lilac.jpg',
                            'checkpoint': 'dreamshaper_8.safetensors',
                            'input_prompt': 'purple lilacs, vibrant, dense, natural, fresh, close-up, detailed petals, bright colors',
                            'output_width': 720,
                            'output_height': 1280,
                            'hires_steps': 5,
                            'hires_upscale': 1.2,
                            'hires_denoise': 0.56,
                            'seed': 4566245810894214660
                            }
        
        template_values, tempfiles = convert_request_file_url_to_path(template_values)
        json_workflow = copy.deepcopy(self.json_workflow)
        json_workflow = fill_template(json_workflow, template_values)
        print(json_workflow)

        # should send the image here 

        try:
            outputs = get_images(
                self.ws, json_workflow, self.client_id, self.server_address
            )

        except Exception as e:
            print("Error occurred while running Comfy workflow: ", e)

        for file in tempfiles:
            file.close()

        result = []

        print('outputs',outputs)
        for node_id in outputs:
            for item in outputs[node_id]:
                file_name = self.directory_path+item.get("filename")
                file_data = item.get("data")
                print('file_name, file_data', file_name, file_data)
                output = convert_outputs_to_base64(
                    node_id=node_id, file_name=file_name, file_data=file_data
                )
                result.append(output)
                # print('result', result)

        #return {"result": result}

        projectid = str("inferless")
        # result = [{'node_id': '449', 'data': 'ComfyUI/output/output_video_00001.mp4', 'format': 'mp4'}]        
        
        local_file_path = self.directory_path+"/"+result[0]['data']  # Assuming you want the first item in the list
        s3_file_name = f'{projectid}-{local_file_path.split("/")[-1]}.mp4'  # New name for the file in S3

        # Step 1: Upload the file to S3
        s3_client = boto3.client(
            's3',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        s3_client.meta.events.register('before-send.s3.*', self._patch_headers)
        s3_client.upload_file(local_file_path, self.bucket_name, s3_file_name)
        print(f"File uploaded successfully to S3 as {s3_file_name}.")

        s3_file_path = f'https://{bucket_name}.s3.amazonaws.com/{s3_file_name}'

        return {"s3_file_path":s3_file_path}
