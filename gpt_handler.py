import os
import openai
import base64

# Pega variáveis direto do ambiente (deploy e local)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEU_HOST = os.getenv("SEU_HOST")
SEU_USUARIO = os.getenv("SEU_USUARIO")
SUA_SENHA = os.getenv("SUA_SENHA")
SEU_BANCO = os.getenv("SEU_BANCO")


OPENAI_API_KEY = "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"

if not OPENAI_API_KEY:
    print("⚠️ OPENAI_API_KEY não encontrada, algumas funções podem não funcionar.")
else:
    openai.api_key = OPENAI_API_KEY

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
