from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from core.models import Analysis, Alternative, Criterion, SEVEN_LEVEL_SCALE, level_score
from core.storage import DATA_DIR, analysis_to_json, load_analysis, load_analysis_from_json_text, save_analysis
from core.sample_data import create_fruit_supplier_analysis
from core.calculation import criterion_contributions, evaluate_all, evaluate_phase, normalize_weights, robustness_summary, selected_criteria, sensitivity_scenarios


DARK_BLUE = "#173A5E"
TEAL = "#178F88"
BRIGHT_TEAL = "#2AC6B6"
GREEN = "#49B051"
LIGHT_BG = "#F3F8F4"
MENU_ITEMS = [
    "Dashboard",
    "Análise",
    "Fornecedores",
    "Critérios & Pesos",
    "Escala 7 Níveis",
    "Avaliações",
    "Resultados",
    "Sensibilidade",
]


st.set_page_config(page_title="RETAILL MCDA", page_icon="📊", layout="wide")


def apply_css() -> None:
    st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, {LIGHT_BG} 0%, #FFFFFF 100%); }}
    .block-container {{ padding-top: 0.45rem; padding-bottom: 0.35rem; }}
    h1, h2, h3 {{ color: {DARK_BLUE}; letter-spacing: -0.02em; }}
    h1 {{ margin-bottom: 0.2rem; }}
    h2 {{ margin-top: 0.3rem; margin-bottom: 0.25rem; }}
    .hero {{
        background: linear-gradient(135deg, {DARK_BLUE} 0%, #1B4B6F 55%, {TEAL} 100%);
        color: white; border-radius: 20px; padding: 18px 20px;
        box-shadow: 0 14px 30px rgba(23,58,94,0.18); margin-bottom: 10px;
        position: relative; overflow: hidden;
    }}
    .hero:after {{
        content: ""; position: absolute; width: 260px; height: 260px; border-radius: 50%;
        border: 42px solid rgba(42,198,182,0.22); right: -80px; top: -80px;
    }}
    .hero-title {{ font-size: 1.9rem; font-weight: 800; margin: 0; line-height: 1.08; }}
    .hero-subtitle {{ color: #CDEFE7; font-size: 0.98rem; margin-top: 8px; max-width: 780px; }}
    .tag {{
        display: inline-block; padding: 6px 12px; border-radius: 999px;
        background: rgba(73,176,81,0.95); color: white; font-size: 0.82rem;
        font-weight: 700; margin-bottom: 16px; letter-spacing: 0.06em; text-transform: uppercase;
    }}
    .metric-card {{
        background: white; border: 1px solid rgba(23,58,94,0.08); border-left: 8px solid {GREEN};
        border-radius: 16px; padding: 18px 18px; box-shadow: 0 10px 26px rgba(23,58,94,0.08);
        min-height: 112px;
    }}
    .metric-card h4 {{ margin: 0 0 6px 0; color: {DARK_BLUE}; font-size: 0.95rem; }}
    .metric-card p {{ margin: 0; color: #466; font-size: 0.88rem; }}
    .top-logo-row {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin: 0 0 12px 0; }}
    .top-logo-row img {{ max-height: 34px; width: auto; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(23,58,94,0.12)); }}
    .top-logo-bar {{ display:flex; align-items:center; gap:12px; min-height:118px; padding: 18px 0 16px 0; margin: 4px 0 12px 0; flex-wrap:wrap; }}
    .top-logo-bar img {{ max-height:46px; max-width:132px; width:auto; object-fit:contain; display:block; filter: drop-shadow(0 4px 8px rgba(23,58,94,0.12)); }}
    .nav-compact {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 10px 0; }}
    .nav-chip {{
        display: inline-flex; align-items: center; justify-content: center;
        min-height: 36px; padding: 6px 12px; border-radius: 999px;
        font-size: 0.85rem; line-height: 1.05; font-weight: 800;
        text-decoration: none; white-space: nowrap;
        color: #FFFFFF !important;
        border: 1px solid {DARK_BLUE};
        background: linear-gradient(135deg, {DARK_BLUE} 0%, #1B4B6F 100%);
        box-shadow: 0 6px 12px rgba(23,58,94,0.12);
    }}
    .nav-chip.active {{
        background: linear-gradient(135deg, {GREEN} 0%, #2B8A3E 100%);
        border-color: {GREEN};
        box-shadow: 0 8px 14px rgba(73,176,81,0.18);
    }}
    .step-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 10px 0 8px 0; }}
    .step-card {{
        background: linear-gradient(180deg, #19506B 0%, #15465D 100%); color: white;
        border-radius: 16px; padding: 12px 12px; min-height: 110px;
        border: 1px solid rgba(42,198,182,0.22); box-shadow: 0 10px 20px rgba(23,58,94,0.14);
    }}
    .step-number {{
        width: 40px; height: 40px; border-radius: 999px; background: {BRIGHT_TEAL};
        display: flex; align-items: center; justify-content: center; font-weight: 800;
        color: {DARK_BLUE}; margin-bottom: 10px; font-size: 0.92rem;
    }}
    .step-card.active {{ background: linear-gradient(135deg, {GREEN} 0%, #2B8A3E 100%); }}
    .winner-box {{
        background: linear-gradient(135deg, #76C879 0%, {GREEN} 100%); color: white;
        padding: 12px 14px; border-radius: 14px; font-weight: 800;
        box-shadow: 0 8px 18px rgba(73,176,81,0.18); margin-top: 6px;
    }}
    </style>
    """, unsafe_allow_html=True)


def init_state() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    st.session_state.setdefault("active_page", 0)
    st.session_state.setdefault("criteria_revision", 0)
    st.session_state.setdefault("active_dialog", None)
    st.session_state.setdefault("post_save_action", None)
    st.session_state.setdefault("new_analysis_name", "Nova análise")
    st.session_state.setdefault("save_analysis_filename", "")
    sample_path = DATA_DIR / "fornecedores_fruta_alpha.json"
    if not sample_path.exists():
        save_analysis(create_fruit_supplier_analysis(), sample_path)
    if "analysis" not in st.session_state:
        st.session_state.analysis = load_analysis(sample_path)
        st.session_state.current_path = str(sample_path)


def rerun_save(path: str | Path | None = None):
    saved_path = save_analysis(st.session_state.analysis, path or st.session_state.get("current_path"))
    st.session_state.current_path = str(saved_path)
    st.toast(f"Guardado em {saved_path.name}")


def safe_json_path(filename: str) -> Path:
    name = Path(filename or "").name.strip()
    if not name.lower().endswith(".json"):
        name = f"{name}.json"
    safe_name = "".join(char if char.isalnum() or char in "-_ ." else "_" for char in name).strip()
    if not safe_name or safe_name == ".json":
        safe_name = "analise.json"
    return DATA_DIR / safe_name


def mark_analysis_replaced() -> None:
    st.session_state.criteria_revision = int(st.session_state.get("criteria_revision", 0)) + 1


def set_empty_analysis(name: str) -> None:
    analysis_name = (name or "").strip() or "Nova análise"
    st.session_state.analysis = Analysis(name=analysis_name)
    st.session_state.current_path = str(safe_json_path(f"{analysis_name}.json"))
    mark_analysis_replaced()


def open_save_dialog(post_save_action: str | None = None) -> None:
    current_name = Path(st.session_state.get("current_path", "")).name
    st.session_state.save_analysis_filename = current_name or f"{st.session_state.analysis.name}.json"
    st.session_state.post_save_action = post_save_action
    st.session_state.active_dialog = "save"


@st.dialog("Deseja Gravar a Análise Atual?")
def confirm_new_analysis_dialog() -> None:
    st.write("Antes de criar uma nova análise, escolha o que fazer com a análise atual.")
    c1, c2, c3 = st.columns(3)
    if c1.button("Sim", use_container_width=True):
        open_save_dialog("new_name")
        st.rerun()
    if c2.button("Não", use_container_width=True):
        st.session_state.active_dialog = "new_name"
        st.rerun()
    if c3.button("Cancelar", use_container_width=True):
        st.session_state.active_dialog = None
        st.rerun()


@st.dialog("Nome da Nova Análise")
def new_analysis_name_dialog() -> None:
    st.text_input("Nome da nova análise", key="new_analysis_name")
    c1, c2 = st.columns(2)
    if c1.button("Criar", use_container_width=True):
        set_empty_analysis(st.session_state.new_analysis_name)
        st.session_state.active_dialog = None
        st.toast("Nova análise criada.")
        st.rerun()
    if c2.button("Cancelar", use_container_width=True):
        st.session_state.active_dialog = None
        st.rerun()


@st.dialog("Gravar Análise")
def save_analysis_dialog() -> None:
    st.text_input("Nome do ficheiro JSON", key="save_analysis_filename")
    c1, c2 = st.columns(2)
    if c1.button("Gravar", use_container_width=True):
        target_path = safe_json_path(st.session_state.save_analysis_filename)
        rerun_save(target_path)
        post_save_action = st.session_state.get("post_save_action")
        st.session_state.post_save_action = None
        if post_save_action == "new_name":
            st.session_state.active_dialog = "new_name"
        elif post_save_action == "read_file":
            set_empty_analysis("Análise a carregar")
            st.session_state.active_dialog = "read_file"
        else:
            st.session_state.active_dialog = None
        st.rerun()
    if c2.button("Cancelar", use_container_width=True):
        st.session_state.post_save_action = None
        st.session_state.active_dialog = None
        st.rerun()


@st.dialog("Deseja Gravar a Análise Atual?")
def confirm_read_analysis_dialog() -> None:
    st.write("Antes de ler outra análise JSON, escolha o que fazer com a análise atual.")
    c1, c2, c3 = st.columns(3)
    if c1.button("Sim", use_container_width=True):
        open_save_dialog("read_file")
        st.rerun()
    if c2.button("Não", use_container_width=True):
        set_empty_analysis("Análise a carregar")
        st.session_state.active_dialog = "read_file"
        st.rerun()
    if c3.button("Cancelar", use_container_width=True):
        st.session_state.active_dialog = None
        st.rerun()


@st.dialog("Ler Análise")
def read_analysis_dialog() -> None:
    uploaded = st.file_uploader("Selecionar ficheiro JSON", type=["json"])
    c1, c2 = st.columns(2)
    if c1.button("Ler Análise", use_container_width=True):
        if uploaded is None:
            st.error("Selecione um ficheiro JSON.")
            return
        try:
            text_from_file = uploaded.getvalue().decode("utf-8")
            st.session_state.analysis = load_analysis_from_json_text(text_from_file)
            st.session_state.current_path = str(safe_json_path(uploaded.name))
            mark_analysis_replaced()
            rerun_save(st.session_state.current_path)
            st.session_state.active_dialog = None
            st.toast("Análise carregada.")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler análise: {e}")
    if c2.button("Cancelar", use_container_width=True):
        st.session_state.active_dialog = None
        st.rerun()


def render_active_dialog() -> None:
    active_dialog = st.session_state.get("active_dialog")
    if active_dialog == "confirm_new":
        confirm_new_analysis_dialog()
    elif active_dialog == "new_name":
        new_analysis_name_dialog()
    elif active_dialog == "save":
        save_analysis_dialog()
    elif active_dialog == "confirm_read":
        confirm_read_analysis_dialog()
    elif active_dialog == "read_file":
        read_analysis_dialog()


def render_sidebar():
    retail_logo = Path(__file__).resolve().parent / "logos" / "RETAILL_MCDA.png"
    if retail_logo.exists():
        st.sidebar.image(str(retail_logo), width=260)
    else:
        st.sidebar.title("RETAILL MCDA")
    st.sidebar.markdown(f"**Análise atual:** {st.session_state.analysis.name}")
    st.sidebar.divider()
    if st.sidebar.button("Nova Análise", use_container_width=True):
        st.session_state.active_dialog = "confirm_new"
        st.rerun()
    if st.sidebar.button("Ler Análise", use_container_width=True):
        st.session_state.active_dialog = "confirm_read"
        st.rerun()
    if st.sidebar.button("Gravar Análise", use_container_width=True):
        open_save_dialog()
        st.rerun()
    st.sidebar.divider()
    st.sidebar.download_button("Descarregar JSON", data=analysis_to_json(st.session_state.analysis), file_name=f"{st.session_state.analysis.name}.json", mime="application/json")
    st.sidebar.caption("Exportação completa")
    render_export_buttons()


def render_top_logos() -> None:
    logo_dir = Path(__file__).resolve().parent / "logos"
    if not logo_dir.exists():
        return

    logos = sorted(
        [path for path in logo_dir.iterdir() if "retaill_mcda" not in path.stem.lower()],
        key=lambda p: p.name,
    )
    if not logos:
        return

    html_parts = ['<div class="top-logo-bar">']
    for image in logos:
        suffix = image.suffix.lower()
        if suffix in {".png"}:
            mime = "image/png"
        elif suffix in {".jpg", ".jpeg"}:
            mime = "image/jpeg"
        elif suffix == ".svg":
            mime = "image/svg+xml"
        else:
            mime = "image/*"

        encoded = base64.b64encode(image.read_bytes()).decode("utf-8")
        html_parts.append(f'<img src="data:{mime};base64,{encoded}" alt="{image.name}" />')

    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_section_nav() -> None:
    active = int(st.query_params.get("page", st.session_state.get("active_page", 0)))
    active = min(max(active, 0), len(MENU_ITEMS) - 1)
    st.session_state.active_page = active

    html = '<div class="nav-compact">'
    for idx, label in enumerate(MENU_ITEMS):
        cls = "nav-chip active" if idx == active else "nav-chip"
        html += f'<a class="{cls}" href="?page={idx}">{idx + 1}. {label}</a>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_hero():
    analysis = st.session_state.analysis
    st.markdown(f"""
    <div class="hero">
      <div class="tag">RETAILL MCDA</div>
      <div class="hero-title">RETAILL MCDA</div>
      <div class="hero-subtitle">{analysis.description}</div>
    </div>
    """, unsafe_allow_html=True)


def render_steps(active: int = 1):
    html = '<div class="step-grid">'
    for i, name in enumerate(MENU_ITEMS, start=1):
        cls = "step-card active" if i == active else "step-card"
        html += f'<div class="{cls}"><div class="step-number">{i}</div><strong>{name}</strong></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def alternatives_dataframe(analysis):
    columns = ["Nome", "Custo", "Selecionada para 2.ª fase", "Descrição"]
    return pd.DataFrame(
        [
            {"Nome": a.name, "Custo": a.cost, "Selecionada para 2.ª fase": a.selected_for_phase2, "Descrição": a.description}
            for a in analysis.alternatives
        ],
        columns=columns,
    )


def criteria_dataframe(analysis):
    columns = ["Código", "Nome", "Fase", "Selecionado", "Peso", "Custo/Risco?", "Ordem", "Descrição"]
    return pd.DataFrame(
        [
            {"Código": c.code, "Nome": c.name, "Fase": c.phase, "Selecionado": c.selected, "Peso": c.weight, "Custo/Risco?": c.is_cost, "Ordem": c.order, "Descrição": c.description}
            for c in analysis.criteria
        ],
        columns=columns,
    )


def semantic_scores_dataframe(analysis):
    rows = []
    for alt in analysis.alternatives:
        row = {"Alternativa": alt.name}
        for c in analysis.criteria:
            row[c.code] = analysis.semantic_scores.get(alt.name, {}).get(c.code, "N")
        rows.append(row)
    return pd.DataFrame(rows)


def apply_alternatives_dataframe(df):
    st.session_state.analysis.alternatives = [
        Alternative(name=str(r["Nome"]).strip(), cost=float(r.get("Custo", 0) or 0), selected_for_phase2=bool(r.get("Selecionada para 2.ª fase", False)), description=str(r.get("Descrição", "") or ""))
        for _, r in df.iterrows() if str(r.get("Nome", "")).strip()
    ]


def sync_scores_with_structure(rename_map: dict[str, str] | None = None) -> None:
    analysis = st.session_state.analysis
    criterion_codes = [criterion.code for criterion in analysis.criteria]
    alternative_names = [alternative.name for alternative in analysis.alternatives]
    valid_levels = {scale_level.code for scale_level in SEVEN_LEVEL_SCALE}
    rename_map = rename_map or {}
    synced_semantic_scores = {}
    synced_scores = {}

    for alternative_name in alternative_names:
        synced_semantic_scores[alternative_name] = {}
        synced_scores[alternative_name] = {}
        existing_semantic = analysis.semantic_scores.get(alternative_name, {})
        existing_scores = analysis.scores.get(alternative_name, {})
        for criterion_code in criterion_codes:
            level = str(existing_semantic.get(criterion_code, "") or "")
            old_code = rename_map.get(criterion_code)
            if level not in valid_levels and old_code:
                level = str(existing_semantic.get(old_code, "") or "")
            if level not in valid_levels:
                numeric_score = existing_scores.get(criterion_code)
                if numeric_score is None and old_code:
                    numeric_score = existing_scores.get(old_code)
                level = "N" if numeric_score is None else next((scale_level.code for scale_level in SEVEN_LEVEL_SCALE if scale_level.score == numeric_score), "N")
            synced_semantic_scores[alternative_name][criterion_code] = level
            synced_scores[alternative_name][criterion_code] = level_score(level)

    analysis.semantic_scores = synced_semantic_scores
    analysis.scores = synced_scores


def apply_criteria_dataframe(df):
    def value_or_default(value, default):
        if value is None or pd.isna(value):
            return default
        return value

    existing_criteria = {criterion.code: criterion for criterion in st.session_state.analysis.criteria}
    existing_codes_by_index = [criterion.code for criterion in st.session_state.analysis.criteria]
    criteria = []
    rename_map = {}
    used_codes = set()
    for index, row in df.iterrows():
        code = str(row.get("Código", "")).strip()
        if not code or code in used_codes:
            continue
        used_codes.add(code)
        old_code = existing_codes_by_index[index] if index < len(existing_codes_by_index) else None
        existing = existing_criteria.get(code) or (existing_criteria.get(old_code) if old_code else None)
        if old_code and old_code != code and old_code in existing_criteria:
            rename_map[code] = old_code
        criteria.append(
            Criterion(
                code=code,
                name=str(row.get("Nome", "") or code).strip(),
                phase=int(value_or_default(row.get("Fase", 1), 1)),
                selected=bool(value_or_default(row.get("Selecionado", True), True)),
                weight=float(value_or_default(row.get("Peso", 1), 0)),
                is_cost=bool(value_or_default(row.get("Custo/Risco?", False), False)),
                order=int(value_or_default(row.get("Ordem", index + 1), index + 1)),
                description=str(row.get("Descrição", "") or ""),
                neutral_level=existing.neutral_level if existing else "N",
                best_level=existing.best_level if existing else "MM",
                levels=existing.levels if existing and existing.levels else SEVEN_LEVEL_SCALE,
            )
        )
    st.session_state.analysis.criteria = criteria
    sync_scores_with_structure(rename_map)
    st.session_state.criteria_revision = int(st.session_state.get("criteria_revision", 0)) + 1


def apply_semantic_scores_dataframe(df):
    semantic_scores, scores = {}, {}
    criterion_codes = [c.code for c in st.session_state.analysis.criteria]
    for _, row in df.iterrows():
        alt_name = str(row.get("Alternativa", "")).strip()
        if not alt_name:
            continue
        semantic_scores[alt_name], scores[alt_name] = {}, {}
        for code in criterion_codes:
            level = str(row.get(code, "N") or "N")
            semantic_scores[alt_name][code] = level
            scores[alt_name][code] = level_score(level)
    st.session_state.analysis.semantic_scores = semantic_scores
    st.session_state.analysis.scores = scores


def level_color(level_code):
    for level in SEVEN_LEVEL_SCALE:
        if level.code == level_code:
            return level.color
    return "#EAF4EC"


def _safe_download_name(name: str, suffix: str) -> str:
    safe_name = "".join(char if char.isalnum() or char in "-_ " else "_" for char in name).strip()
    if not safe_name:
        safe_name = "analise"
    return f"{safe_name}.{suffix}"


def evaluation_matrix_dataframe(analysis) -> pd.DataFrame:
    rows = []
    for criterion in analysis.criteria:
        row = {"Critério": criterion.code, "Nome": criterion.name, "Fase": criterion.phase}
        for alternative in analysis.alternatives:
            level = analysis.semantic_scores.get(alternative.name, {}).get(criterion.code, "N")
            row[alternative.name] = f"{level} ({level_score(level):+.0f})"
        rows.append(row)
    return pd.DataFrame(rows)


def numeric_scores_dataframe(analysis) -> pd.DataFrame:
    rows = []
    for alternative in analysis.alternatives:
        row = {"Alternativa": alternative.name}
        for criterion in analysis.criteria:
            row[criterion.code] = analysis.scores.get(alternative.name, {}).get(criterion.code, level_score(analysis.semantic_scores.get(alternative.name, {}).get(criterion.code, "N")))
        rows.append(row)
    return pd.DataFrame(rows)


def normalized_weights_dataframe(analysis, phase: int) -> pd.DataFrame:
    criteria = selected_criteria(analysis, phase)
    weights = normalize_weights(criteria)
    return pd.DataFrame(
        [
            {
                "Fase": phase,
                "Critério": criterion.code,
                "Nome": criterion.name,
                "Peso": criterion.weight,
                "Peso normalizado": weights.get(criterion.code, 0.0),
                "Peso normalizado (%)": weights.get(criterion.code, 0.0) * 100,
            }
            for criterion in criteria
        ]
    )


def analysis_export_tables(analysis) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {
        "Resumo": pd.DataFrame(
            [
                {"Campo": "Nome", "Valor": analysis.name},
                {"Campo": "Descrição", "Valor": analysis.description},
                {"Campo": "Contexto", "Valor": analysis.context},
                {"Campo": "Metodologia", "Valor": analysis.methodology},
                {"Campo": "Criado por", "Valor": analysis.created_by},
                {"Campo": "Notas", "Valor": analysis.notes},
                {"Campo": "Alternativas", "Valor": len(analysis.alternatives)},
                {"Campo": "Critérios", "Valor": len(analysis.criteria)},
            ]
        ),
        "Alternativas": alternatives_dataframe(analysis),
        "Critérios": criteria_dataframe(analysis),
        "Escala": pd.DataFrame([level.model_dump() for level in SEVEN_LEVEL_SCALE]),
        "Avaliações semânticas": semantic_scores_dataframe(analysis),
        "Avaliações numéricas": numeric_scores_dataframe(analysis),
        "Matriz avaliação": evaluation_matrix_dataframe(analysis),
    }

    for phase in (1, 2):
        tables[f"Pesos fase {phase}"] = normalized_weights_dataframe(analysis, phase)
        result = evaluate_phase(analysis, phase)
        if not result.empty:
            tables[f"Resultados fase {phase}"] = result
            tables[f"Contribuições fase {phase}"] = criterion_contributions(analysis, phase)
            tables[f"Sensibilidade fase {phase}"] = sensitivity_scenarios(analysis, phase)
            tables[f"Robustez fase {phase}"] = robustness_summary(analysis, phase)
    return tables


def build_complete_csv(analysis) -> bytes:
    chunks = []
    for name, table in analysis_export_tables(analysis).items():
        chunks.append(f"### {name}\n")
        chunks.append(table.to_csv(index=False))
        chunks.append("\n")
    return "".join(chunks).encode("utf-8-sig")


def build_complete_excel(analysis) -> bytes:
    from openpyxl.styles import Font, PatternFill

    output = BytesIO()
    tables = analysis_export_tables(analysis)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, table in tables.items():
            sheet_name = name[:31]
            table.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            for cell in worksheet[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor=DARK_BLUE.replace("#", ""))
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 42)

        matrix_sheet = writer.sheets.get("Matriz avaliação")
        if matrix_sheet is not None:
            for row in matrix_sheet.iter_rows(min_row=2, min_col=4):
                for cell in row:
                    level = str(cell.value or "N").split(" ", 1)[0]
                    color = level_color(level).replace("#", "")
                    cell.fill = PatternFill("solid", fgColor=color)
                    if level in {"MM", "M", "MP"}:
                        cell.font = Font(bold=True, color="FFFFFF")
                    else:
                        cell.font = Font(bold=True, color=DARK_BLUE.replace("#", ""))
    return output.getvalue()


def build_complete_pdf(analysis) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(A4), leftMargin=1 * cm, rightMargin=1 * cm, topMargin=1 * cm, bottomMargin=1 * cm)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"RETAILL MCDA - {analysis.name}", styles["Title"]), Spacer(1, 0.3 * cm)]

    for name, table in analysis_export_tables(analysis).items():
        if table.empty:
            continue
        story.append(Paragraph(name, styles["Heading2"]))
        printable = table.copy().astype(str)
        max_rows = 28 if name != "Matriz avaliação" else 18
        if len(printable) > max_rows:
            printable = printable.head(max_rows)
            truncated = True
        else:
            truncated = False
        data = [list(printable.columns)] + printable.values.tolist()
        pdf_table = Table(data, repeatRows=1)
        pdf_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(DARK_BLUE)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDE8E0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(pdf_table)
        if truncated:
            story.append(Paragraph("Tabela truncada no PDF. A exportação Excel contém todos os registos.", styles["Italic"]))
        story.append(PageBreak())

    if story and isinstance(story[-1], PageBreak):
        story.pop()
    doc.build(story)
    return output.getvalue()


def render_export_buttons() -> None:
    analysis = st.session_state.analysis
    st.sidebar.download_button(
        "Exportar CSV",
        data=build_complete_csv(analysis),
        file_name=_safe_download_name(analysis.name, "csv"),
        mime="text/csv",
        use_container_width=True,
    )
    st.sidebar.download_button(
        "Exportar Excel",
        data=build_complete_excel(analysis),
        file_name=_safe_download_name(analysis.name, "xlsx"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.sidebar.download_button(
        "Exportar PDF",
        data=build_complete_pdf(analysis),
        file_name=_safe_download_name(analysis.name, "pdf"),
        mime="application/pdf",
        use_container_width=True,
    )


def page_dashboard():
    analysis = st.session_state.analysis
    st.header("1. Dashboard")
    render_hero()
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card"><h4>Problema</h4><p>{analysis.context}</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><h4>Conflitos de decisão</h4><p>Preço vs. qualidade, prazo vs. variedade, sustentabilidade vs. custo e reputação vs. proximidade.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><h4>Escala</h4><p>Sete níveis semânticos de -100 a +100, com neutro e melhor como referências.</p></div>', unsafe_allow_html=True)
    st.caption("Navegação rápida e fluxo principal na barra superior.")
    st.subheader("8 etapas MMASSI/IT")
    render_steps()
    results = evaluate_phase(analysis, 1)
    if not results.empty:
        winner, value = results.iloc[0]["Alternativa"], results.iloc[0]["Valor Global"]
        st.markdown(f'<div class="winner-box">Fornecedor recomendado: {winner} — Valor Global {value:.1f}</div>', unsafe_allow_html=True)
        fig = px.bar(results.sort_values("Valor Global"), x="Valor Global", y="Alternativa", orientation="h", text="Valor Global", title="Ranking final", color_discrete_sequence=[GREEN])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color=DARK_BLUE, title_font_color=DARK_BLUE, xaxis_title="Valor global", yaxis_title="Fornecedor", height=360)
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)


def page_analysis():
    a = st.session_state.analysis
    st.header("2. Análise")
    col1, col2 = st.columns([2, 1])
    with col1:
        a.name = st.text_input("Nome da análise", a.name)
        a.description = st.text_area("Descrição", a.description, height=90)
        a.context = st.text_area("Contexto do problema", a.context, height=120)
        a.notes = st.text_area("Notas", a.notes, height=100)
    with col2:
        a.methodology = st.selectbox("Metodologia", ["1fase", "2fases", "1e2fases"], index=["1fase", "2fases", "1e2fases"].index(a.methodology))
        a.created_by = st.text_input("Responsável", a.created_by)
        st.metric("Alternativas", len(a.alternatives)); st.metric("Critérios", len(a.criteria))
    if st.button("Guardar alterações da análise"):
        rerun_save()


def page_alternatives():
    st.header("3. Fornecedores")
    df = alternatives_dataframe(st.session_state.analysis)
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Custo": st.column_config.NumberColumn("Custo", min_value=0.0, step=1000.0, format="€ %.0f")
        },
    )
    if st.button("Aplicar fornecedores"):
        apply_alternatives_dataframe(edited)
        sync_scores_with_structure()
        rerun_save(); st.rerun()


def page_criteria():
    st.header("4. Critérios & Pesos")
    st.caption("Adicione linhas para criar critérios; edite linhas existentes; apague linhas para remover critérios.")
    edited = st.data_editor(
        criteria_dataframe(st.session_state.analysis),
        key=f"criteria_editor_{st.session_state.get('criteria_revision', 0)}",
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Código": st.column_config.TextColumn("Código", help="Identificador único do critério, por exemplo A1.7."),
            "Nome": st.column_config.TextColumn("Nome"),
            "Fase": st.column_config.SelectboxColumn("Fase", options=[1, 2], default=1),
            "Selecionado": st.column_config.CheckboxColumn("Selecionado", default=True),
            "Peso": st.column_config.NumberColumn("Peso", min_value=0.0, step=1.0, default=1.0),
            "Custo/Risco?": st.column_config.CheckboxColumn("Custo/Risco?", default=False),
            "Ordem": st.column_config.NumberColumn("Ordem", min_value=0, step=1, default=0),
            "Descrição": st.column_config.TextColumn("Descrição"),
        },
    )
    if st.button("Aplicar critérios e pesos"):
        apply_criteria_dataframe(edited); rerun_save(); st.rerun()
    criteria = selected_criteria(st.session_state.analysis, 1)
    weights = normalize_weights(criteria)
    if criteria:
        weights_df = pd.DataFrame([{"Critério": c.code, "Nome": c.name, "Peso original": c.weight, "Peso normalizado (%)": round(weights[c.code] * 100, 1)} for c in criteria])
        st.dataframe(weights_df, use_container_width=True)
        fig = px.bar(weights_df, x="Peso normalizado (%)", y="Critério", orientation="h", text="Peso normalizado (%)", hover_data=["Nome"], title="Importância relativa dos critérios", color_discrete_sequence=[GREEN])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color=DARK_BLUE, height=360)
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)


def page_levels():
    st.header("5. Escala 7 Níveis")
    level_df = pd.DataFrame([{"Código": l.code, "Nível": l.name, "Pontuação": l.score} for l in SEVEN_LEVEL_SCALE])
    st.dataframe(level_df, use_container_width=True, hide_index=True)
    fig = px.bar(level_df.sort_values("Pontuação"), x="Pontuação", y="Código", orientation="h", text="Nível", title="Escala semântica de 7 níveis", color_discrete_sequence=[TEAL])
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color=DARK_BLUE, height=360)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Exemplo de referência: Calibre")
    cols = st.columns(3)
    cols[0].markdown('<div class="metric-card"><h4>Neutro (N)</h4><p>Calibre extra ≥ 70%</p></div>', unsafe_allow_html=True)
    cols[1].markdown('<div class="metric-card"><h4>Melhor (M)</h4><p>Calibre extra ≥ 85%</p></div>', unsafe_allow_html=True)
    cols[2].markdown('<div class="metric-card"><h4>Pior (P)</h4><p>Calibre extra &lt; 55%</p></div>', unsafe_allow_html=True)


def page_scores():
    st.header("6. Avaliações")
    df = semantic_scores_dataframe(st.session_state.analysis)
    level_options = [level.code for level in SEVEN_LEVEL_SCALE]
    edited = st.data_editor(
        df,
        key=f"scores_editor_{st.session_state.get('criteria_revision', 0)}",
        use_container_width=True,
        column_config={c.code: st.column_config.SelectboxColumn(f"{c.code} — {c.name}", options=level_options, help=c.description) for c in st.session_state.analysis.criteria},
        disabled=["Alternativa"],
    )
    if st.button("Aplicar avaliações"):
        apply_semantic_scores_dataframe(edited); rerun_save(); st.rerun()
    st.subheader("Matriz de avaliação colorida")
    html = '<table style="width:100%; border-collapse: collapse; background:white; box-shadow:0 8px 22px rgba(23,58,94,0.08);"><tr style="background:#173A5E;color:white;"><th style="padding:12px;text-align:left;">Critério</th>'
    for alt in st.session_state.analysis.alternatives:
        html += f'<th style="padding:12px;text-align:center;">{alt.name}</th>'
    html += '</tr>'
    for c in selected_criteria(st.session_state.analysis, 1):
        html += f'<tr><td style="padding:12px;border-bottom:1px solid #E8EFEA;"><strong>{c.code}</strong><br><span style="font-size:0.85rem;color:#466;">{c.name}</span></td>'
        for alt in st.session_state.analysis.alternatives:
            level = st.session_state.analysis.semantic_scores.get(alt.name, {}).get(c.code, "N")
            color = level_color(level)
            text_color = "white" if level in ["MM", "M", "MP"] else DARK_BLUE
            html += f'<td style="padding:12px;text-align:center;border-bottom:1px solid #E8EFEA;background:{color};color:{text_color};font-weight:800;">{level}<br><span style="font-size:0.75rem;">({level_score(level):+.0f})</span></td>'
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)


def page_results():
    st.header("7. Resultados")
    results = evaluate_all(st.session_state.analysis)
    if not results:
        st.info("Não existem critérios selecionados para calcular resultados."); return
    for phase, df in results.items():
        st.subheader(f"Fase {phase}")
        st.markdown('<div class="metric-card"><h4>Fórmula</h4><p>Valor Global = Σ (Peso normalizado do Critério × Pontuação na Escala)</p></div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        if not df.empty:
            winner, value = df.iloc[0]["Alternativa"], df.iloc[0]["Valor Global"]
            st.markdown(f'<div class="winner-box">Fornecedor recomendado: {winner} — Valor Global {value:.1f}</div>', unsafe_allow_html=True)
            fig = px.bar(df[["Alternativa", "Valor Global"]].sort_values("Valor Global"), x="Valor Global", y="Alternativa", orientation="h", text="Valor Global", title=f"Ranking final — Fase {phase}", color_discrete_sequence=[GREEN])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color=DARK_BLUE, title_font_color=DARK_BLUE, xaxis_title="Valor global", yaxis_title="Fornecedor", height=420)
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
            contrib = criterion_contributions(st.session_state.analysis, phase)
            fig2 = px.bar(contrib, x="Alternativa", y="Contribuição", color="Critério", title="Contribuição dos critérios por fornecedor")
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color=DARK_BLUE, height=420)
            st.plotly_chart(fig2, use_container_width=True)
        st.download_button(f"Descarregar resultados da fase {phase} em CSV", data=df.to_csv(index=False).encode("utf-8"), file_name=f"resultados_fase_{phase}.csv", mime="text/csv")


def page_sensitivity():
    st.header("8. Sensibilidade")
    phase = st.selectbox("Fase", [1, 2], index=0)
    sens_df = sensitivity_scenarios(st.session_state.analysis, phase)
    if sens_df.empty:
        st.info("Não existem dados suficientes para análise de sensibilidade."); return
    st.subheader("Cenários")
    st.dataframe(sens_df, use_container_width=True)
    fig = px.line(sens_df, x="Cenário", y="Valor Global", color="Alternativa", markers=True, title="Estabilidade do ranking por cenário")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color=DARK_BLUE, height=430)
    st.plotly_chart(fig, use_container_width=True)
    robust = robustness_summary(st.session_state.analysis, phase)
    st.subheader("Resumo de robustez")
    st.dataframe(robust, use_container_width=True)

    if not robust.empty and bool(robust["Mantém vencedor base?"].all()):
        base_winner = robust.iloc[0]["Vencedor"]
        st.markdown(f'<div class="winner-box">Conclusão: ranking robusto — {base_winner} mantém a recomendação nos cenários testados.</div>', unsafe_allow_html=True)
    else:
        st.warning("O ranking é sensível em pelo menos um cenário.")


def page_json():
    st.header("9. JSON")
    uploaded = st.file_uploader("Importar JSON", type=["json"])
    if uploaded is not None and st.button("Carregar ficheiro JSON"):
        try:
            text_from_file = uploaded.getvalue().decode("utf-8")
            st.session_state.analysis = load_analysis_from_json_text(text_from_file)
            rerun_save()
            st.success("JSON importado com sucesso.")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao importar JSON: {e}")
    text = st.text_area("JSON da análise", analysis_to_json(st.session_state.analysis), height=500)
    c1, c2 = st.columns(2)
    if c1.button("Validar e carregar JSON"):
        try:
            st.session_state.analysis = load_analysis_from_json_text(text); rerun_save(); st.success("JSON carregado com sucesso."); st.rerun()
        except Exception as e:
            st.error(f"Erro ao validar JSON: {e}")
    c2.download_button("Descarregar JSON atual", data=analysis_to_json(st.session_state.analysis), file_name=f"{st.session_state.analysis.name}.json", mime="application/json")


def main():
    init_state(); apply_css(); render_sidebar(); render_active_dialog()

    selected_page = int(st.query_params.get("page", st.session_state.get("active_page", 0)))
    selected_page = min(max(selected_page, 0), len(MENU_ITEMS) - 1)
    st.session_state.active_page = selected_page

    render_top_logos()
    render_section_nav()

    pages = [
        page_dashboard,
        page_analysis,
        page_alternatives,
        page_criteria,
        page_levels,
        page_scores,
        page_results,
        page_sensitivity,
    ]

    pages[selected_page]()


if __name__ == "__main__":
    main()
