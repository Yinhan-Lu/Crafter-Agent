import base64
import requests
import os
from openai import OpenAI

# Function to encode images to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Paths to images
image_path = "./partial_map_with_drawing.png"
diamond_path = './diamond.png'

# Encode images
map_encoded = encode_image(image_path)
diamond_encoded = encode_image(diamond_path)

# OpenAI API key and client setup
api_key = "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"
client = OpenAI(api_key=api_key)

# Headers for HTTP request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}


assets_path = './assets'
prompt = [ 
            {"type": "text", "text": "Here is the map"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{map_encoded}", "detail": "high"}},
            {"type": "text", "text": """Given there are no diamonds in the map and diamonds can be found near stone, iron, coal, lava and path, which direction should the player to explore?"""}
        ]

for asset_name in os.listdir(assets_path):
    asset_path = os.path.join(assets_path, asset_name)
    if asset_name.startswith('grass'):
        continue
    with open(asset_path, 'rb') as file:
        asset_base64 = base64.b64encode(file.read()).decode('utf-8')
    prompt.append({"type": "text", "text": f"Here is an image of {asset_name.removesuffix('.png')}"})
    prompt.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{asset_base64}", "detail": "low"}})

# Create chat completions
for _ in range(2):
    response = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer in json format"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    print(response)
