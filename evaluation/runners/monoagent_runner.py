# evaluation/runners/monoagent_runner.py

from __future__ import annotations

import time
import traceback
from datetime import datetime

from evaluation.runners.base_runner import BaseRunner, ModelRunResult


class MonoAgentRunner(BaseRunner):
    """
    Executor experimental da arquitetura monoagente.

    Quando o monoagente estiver implementado, substitua o trecho TODO
    pela chamada real do agente único.
    """

    arquitetura = "monoagente"

    def run(self, row: dict) -> ModelRunResult:
        id_consulta = str(row.get("id_consulta", "")).strip()
        tipo_tarefa = str(row.get("tipo_tarefa", "")).strip()
        pergunta = str(row.get("pergunta", "")).strip()
        ferramenta_esperada = str(row.get("ferramenta_esperada", "")).strip() or None

        inicio = datetime.now()
        t0 = time.perf_counter()

        erro = None
        resposta = ""

        try:
            # TODO: substituir pela chamada real do monoagente.
            # Exemplo futuro:
            # resposta = monoagente.run(pergunta)
            resposta = "Monoagente ainda não implementado."

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