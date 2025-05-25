import os
import pytz
import uuid
import tempfile
import logging
import traceback
from gpt_handler import transcrever_audio, classificar_texto
from mysql_conn import get_connection
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

# Diretório de logs
logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)

# Logger principal
logger = logging.getLogger("transcricao")
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

# Console handler fixo
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


def get_file_logger(safe_filename: str) -> logging.FileHandler:
    log_filename = f"log_{safe_filename}.log"
    log_path = os.path.join(logs_dir, log_filename)
    
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    return file_handler


def salvar_gasto_no_banco(desc, classificacao, valor, data_hora):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO gastos (descricao, classificacao, valor, data_hora) VALUES (%s, %s, %s, %s)",
            (desc, classificacao, valor, data_hora)
        )
        conn.commit()


@router.post("/")
async def transcrever(file: UploadFile = File(...)):
    safe_filename = os.path.splitext(os.path.basename(file.filename))[0]
    req_id = str(uuid.uuid4())[:8]
    file_handler = get_file_logger(safe_filename)

    logger.info(f"[{req_id}] Início do processamento do arquivo: {file.filename}")

    if not file.content_type.startswith("audio/"):
        mensagem = "O arquivo enviado não é um áudio válido."
        logger.error(f"[{req_id}] {mensagem}")
        logger.removeHandler(file_handler)
        file_handler.close()
        raise HTTPException(status_code=400, detail=mensagem)

    ext = os.path.splitext(file.filename)[1] or ".mp3"
    logger.debug(f"[{req_id}] Extensão do arquivo: {ext}")

    try:
        conteudo = await file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(conteudo)
            temp_file_path = temp_file.name

        debug_audio_path = os.path.join(logs_dir, f"{safe_filename}{ext}")
        with open(debug_audio_path, "wb") as f_debug:
            f_debug.write(conteudo)

        logger.info(f"[{req_id}] Áudio salvo para debug: {debug_audio_path}")
        logger.debug(f"[{req_id}] Arquivo temporário: {temp_file_path}")
        logger.debug(f"[{req_id}] Tamanho do arquivo: {len(conteudo)} bytes")

        logger.info(f"[{req_id}] Iniciando transcrição...")
        texto = transcrever_audio(temp_file_path)
        logger.info(f"[{req_id}] Transcrição concluída.")
        logger.debug(f"[{req_id}] Texto: {texto}")

        resultado = classificar_texto(texto)

        desc = resultado.get("descricao", "").strip()
        classificacao = resultado.get("classificacao", "").strip()
        valor_raw = str(resultado.get("valor", "")).strip()

        logger.info(f"[{req_id}] Descrição recebida: {desc}")
        logger.info(f"[{req_id}] Classificação recebida: {classificacao}")
        logger.info(f"[{req_id}] Valor recebido: {valor_raw}")

        # Regras: valor deve ser válido e diferente de zero, e classificação obrigatória
        try:
            valor = float(valor_raw)
            if valor == 0.0:
                logger.warning(f"[{req_id}] Valor é zero. Não será salvo no banco.")
                return {
                    "mensagem": "Gasto classificado, mas não salvo porque o valor é zero.",
                    "response": resultado,
                    "salvo": False
                }
        except ValueError:
            logger.warning(f"[{req_id}] Valor inválido. Não será salvo no banco.")
            return {
                "mensagem": "Gasto classificado, mas não salvo devido a valor inválido.",
                "response": resultado,
                "salvo": False
            }

        if not classificacao:
            logger.warning(f"[{req_id}] Classificação ausente. Não será salvo no banco.")
            return {
                "mensagem": "Gasto classificado, mas não salvo por falta de classificação.",
                "response": resultado,
                "salvo": False
            }

        # Capitaliza os campos
        desc = desc.capitalize()
        classificacao = classificacao.capitalize()

        fuso_brasilia = pytz.timezone("America/Sao_Paulo")
        data_hora_brasilia = datetime.now(fuso_brasilia).strftime("%Y-%m-%d %H:%M:%S")

        salvar_gasto_no_banco(desc, classificacao, valor, data_hora_brasilia)
        logger.info(f"[{req_id}] Gasto salvo no banco com sucesso.")
        
        return {
            "mensagem": "Gasto classificado e salvo com sucesso!",
            "response": resultado,
            "salvo": True
        }

    except Exception as e:
        erro_str = traceback.format_exc()
        logger.error(f"[{req_id}] Erro: {str(e)}")
        logger.error(f"[{req_id}] Detalhes:\n{erro_str}")
        raise HTTPException(status_code=500, detail=f"Erro ao transcrever o áudio: {str(e)}")

    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.debug(f"[{req_id}] Arquivo temporário removido: {temp_file_path}")

        logger.info(f"[{req_id}] Fim do processamento.\n")
        logger.removeHandler(file_handler)
        file_handler.close()
