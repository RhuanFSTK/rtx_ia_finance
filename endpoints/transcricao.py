import os
import tempfile
import logging
import traceback
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from gpt_handler import transcrever_audio

router = APIRouter()

# Configuração do logger (pode ser movida para outro módulo se quiser)
logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)

logger = logging.getLogger("transcricao")
logger.setLevel(logging.DEBUG)  # Capture tudo, DEBUG até CRITICAL

log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

# Handler arquivo com nome dinâmico será criado dentro do endpoint, para diferenciar por arquivo
# Handler console fixo, para debug em tempo real
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

@router.post("/")
async def transcrever(file: UploadFile = File(...)):
    safe_filename = os.path.splitext(os.path.basename(file.filename))[0]
    log_filename = f"log_{safe_filename}.log"
    log_path = os.path.join(logs_dir, log_filename)

    # Handler arquivo dinâmico (único para essa requisição)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    logger.info(f"Início do processamento do arquivo: {file.filename}")

    if not file.content_type.startswith("audio/"):
        mensagem = "O arquivo enviado não é um áudio válido."
        logger.error(mensagem)
        logger.removeHandler(file_handler)
        file_handler.close()
        raise HTTPException(status_code=400, detail=mensagem)

    ext = os.path.splitext(file.filename)[1] or ".mp3"
    logger.debug(f"Extensão do arquivo identificada: {ext}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            conteudo = await file.read()
            temp_file.write(conteudo)
            temp_file_path = temp_file.name
            
            # Salvar uma cópia do áudio recebido para verificação manual
            debug_audio_path = os.path.join(logs_dir, f"{safe_filename}{ext}")
            with open(debug_audio_path, "wb") as f_debug:
                f_debug.write(conteudo)
            logger.info(f"Áudio salvo para debug: {debug_audio_path}")

        logger.debug(f"Arquivo temporário criado: {temp_file_path}")
        logger.debug(f"Tamanho do arquivo temporário: {len(conteudo)} bytes")

        logger.info("Iniciando transcrição do áudio...")
        texto = transcrever_audio(temp_file_path)
        logger.info("Transcrição concluída com sucesso.")
        logger.debug(f"Texto transcrito: {texto}")

        return {"transcricao": texto}

    except Exception as e:
        erro_str = traceback.format_exc()
        logger.error(f"Erro durante a transcrição: {str(e)}")
        logger.error(f"Detalhes do erro:\n{erro_str}")
        raise HTTPException(status_code=500, detail=f"Erro ao transcrever o áudio: {str(e)}")

    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.debug(f"Arquivo temporário removido: {temp_file_path}")

        logger.info("Fim do processamento do arquivo.\n")

        # Remove handler de arquivo para não duplicar logs em próximas requisições
        logger.removeHandler(file_handler)
        file_handler.close()
