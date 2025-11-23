import os
from datetime import datetime, time, date
from typing import Any, Dict, Optional

import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(override=False)


def get_default_backend_url() -> str:
    return os.getenv("BACKEND_BASE_URL", "http://localhost:8000")


@st.cache_resource
def get_http_client() -> httpx.Client:
    return httpx.Client(timeout=30.0)


def http_get(
    client: httpx.Client,
    url: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    response = client.get(url, params=params)
    response.raise_for_status()
    try:
        return response.json()
    except Exception:
        return {"content": response.text}


@st.cache_data
def load_sdes_example() -> Optional[pd.DataFrame]:
    """
    Charge le fichier d'exemple SDES pour extraire les libellés.
    Retourne None si indisponible.
    """
    try:
        base_dir = Path(__file__).resolve().parent
        csv_path = base_dir / "data" / "SDES_ITDD_Example.csv"
        if not csv_path.exists():
            return None
        # Auto-detect delimiter, handle UTF-8 BOM, drop empty rows
        df = pd.read_csv(
            csv_path,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
        )
        df = df.rename(columns=lambda c: str(c).strip())
        df = df.dropna(how="all")
        return df
    except Exception:
        return None


def _first_present_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> Optional[str]:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def render_sidebar() -> str:
    st.sidebar.title("Observatoire Citadin")
    st.sidebar.caption("Frontend Streamlit")

    if "backend_url" not in st.session_state:
        st.session_state.backend_url = get_default_backend_url()

    backend_url = st.sidebar.text_input(
        "Backend URL",
        value=st.session_state.backend_url,
    )
    st.session_state.backend_url = backend_url.rstrip("/")
    st.sidebar.markdown(f"Utilisation: {st.session_state.backend_url}")
    # Quick health check button
    if st.sidebar.button("Tester la connexion backend"):
        client = get_http_client()
        try:
            data = http_get(
                client,
                f"{st.session_state.backend_url}/api/v1/health",
            )
            st.sidebar.success("Backend OK")
            st.sidebar.json(data)
        except Exception as exc:
            st.sidebar.error(f"Backend injoignable: {exc}")
    st.sidebar.divider()
    st.sidebar.markdown("Endpoints:")
    st.sidebar.code(
        "/api/v1/health\n/api/v1/atmo/indices\n/api/v1/sdes/commune",
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
    st.caption(
        "Renseigner les paramètres puis interroger l'API backend "
        "(proxy vers ATMO)."
    )
    today = datetime.now()
    with st.form("atmo_indices_form"):
        code_zone = st.text_input(
            "code_zone (ex: code INSEE/EPCI...)",
            value="",
        )
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("date", value=today.date())
        with col2:
            date_hist_val = st.date_input(
                "date_historique",
                value=today.date(),
            )
        submitted = st.form_submit_button("Interroger")

    if submitted:
        params: Dict[str, Any] = {}
        if code_zone.strip():
            params["code_zone"] = code_zone.strip()
        # Required
        params["date"] = date_val.isoformat()
        params["date_historique"] = date_hist_val.isoformat()

        try:
            data = http_get(
                client,
                f"{base_url}/api/v1/atmo/indices",
                params=params,
            )
            # Expect strict response: {"results": [{"date", "code_qual"}, ...]}
            if not (
                isinstance(data, dict)
                and isinstance(data.get("results"), list)
            ):
                st.error(
                    "Réponse inattendue du backend. Attendu: "
                    "{ 'results': [ { 'date', 'code_qual' } ] }"
                )
                with st.expander("Réponse brute"):
                    st.json(data)
                return
            rows = data["results"]
            timeseries_rows = [
                {"date": r.get("date"), "code_qual": r.get("code_qual")}
                for r in rows
                if (
                    isinstance(r, dict)
                    and r.get("date") is not None
                    and r.get("code_qual") is not None
                )
            ]
            df_ts = pd.DataFrame(timeseries_rows)
            if not df_ts.empty:
                # Only day on x-axis
                df_ts["date"] = pd.to_datetime(
                    df_ts["date"],
                    errors="coerce",
                ).dt.date
                df_ts = df_ts.dropna(subset=["date"]).sort_values("date")
                st.line_chart(df_ts.set_index("date")["code_qual"])
                with st.expander("Données (table)"):
                    st.dataframe(df_ts, use_container_width=True)
            else:
                st.info("Aucune série temporelle trouvée dans la réponse.")
                with st.expander("Réponse brute"):
                    st.json(data)
        except Exception as exc:
            st.error(f"Erreur: {exc}")


def tab_sdes_commune(client: httpx.Client, base_url: str) -> None:
    st.subheader("SDES - Commune")
    st.caption(
        "Renseigner le code INSEE, le libellé de la variable "
        "et du sous-champ, puis interroger l'API backend "
        "(proxy vers SDES)."
    )
    df_example = load_sdes_example()
    has_labels = False
    var_choices: list[str] = []
    var_col: Optional[str] = None
    sub_col: Optional[str] = None
    if df_example is not None:
        var_col = _first_present_column(
            df_example,
            [
                "Libellé de la variable",
                "LIBELLÉ DE LA VARIABLE",
                "LIBELLE_VARIABLE",
            ],
        )
        sub_col = _first_present_column(
            df_example,
            [
                "Libellé du sous-champ",
                "LIBELLÉ DU SOUS-CHAMP",
                "LIBELLE_SOUS_CHAMP",
            ],
        )
        if var_col and sub_col:
            has_labels = True
            var_choices = (
                df_example[var_col]
                .dropna()
                .astype(str)
                .str.strip()
                .drop_duplicates()
                .sort_values()
                .tolist()
            )

    with st.form("sdes_commune_form"):
        code_insee = st.text_input(
            "Code INSEE de la ville",
            value="",
            help="Exemple: 69123",
        )
        if has_labels and var_choices:
            variable_label = st.selectbox(
                "Libellé de la variable",
                options=var_choices,
                index=0,
            )
            subfield_choices = []
            if var_col and sub_col:
                subfield_choices = (
                    df_example.loc[
                        df_example[var_col].astype(str).str.strip()
                        == str(variable_label).strip(),
                        sub_col,
                    ]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .drop_duplicates()
                    .sort_values()
                    .tolist()
                )
            if subfield_choices:
                subfield_label = st.selectbox(
                    "Libellé du sous-champ",
                    options=subfield_choices,
                    index=0,
                )
            else:
                st.caption("Aucun sous-champ disponible pour cette variable.")
                st.selectbox(
                    "Libellé du sous-champ",
                    options=["(Aucun sous-champ)"],
                    index=0,
                )
                subfield_label = ""
        else:
            variable_label = st.text_input(
                "Libellé de la variable",
                value="",
            )
            subfield_label = st.text_input(
                "Libellé du sous-champ",
                value="",
            )
        submitted = st.form_submit_button("Interroger")

    if submitted:
        # Safe strip helpers
        v_label = (
            variable_label.strip()
            if isinstance(variable_label, str)
            else ""
        )
        s_label = (
            subfield_label.strip()
            if isinstance(subfield_label, str)
            else ""
        )
        params: Dict[str, Any] = {
            "code_insee": code_insee.strip(),
            "variable_label": v_label,
            "subfield_label": s_label,
        }
        try:
            data = http_get(
                client,
                f"{base_url}/api/v1/sdes/commune",
                params=params,
            )
            # Attendu: results -> [{year: int, value: number|null}, ...]
            results = data.get("results") if isinstance(data, dict) else None
            if not isinstance(results, list):
                st.error(
                    "Réponse inattendue du backend. "
                    "Attendu: { 'results': [ { 'year', 'value' } ] }"
                )
                with st.expander("Réponse brute"):
                    st.json(data)
                return
            rows = [
                {"year": r.get("year"), "value": r.get("value")}
                for r in results
                if isinstance(r, dict)
            ]
            df_ts = pd.DataFrame(rows)
            if df_ts.empty:
                st.info("Aucune donnée de série temporelle.")
                with st.expander("Réponse brute"):
                    st.json(data)
                return
            # Clean and sort
            df_ts = df_ts.dropna(subset=["year"]).copy()
            df_ts["year"] = pd.to_numeric(df_ts["year"], errors="coerce")
            df_ts = df_ts.dropna(subset=["year"]).astype({"year": int})
            df_ts = df_ts.sort_values("year")
            st.line_chart(df_ts.set_index("year")["value"])
            with st.expander("Données (table)"):
                st.dataframe(df_ts, use_container_width=True)
        except Exception as exc:
            st.error(f"Erreur: {exc}")


def main() -> None:
    st.set_page_config(page_title="Observatoire Citadin", layout="wide")
    base_url = render_sidebar()
    client = get_http_client()

    tabs = st.tabs(["Health", "Indice ATMO", "SDES Commune"])
    with tabs[0]:
        tab_health(client, base_url)
    with tabs[1]:
        tab_atmo_indices(client, base_url)
    with tabs[2]:
        tab_sdes_commune(client, base_url)


if __name__ == "__main__":
    main()
