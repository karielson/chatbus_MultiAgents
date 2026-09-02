# evaluation/references/reference_status.py

from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

from services.sptrans import sptrans


@dataclass
class StatusReference:
    linha: str
    sentido: Optional[str]
    codigo_linha: Optional[int]
    letreiro_completo: Optional[str]
    sentido_descricao: Optional[str]
    url_esperada: Optional[str]
    erro: Optional[str] = None
    observacao: Optional[str] = None
    timestamp_referencia_inicio: Optional[str] = None
    timestamp_referencia_fim: Optional[str] = None


def _letreiro_completo(linha_info: dict) -> str:
    return f"{linha_info.get('lt')}-{linha_info.get('tl')}"


def _resolver_linha_status(linha: str) -> tuple[Optional[dict], Optional[str], Optional[str]]:
    """
    Resolve uma linha retornada pela SPTrans para fins de gabarito.

    Retorna:
        linha_info, erro, observacao
    """

    linhas_info = sptrans.buscar_info_linhas(linha)

    if not linhas_info:
        return None, "Linha não encontrada na SPTrans.", None

    # Primeiro tenta correspondência exata com o letreiro lt-tl.
    linhas_exatas = [
        item for item in linhas_info
        if _letreiro_completo(item).strip().lower() == linha.strip().lower()
    ]

    if linhas_exatas:
        if len(linhas_exatas) > 1:
            return (
                linhas_exatas[0],
                None,
                f"Foram encontrados {len(linhas_exatas)} registros para o mesmo letreiro; foi usado o primeiro retorno da SPTrans.",
            )

        return linhas_exatas[0], None, None

    # Se não houver correspondência exata, verifica se há múltiplos letreiros distintos.
    letreiros_distintos = sorted({_letreiro_completo(item) for item in linhas_info})

    if len(letreiros_distintos) > 1:
        return (
            None,
            f"Mais de uma linha distinta encontrada para o termo: {linha}. Opções: {', '.join(letreiros_distintos)}.",
            None,
        )

    # Caso só exista um letreiro distinto, usa o primeiro registro.
    return (
        linhas_info[0],
        None,
        "Não houve correspondência exata com o termo informado, mas apenas um letreiro distinto foi encontrado.",
    )


def build_status_reference(linha: str, sentido: str | None = None) -> StatusReference:
    timestamp_inicio = datetime.now().isoformat()
    timestamp_referencia = datetime.now().isoformat()
    """
    Gera o gabarito oficial para consultas de status/mapa.

    Fonte:
        SPTrans/Olho Vivo - Linha/Buscar

    Retorna:
        URL parametrizada esperada do Olho Vivo para linha e sentido.
    """

    linha = (linha or "").strip()
    sentido = (sentido or "").strip() if sentido is not None else None

    if not linha:
        timestamp_fim = datetime.now().isoformat()
        return StatusReference(
            linha=linha,
            sentido=sentido,
            codigo_linha=None,
            letreiro_completo=None,
            sentido_descricao=None,
            url_esperada=None,
            erro="Linha não informada.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    linha_info, erro, observacao = _resolver_linha_status(linha)

    if erro or not linha_info:
        timestamp_fim = datetime.now().isoformat()
        return StatusReference(
            linha=linha,
            sentido=sentido,
            codigo_linha=None,
            letreiro_completo=None,
            sentido_descricao=None,
            url_esperada=None,
            erro=erro,
            observacao=observacao,
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    codigo_linha = linha_info.get("cl")
    letreiro_completo = _letreiro_completo(linha_info)

    if not sentido:
        timestamp_fim = datetime.now().isoformat()
        return StatusReference(
            linha=linha,
            sentido=sentido,
            codigo_linha=codigo_linha,
            letreiro_completo=letreiro_completo,
            sentido_descricao=None,
            url_esperada=None,
            erro="Sentido não informado.",
            observacao=observacao,
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    if sentido == "1":
        sentido_descricao = linha_info.get("tp")
    elif sentido == "2":
        sentido_descricao = linha_info.get("ts")
    else:
        timestamp_fim = datetime.now().isoformat()
        return StatusReference(
            linha=linha,
            sentido=sentido,
            codigo_linha=codigo_linha,
            letreiro_completo=letreiro_completo,
            sentido_descricao=None,
            url_esperada=None,
            erro="Sentido inválido. Use 1 ou 2.",
            observacao=observacao,
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    sentido_encoded = quote(sentido_descricao or "")

    url_esperada = (
        "https://olhovivo.sptrans.com.br/#sp"
        f"?cat=Mapa2&l={codigo_linha}"
        f"&s={letreiro_completo}"
        f"&sc={sentido_encoded}"
    )
    timestamp_fim = datetime.now().isoformat()
    return StatusReference(
        
        linha=linha,
        sentido=sentido,
        codigo_linha=codigo_linha,
        letreiro_completo=letreiro_completo,
        sentido_descricao=sentido_descricao,
        url_esperada=url_esperada,
        erro=None,
        observacao=observacao,
        timestamp_referencia_inicio=timestamp_inicio,
        timestamp_referencia_fim=timestamp_fim,
    )