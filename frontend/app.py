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
        "/api/v1/health\n/api/v1/atmo/indices",
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


def to_iso(date_value: date, time_value: time) -> str:
    combined = datetime.combine(date_value, time_value)
    return combined.isoformat()


def tab_atmo_indices(client: httpx.Client, base_url: str) -> None:
    st.subheader("Indice ATMO (Atmo France)")
    st.caption("Renseigner les paramètres puis interroger l'API backend (proxy vers ATMO).")
    today = datetime.now()
    with st.form("atmo_indices_form"):
        code_zone = st.text_input("code_zone (ex: code INSEE/EPCI...)", value="")
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("date", value=today.date())
        with col2:
            date_hist_val = st.date_input("date_historique", value=today.date())
        submitted = st.form_submit_button("Interroger")

    if submitted:
        params: Dict[str, Any] = {}
        if code_zone.strip():
            params["code_zone"] = code_zone.strip()
        # Required
        params["date"] = date_val.isoformat()
        params["date_historique"] = date_hist_val.isoformat()

        try:
            data = http_get(client, f"{base_url}/api/v1/atmo/indices", params=params)
            # Expect strict response: {"results": [{"date", "code_qual"}, ...]}
            if not (isinstance(data, dict) and isinstance(data.get("results"), list)):
                st.error("Réponse inattendue du backend. Attendu: { 'results': [ { 'date', 'code_qual' } ] }")
                with st.expander("Réponse brute"):
                    st.json(data)
                return
            rows = data["results"]
            timeseries_rows = [
                {"date": r.get("date"), "code_qual": r.get("code_qual")}
                for r in rows
                if isinstance(r, dict) and r.get("date") is not None and r.get("code_qual") is not None
            ]
            df_ts = pd.DataFrame(timeseries_rows)
            if not df_ts.empty:
                # Only day on x-axis
                df_ts["date"] = pd.to_datetime(df_ts["date"], errors="coerce").dt.date
                df_ts = df_ts.dropna(subset=["date"]).sort_values("date")
                st.line_chart(df_ts.set_index("date")["code_qual"])
                with st.expander("Données (table)"):
                    st.dataframe(df_ts, use_container_width=True)
            else:
                st.info("Aucune donnée de série temporelle trouvée dans la réponse.")
                with st.expander("Réponse brute"):
                    st.json(data)
        except Exception as exc:
            st.error(f"Erreur: {exc}")


def main() -> None:
    st.set_page_config(page_title="Observatoire Citadin", layout="wide")
    base_url = render_sidebar()
    client = get_http_client()

    tabs = st.tabs(["Health", "Indice ATMO"])
    with tabs[0]:
        tab_health(client, base_url)
    with tabs[1]:
        tab_atmo_indices(client, base_url)


if __name__ == "__main__":
    main()


