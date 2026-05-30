import streamlit as st
import pandas as pd
import altair as alt
from modelo_walmart import resolver, NODOS, ARCOS_BASE, COORDS, ORIGEN, DESTINO

# ── Configuración ────────────────────────────────────────────
st.set_page_config(
    page_title="Walmart CR — Ruta Óptima",
    page_icon="🚛",
    layout="wide",
)

# ── Tema rosado oscuro ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600;700&display=swap');

*, body, .stApp { font-family: 'DM Sans', sans-serif; }
h1, h2, h3     { font-family: 'DM Serif Display', serif !important; }

.stApp                        { background-color: #1a000d; }
[data-testid="stSidebar"]     { background-color: #2a0016; }
[data-testid="stSidebar"] *   { color: #f8bbd0 !important; }

.stTabs [data-baseweb="tab-list"] { background: #2a0016; border-radius: 12px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"]      { color: #f48fb1; font-weight: 600; border-radius: 8px; }
.stTabs [aria-selected="true"]    { background: #880e4f !important; color: #fff !important; }

.stApp, .stApp p, .stApp label, .stApp span, .stApp div { color: #f8bbd0; }
h1, h2, h3 { color: #f48fb1 !important; }

[data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #f48fb1; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #f8bbd0; font-weight: 600; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #3d0022 0%, #2a0016 100%);
    border: 1px solid #880e4f; border-radius: 14px; padding: 16px 20px;
}

.stButton > button {
    background: linear-gradient(135deg, #880e4f, #c2185b);
    color: white; border: none; border-radius: 10px;
    font-weight: 700; font-size: 1rem; padding: 0.55rem 1.5rem;
    transition: all 0.2s;
}
.stButton > button:hover { background: linear-gradient(135deg, #ad1457, #e91e8c); transform: translateY(-1px); }

hr { border-color: #880e4f; opacity: 0.5; }

.stSuccess { background: #3d0022 !important; border-left: 4px solid #f48fb1 !important; color: #f8bbd0 !important; }
.stInfo    { background: #2a0016 !important; border-left: 4px solid #880e4f !important; color: #f8bbd0 !important; }
.stWarning { background: #3d0022 !important; border-left: 4px solid #f48fb1 !important; }
.stError   { background: #3d0022 !important; border-left: 4px solid #c2185b !important; }

[data-testid="stDataFrame"]   { background: #2a0016; border-radius: 10px; }
[data-testid="stDataFrame"] * { color: #f8bbd0 !important; }

div[data-testid="stDataEditor"] { background: #2a0016 !important; border-radius: 10px; }

.block-container { padding-top: 1.8rem; max-width: 1250px; }

.ruta-step {
    display: inline-flex; align-items: center; gap: 6px;
    background: #3d0022; border: 1px solid #880e4f;
    border-radius: 20px; padding: 6px 14px;
    font-weight: 600; font-size: 0.9rem; color: #f8bbd0;
    margin: 4px;
}
.ruta-arrow { color: #f48fb1; font-size: 1.1rem; margin: 0 2px; }
.ruta-tiempo { color: #f48fb1; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.title("🚛 Walmart CR — Distribución CEDI Coyol → Pérez Zeledón")
st.caption("Modelo de camino mínimo · Programación Entera Binaria · PuLP + CBC")

# ── Estado de tiempos editables ──────────────────────────────
if "tiempos" not in st.session_state:
    st.session_state["tiempos"] = ARCOS_BASE.copy()
if "resultado" not in st.session_state:
    st.session_state["resultado"] = resolver()

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🗺️ Ruta Óptima",
    "✏️ Editar Tiempos",
    "📐 Modelo Matemático",
])

# ════════════════════════════════════════════════════════════
# TAB 1 — RUTA ÓPTIMA + MAPA
# ════════════════════════════════════════════════════════════
with tab1:
    res = st.session_state["resultado"]
    ok  = res["estado"] == 1

    if not ok:
        st.error("❌ No se encontró solución factible con los tiempos actuales.")
    else:
        ruta    = res["ruta"]
        t_activ = res["tiempos"]
        activos = set(res["arcos_activos"])

        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⏱️ Tiempo total",   f"{int(res['tiempo_total'])} min",
                    f"{res['tiempo_total']/60:.1f} horas")
        col2.metric("📍 Paradas",        f"{len(ruta)} nodos")
        col3.metric("🛣️ Tramos",         f"{len(activos)}")
        col4.metric("🚦 Origen → Destino",
                    f"{NODOS[ORIGEN]} → {NODOS[DESTINO]}")

        # Ruta en pasos
        st.markdown("---")
        st.subheader("📍 Secuencia de la ruta óptima")
        pasos_html = ""
        for i, n in enumerate(ruta):
            pasos_html += f"<span class='ruta-step'>{'🏭' if n==ORIGEN else ('🏁' if n==DESTINO else '📍')} {NODOS[n]}</span>"
            if i < len(ruta) - 1:
                arco = (ruta[i], ruta[i+1])
                mins = t_activ.get(arco, "?")
                pasos_html += f"<span class='ruta-arrow'>→ <span class='ruta-tiempo'>{mins} min</span> →</span>"
        st.markdown(pasos_html, unsafe_allow_html=True)

        # ── Mapa ────────────────────────────────────────────
        st.markdown("---")
        st.subheader("🗺️ Mapa de la ruta")

        # Nodos
        df_nodos = pd.DataFrame([
            {
                "lon":    COORDS[n][0],
                "lat":    COORDS[n][1],
                "nombre": NODOS[n],
                "tipo":   "Origen" if n == ORIGEN else ("Destino" if n == DESTINO else
                          ("En ruta" if n in ruta else "No usado")),
                "orden":  ruta.index(n) + 1 if n in ruta else None,
            }
            for n in NODOS
        ])

        color_nodos = alt.Color("tipo:N", scale=alt.Scale(
            domain=["Origen", "Destino", "En ruta", "No usado"],
            range=["#f48fb1", "#e91e8c", "#f06292", "#4a0028"]
        ))
        size_nodos = alt.Size("tipo:N", scale=alt.Scale(
            domain=["Origen", "Destino", "En ruta", "No usado"],
            range=[300, 300, 180, 80]
        ))

        puntos = (
            alt.Chart(df_nodos)
            .mark_point(filled=True, stroke="#1a000d", strokeWidth=1.5)
            .encode(
                x=alt.X("lon:Q", scale=alt.Scale(domain=[-84.8, -83.5]), title="Longitud"),
                y=alt.Y("lat:Q", scale=alt.Scale(domain=[9.1, 10.15]),  title="Latitud"),
                color=color_nodos,
                size=size_nodos,
                tooltip=["nombre:N", "tipo:N"]
            )
        )

        etiquetas = (
            alt.Chart(df_nodos[df_nodos["tipo"] != "No usado"])
            .mark_text(dy=-14, fontSize=11, fontWeight="bold", color="#f8bbd0")
            .encode(
                x=alt.X("lon:Q"),
                y=alt.Y("lat:Q"),
                text="nombre:N",
            )
        )

        # Arcos — todos en gris tenue
        filas_arcos = []
        for (a, b), mins in ARCOS_BASE.items():
            filas_arcos.append({"lon": COORDS[a][0], "lat": COORDS[a][1],
                                 "arco": f"{NODOS[a]}→{NODOS[b]}", "activo": (a,b) in activos})
            filas_arcos.append({"lon": COORDS[b][0], "lat": COORDS[b][1],
                                 "arco": f"{NODOS[a]}→{NODOS[b]}", "activo": (a,b) in activos})

        df_arcos = pd.DataFrame(filas_arcos)

        lineas_inactivas = (
            alt.Chart(df_arcos[~df_arcos["activo"]])
            .mark_line(strokeWidth=1.5, opacity=0.25, color="#4a0028")
            .encode(x="lon:Q", y="lat:Q", detail="arco:N")
        )

        lineas_activas = (
            alt.Chart(df_arcos[df_arcos["activo"]])
            .mark_line(strokeWidth=4, opacity=0.95, color="#e91e8c")
            .encode(x="lon:Q", y="lat:Q", detail="arco:N",
                    tooltip=["arco:N"])
        )

        mapa = (lineas_inactivas + lineas_activas + puntos + etiquetas).properties(
            height=480,
            title=alt.TitleParams(
                text=f"Ruta óptima: {' → '.join(NODOS[n] for n in ruta)}",
                color="#f48fb1", fontSize=14
            )
        ).configure_view(
            fill="#1a000d", stroke="#880e4f", strokeWidth=1
        ).configure_axis(
            gridColor="#3d0022", labelColor="#f8bbd0", titleColor="#f8bbd0"
        ).configure_title(color="#f48fb1")

        st.altair_chart(mapa, use_container_width=True)

        # Tabla de tramos de la ruta
        st.markdown("---")
        st.subheader("📋 Detalle de tramos")
        filas_detalle = []
        for i in range(len(ruta) - 1):
            arco = (ruta[i], ruta[i+1])
            base = ARCOS_BASE.get(arco, "—")
            actual = t_activ.get(arco, "—")
            filas_detalle.append({
                "Tramo":            f"{NODOS[ruta[i]]} → {NODOS[ruta[i+1]]}",
                "Tiempo base (min)": base,
                "Tiempo actual (min)": actual,
                "Cambio":           f"+{actual-base} min" if isinstance(actual,int) and isinstance(base,int) and actual!=base else ("—" if actual==base else ""),
            })
        filas_detalle.append({
            "Tramo": "TOTAL",
            "Tiempo base (min)": sum(ARCOS_BASE[a] for a in activos if a in ARCOS_BASE),
            "Tiempo actual (min)": int(res["tiempo_total"]),
            "Cambio": "",
        })
        st.dataframe(pd.DataFrame(filas_detalle), use_container_width=True, hide_index=True)

        # Comparar todas las rutas posibles
        st.markdown("---")
        st.subheader("🔀 Comparación de todas las rutas")

        rutas_conocidas = [
            [1, 2, 4, 5, 7, 13],
            [1, 2, 4, 6, 7, 13],
            [1, 3, 4, 5, 7, 13],
            [1, 3, 4, 6, 7, 13],
            [1, 8, 9, 10, 11, 12, 13],
        ]

        filas_comp = []
        for ruta_c in rutas_conocidas:
            arcos_r = [(ruta_c[i], ruta_c[i+1]) for i in range(len(ruta_c)-1)]
            if all(a in t_activ for a in arcos_r):
                tiempo_r = sum(t_activ[a] for a in arcos_r)
                filas_comp.append({
                    "Ruta": " → ".join(NODOS[n] for n in ruta_c),
                    "Tiempo (min)": tiempo_r,
                    "Óptima": "✅" if ruta_c == ruta else "",
                })

        df_comp = pd.DataFrame(filas_comp).sort_values("Tiempo (min)")
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — EDITAR TIEMPOS
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("✏️ Modificar tiempos de los arcos")
    st.markdown(
        "Editá los tiempos directamente en la tabla. "
        "Luego presioná **Resolver** para encontrar la nueva ruta óptima."
    )

    tiempos_actuales = st.session_state["tiempos"]

    # Construir tabla editable
    df_edit = pd.DataFrame([
        {
            "Arco":              f"{NODOS[a]} → {NODOS[b]}",
            "Desde":             a,
            "Hasta":             b,
            "Tiempo (min)":      tiempos_actuales.get((a, b), ARCOS_BASE[(a, b)]),
            "Tiempo base (min)": ARCOS_BASE[(a, b)],
        }
        for (a, b) in ARCOS_BASE
    ])

    editado = st.data_editor(
        df_edit[["Arco", "Tiempo (min)", "Tiempo base (min)"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Arco":              st.column_config.TextColumn("Arco", disabled=True),
            "Tiempo (min)":      st.column_config.NumberColumn("⏱️ Tiempo (min)", min_value=1, max_value=999, step=1),
            "Tiempo base (min)": st.column_config.NumberColumn("📌 Base original", disabled=True),
        },
        key="editor_tiempos"
    )

    col_btn1, col_btn2, _ = st.columns([1.2, 1.2, 3])
    resolver_btn   = col_btn1.button("🚀 Resolver con nuevos tiempos", use_container_width=True)
    restaurar_btn  = col_btn2.button("↩️ Restaurar tiempos originales", use_container_width=True)

    if restaurar_btn:
        st.session_state["tiempos"]    = ARCOS_BASE.copy()
        st.session_state["resultado"]  = resolver()
        st.success("✅ Tiempos restaurados a los valores originales.")
        st.rerun()

    if resolver_btn:
        claves = list(ARCOS_BASE.keys())
        nuevos = {}
        for i, (a, b) in enumerate(claves):
            nuevos[(a, b)] = int(editado.iloc[i]["Tiempo (min)"])
        st.session_state["tiempos"]   = nuevos
        st.session_state["resultado"] = resolver(nuevos)
        res_nuevo = st.session_state["resultado"]
        if res_nuevo["estado"] == 1:
            ruta_nueva = res_nuevo["ruta"]
            st.success(
                f"✅ Nueva ruta óptima: **{' → '.join(NODOS[n] for n in ruta_nueva)}** "
                f"— **{int(res_nuevo['tiempo_total'])} minutos**"
            )
        else:
            st.error("❌ No se encontró solución factible.")
        st.rerun()

    st.markdown("---")
    st.subheader("📊 Comparación base vs actual")
    df_cmp = pd.DataFrame([
        {
            "Arco":              f"{NODOS[a]} → {NODOS[b]}",
            "Base (min)":        ARCOS_BASE[(a, b)],
            "Actual (min)":      tiempos_actuales.get((a, b), ARCOS_BASE[(a, b)]),
            "Diferencia":        tiempos_actuales.get((a, b), ARCOS_BASE[(a, b)]) - ARCOS_BASE[(a, b)],
        }
        for (a, b) in ARCOS_BASE
    ])
    df_cmp["Diferencia"] = df_cmp["Diferencia"].apply(
        lambda d: f"+{d} min" if d > 0 else (f"{d} min" if d < 0 else "—")
    )
    st.dataframe(df_cmp, use_container_width=True, hide_index=True)

    # Mini bar chart de diferencias
    df_bar = pd.DataFrame([
        {
            "Arco": f"{NODOS[a]}→{NODOS[b]}",
            "Δ min": tiempos_actuales.get((a,b), ARCOS_BASE[(a,b)]) - ARCOS_BASE[(a,b)],
        }
        for (a,b) in ARCOS_BASE
    ])
    bar = (
        alt.Chart(df_bar)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Arco:N", axis=alt.Axis(labelAngle=-35), title=None),
            y=alt.Y("Δ min:Q", title="Cambio vs base (min)"),
            color=alt.condition(
                alt.datum["Δ min"] > 0,
                alt.value("#c2185b"),
                alt.value("#f48fb1")
            ),
            tooltip=["Arco:N", "Δ min:Q"]
        )
        .properties(height=260, title="Cambios respecto al tiempo base")
    )
    st.altair_chart(bar, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — MODELO MATEMÁTICO
# ════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📐 Formulación del Modelo de Camino Mínimo")
    st.markdown("---")

    col_m, col_d = st.columns([1, 1], gap="large")

    with col_m:
        st.markdown("### Conjuntos")
        st.markdown("""
- $N$ = conjunto de nodos (ciudades/bodegas) = {1, 2, …, 13}  
- $A$ = conjunto de arcos (rutas disponibles) = 15 arcos
""")

        st.markdown("### Variables de decisión")
        st.latex(r"x_{ij} \in \{0,1\} \quad \forall\,(i,j) \in A")
        st.markdown("$x_{ij} = 1$ si el arco $(i,j)$ forma parte de la ruta óptima.")

        st.markdown("### Función objetivo")
        st.markdown("Minimizar el tiempo total de recorrido:")
        st.latex(r"\min Z = \sum_{(i,j) \in A} t_{ij} \cdot x_{ij}")

        st.markdown("### Restricciones de flujo")
        st.latex(r"""
\sum_{j:(i,j)\in A} x_{ij} - \sum_{j:(j,i)\in A} x_{ji} =
\begin{cases}
 1  & \text{si } i = \text{CEDI Coyol (origen)} \\
-1  & \text{si } i = \text{Pérez Zeledón (destino)} \\
 0  & \text{en caso contrario}
\end{cases}
""")
        st.markdown("**R2 — Integralidad:**")
        st.latex(r"x_{ij} \in \{0,1\} \quad \forall\,(i,j) \in A")

        st.markdown("---")
        st.markdown("### Modelo completo")
        st.latex(r"""
\min Z = \sum_{(i,j) \in A} t_{ij} \cdot x_{ij}
\\[6pt]
\text{s.a.: flujo en cada nodo} = \{1, 0, -1\}
\\
x_{ij} \in \{0,1\}
""")

    with col_d:
        st.markdown("### Red de nodos y arcos")
        df_arcos_mod = pd.DataFrame([
            {
                "Arco":          f"{a} → {b}",
                "Desde":         f"{a}. {NODOS[a]}",
                "Hasta":         f"{b}. {NODOS[b]}",
                "Tiempo (min)":  t,
            }
            for (a, b), t in ARCOS_BASE.items()
        ])
        st.dataframe(df_arcos_mod, use_container_width=True, hide_index=True)

        res_m = st.session_state["resultado"]
        if res_m["estado"] == 1:
            st.markdown("---")
            st.markdown("### ✅ Solución actual")
            ruta_m = res_m["ruta"]
            arcos_m = [(ruta_m[i], ruta_m[i+1]) for i in range(len(ruta_m)-1)]
            terminos = " + ".join(
                str(res_m["tiempos"].get(a, "?")) for a in arcos_m
            )
            st.latex(
                rf"Z = {terminos} = {int(res_m['tiempo_total'])}\text{{ min}}"
            )
            st.markdown("**Variables activas ($x_{{ij}} = 1$):**")
            for (a, b) in arcos_m:
                st.markdown(f"- $x_{{{a},{b}}}$ = 1 &nbsp;·&nbsp; {NODOS[a]} → {NODOS[b]}: {res_m['tiempos'].get((a,b),'?')} min")
