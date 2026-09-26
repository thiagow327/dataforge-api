"""Cliente REST para o insight-service (a API secundária)."""

import httpx

from app.config import settings


def request_analysis(dataset_id: int, records: list[dict]) -> dict:
    """Envia os registros para o insight-service e devolve o resultado da análise.

    Levanta httpx.HTTPError se o serviço estiver indisponível ou responder com erro.
    """
    resp = httpx.post(
        f"{settings.insight_url}/analysis",
        json={"dataset_id": dataset_id, "records": records},
        timeout=150.0,  # a etapa de IA pode levar dezenas de segundos no CPU
    )
    resp.raise_for_status()
    return resp.json()
