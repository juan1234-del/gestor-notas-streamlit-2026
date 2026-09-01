"""
Gestor Académico de Notas - Aplicación Principal
Interfaz Streamlit para gestión de asignaturas, cortes y actividades
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional
import database as db
import utils as utils


# ============ CONFIGURACIÓN INICIAL ============

st.set_page_config(
    page_title="Gestor Académico de Notas",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar base de datos
db.init_database()

# Inicializar sesión
if "asignatura_seleccionada" not in st.session_state:
    st.session_state.asignatura_seleccionada = None


# ============ FUNCIONES AUXILIARES ============

def obtener_nombres_asignaturas_existentes():
    """Obtiene nombres de asignaturas existentes (para validación)"""
    asignaturas = db.obtener_asignaturas()
    return [a["nombre"] for a in asignaturas]


def obtener_nombres_actividades_corte(corte_id):
    """Obtiene nombres de actividades de un corte (para validación)"""
    actividades = db.obtener_actividades(corte_id)
    return [a["nombre"] for a in actividades]


# ============ BARRA LATERAL - NAVEGACIÓN ============

st.sidebar.markdown("# 📚 Gestor de Notas")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegación",
    ["Dashboard", "Asignaturas", "Cortes y Porcentajes", "Actividades y Notas", "Configuración"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Asignatura actual:**")
if st.session_state.asignatura_seleccionada:
    asig = db.obtener_asignatura(st.session_state.asignatura_seleccionada)
    if asig:
        st.sidebar.info(f"✓ {asig['nombre']}")
    else:
        st.sidebar.warning("Asignatura no encontrada")
        st.session_state.asignatura_seleccionada = None
else:
    st.sidebar.warning("Sin asignatura seleccionada")


# ============ PÁGINA: DASHBOARD ============

if pagina == "Dashboard":
    st.markdown("# 📊 Dashboard")
    st.markdown("Resumen general de tu desempeño académico")
    st.markdown("---")
    
    # Obtener todas las asignaturas con datos
    asignaturas = db.obtener_todas_asignaturas_con_datos()
    
    if not asignaturas:
        st.info("📌 No hay asignaturas creadas. Ve a la sección 'Asignaturas' para crear una.")
    else:
        # Calcular promedio general
        promedio = utils.calcular_promedio_general(asignaturas)
        
        # Tarjeta de promedio general
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="📈 Promedio General",
                value=f"{promedio:.2f}",
                delta=f"sobre 5.0",
                delta_color="off"
            )
        
        with col2:
            total_asignaturas = len(asignaturas)
            asig_con_notas = sum(
                1 for a in asignaturas
                if utils.obtener_estado_nota_asignatura(a)["nota_acumulada"] > 0
            )
            st.metric(
                label="📚 Asignaturas",
                value=f"{asig_con_notas}/{total_asignaturas}",
                delta="con notas registradas",
                delta_color="off"
            )
        
        with col3:
            st.metric(
                label="✅ Completadas",
                value=f"{sum(1 for a in asignaturas if utils.obtener_estado_nota_asignatura(a)['completada'])}",
                delta="evaluación ≥95%",
                delta_color="off"
            )
        
        st.markdown("---")
        
        # Resumen por asignatura
        st.subheader("📋 Resumen por Asignatura")
        
        datos_tabla = []
        for asig in asignaturas:
            estado = utils.obtener_estado_nota_asignatura(asig)
            datos_tabla.append({
                "Asignatura": asig["nombre"],
                "Acumulada": f"{estado['nota_acumulada']:.2f}",
                "Evaluado": f"{estado['porcentaje_evaluado']:.1f}%",
                "Final": f"{estado['nota_final']:.2f}" if estado['nota_final'] else "-",
                "Estado": "✅ Completa" if estado['completada'] else "⏳ En curso"
            })
        
        df = pd.DataFrame(datos_tabla)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Gráfico de barras
        st.subheader("📊 Gráfico de Notas Acumuladas")
        
        nombres = [a["nombre"] for a in asignaturas]
        notas = [utils.obtener_estado_nota_asignatura(a)["nota_acumulada"] for a in asignaturas]
        
        fig = go.Figure(data=[
            go.Bar(
                x=nombres,
                y=notas,
                marker=dict(color=notas, colorscale='Blues', showscale=True),
                text=[f"{n:.2f}" for n in notas],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Nota: %{y:.2f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Desempeño por Asignatura",
            xaxis_title="Asignatura",
            yaxis_title="Nota Acumulada (0-5)",
            height=400,
            showlegend=False,
            yaxis=dict(range=[0, 5])
        )
        
        st.plotly_chart(fig, use_container_width=True)


# ============ PÁGINA: ASIGNATURAS ============

elif pagina == "Asignaturas":
    st.markdown("# 📚 Asignaturas")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    # Crear nueva asignatura
    with col1:
        st.subheader("➕ Crear Nueva Asignatura")
        nombre_nuevo = st.text_input(
            "Nombre de la asignatura",
            placeholder="Ej: Matemáticas, Inglés, Biología",
            key="input_nueva_asignatura"
        )
        
        if st.button("Crear Asignatura", key="btn_crear_asignatura", use_container_width=True):
            # Validar nombre
            nombres_existentes = obtener_nombres_asignaturas_existentes()
            es_válido, mensaje = utils.validar_nombre(nombre_nuevo, nombres_existentes)
            
            if es_válido:
                if db.crear_asignatura(nombre_nuevo):
                    st.success(f"✅ Asignatura '{nombre_nuevo}' creada correctamente")
                    st.rerun()
                else:
                    st.error("❌ Error al crear la asignatura")
            else:
                st.error(f"❌ {mensaje}")
    
    # Seleccionar asignatura existente
    with col2:
        st.subheader("🔍 Seleccionar Asignatura")
        asignaturas = db.obtener_asignaturas()
        
        if asignaturas:
            nombres = [f"{a['nombre']}" for a in asignaturas]
            indice_actual = 0
            
            if st.session_state.asignatura_seleccionada:
                try:
                    indice_actual = next(
                        i for i, a in enumerate(asignaturas)
                        if a["id"] == st.session_state.asignatura_seleccionada
                    )
                except StopIteration:
                    pass
            
            seleccion = st.selectbox(
                "Selecciona una asignatura",
                range(len(asignaturas)),
                format_func=lambda x: nombres[x],
                index=indice_actual,
                key="select_asignatura"
            )
            
            st.session_state.asignatura_seleccionada = asignaturas[seleccion]["id"]
            st.success(f"✓ Asignatura seleccionada: {asignaturas[seleccion]['nombre']}")
        else:
            st.info("No hay asignaturas creadas")
    
    st.markdown("---")
    
    # Listado de asignaturas
    st.subheader("📋 Asignaturas Registradas")
    asignaturas = db.obtener_asignaturas()
    
    if asignaturas:
        for asig in asignaturas:
            col_nombre, col_accion = st.columns([4, 1])
            
            with col_nombre:
                st.write(f"**{asig['nombre']}** (ID: {asig['id']})")
            
            with col_accion:
                if st.button("🗑️ Eliminar", key=f"btn_eliminar_asig_{asig['id']}", use_container_width=True):
                    if db.eliminar_asignatura(asig["id"]):
                        if st.session_state.asignatura_seleccionada == asig["id"]:
                            st.session_state.asignatura_seleccionada = None
                        st.success("✅ Asignatura eliminada")
                        st.rerun()
    else:
        st.info("No hay asignaturas registradas")


# ============ PÁGINA: CORTES Y PORCENTAJES ============

elif pagina == "Cortes y Porcentajes":
    st.markdown("# 📊 Cortes y Porcentajes")
    st.markdown("---")
    
    if not st.session_state.asignatura_seleccionada:
        st.warning("⚠️ Debes seleccionar una asignatura primero")
    else:
        asig = db.obtener_asignatura(st.session_state.asignatura_seleccionada)
        st.markdown(f"### Asignatura: **{asig['nombre']}**")
        
        # Obtener cortes
        cortes = db.obtener_cortes(st.session_state.asignatura_seleccionada)
        
        st.subheader("⚙️ Configurar Porcentajes")
        st.markdown("La suma de los tres cortes debe ser exactamente **100%**")
        
        col1, col2, col3 = st.columns(3)
        
        porcentajes = []
        for i, corte in enumerate(cortes):
            with [col1, col2, col3][i]:
                st.markdown(f"#### Corte {corte['numero']}")
                porcentaje = st.number_input(
                    f"Porcentaje Corte {corte['numero']}",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(corte["porcentaje"]),
                    step=0.1,
                    label_visibility="collapsed",
                    key=f"input_porcentaje_corte_{corte['id']}"
                )
                porcentajes.append((corte["id"], porcentaje))
        
        if st.button("💾 Guardar Porcentajes", use_container_width=True, key="btn_guardar_porcentajes"):
            porcentajes_valores = [p[1] for p in porcentajes]
            es_válido, mensaje = utils.validar_guardar_corte(cortes, porcentajes_valores)
            
            if es_válido:
                for corte_id, porcentaje in porcentajes:
                    db.actualizar_porcentaje_corte(corte_id, porcentaje)
                st.success("✅ Porcentajes guardados correctamente")
                st.rerun()
            else:
                st.error(f"❌ {mensaje}")
        
        st.markdown("---")
        
        # Mostrar estado actual
        st.subheader("📈 Estado Actual")
        
        datos_cortes = []
        suma_total = 0
        for corte in cortes:
            actividades = db.obtener_actividades(corte["id"])
            nota_corte = utils.calcular_nota_corte(actividades)
            porcentaje_eval = utils.calcular_porcentaje_evaluado_corte(actividades)
            aporte = utils.calcular_aporte_corte(nota_corte, corte["porcentaje"])
            suma_total += aporte
            
            datos_cortes.append({
                "Corte": f"Corte {corte['numero']}",
                "Porcentaje": f"{corte['porcentaje']:.2f}%",
                "Nota Corte": f"{nota_corte:.2f}",
                "Evaluado": f"{porcentaje_eval:.1f}%",
                "Aporte": f"{aporte:.2f}"
            })
        
        df = pd.DataFrame(datos_cortes)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.metric(
            label="Nota Acumulada",
            value=f"{suma_total:.2f}",
            delta="sobre 5.0",
            delta_color="off"
        )


# ============ PÁGINA: ACTIVIDADES Y NOTAS ============

elif pagina == "Actividades y Notas":
    st.markdown("# 📝 Actividades y Notas")
    st.markdown("---")
    
    if not st.session_state.asignatura_seleccionada:
        st.warning("⚠️ Debes seleccionar una asignatura primero")
    else:
        asig = db.obtener_asignatura(st.session_state.asignatura_seleccionada)
        st.markdown(f"### Asignatura: **{asig['nombre']}**")
        
        # Obtener cortes
        cortes = db.obtener_cortes(st.session_state.asignatura_seleccionada)
        
        # Tabs para cada corte
        tabs = st.tabs([f"Corte {c['numero']}" for c in cortes])
        
        for tab_idx, (tab, corte) in enumerate(zip(tabs, cortes)):
            with tab:
                actividades = db.obtener_actividades(corte["id"])
                
                st.markdown(f"#### Corte {corte['numero']} (Peso: {corte['porcentaje']}%)")
                
                # Formulario para agregar actividad
                with st.expander("➕ Agregar Nueva Actividad", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nombre_act = st.text_input(
                            "Nombre de la actividad",
                            placeholder="Ej: Quiz, Tarea, Examen",
                            key=f"input_nombre_act_corte_{corte['id']}"
                        )
                    
                    with col2:
                        porcentaje_act = st.number_input(
                            "Porcentaje en el corte",
                            min_value=0.0,
                            max_value=100.0,
                            value=0.0,
                            step=0.1,
                            key=f"input_porcent_act_corte_{corte['id']}"
                        )
                    
                    with col3:
                        st.write("")  # Espacio
                        if st.button("Agregar", key=f"btn_agregar_act_corte_{corte['id']}", use_container_width=True):
                            # Validar
                            actividades_existentes = [a for a in actividades]
                            es_válido, mensaje = utils.validar_guardar_actividad(
                                actividades_existentes, nombre_act, porcentaje_act
                            )
                            
                            if es_válido:
                                if db.crear_actividad(corte["id"], nombre_act, porcentaje_act):
                                    st.success("✅ Actividad agregada")
                                    st.rerun()
                                else:
                                    st.error("❌ Error al agregar actividad")
                            else:
                                st.error(f"❌ {mensaje}")
                
                st.markdown("---")
                
                # Tabla de actividades
                if actividades:
                    st.markdown("#### 📋 Actividades Registradas")
                    
                    for act in actividades:
                        with st.container(border=True):
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{act['nombre']}**")
                                st.caption(f"Porcentaje: {act['porcentaje']:.2f}%")
                            
                            with col2:
                                nota_actual = act["nota"] if act["nota"] is not None else None
                                nueva_nota = st.number_input(
                                    "Nota",
                                    min_value=0.0,
                                    max_value=5.0,
                                    value=float(nota_actual) if nota_actual else 0.0,
                                    step=0.1,
                                    label_visibility="collapsed",
                                    key=f"input_nota_act_{act['id']}"
                                )
                                
                                if st.button("Guardar", key=f"btn_guardar_nota_{act['id']}", use_container_width=True):
                                    if db.actualizar_nota_actividad(act["id"], nueva_nota):
                                        st.success("✅ Nota guardada")
                                        st.rerun()
                            
                            with col3:
                                nombre_edit = st.text_input(
                                    "Nombre",
                                    value=act["nombre"],
                                    label_visibility="collapsed",
                                    key=f"input_edit_nombre_{act['id']}"
                                )
                                
                                if st.button("Editar", key=f"btn_editar_act_{act['id']}", use_container_width=True):
                                    porcentaje_act = act["porcentaje"]
                                    if db.actualizar_actividad(act["id"], nombre_edit, porcentaje_act):
                                        st.success("✅ Actividad actualizada")
                                        st.rerun()
                            
                            with col4:
                                if st.button("🗑️", key=f"btn_eliminar_act_{act['id']}", use_container_width=True):
                                    if db.eliminar_actividad(act["id"]):
                                        st.success("✅ Actividad eliminada")
                                        st.rerun()
                    
                    st.markdown("---")
                    
                    # Resumen del corte
                    nota_corte = utils.calcular_nota_corte(actividades)
                    porcentaje_eval = utils.calcular_porcentaje_evaluado_corte(actividades)
                    suma_porcent = sum(a["porcentaje"] for a in actividades)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Nota del Corte", f"{nota_corte:.2f}", delta="sobre 5.0", delta_color="off")
                    with col2:
                        st.metric("Evaluado", f"{porcentaje_eval:.1f}%")
                    with col3:
                        st.metric("% Actividades", f"{suma_porcent:.2f}%")
                    with col4:
                        aporte = utils.calcular_aporte_corte(nota_corte, corte["porcentaje"])
                        st.metric("Aporte", f"{aporte:.2f}")
                
                else:
                    st.info("Sin actividades registradas en este corte")


# ============ PÁGINA: CONFIGURACIÓN ============

elif pagina == "Configuración":
    st.markdown("# ⚙️ Configuración")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Herramientas")
        
        if st.button("🗑️ Limpiar Caché", use_container_width=True, key="btn_limpiar_cache"):
            st.cache_data.clear()
            st.success("✅ Caché limpiado")
        
        if st.button("📥 Exportar Datos a CSV", use_container_width=True, key="btn_exportar_csv"):
            asignaturas = db.obtener_todas_asignaturas_con_datos()
            
            datos_export = []
            for asig in asignaturas:
                for corte in asig.get("cortes", []):
                    for act in corte.get("actividades", []):
                        datos_export.append({
                            "Asignatura": asig["nombre"],
                            "Corte": corte["numero"],
                            "% Corte": corte["porcentaje"],
                            "Actividad": act["nombre"],
                            "% Actividad": act["porcentaje"],
                            "Nota": act["nota"] if act["nota"] else ""
                        })
            
            if datos_export:
                df_export = pd.DataFrame(datos_export)
                csv = df_export.to_csv(index=False)
                st.download_button(
                    "📥 Descargar CSV",
                    csv,
                    "notas_academicas.csv",
                    "text/csv"
                )
            else:
                st.info("No hay datos para exportar")
    
    with col2:
        st.subheader("ℹ️ Información")
        st.markdown("""
        **Gestor Académico de Notas**
        
        - Versión: 1.0
        - Base de datos: SQLite
        - Framework: Streamlit
        
        **Características:**
        - 3 Cortes por asignatura
        - Actividades ilimitadas
        - Cálculos automáticos
        - Persistencia local
        """)
    
    st.markdown("---")
    st.subheader("📊 Estadísticas Generales")
    
    asignaturas = db.obtener_asignaturas()
    total_actividades = 0
    for asig in asignaturas:
        cortes = db.obtener_cortes(asig["id"])
        for corte in cortes:
            total_actividades += len(db.obtener_actividades(corte["id"]))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Asignaturas", len(asignaturas))
    with col2:
        st.metric("Cortes", len(asignaturas) * 3 if asignaturas else 0)
    with col3:
        st.metric("Actividades", total_actividades)


# ============ FOOTER ============

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; font-size: 12px; color: gray;'>
    Gestor Académico de Notas v1.0<br>
    Desarrollado con ❤️
    </div>
    """,
    unsafe_allow_html=True
)
