import openai

openai.api_key = "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"  # Substitua pela sua chave real

def classificar_texto(texto):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Você é um analista financeiro."},
                  {"role": "user", "content": f"Classifique: {texto}"}]
    )
    return response['choices'][0]['message']['content'].strip()

# Teste com um exemplo
print(classificar_texto("Comprei gasolina no posto"))