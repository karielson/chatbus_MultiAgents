# evaluation/references/reference_rotas.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

import requests

from config.settings import settings


@dataclass
class RotasReference:
    origem: str
    destino: str
    preferencia: Optional[str]
    tempo_total_min: Optional[int]
    distancia_total_km: Optional[float]
    qtd_baldeacoes: Optional[int]
    linhas_utilizadas: list[str]
    pontos_embarque: list[str]
    pontos_desembarque: list[str]
    passos: list[dict[str, Any]]
    erro: Optional[str] = None
    observacao: Optional[str] = None
    timestamp_referencia_inicio: Optional[str] = None
    timestamp_referencia_fim: Optional[str] = None


def _format_location(value: str | None) -> str:
    value = (value or "").strip()

    if not value:
        return ""

    # Se for coordenada, não acrescenta São Paulo.
    if "," in value:
        parts = [p.strip() for p in value.split(",")]
        if len(parts) == 2:
            try:
                float(parts[0])
                float(parts[1])
                return value
            except ValueError:
                pass

    if "são paulo" in value.lower() or "sao paulo" in value.lower():
        return value

    return f"{value}, São Paulo, SP, Brasil"


def _minutes_from_seconds(seconds: int | None) -> Optional[int]:
    if seconds is None:
        return None

    return round(seconds / 60)


def _km_from_meters(meters: int | None) -> Optional[float]:
    if meters is None:
        return None

    return round(meters / 1000, 2)


def _build_params(origem: str, destino: str, preferencia: str | None) -> dict:
    params = {
        "origin": _format_location(origem),
        "destination": _format_location(destino),
        "mode": "transit",
        "transit_mode": "bus",
        "key": settings.GOOGLE_MAPS_API_KEY,
    }

    if preferencia == "menos_baldeacoes":
        params["transit_routing_preference"] = "fewer_transfers"
    elif preferencia == "menos_caminhada":
        params["transit_routing_preference"] = "less_walking"
    elif preferencia == "rapida":
        params["alternatives"] = "true"

    return params


def _is_bus_transit_step(step: dict) -> bool:
    """
    Retorna True se o trecho TRANSIT for ônibus/trolebus.

    A Google Directions pode retornar metrô/trem mesmo com transit_mode=bus.
    Por isso o gabarito precisa filtrar explicitamente pelo tipo de veículo.
    """

    if step.get("travel_mode") != "TRANSIT":
        return True

    transit = step.get("transit_details", {})
    line = transit.get("line", {})
    vehicle = line.get("vehicle", {})

    vehicle_type = str(vehicle.get("type", "")).upper().strip()
    vehicle_name = str(vehicle.get("name", "")).lower().strip()

    tipos_aceitos = {
        "BUS",
        "INTERCITY_BUS",
        "TROLLEYBUS",
    }

    if vehicle_type in tipos_aceitos:
        return True

    if "ônibus" in vehicle_name or "onibus" in vehicle_name or "bus" in vehicle_name:
        return True

    return False


def _route_is_bus_only(route: dict) -> bool:
    """
    Aceita apenas rotas cujos trechos TRANSIT sejam ônibus/trolebus.
    Trechos de caminhada são permitidos.
    """

    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            if not _is_bus_transit_step(step):
                return False

    return True


def _select_route(routes: list[dict], preferencia: str | None) -> dict | None:
    """
    Seleciona rota válida exclusivamente por ônibus/trolebus.

    A rota de referência para perguntas de ônibus não deve usar metrô/trem.
    """

    bus_routes = [
        route
        for route in routes
        if _route_is_bus_only(route)
    ]

    if not bus_routes:
        return None

    if preferencia == "rapida" and len(bus_routes) > 1:
        return sorted(
            bus_routes,
            key=lambda r: r["legs"][0]["duration"]["value"]
        )[0]

    return bus_routes[0]


def build_rotas_reference(
    origem: str,
    destino: str,
    preferencia: str | None = None,
) -> RotasReference:
    """
    Gera o gabarito oficial para consultas de rota.

    Fonte:
        Google Directions API, modo transit/bus.

    Observação metodológica:
        Apenas rotas cujos trechos TRANSIT sejam ônibus/trolebus são aceitas
        como gabarito válido para perguntas formuladas como rota de ônibus.
    """

    timestamp_inicio = datetime.now().isoformat()

    origem = (origem or "").strip()
    destino = (destino or "").strip()
    preferencia = (preferencia or "rapida").strip()

    if not origem or not destino:
        timestamp_fim = datetime.now().isoformat()
        return RotasReference(
            origem=origem,
            destino=destino,
            preferencia=preferencia,
            tempo_total_min=None,
            distancia_total_km=None,
            qtd_baldeacoes=None,
            linhas_utilizadas=[],
            pontos_embarque=[],
            pontos_desembarque=[],
            passos=[],
            erro="Origem ou destino não informado.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    params = _build_params(origem, destino, preferencia)

    try:
        response = requests.get(
            settings.MAPS_API_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        timestamp_fim = datetime.now().isoformat()
        return RotasReference(
            origem=origem,
            destino=destino,
            preferencia=preferencia,
            tempo_total_min=None,
            distancia_total_km=None,
            qtd_baldeacoes=None,
            linhas_utilizadas=[],
            pontos_embarque=[],
            pontos_desembarque=[],
            passos=[],
            erro=f"Erro ao consultar Google Directions API: {type(e).__name__}: {e}",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    if data.get("status") != "OK":
        timestamp_fim = datetime.now().isoformat()
        return RotasReference(
            origem=origem,
            destino=destino,
            preferencia=preferencia,
            tempo_total_min=None,
            distancia_total_km=None,
            qtd_baldeacoes=None,
            linhas_utilizadas=[],
            pontos_embarque=[],
            pontos_desembarque=[],
            passos=[],
            erro=f"Google Directions retornou status: {data.get('status')}",
            observacao=data.get("error_message"),
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    routes = data.get("routes", [])

    if not routes:
        timestamp_fim = datetime.now().isoformat()
        return RotasReference(
            origem=origem,
            destino=destino,
            preferencia=preferencia,
            tempo_total_min=None,
            distancia_total_km=None,
            qtd_baldeacoes=None,
            linhas_utilizadas=[],
            pontos_embarque=[],
            pontos_desembarque=[],
            passos=[],
            erro="Nenhuma rota retornada pela Google Directions API.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    route = _select_route(routes, preferencia)

    if route is None:
        timestamp_fim = datetime.now().isoformat()
        return RotasReference(
            origem=origem,
            destino=destino,
            preferencia=preferencia,
            tempo_total_min=None,
            distancia_total_km=None,
            qtd_baldeacoes=None,
            linhas_utilizadas=[],
            pontos_embarque=[],
            pontos_desembarque=[],
            passos=[],
            erro="Nenhuma rota exclusivamente por ônibus foi retornada pela Google Directions API.",
            observacao="A API retornou apenas rotas com metrô, trem ou outro modo não aceito para esta tarefa.",
            timestamp_referencia_inicio=timestamp_inicio,
            timestamp_referencia_fim=timestamp_fim,
        )

    leg = route["legs"][0]

    linhas_utilizadas = []
    pontos_embarque = []
    pontos_desembarque = []
    passos = []

    for step in leg.get("steps", []):
        step_info = {
            "modo": step.get("travel_mode"),
            "distancia_m": step.get("distance", {}).get("value"),
            "duracao_seg": step.get("duration", {}).get("value"),
            "instrucao": step.get("html_instructions"),
        }

        if step.get("travel_mode") == "TRANSIT":
            transit = step.get("transit_details", {})
            line = transit.get("line", {})

            linha_nome = line.get("short_name") or line.get("name")
            embarque = transit.get("departure_stop", {}).get("name")
            desembarque = transit.get("arrival_stop", {}).get("name")
            vehicle = line.get("vehicle", {})

            if linha_nome:
                linhas_utilizadas.append(str(linha_nome))
            if embarque:
                pontos_embarque.append(str(embarque))
            if desembarque:
                pontos_desembarque.append(str(desembarque))

            step_info.update({
                "linha": linha_nome,
                "linha_nome_completo": line.get("name"),
                "tipo_veiculo": vehicle.get("type"),
                "nome_veiculo": vehicle.get("name"),
                "ponto_embarque": embarque,
                "ponto_desembarque": desembarque,
                "horario_saida": transit.get("departure_time", {}).get("text"),
                "horario_chegada": transit.get("arrival_time", {}).get("text"),
            })

        passos.append(step_info)

    qtd_trechos_onibus = len(linhas_utilizadas)
    qtd_baldeacoes = max(qtd_trechos_onibus - 1, 0)

    timestamp_fim = datetime.now().isoformat()

    return RotasReference(
        origem=origem,
        destino=destino,
        preferencia=preferencia,
        tempo_total_min=_minutes_from_seconds(leg.get("duration", {}).get("value")),
        distancia_total_km=_km_from_meters(leg.get("distance", {}).get("value")),
        qtd_baldeacoes=qtd_baldeacoes,
        linhas_utilizadas=linhas_utilizadas,
        pontos_embarque=pontos_embarque,
        pontos_desembarque=pontos_desembarque,
        passos=passos,
        erro=None,
        observacao=None,
        timestamp_referencia_inicio=timestamp_inicio,
        timestamp_referencia_fim=timestamp_fim,
    )