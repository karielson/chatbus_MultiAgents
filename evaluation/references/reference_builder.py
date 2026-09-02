# evaluation/references/reference_builder.py

from __future__ import annotations

from dataclasses import asdict
from typing import Any
from evaluation.references.reference_horarios import build_horarios_reference
from evaluation.references.reference_status import build_status_reference
from evaluation.references.reference_rotas import build_rotas_reference
from evaluation.references.reference_faq import build_faq_reference_from_row

def build_reference(row: dict) -> dict[str, Any]:
    tipo_tarefa = str(row.get("tipo_tarefa", "")).strip().lower()

    if tipo_tarefa == "status":
        ref = build_status_reference(
            linha=row.get("linha"),
            sentido=row.get("sentido"),
        )

        data = asdict(ref)
        data["tipo_referencia"] = "status"
        return data

    if tipo_tarefa == "horarios":
        ref = build_horarios_reference(
            linha=row.get("linha"),
            dia_operacional=row.get("dia_operacional"),
        )

        data = asdict(ref)
        data["tipo_referencia"] = "horarios"
        return data

    if tipo_tarefa == "rota":
        ref = build_rotas_reference(
            origem=row.get("origem"),
            destino=row.get("destino"),
            preferencia=row.get("preferencia"),
        )

        data = asdict(ref)
        data["tipo_referencia"] = "rota"
        return data
    
    if tipo_tarefa == "faq":
        ref = build_faq_reference_from_row(row)

        data = asdict(ref)
        data["tipo_referencia"] = "faq"
        return data


    return {
        "tipo_referencia": tipo_tarefa,
        "erro": "Gabarito ainda não implementado para este tipo de tarefa.",
    }