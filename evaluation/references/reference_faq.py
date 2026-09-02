# evaluation/references/reference_faq.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FAQReference:
    pergunta_usuario: str
    pergunta_referencia: Optional[str]
    resposta_referencia: Optional[str]
    texto_referencia: Optional[str]
    categoria: Optional[str]
    similaridade_pergunta: Optional[float]
    score_referencia: Optional[float]
    erro: Optional[str] = None
    observacao: Optional[str] = None
    timestamp_referencia_inicio: Optional[str] = None
    timestamp_referencia_fim: Optional[str] = None


def build_faq_reference_from_row(row: dict) -> FAQReference:
    """
    Gera o gabarito oficial de FAQ a partir do próprio CSV de entrada.

    Essa abordagem é usada para evitar seleção automática incorreta do item
    de referência. O pesquisador define previamente o gabarito oficial de cada
    pergunta FAQ no dataset experimental.
    """

    timestamp_inicio = datetime.now().isoformat()

    pergunta_usuario = (row.get("pergunta") or "").strip()
    pergunta_referencia = (row.get("faq_pergunta_referencia") or "").strip()
    resposta_referencia = (row.get("faq_resposta_referencia") or "").strip()
    categoria = (row.get("faq_categoria") or "").strip()

    timestamp_fim = datetime.now().isoformat()

    if not pergunta_usuario:
        return FAQReference(
            pergunta_usuario=pergunta_usuario,
            pergunta_referencia=None,
            resposta_referencia=None,
            texto_referencia=None,
            categoria=None,
            similaridade_pergunta=None,
            score_referencia=None,
            erro="Pergunta do usuário não informada.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    if not resposta_referencia:
        return FAQReference(
            pergunta_usuario=pergunta_usuario,
            pergunta_referencia=pergunta_referencia or None,
            resposta_referencia=None,
            texto_referencia=None,
            categoria=categoria or None,
            similaridade_pergunta=None,
            score_referencia=None,
            erro="Gabarito FAQ não informado no CSV de entrada.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    texto_referencia = (
        f"{pergunta_referencia}\n\n{resposta_referencia}"
        if pergunta_referencia
        else resposta_referencia
    )

    return FAQReference(
        pergunta_usuario=pergunta_usuario,
        pergunta_referencia=pergunta_referencia or None,
        resposta_referencia=resposta_referencia,
        texto_referencia=texto_referencia,
        categoria=categoria or None,
        similaridade_pergunta=1.0,
        score_referencia=1.0,
        erro=None,
        observacao="Gabarito FAQ definido manualmente no CSV de entrada.",
        timestamp_referencia_inicio=timestamp_inicio,
        timestamp_referencia_fim=timestamp_fim,
    )