from __future__ import annotations

import time
import traceback
from datetime import datetime

from agents.coordenador import coordenador
from evaluation.runners.base_runner import BaseRunner, ModelRunResult


class MultiAgentRunner(BaseRunner):
    """
    Executor experimental da arquitetura multiagente.

    Este runner chama diretamente o coordenador Agno,
    registra tempo de execução, resposta e eventuais erros.
    """

    arquitetura = "multiagente"

    def run(self, row: dict) -> ModelRunResult:
        id_consulta = str(row.get("id_consulta", "")).strip()
        tipo_tarefa = str(row.get("tipo_tarefa", "")).strip()
        pergunta = str(row.get("pergunta", "")).strip()
        ferramenta_esperada = str(row.get("ferramenta_esperada", "")).strip() or None

        inicio = datetime.now()
        t0 = time.perf_counter()

        chunks = []
        erro = None

        try:
            user_id = f"eval_multi_{id_consulta}"

            for rr in coordenador.run(
                pergunta,
                stream=True,
                user_id=user_id
            ):
                if getattr(rr, "content", None):
                    chunks.append(str(rr.content))

            resposta = "".join(chunks).strip()

            if not resposta:
                resposta = "Não obtive resposta do modelo."

        except Exception as e:
            resposta = ""
            erro = f"{type(e).__name__}: {str(e)}"
            traceback.print_exc()

        t1 = time.perf_counter()
        fim = datetime.now()

        return ModelRunResult(
            id_consulta=id_consulta,
            tipo_tarefa=tipo_tarefa,
            pergunta=pergunta,
            resposta=resposta,
            arquitetura=self.arquitetura,
            tempo_resposta_seg=round(t1 - t0, 4),
            ferramenta_esperada=ferramenta_esperada,
            ferramenta_usada=None,
            erro=erro,
            timestamp_inicio=inicio.isoformat(),
            timestamp_fim=fim.isoformat(),
        )