cd /var/nfs-mount/ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git && cd ComfyUI && git pull
pip install -r requirements.txt
pip install xformers numba spandrel deepdiff boto3
cd models && mkdir -p ipadapter clip_vision animatediff_models
cd ..
cd custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved --recursive 
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite --recursive && cd ComfyUI-VideoHelperSuite && pip install -r requirements.txt
cd ..
git clone https://github.com/ArtVentureX/comfyui-animatediff --recursive && cd comfyui-animatediff && pip install -r requirements.txt
cd ..
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack --recursive && cd ComfyUI-Impact-Pack && python3 install.py
cd ..
git clone https://github.com/Fannovel16/comfyui_controlnet_aux --recursive && cd comfyui_controlnet_aux && mkdir -p ckpts/yzd-v/DWPose ckpts/hr16/DWPose-TorchScript-BatchSize5 && pip install -r requirements.txt
cd ..
git clone https://github.com/jags111/efficiency-nodes-comfyui --recursive && cd efficiency-nodes-comfyui && pip install -r requirements.txt
cd ..
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus --recursive
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet --recursive && cd ComfyUI-Advanced-ControlNet  && git pull
cd ..
git clone https://github.com/cubiq/ComfyUI_essentials --recursive && cd ComfyUI_essentials && pip install -r requirements.txt
cd ..
git clone https://github.com/SLAPaper/ComfyUI-Image-Selector.git --recursive
git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git --recursive
git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git --recursive && cd ComfyUI-Frame-Interpolation && python3 install.py
cd ..
git clone https://github.com/rgthree/rgthree-comfy.git --recursive 
git clone https://github.com/ty0x2333/ComfyUI-Dev-Utils.git --recursive && cd ComfyUI-Dev-Utils && pip install -r requirements.txt
cd ..
git clone https://github.com/Fannovel16/ComfyUI-Video-Matting.git --recursive && cd ComfyUI-Video-Matting && pip install -r requirements.txt
cd ..
git clone https://github.com/city96/ComfyUI_ColorMod.git --recursive && cd ComfyUI_ColorMod && pip install -r requirements.txt
cd ..
git clone https://github.com/MNeMoNiCuZ/ComfyUI-mnemic-nodes.git --recursive && cd ComfyUI-mnemic-nodes && pip install -r requirements.txt
cd ..
git clone https://github.com/sipherxyz/comfyui-art-venture.git --recursive && cd comfyui-art-venture && pip install -r requirements.txt
cd ..
cd ..
cd models
wget -O vae/vae-ft-mse-840000-ema-pruned.safetensors https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors
wget -O checkpoints/dreamshaper_8.safetensors https://civitai.com/api/download/models/128713?type=Model&format=SafeTensor&size=pruned&fp=fp16&token=fc327fd702a67e653369455b3a5e7d5c
wget -O ipadapter/ip-adapter-plus_sd15.safetensors https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors
wget -O clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors https://huggingface.co/laion/CLIP-ViT-H-14-laion2B-s32B-b79K/resolve/main/model.safetensors
wget -O loras/AnimateLCM_sd15_t2v_lora.safetensors https://huggingface.co/wangfuyun/AnimateLCM/resolve/main/AnimateLCM_sd15_t2v_lora.safetensors
wget -O animatediff_models/AnimateLCM_sd15_t2v.ckpt https://huggingface.co/wangfuyun/AnimateLCM/resolve/main/AnimateLCM_sd15_t2v.ckpt
wget -O controlnet/control_v1p_sd15_qrcode_monster.safetensors https://huggingface.co/monster-labs/control_v1p_sd15_qrcode_monster/resolve/main/control_v1p_sd15_qrcode_monster.safetensors
wget -O upscale_models/2x-AniScale.pth https://objectstorage.us-phoenix-1.oraclecloud.com/n/ax6ygfvpvzka/b/open-modeldb-files/o/2x-AniScale.pth
wget -O embeddings/easynegative.safetensors https://civitai.com/api/download/models/9208?type=Model&format=SafeTensor&size=full&fp=fp16&token=fc327fd702a67e653369455b3a5e7d5c
wget -O loras/add_detail.safetensors https://civitai.com/api/download/models/62833?type=Model&format=SafeTensor&token=fc327fd702a67e653369455b3a5e7d5c
cd ..
