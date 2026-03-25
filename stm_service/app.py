import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Импортируем существующий класс
from SemanticEmbeddingProcessor import SemanticEmbeddingProcessor

logger = logging.getLogger(__name__)

# --- Конфигурация из переменных окружения ---
DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "models/all-MiniLM-L6-v2")
DEFAULT_ABBR_PATH = os.getenv("ABBR_PATH", None)
DEFAULT_CACHE_SIZE = int(os.getenv("CACHE_SIZE", "1000"))
DEFAULT_THRESHOLD = float(os.getenv("THRESHOLD", "0.85"))

# Глобальные переменные
processor: Optional[SemanticEmbeddingProcessor] = None
_loading_lock = asyncio.Lock()
_current_config = {
    "model_path": DEFAULT_MODEL_PATH,
    "abbr_dataset_path": DEFAULT_ABBR_PATH,
    "cache_size": DEFAULT_CACHE_SIZE,
    "threshold": DEFAULT_THRESHOLD,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: загружаем модель с параметрами по умолчанию
    global processor
    await _reload_processor(
        model_path=_current_config["model_path"],
        abbr_dataset_path=_current_config["abbr_dataset_path"],
        cache_size=_current_config["cache_size"],
        threshold=_current_config["threshold"]
    )
    yield
    # Shutdown: при желании можно освободить ресурсы (модель остаётся в памяти)

async def _reload_processor(model_path: str, abbr_dataset_path: Optional[str],
                            cache_size: int, threshold: float):
    """Загрузка/перезагрузка процессора с новыми параметрами."""
    global processor
    logger.info(f"Reloading model: path={model_path}, cache={cache_size}, threshold={threshold}")
    # Можно добавить проверку существования пути, но это сделает сам конструктор
    # Создаём новый процессор
    new_processor = SemanticEmbeddingProcessor(
        model_path=model_path,
        abbr_dataset_path=abbr_dataset_path,
        cache_size=cache_size,
        threshold=threshold
    )
    # Заменяем глобальный процессор
    processor = new_processor
    # Обновляем текущую конфигурацию
    _current_config.update({
        "model_path": model_path,
        "abbr_dataset_path": abbr_dataset_path,
        "cache_size": cache_size,
        "threshold": threshold,
    })
    logger.info("Processor reloaded successfully")

app = FastAPI(title="Semantic Embedding Service", lifespan=lifespan)

# --- Модели Pydantic ---
class EmbedRequest(BaseModel):
    strings: List[str]

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]

class FindSimilarRequest(BaseModel):
    queries: List[str]
    corpus_terms: List[str]
    threshold: Optional[float] = None
    top_k: int = 1

class FindSimilarResponse(BaseModel):
    results: Dict[str, List[Dict[str, Any]]]

class ClusterRequest(BaseModel):
    strings: List[str]
    threshold: Optional[float] = None

class ClusterResponse(BaseModel):
    clusters: Dict[str, List[str]]

class ConfigRequest(BaseModel):
    model_path: Optional[str] = None
    abbr_dataset_path: Optional[str] = None
    cache_size: Optional[int] = None
    threshold: Optional[float] = None

class ConfigResponse(BaseModel):
    model_path: str
    abbr_dataset_path: Optional[str]
    cache_size: int
    threshold: float

# --- Эндпоинты ---
@app.get("/health")
async def health():
    """Проверка готовности сервиса"""
    return {"status": "ok", "model_loaded": processor is not None}

@app.get("/config", response_model=ConfigResponse)
async def get_config():
    """Получить текущую конфигурацию"""
    return ConfigResponse(
        model_path=_current_config["model_path"],
        abbr_dataset_path=_current_config["abbr_dataset_path"],
        cache_size=_current_config["cache_size"],
        threshold=_current_config["threshold"]
    )

@app.post("/config", response_model=ConfigResponse)
async def update_config(request: ConfigRequest):
    """
    Обновить конфигурацию и перезагрузить модель.
    Если какой-то параметр не указан, остаётся прежним.
    """
    async with _loading_lock:
        # Определяем новые значения
        new_model_path = request.model_path or _current_config["model_path"]
        new_abbr_path = request.abbr_dataset_path  # может быть None (явно)
        # Если не передано, оставляем старое значение
        if request.abbr_dataset_path is None:
            new_abbr_path = _current_config["abbr_dataset_path"]
        new_cache_size = request.cache_size or _current_config["cache_size"]
        new_threshold = request.threshold or _current_config["threshold"]

        # Проверка, что изменилось
        if (new_model_path == _current_config["model_path"] and
            new_abbr_path == _current_config["abbr_dataset_path"] and
            new_cache_size == _current_config["cache_size"] and
            new_threshold == _current_config["threshold"]):
            # Ничего не изменилось, можно вернуть текущую конфигурацию без перезагрузки
            return ConfigResponse(**_current_config)

        try:
            await _reload_processor(
                model_path=new_model_path,
                abbr_dataset_path=new_abbr_path,
                cache_size=new_cache_size,
                threshold=new_threshold
            )
        except Exception as e:
            logger.exception("Failed to reload model")
            raise HTTPException(500, f"Failed to reload model: {str(e)}")

    return ConfigResponse(**_current_config)

# --- Остальные эндпоинты без изменений ---
@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    if processor is None:
        raise HTTPException(503, "Model not loaded")
    try:
        embeddings = processor.get_embeddings_batch(request.strings)
        return {"embeddings": embeddings.tolist()}
    except Exception as e:
        logger.exception("Error in embed")
        raise HTTPException(500, str(e))

@app.post("/find_similar", response_model=FindSimilarResponse)
async def find_similar(request: FindSimilarRequest):
    if processor is None:
        raise HTTPException(503, "Model not loaded")
    try:
        results = processor.find_similar_terms(
            queries=request.queries,
            corpus_terms=request.corpus_terms,
            threshold=request.threshold,
            top_k=request.top_k
        )
        return {"results": results}
    except Exception as e:
        logger.exception("Error in find_similar")
        raise HTTPException(500, str(e))

@app.post("/cluster", response_model=ClusterResponse)
async def cluster(request: ClusterRequest):
    if processor is None:
        raise HTTPException(503, "Model not loaded")
    try:
        clusters = processor.cluster_similar_strings(
            strings_list=request.strings,
            threshold=request.threshold
        )
        return {"clusters": clusters}
    except Exception as e:
        logger.exception("Error in cluster")
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)