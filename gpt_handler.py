import os
import openai
import base64
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

def classificar_texto(texto):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um analista financeiro."},
            {"role": "user", "content": f"Classifique: {texto}"}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def transcrever_audio(caminho):
    with open(caminho, "rb") as audio_file:
        transcript = openai.Audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
    return transcript['text'].strip()

def analisar_imagem(base64_img):
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "Você é um assistente que analisa notas fiscais."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analise essa nota fiscal."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_img}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )
    return response['choices'][0]['message']['content'].strip()