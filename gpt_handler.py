import os
import openai
import base64
from dotenv import load_dotenv

# Desabilita trace
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "true"
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY") 
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")


def classificar_texto(texto):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "Você é um analista financeiro."},
            {"role": "user", "content": f"Classifique: {texto}"}
        ]
    )
    return response['choices'][0]['message']['content']

def transcrever_audio(caminho):
    with open(caminho, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

def analisar_imagem(base64_img):
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Analise essa nota fiscal."},
                {"type": "image_url", "image_url": {"url": base64_img}}
            ]}
        ]
    )
    return response['choices'][0]['message']['content']
