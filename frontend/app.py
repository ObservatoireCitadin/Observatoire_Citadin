import os
from datetime import datetime, time, date
from typing import Any, Dict, Optional

import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv


load_dotenv(override=False)


def get_default_backend_url() -> str:
    return os.getenv("BACKEND_BASE_URL", "http://localhost:8000")


@st.cache_resource
def get_http_client() -> httpx.Client:
    return httpx.Client(timeout=30.0)


def http_get(client: httpx.Client, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = client.get(url, params=params)
    response.raise_for_status()
    try:
        return response.json()
    except Exception:
        return {"content": response.text}


def render_sidebar() -> str:
    st.sidebar.title("Observatoire Citadin")
    st.sidebar.caption("Frontend Streamlit")

    if "backend_url" not in st.session_state:
        st.session_state.backend_url = get_default_backend_url()

    backend_url = st.sidebar.text_input("Backend URL", value=st.session_state.backend_url)
    st.session_state.backend_url = backend_url.rstrip("/")
    st.sidebar.markdown(f"Utilisation: {st.session_state.backend_url}")
    # Quick health check button
    if st.sidebar.button("Tester la connexion backend"):
        client = get_http_client()
        try:
            data = http_get(client, f"{st.session_state.backend_url}/api/v1/health")
            st.sidebar.success("Backend OK")
            st.sidebar.json(data)
        except Exception as exc:
            st.sidebar.error(f"Backend injoignable: {exc}")
    st.sidebar.divider()
    st.sidebar.markdown("Endpoints:")
    st.sidebar.code(
        "/api/v1/health\n/api/v1/indicators\n/api/v1/air-quality",
        language=None,
    )
    return st.session_state.backend_url


def tab_health(client: httpx.Client, base_url: str) -> None:
    st.subheader("Health")
    if st.button("Vérifier l'état"):
        try:
            data = http_get(client, f"{base_url}/api/v1/health")
            st.success("OK")
            st.json(data)
        except Exception as exc:
            st.error(f"Erreur: {exc}")


def tab_indicators(client: httpx.Client, base_url: str) -> None:
    st.subheader("Indicateurs")
    with st.form("indicators_form"):
        use_city = st.checkbox("Filtrer par city_id", value=False)
        city_id_val: Optional[int] = None
        if use_city:
            city_id_val = st.number_input("city_id", min_value=0, step=1, value=0)
        indicator_type = st.text_input("type (optionnel)", value="")
        submitted = st.form_submit_button("Charger")

    if submitted:
        try:
            params: Dict[str, Any] = {}
            if use_city and city_id_val is not None:
                params["city_id"] = int(city_id_val)
            if indicator_type.strip():
                params["type"] = indicator_type.strip()
            data = http_get(client, f"{base_url}/api/v1/indicators", params=params)
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Aucun résultat")
            with st.expander("Réponse brute"):
                st.json(data)
        except Exception as exc:
            st.error(f"Erreur: {exc}")


def to_iso(date_value: date, time_value: time) -> str:
    combined = datetime.combine(date_value, time_value)
    return combined.isoformat()


def tab_air_quality(client: httpx.Client, base_url: str) -> None:
    st.subheader("Qualité de l'air (Geod'air)")
    st.caption("Renseigner les paramètres puis interroger l'API backend (proxy vers Geod'air).")
    today = datetime.now()
    with st.form("air_quality_form"):
        pollutant_code = st.text_input("Code polluant (ex: NO2, PM10...)", value="")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Début (date)", value=today.date())
            start_time = st.time_input("Début (heure)", value=time(0, 0))
        with col2:
            end_date = st.date_input("Fin (date)", value=today.date())
            end_time = st.time_input("Fin (heure)", value=time(23, 59))
        station = st.text_input("Code station (optionnel)", value="")
        submitted = st.form_submit_button("Interroger")

    if submitted:
        if not pollutant_code.strip():
            st.warning("Le code polluant est requis.")
            return
        start_iso = to_iso(start_date, start_time)
        end_iso = to_iso(end_date, end_time)
        params = {
            "pollutant_code": pollutant_code.strip(),
            "start": start_iso,
            "end": end_iso,
        }
        if station.strip():
            params["station"] = station.strip()

        try:
            data = http_get(client, f"{base_url}/api/v1/air-quality", params=params)
            # Display best-effort
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], (list, dict)):
                # Try to tabularize if list of dicts
                payload = data["data"]
                if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                    df = pd.DataFrame(payload)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.json(payload)
            else:
                st.json(data)
        except Exception as exc:
            st.error(f"Erreur: {exc}")


def main() -> None:
    st.set_page_config(page_title="Observatoire Citadin", layout="wide")
    base_url = render_sidebar()
    client = get_http_client()

    tabs = st.tabs(["Health", "Indicateurs", "Qualité de l'air"])
    with tabs[0]:
        tab_health(client, base_url)
    with tabs[1]:
        tab_indicators(client, base_url)
    with tabs[2]:
        tab_air_quality(client, base_url)


if __name__ == "__main__":
    main()


