INPUT_SCHEMA = {
    "input_video_url": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["https://sukuru.s3.amazonaws.com/videos/db76940a-db5f-4578-8f87-9db41af32647.MP4"]
    }
    "project_id": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["Inferless_"]
    },
    "frame_load_cap": {
        'datatype': 'INT8',
        'required': True,
        'shape': [1],
        'example': [60]
    },
    "input_width": {
        'datatype': 'INT8',
        'required': True,
        'shape': [1],
        'example': [360]
    },
    "input_height": {
        'datatype': 'INT8',
        'required': True,
        'shape': [1],
        'example': [640]
    },
    "prompt_styler": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["(ultra high res:1.4), (masterpiece), (beautiful lighting:1.4) , Bright sunlight illuminates , (mesmerizing:1.5), colorful, vibrant,"]
    },
    "ipadapter_image_url": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["https://sukuru.s3.amazonaws.com/custom_themes_main/Flowers/purple-lilac.jpg"]
    },
    "checkpoint": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["dreamshaper_8.safetensors"]
    },
    "input_prompt": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["purple lilacs, vibrant, dense, natural, fresh, close-up, detailed petals, bright colors"]
    },
    "output_width": {
        'datatype': 'INT8',
        'required': True,
        'shape': [1],
        'example': [720]
    },
    "output_height": {
        'datatype': 'INT8',
        'required': True,
        'shape': [1],
        'example': [1280]
    },
    "hires_steps": {
        'datatype': 'INT8',
        'required': True,
        'shape': [1],
        'example': [5]
    },
    "hires_upscale": {
        'datatype': 'FP32',
        'required': True,
        'shape': [1],
        'example': [1.2]
    },
    "hires_denoise": {
        'datatype': 'FP32',
        'required': True,
        'shape': [1],
        'example': [0.56]
    },
    "seed": {
        'datatype': 'INT8',
        'required': True,
        'shape': [1],
        'example': [127]
    }
}
