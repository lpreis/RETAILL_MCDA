from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from core.models import Analysis, Alternative, Criterion, SEVEN_LEVEL_SCALE, level_score
from core.storage import DATA_DIR, analysis_to_json, list_analysis_files, load_analysis, load_analysis_from_json_text, save_analysis
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
    "JSON",
]


st.set_page_config(page_title="MMASSITI Moderno", page_icon="🍎", layout="wide")


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


def render_sidebar():
    st.sidebar.title("🍎 MMASSITI")
    st.sidebar.caption("MCDA moderno com JSON")
    files = list_analysis_files()
    labels = [p.name for p in files]
    current = Path(st.session_state.get("current_path", "")).name
    if labels:
        selected_index = labels.index(current) if current in labels else 0
        selected = st.sidebar.selectbox("Análise", labels, index=selected_index)
        if st.sidebar.button("Abrir análise"):
            selected_path = DATA_DIR / selected
            st.session_state.analysis = load_analysis(selected_path)
            st.session_state.current_path = str(selected_path)
            st.rerun()
    st.sidebar.divider()
    if st.sidebar.button("Carregar exemplo dos slides"):
        st.session_state.analysis = create_fruit_supplier_analysis()
        st.session_state.current_path = str(DATA_DIR / "fornecedores_fruta_alpha.json")
        rerun_save(st.session_state.current_path)
        st.rerun()
    if st.sidebar.button("Criar nova análise"):
        st.session_state.analysis = Analysis(name="Nova análise", criteria=create_fruit_supplier_analysis().criteria)
        st.session_state.current_path = str(DATA_DIR / "Nova análise.json")
        rerun_save(st.session_state.current_path)
        st.rerun()
    if st.sidebar.button("Guardar agora"):
        rerun_save()
    st.sidebar.divider()
    st.sidebar.download_button("Descarregar JSON", data=analysis_to_json(st.session_state.analysis), file_name=f"{st.session_state.analysis.name}.json", mime="application/json")


def render_section_nav() -> None:
    st.markdown("<div style='margin: 0 0 8px 0;'><strong>Navegação rápida</strong></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, label in enumerate(MENU_ITEMS):
        with cols[idx % 3]:
            is_active = st.session_state.get("active_page", 0) == idx
            if st.button(f"{idx + 1}. {label}", key=f"nav_{idx}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.active_page = idx
                st.rerun()


def render_hero():
    analysis = st.session_state.analysis
    st.markdown(f"""
    <div class="hero">
      <div class="tag">Modelo MCDA / MMASSI-IT</div>
      <div class="hero-title">Apoio à Decisão Multicritério</div>
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
    return pd.DataFrame([{"Nome": a.name, "Custo": a.cost, "Selecionada para 2.ª fase": a.selected_for_phase2, "Descrição": a.description} for a in analysis.alternatives])


def criteria_dataframe(analysis):
    return pd.DataFrame([{"Código": c.code, "Nome": c.name, "Fase": c.phase, "Selecionado": c.selected, "Peso": c.weight, "Custo/Risco?": c.is_cost, "Ordem": c.order, "Descrição": c.description} for c in analysis.criteria])


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


def apply_criteria_dataframe(df):
    st.session_state.analysis.criteria = [
        Criterion(code=str(r.get("Código", "")).strip(), name=str(r.get("Nome", "") or r.get("Código", "")), phase=int(r.get("Fase", 1)), selected=bool(r.get("Selecionado", True)), weight=float(r.get("Peso", 1) or 0), is_cost=bool(r.get("Custo/Risco?", False)), order=int(r.get("Ordem", 0) or 0), description=str(r.get("Descrição", "") or ""), levels=SEVEN_LEVEL_SCALE)
        for _, r in df.iterrows() if str(r.get("Código", "")).strip()
    ]


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


def page_dashboard():
    analysis = st.session_state.analysis
    st.header("1. Dashboard")
    render_hero()
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card"><h4>Problema</h4><p>{analysis.context}</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><h4>Conflitos de decisão</h4><p>Preço vs. qualidade, prazo vs. variedade, sustentabilidade vs. custo e reputação vs. proximidade.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><h4>Escala</h4><p>Sete níveis semânticos de -100 a +100, com neutro e melhor como referências.</p></div>', unsafe_allow_html=True)
    st.subheader("Fluxo do modelo")
    render_steps(active=1)
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
    render_steps(active=2)
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
    render_steps(active=3)
    df = alternatives_dataframe(st.session_state.analysis)
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, column_config={"Custo": st.column_config.NumberColumn("Custo", min_value=0.0, step=1000.0, format="€ %.0f")})
    if st.button("Aplicar fornecedores"):
        apply_alternatives_dataframe(edited)
        for alt in st.session_state.analysis.alternatives:
            st.session_state.analysis.scores.setdefault(alt.name, {})
            st.session_state.analysis.semantic_scores.setdefault(alt.name, {})
        rerun_save(); st.rerun()


def page_criteria():
    st.header("4. Critérios & Pesos")
    render_steps(active=4)
    st.caption("Pesos semelhantes aos slides: A1.1=100, A1.2=80, A1.3=60, A1.4=50, A1.5=40, A1.6=40.")
    edited = st.data_editor(criteria_dataframe(st.session_state.analysis), num_rows="dynamic", use_container_width=True, column_config={"Fase": st.column_config.SelectboxColumn("Fase", options=[1, 2]), "Selecionado": st.column_config.CheckboxColumn("Selecionado"), "Peso": st.column_config.NumberColumn("Peso", min_value=0.0, step=1.0), "Custo/Risco?": st.column_config.CheckboxColumn("Custo/Risco?")})
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
    render_steps(active=5)
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
    render_steps(active=6)
    df = semantic_scores_dataframe(st.session_state.analysis)
    level_options = [level.code for level in SEVEN_LEVEL_SCALE]
    edited = st.data_editor(df, use_container_width=True, column_config={c.code: st.column_config.SelectboxColumn(f"{c.code} — {c.name}", options=level_options, help=c.description) for c in st.session_state.analysis.criteria}, disabled=["Alternativa"])
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
    render_steps(active=7)
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
    render_steps(active=8)
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
    text = st.text_area("JSON da análise", analysis_to_json(st.session_state.analysis), height=500)
    c1, c2 = st.columns(2)
    if c1.button("Validar e carregar JSON"):
        try:
            st.session_state.analysis = load_analysis_from_json_text(text); rerun_save(); st.success("JSON carregado com sucesso."); st.rerun()
        except Exception as e:
            st.error(f"Erro ao validar JSON: {e}")
    c2.download_button("Descarregar JSON atual", data=analysis_to_json(st.session_state.analysis), file_name=f"{st.session_state.analysis.name}.json", mime="application/json")


def main():
    init_state(); apply_css(); render_sidebar()
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
        page_json,
    ]

    selected_page = st.session_state.get("active_page", 0)
    pages[selected_page]()


if __name__ == "__main__":
    main()
