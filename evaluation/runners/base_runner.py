from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelRunResult:
    id_consulta: str
    tipo_tarefa: str
    pergunta: str
    resposta: str
    arquitetura: str
    tempo_resposta_seg: float
    ferramenta_esperada: Optional[str]
    ferramenta_usada: Optional[str]
    erro: Optional[str]
    timestamp_inicio: str
    timestamp_fim: str


class BaseRunner:
    """
    Classe base para execução de uma arquitetura do ChatBus.

    A ideia é que tanto o modelo multiagente quanto o monoagente
    implementem o mesmo método run(row).

    Assim, a avaliação fica independente da arquitetura.
    """

    arquitetura: str = "base"

    def run(self, row: dict) -> ModelRunResult:
        raise NotImplementedError("Cada arquitetura deve implementar seu próprio método run().")