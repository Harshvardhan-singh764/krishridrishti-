import requests, json

key='vW7RXdeg6ppjoHpGBsLoCa1tnNACvY6X'
img='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
prompt='Analyze this plant leaf image. Identify the crop and any disease present. Provide the disease name, confidence level (e.g. 95%), and 3 recommended treatment steps. Output exactly as JSON: {"disease": "...", "confidence": "...", "treatment": ["...", "...", "..."]}'
payload={
    'model': 'pixtral-12b-2409', 
    'messages': [
        {
            'role': 'user', 
            'content': [
                {'type': 'text', 'text': prompt}, 
                {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{img}'}}
            ]
        }
    ], 
    'response_format': {'type': 'json_object'}
}

r = requests.post('https://api.mistral.ai/v1/chat/completions', headers={'Authorization': f'Bearer {key}'}, json=payload)
print(r.text)
