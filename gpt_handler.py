import json
import re
import os
import openai
import base64
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

def fallback_parse(texto: str) -> dict:
    # Valor (ex: 100, R$ 120.50)
    valor = 0.0
    match = re.search(r'(?:R\$)?\s?(\d+(?:[.,]\d{2})?)', texto)
    if match:
        valor_str = match.group(1).replace(',', '.')
        try:
            valor = float(valor_str)
        except ValueError:
            pass

    # Palavra-chave (descrição)
    palavras = re.findall(r'\b\w+\b', texto.lower())
    descricao = next((p for p in palavras if p not in ['foi', 'no', 'na', 'com', 'de', 'uma', 'um']), "Gasto").capitalize()

    return {
        "descricao": descricao,
        "valor": valor,
        "classificacao": "Não classificado"
    }

def agent_master(texto: str) -> dict:
    prompt = f"""
                Você é um assistente inteligente de classificação de despesas. Sua missão é analisar a descrição de um gasto e retornar um JSON estruturado contendo:

                - **descricao**: palavra-chave principal do gasto + informações relevantes como local ou serviço
                - **valor**: número extraído da frase que represente o valor financeiro (em reais). Se não houver valor claro, retorne vazio
                - **classificacao**: escolha **apenas uma** das seguintes categorias:
                - pessoal
                - profissional
                - alimentação
                - transporte
                - fixa (relacionado a moradia: aluguel, luz, água, internet etc.)
                - saúde
                - outros

                ### Contexto profissional do usuário:
                Profissão: Técnico em Refrigeração. Gastos com **gás**, **peças técnicas**, **manutenção de equipamentos**, entre outros relacionados a serviços de refrigeração, devem ser classificados como **profissional**.

                ### Instruções adicionais:
                - Classifique corretamente com base no **uso ou finalidade do gasto**, e não apenas na palavra usada.
                - Retorne **apenas o JSON**, sem comentários ou explicações adicionais.
                - Se não for possível identificar com clareza o valor, a descrição ou a classificação, retorne a string "vazio" no respectivo campo.

                ### Entrada:
                "{texto}"

                ### Retorno esperado:
                {{
                "descricao": "Almoço no restaurante da esquina",
                "valor": 38.50,
                "classificacao": "alimentação"
                }}
            """

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # ou gpt-4
            messages=[
                {"role": "system", "content": "Você é um assistente financeiro que estrutura dados de gastos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        conteudo = resposta['choices'][0]['message']['content']

        try:
            dados = json.loads(conteudo)
            return {
                "descricao": dados.get("descricao", "Não identificado").capitalize(),
                "valor": float(dados.get("valor", 0.0)),
                "classificacao": dados.get("classificacao", "Não classificado").capitalize()
            }
        except json.JSONDecodeError:
            print("Resposta da IA não é JSON válido. Aplicando fallback.")
            return fallback_parse(texto)

    except Exception as e:
        print("Erro ao classificar texto com OpenAI:", e)
        return fallback_parse(texto)


def agent_audio(caminho: str) -> str:
    try:
        with open(caminho, "rb") as audio_file:
            resposta = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="pt",  # força português BR
                temperature=0.0  # consistente e preciso
            )
        return resposta["text"].strip()

    except Exception as e:
        print(f"[ERRO] Falha ao transcrever áudio: {e}")
        return ""

def agent_img(base64_img):
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