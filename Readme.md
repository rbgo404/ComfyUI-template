<img width="1083" alt="image" src="https://github.com/user-attachments/assets/299345fc-7b4b-486b-b688-4d1f9e051c9e"># Model Template - Deploy Comfy-UI using Inferless
Deploy Comfy-UI using Inferless.

### Fork the Repository
Get started by forking the repository. You can do this by clicking on the fork button in the top right corner of the repository page.

This will create a copy of the repository in your own GitHub account, allowing you to make changes and customize it according to your needs.

### Create a Custom Runtime in Inferless
To access the custom runtime window in Inferless, simply navigate to the sidebar and click on the Create new Runtime button. A pop-up will appear.

Next, provide a suitable name for your custom runtime and proceed by uploading the **inferless-runtime-config.yaml** file given above. Finally, ensure you save your changes by clicking on the save button.

### Add Your NFS VOLUME PATH:
Go into the `inferless.yaml`, `build.sh` and replace `<YOUR_NFS_Mount_Path>` with your Mount Path.

### Add ENV Variables:
During the import you need to add these environment variables.
```
NFS_VOLUME
BUCKET_NAME
BUCKET_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```
### Import the Model in Inferless
Log in to your inferless account, select the workspace you want the model to be imported into and click the Add Model button.

### NOTE:
- `build.sh` is used inside the `app.py` which gets downloads from this repository(rbgo404/ComfyUI-template). In case you want to fork it, please make changes to the line number `44` of `app.py`.
- `build.sh` will download the `comfy_ui_workflow.json` from this repository(rbgo404/ComfyUI-template). In case you want to fork it, please make changes to the line number `65` of `build.sh`.
