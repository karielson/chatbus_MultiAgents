from __future__ import annotations

import csv
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from evaluation.runners.multiagent_runner import MultiAgentRunner


load_dotenv()


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "evaluation" / "datasets" / "consultas_piloto.csv"
OUTPUT_DIR = ROOT / "evaluation" / "outputs"


def read_dataset(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de consultas não encontrado: {path}")

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_results(results: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not results:
        raise ValueError("Não há resultados para salvar.")

    fieldnames = list(results[0].keys())

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    print("=" * 70)
    print("AVALIAÇÃO EXPERIMENTAL DO CHATBUS — MULTIAGENTE")
    print("=" * 70)

    rows = read_dataset(DATASET_PATH)
    print(f"Consultas carregadas: {len(rows)}")

    runner = MultiAgentRunner()
    results = []

    for i, row in enumerate(rows, start=1):
        print("-" * 70)
        print(f"[{i}/{len(rows)}] Executando consulta {row.get('id_consulta')}")
        print(f"Tipo: {row.get('tipo_tarefa')}")
        print(f"Pergunta: {row.get('pergunta')}")

        result = runner.run(row)
        result_dict = asdict(result)
        results.append(result_dict)

        print(f"Tempo: {result.tempo_resposta_seg:.2f} s")

        if result.erro:
            print(f"Erro: {result.erro}")
        else:
            print("Status: OK")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"runs_multiagente_{timestamp}.csv"

    save_results(results, output_path)

    print("=" * 70)
    print("Avaliação finalizada.")
    print(f"Arquivo salvo em: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()