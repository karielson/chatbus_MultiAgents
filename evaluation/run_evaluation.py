# evaluation/run_evaluation.py

from __future__ import annotations
from evaluation.references.reference_builder import build_reference
import csv
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import argparse
from dotenv import load_dotenv
from evaluation.metrics.tool_choice import calculate_pef

load_dotenv()


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "evaluation" / "datasets" / "consultas_piloto.csv"
OUTPUT_DIR = ROOT / "evaluation" / "outputs"


def get_runner(arquitetura: str):
    arquitetura = str(arquitetura).strip().lower()

    if arquitetura == "multiagente":
        from evaluation.runners.multiagent_runner import MultiAgentRunner
        return MultiAgentRunner()

    if arquitetura == "monoagente":
        from evaluation.runners.monoagent_runner import MonoAgentRunner
        return MonoAgentRunner()

    raise ValueError(
        "Arquitetura inválida. Use 'multiagente' ou 'monoagente'."
    )

def parse_args():
    parser = argparse.ArgumentParser(
        description="Avaliação experimental do ChatBus."
    )

    parser.add_argument(
        "--arquitetura",
        choices=["multiagente", "monoagente"],
        default="multiagente",
        help="Arquitetura a ser avaliada.",
    )

    parser.add_argument(
        "--dataset",
        default=str(DATASET_PATH),
        help="Caminho do CSV de consultas.",
    )

    return parser.parse_args()

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


def print_summary(results: list[dict]) -> None:
    total = len(results)

    if total == 0:
        print("Nenhum resultado para resumir.")
        return

    tempos = [
        float(r["tempo_resposta_seg"])
        for r in results
        if r.get("tempo_resposta_seg") not in (None, "")
    ]

    pefs = [
        int(r["pef"])
        for r in results
        if r.get("pef") not in (None, "")
    ]

    erros = [
        r for r in results
        if r.get("erro")
    ]

    trm_geral = sum(tempos) / len(tempos) if tempos else 0
    pef_geral = sum(pefs) / len(pefs) if pefs else 0
    taxa_erro = len(erros) / total

    print("\n" + "=" * 70)
    print("RESUMO DA AVALIAÇÃO")
    print("=" * 70)
    print(f"Total de consultas: {total}")
    print(f"TRM geral: {trm_geral:.2f} s")
    print(f"PEF geral: {pef_geral:.2f}")
    print(f"Taxa de erro: {taxa_erro:.2%}")

    print("\nResumo por tipo de tarefa:")
    tipos = sorted(set(r["tipo_tarefa"] for r in results))

    for tipo in tipos:
        subset = [r for r in results if r["tipo_tarefa"] == tipo]

        tempos_tipo = [
            float(r["tempo_resposta_seg"])
            for r in subset
            if r.get("tempo_resposta_seg") not in (None, "")
        ]

        pefs_tipo = [
            int(r["pef"])
            for r in subset
            if r.get("pef") not in (None, "")
        ]

        trm_tipo = sum(tempos_tipo) / len(tempos_tipo) if tempos_tipo else 0
        pef_tipo = sum(pefs_tipo) / len(pefs_tipo) if pefs_tipo else 0

        print(
            f"- {tipo}: "
            f"n={len(subset)}, "
            f"TRM={trm_tipo:.2f}s, "
            f"PEF={pef_tipo:.2f}"
        )


def main():
    args = parse_args()
    dataset_path = Path(args.dataset)

    print("=" * 70)
    print(f"AVALIAÇÃO EXPERIMENTAL DO CHATBUS — {args.arquitetura.upper()}")
    print("=" * 70)

    rows = read_dataset(dataset_path)
    print(f"Consultas carregadas: {len(rows)}")

    runner = get_runner(args.arquitetura)
    results = []

    for i, row in enumerate(rows, start=1):
        print("-" * 70)
        print(f"[{i}/{len(rows)}] Executando consulta {row.get('id_consulta')}")
        print(f"Tipo: {row.get('tipo_tarefa')}")
        print(f"Pergunta: {row.get('pergunta')}")

        reference = build_reference(row)

        result = runner.run(row)
        result_dict = asdict(result)

        result_dict["referencia_tipo"] = reference.get("tipo_referencia")
        result_dict["referencia_url_esperada"] = reference.get("url_esperada")
        result_dict["referencia_codigo_linha"] = reference.get("codigo_linha")
        result_dict["referencia_letreiro"] = reference.get("letreiro_completo")
        result_dict["referencia_sentido_descricao"] = reference.get("sentido_descricao")
        result_dict["referencia_erro"] = reference.get("erro")
        result_dict["referencia_observacao"] = reference.get("observacao")
        result_dict["referencia_timestamp_inicio"] = reference.get("timestamp_referencia_inicio")
        result_dict["referencia_timestamp_fim"] = reference.get("timestamp_referencia_fim")
        result_dict["referencia_linha_resolvida"] = reference.get("linha_resolvida")
        result_dict["referencia_horarios_esperados"] = "|".join(reference.get("horarios_esperados", []))
        result_dict["referencia_rota_tempo_total_min"] = reference.get("tempo_total_min")
        result_dict["referencia_rota_distancia_total_km"] = reference.get("distancia_total_km")
        result_dict["referencia_rota_qtd_baldeacoes"] = reference.get("qtd_baldeacoes")
        result_dict["referencia_rota_linhas_utilizadas"] = "|".join(reference.get("linhas_utilizadas", []))
        result_dict["referencia_rota_pontos_embarque"] = "|".join(reference.get("pontos_embarque", []))
        result_dict["referencia_rota_pontos_desembarque"] = "|".join(reference.get("pontos_desembarque", []))
        result_dict["referencia_faq_pergunta"] = reference.get("pergunta_referencia")
        result_dict["referencia_faq_resposta"] = reference.get("resposta_referencia")
        result_dict["referencia_faq_texto"] = reference.get("texto_referencia")
        result_dict["referencia_faq_categoria"] = reference.get("categoria")
        result_dict["referencia_faq_similaridade_pergunta"] = reference.get("similaridade_pergunta")
        result_dict["referencia_faq_score"] = reference.get("score_referencia")


        result_dict["pef"] = calculate_pef(
            result_dict.get("ferramenta_esperada"),
            result_dict.get("ferramenta_usada"),
        )

        # Conforme o protocolo da dissertação, a acurácia, a completude e a
        # atualidade são atribuídas manualmente após a comparação individual
        # da resposta com o respectivo gabarito. O QoI também não é calculado
        # durante a execução: ele somente pode ser obtido posteriormente, com
        # base nos três escores revisados pelo pesquisador.
        result_dict["acuracia"] = ""
        result_dict["completude"] = ""
        result_dict["atualidade"] = ""
        result_dict["qoi"] = ""

        # Os timestamps da execução e da captura do gabarito são preservados.
        # Estes campos legados permanecem vazios porque o tempo de resposta não
        # é utilizado para determinar a atualidade na avaliação manual.
        result_dict["delta_temporal_status_seg"] = ""
        result_dict["delta_temporal_horarios_seg"] = ""
        result_dict["delta_temporal_rotas_seg"] = ""
        result_dict["delta_temporal_faq_seg"] = ""

        results.append(result_dict)

        print(f"Ferramenta esperada: {result_dict.get('ferramenta_esperada')}")
        print(f"Ferramenta usada: {result_dict.get('ferramenta_usada')}")
        print(f"PEF: {result_dict.get('pef')}")
        print(f"Tempo: {result.tempo_resposta_seg:.2f} s")

        if result.erro:
            print(f"Erro: {result.erro}")
        else:
            print("Status: OK")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"runs_{args.arquitetura}_{timestamp}.csv"

    save_results(results, output_path)
    print_summary(results)

    print("=" * 70)
    print("Avaliação finalizada.")
    print(f"Arquivo salvo em: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
