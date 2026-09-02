# evaluation/references/reference_horarios.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from services.sptrans import sptrans
from scrapers.horarios import horarios_scraper


@dataclass
class HorariosReference:
    linha: str
    dia_operacional: Optional[str]
    linha_resolvida: Optional[str]
    horarios_esperados: list[str]
    erro: Optional[str] = None
    observacao: Optional[str] = None
    timestamp_referencia_inicio: Optional[str] = None
    timestamp_referencia_fim: Optional[str] = None


def build_horarios_reference(
    linha: str,
    dia_operacional: str | None = None,
) -> HorariosReference:
    """
    Gera o gabarito oficial para consultas de horários programados.

    Fonte:
        Site oficial da SPTrans, por meio do scraper de horários.
    """

    timestamp_inicio = datetime.now().isoformat()

    linha = (linha or "").strip()
    dia_operacional = (dia_operacional or "").strip() if dia_operacional is not None else None

    if not linha:
        timestamp_fim = datetime.now().isoformat()
        return HorariosReference(
            linha=linha,
            dia_operacional=dia_operacional,
            linha_resolvida=None,
            horarios_esperados=[],
            erro="Linha não informada.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    linhas = sptrans.buscar_linha(linha)

    if not linhas:
        timestamp_fim = datetime.now().isoformat()
        return HorariosReference(
            linha=linha,
            dia_operacional=dia_operacional,
            linha_resolvida=None,
            horarios_esperados=[],
            erro="Linha não encontrada na SPTrans.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    linha_exata = [
        item for item in linhas
        if str(item).strip().lower() == linha.lower()
    ]

    if linha_exata:
        linha_resolvida = linha_exata[0]
        observacao = None
    elif len(linhas) == 1:
        linha_resolvida = linhas[0]
        observacao = "Não houve correspondência exata, mas apenas uma linha foi retornada pela SPTrans."
    else:
        timestamp_fim = datetime.now().isoformat()
        return HorariosReference(
            linha=linha,
            dia_operacional=dia_operacional,
            linha_resolvida=None,
            horarios_esperados=[],
            erro=f"Mais de uma linha encontrada para o termo: {linha}. Opções: {', '.join(linhas)}.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    horarios = horarios_scraper.scrape(linha_resolvida, dia_operacional)

    timestamp_fim = datetime.now().isoformat()

    if not horarios:
        return HorariosReference(
            linha=linha,
            dia_operacional=dia_operacional,
            linha_resolvida=linha_resolvida,
            horarios_esperados=[],
            erro="Nenhum horário encontrado no site da SPTrans.",
            observacao=observacao,
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    horarios_limpos = [
        str(h).strip()
        for h in horarios
        if str(h).strip()
    ]

    return HorariosReference(
        linha=linha,
        dia_operacional=dia_operacional,
        linha_resolvida=linha_resolvida,
        horarios_esperados=horarios_limpos,
        erro=None,
        observacao=observacao,
        timestamp_referencia_inicio=timestamp_inicio,
        timestamp_referencia_fim=timestamp_fim,
    )