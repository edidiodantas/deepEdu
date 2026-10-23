"""Escolha automática de onde e como rodar o LLM (GPU ou CPU, tipo numérico).

Funciona em qualquer máquina sem configuração: GPU NVIDIA nova ou antiga,
notebook com pouca memória de vídeo, só processador. Se a GPU falhar no teste
de carregamento, o llm_factory volta para a CPU e o motivo fica registrado
aqui para aparecer no /health e na aba Início do painel.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

logger = logging.getLogger(__name__)

# Amadeus 0,5B em float16 ocupa ~1 GB; a folga cobre ativações e o cache de atenção.
MIN_FREE_VRAM_GB = 1.5


@dataclass
class LlmPlacement:
    device_map: str          # o que vai para from_pretrained ("auto" ou "cpu")
    dtype_name: str          # "float32" | "float16" | "bfloat16"
    device_label: str        # texto para pessoas: "GPU NVIDIA ... " ou "Processador (CPU)"
    reason: str = ""         # por que caiu na CPU, se caiu


_runtime: dict | None = None


def _llm_dtype(device_map: str, requested: str):
    """Escolhe o tipo numérico que o hardware realmente suporta.

    O Amadeus vem em bfloat16, mas GPUs NVIDIA anteriores à série RTX 30
    (compute capability < 8) falham com CUBLAS_STATUS_NOT_SUPPORTED nesse
    formato. Não usamos torch.cuda.is_bf16_supported(): ele também aceita
    bf16 "emulado", que é justamente o que quebra nessas placas.
    """
    import torch

    requested = (requested or "auto").strip().lower()
    if requested != "auto":
        return getattr(torch, requested)
    if device_map != "cpu" and torch.cuda.is_available():
        major, _ = torch.cuda.get_device_capability()
        return torch.bfloat16 if major >= 8 else torch.float16
    return torch.float32


def cpu_placement(reason: str = "", requested_dtype: str = "auto") -> LlmPlacement:
    dtype = _llm_dtype("cpu", requested_dtype)
    return LlmPlacement("cpu", str(dtype).replace("torch.", ""), "Processador (CPU)", reason)


def plan_llm_placement(device_map: str, requested_dtype: str) -> LlmPlacement:
    """Decide GPU ou CPU antes de carregar o modelo."""
    import torch

    if (device_map or "auto").strip().lower() == "cpu":
        return cpu_placement("LLM_DEVICE_MAP=cpu no .env", requested_dtype)
    if not torch.cuda.is_available():
        return cpu_placement("nenhuma GPU NVIDIA disponível", requested_dtype)

    name = torch.cuda.get_device_name(0)
    try:
        free_bytes, _total = torch.cuda.mem_get_info(0)
        free_gb = free_bytes / 1024**3
    except Exception:  # driver antigo sem mem_get_info: tenta a GPU mesmo assim
        free_gb = None
    if free_gb is not None and free_gb < MIN_FREE_VRAM_GB:
        return cpu_placement(
            f"GPU {name} com só {free_gb:.1f} GB livres (mínimo {MIN_FREE_VRAM_GB} GB)",
            requested_dtype,
        )

    dtype = _llm_dtype(device_map, requested_dtype)
    dtype_name = str(dtype).replace("torch.", "")
    return LlmPlacement(device_map, dtype_name, f"GPU {name}", "")


def record_runtime(placement: LlmPlacement) -> None:
    global _runtime
    _runtime = asdict(placement)
    if placement.reason and placement.device_map == "cpu":
        logger.warning("LLM na CPU: %s", placement.reason)
    logger.info("LLM em %s (%s)", placement.device_label, placement.dtype_name)


def runtime_status() -> dict:
    """Onde o LLM está rodando. Não importa torch (seguro para o /health)."""
    if _runtime is None:
        return {"status": "modelo ainda não carregado (carrega na primeira pergunta)"}
    return {"status": "carregado", **_runtime}
