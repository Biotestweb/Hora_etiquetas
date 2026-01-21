"""
Aplicación Streamlit - Agregar Horas a Rótulos PDF
VERSIÓN CON CALIBRACIÓN EN TIEMPO REAL
"""
import streamlit as st
from pathlib import Path
import pymupdf  # PyMuPDF (antes era "import fitz")
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(
    page_title="PDF Rótulos - Sistema de Horas",
    page_icon="🏷️",
    layout="wide"
)

# ============================================================
# COORDENADAS PARA CADA POSICIÓN (R01-R12)
# ============================================================
COORDENADAS_DEFAULT = {
    1:  {'he_x': 0.175, 'hv_x': 0.320, 'y': 0.145},  # R01 - Fila 1, Izquierda
    2:  {'he_x': 0.595, 'hv_x': 0.735, 'y': 0.145},  # R02 - Fila 1, Derecha
    3:  {'he_x': 0.175, 'hv_x': 0.320, 'y': 0.295},  # R03 - Fila 2, Izquierda
    4:  {'he_x': 0.595, 'hv_x': 0.735, 'y': 0.295},  # R04 - Fila 2, Derecha
    5:  {'he_x': 0.175, 'hv_x': 0.320, 'y': 0.440},  # R05 - Fila 3, Izquierda
    6:  {'he_x': 0.595, 'hv_x': 0.735, 'y': 0.440},  # R06 - Fila 3, Derecha
    7:  {'he_x': 0.175, 'hv_x': 0.320, 'y': 0.585},  # R07 - Fila 4, Izquierda
    8:  {'he_x': 0.595, 'hv_x': 0.735, 'y': 0.585},  # R08 - Fila 4, Derecha
    9:  {'he_x': 0.175, 'hv_x': 0.320, 'y': 0.735},  # R09 - Fila 5, Izquierda
    10: {'he_x': 0.595, 'hv_x': 0.735, 'y': 0.735},  # R10 - Fila 5, Derecha
    11: {'he_x': 0.175, 'hv_x': 0.320, 'y': 0.880},  # R11 - Fila 6, Izquierda
    12: {'he_x': 0.595, 'hv_x': 0.735, 'y': 0.880},  # R12 - Fila 6, Derecha
}


def dividir_pdf_en_rotulos(pdf_path, columnas=2, filas=6, dpi=200):
    """Divide el PDF en imágenes de rótulos individuales para preview"""
    try:
        imagenes = convert_from_path(pdf_path, dpi=dpi)
    except Exception as e:
        st.error(f"❌ Error al convertir PDF: {e}")
        return None

    rotulos = []

    for num_pagina, imagen in enumerate(imagenes, 1):
        ancho_img, alto_img = imagen.size
        margen_pie = int(alto_img * 0.05)
        alto_util = alto_img - margen_pie
        ancho_rotulo = ancho_img // columnas
        alto_rotulo = alto_util // filas

        for fila in range(filas):
            for col in range(columnas):
                x1 = col * ancho_rotulo
                y1 = fila * alto_rotulo
                x2 = x1 + ancho_rotulo
                y2 = y1 + alto_rotulo

                margen = 5
                try:
                    rotulo_img = imagen.crop((
                        max(0, x1 + margen),
                        max(0, y1 + margen),
                        min(ancho_img, x2 - margen),
                        min(alto_util, y2 - margen)
                    ))
                except:
                    continue

                posicion = (fila * columnas) + col + 1

                rotulos.append({
                    'id': f"P{num_pagina}_R{posicion:02d}",
                    'pagina': num_pagina,
                    'posicion': posicion,
                    'fila': fila + 1,
                    'columna': col + 1,
                    'imagen': rotulo_img,
                    'hora': ''
                })

    return rotulos, imagenes


def obtener_coordenadas(rotulo, calibraciones):
    """Obtiene coordenadas para un rótulo (calibradas o default)"""
    rotulo_id = rotulo['id']
    
    if rotulo_id in calibraciones:
        cal = calibraciones[rotulo_id]
        return cal['he_x'], cal['hv_x'], cal['y']
    
    posicion = rotulo['posicion']
    posicion_mod = ((posicion - 1) % 12) + 1
    
    coords = COORDENADAS_DEFAULT.get(posicion_mod, {'he_x': 0.17, 'hv_x': 0.31, 'y': 0.5})
    return coords['he_x'], coords['hv_x'], coords['y']


def obtener_coordenadas_por_posicion(posicion, calibraciones, rotulos):
    """Obtiene coordenadas para una posición específica"""
    # Buscar si hay calibración guardada para esta posición
    for r in rotulos:
        r_pos = ((r['posicion'] - 1) % 12) + 1
        if r_pos == posicion and r['id'] in calibraciones:
            cal = calibraciones[r['id']]
            return cal['he_x'], cal['hv_x'], cal['y']
    
    # Si no hay calibración, usar default
    coords = COORDENADAS_DEFAULT.get(posicion, {'he_x': 0.17, 'hv_x': 0.31, 'y': 0.5})
    return coords['he_x'], coords['hv_x'], coords['y']


def dibujar_preview_pagina(imagen, rotulos_pagina, calibraciones):
    """Dibuja preview de página con horas en ROJO"""
    img_preview = imagen.copy()
    draw = ImageDraw.Draw(img_preview)
    
    ancho_img, alto_img = img_preview.size

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(alto_img * 0.012))
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()

    for rotulo in rotulos_pagina:
        hora = rotulo.get('hora', '')
        if not hora:
            continue
        
        he_x, hv_x, y = obtener_coordenadas(rotulo, calibraciones)
        
        px_he = int(ancho_img * he_x)
        px_hv = int(ancho_img * hv_x)
        px_y = int(alto_img * y)
        
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            draw.text((px_he+dx, px_y+dy), hora, fill='black', font=font)
            draw.text((px_hv+dx, px_y+dy), hora, fill='black', font=font)
        
        draw.text((px_he, px_y), hora, fill='red', font=font)
        draw.text((px_hv, px_y), hora, fill='red', font=font)

    return img_preview


def dibujar_preview_calibracion(imagen, posicion_seleccionada, he_x, hv_x, y, rotulos_pagina, calibraciones):
    """
    Dibuja preview de página completa para calibración.
    Muestra la posición seleccionada en AZUL y las demás en ROJO.
    Incluye guías visuales y marcadores.
    """
    img_preview = imagen.copy()
    draw = ImageDraw.Draw(img_preview)
    
    ancho_img, alto_img = img_preview.size

    # Cargar fuente
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(alto_img * 0.014))
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(alto_img * 0.010))
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
            font_small = font

    # Dibujar todas las posiciones con sus horas
    for rotulo in rotulos_pagina:
        hora = rotulo.get('hora', '00:00')
        if not hora:
            hora = "00:00"
        
        pos = ((rotulo['posicion'] - 1) % 12) + 1
        
        if pos == posicion_seleccionada:
            # Posición seleccionada: usar coordenadas de los sliders
            curr_he_x, curr_hv_x, curr_y = he_x, hv_x, y
            color_principal = '#0066FF'  # Azul brillante
            color_borde = 'white'
        else:
            # Otras posiciones: usar coordenadas guardadas o default
            curr_he_x, curr_hv_x, curr_y = obtener_coordenadas(rotulo, calibraciones)
            color_principal = '#FF3333'  # Rojo
            color_borde = 'black'
        
        px_he = int(ancho_img * curr_he_x)
        px_hv = int(ancho_img * curr_hv_x)
        px_y = int(alto_img * curr_y)
        
        # Dibujar texto con borde
        for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (-2,0), (2,0), (0,-2), (0,2)]:
            draw.text((px_he+dx, px_y+dy), hora, fill=color_borde, font=font)
            draw.text((px_hv+dx, px_y+dy), hora, fill=color_borde, font=font)
        
        draw.text((px_he, px_y), hora, fill=color_principal, font=font)
        draw.text((px_hv, px_y), hora, fill=color_principal, font=font)
        
        # Para la posición seleccionada, agregar indicadores visuales
        if pos == posicion_seleccionada:
            # Círculos indicadores en las posiciones HE y HV
            radio = 8
            draw.ellipse([px_he - radio, px_y - radio, px_he + radio, px_y + radio], 
                        outline='#0066FF', width=3)
            draw.ellipse([px_hv - radio, px_y - radio, px_hv + radio, px_y + radio], 
                        outline='#0066FF', width=3)
            
            # Etiquetas HE y HV
            draw.text((px_he - 15, px_y - 25), "HE", fill='#0066FF', font=font_small)
            draw.text((px_hv - 15, px_y - 25), "HV", fill='#0066FF', font=font_small)
            
            # Línea horizontal guía
            draw.line([(0, px_y), (ancho_img, px_y)], fill='#0066FF', width=1)
            
            # Líneas verticales guía
            draw.line([(px_he, 0), (px_he, alto_img)], fill='#0066FF', width=1)
            draw.line([(px_hv, 0), (px_hv, alto_img)], fill='#0066FF', width=1)

    # Dibujar grid de referencia (12 rótulos: 6 filas x 2 columnas)
    # Línea vertical central
    draw.line([(ancho_img // 2, 0), (ancho_img // 2, alto_img)], fill='#CCCCCC', width=1)
    
    # Líneas horizontales para cada fila
    alto_util = int(alto_img * 0.95)  # 5% margen inferior
    alto_rotulo = alto_util // 6
    for i in range(1, 6):
        y_linea = i * alto_rotulo
        draw.line([(0, y_linea), (ancho_img, y_linea)], fill='#CCCCCC', width=1)

    return img_preview


def agregar_horas_a_pdf(pdf_path, rotulos, pdf_salida, calibraciones):
    """
    Agrega horas al PDF usando ANOTACIONES.
    """
    try:
        doc = pymupdf.open(pdf_path)

        rotulos_con_hora = [r for r in rotulos if r.get('hora')]
        
        if not rotulos_con_hora:
            doc.close()
            return False

        for rotulo in rotulos_con_hora:
            pagina_num = rotulo['pagina']
            
            if pagina_num < 1 or pagina_num > len(doc):
                continue

            page = doc[pagina_num - 1]
            pw = page.rect.width
            ph = page.rect.height
            
            he_x, hv_x, y = obtener_coordenadas(rotulo, calibraciones)
            
            x_he = pw * he_x
            x_hv = pw * hv_x
            y_pos = ph * y
            
            hora_str = rotulo['hora']
            
            ancho_texto = 35
            alto_texto = 12
            
            rect_he = pymupdf.Rect(
                x_he, 
                y_pos - alto_texto/2, 
                x_he + ancho_texto, 
                y_pos + alto_texto/2
            )
            
            rect_hv = pymupdf.Rect(
                x_hv, 
                y_pos - alto_texto/2, 
                x_hv + ancho_texto, 
                y_pos + alto_texto/2
            )
            
            annot_he = page.add_freetext_annot(
                rect_he,
                hora_str,
                fontsize=8,
                fontname="helv",
                text_color=(0, 0, 0),
                fill_color=None,
                border_color=None,
                align=0
            )
            annot_he.update()
            
            annot_hv = page.add_freetext_annot(
                rect_hv,
                hora_str,
                fontsize=8,
                fontname="helv",
                text_color=(0, 0, 0),
                fill_color=None,
                border_color=None,
                align=0
            )
            annot_hv.update()

        for page in doc:
            page.apply_redactions()
        
        doc.save(pdf_salida)
        doc.close()
        return True

    except Exception as e:
        st.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    st.markdown('<h1 style="text-align:center;color:#1f77b4;">🏷️ Sistema de Horas en Rótulos PDF</h1>', 
                unsafe_allow_html=True)

    # Session state
    if 'rotulos' not in st.session_state:
        st.session_state.rotulos = None
    if 'imagenes' not in st.session_state:
        st.session_state.imagenes = None
    if 'pdf_path' not in st.session_state:
        st.session_state.pdf_path = None
    if 'calibraciones' not in st.session_state:
        st.session_state.calibraciones = {}
    if 'cal_posicion' not in st.session_state:
        st.session_state.cal_posicion = 1
    if 'cal_pagina' not in st.session_state:
        st.session_state.cal_pagina = 1

    # === SIDEBAR ===
    with st.sidebar:
        st.header("📁 1. Cargar PDF")
        
        uploaded_file = st.file_uploader("Selecciona PDF", type=['pdf'])
        
        if uploaded_file:
            temp_path = Path("temp_uploaded.pdf")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("🔄 Procesar PDF", type="primary"):
                with st.spinner("Procesando..."):
                    resultado = dividir_pdf_en_rotulos(temp_path)
                    if resultado:
                        st.session_state.rotulos, st.session_state.imagenes = resultado
                        st.session_state.pdf_path = temp_path
                        st.session_state.calibraciones = {}
                        st.success(f"✅ {len(st.session_state.rotulos)} rótulos")
                        st.rerun()
        
        if st.session_state.rotulos:
            st.divider()
            st.header("📋 3. Configurar Rótulos")
            
            # Calcular número de páginas
            num_paginas = len(st.session_state.imagenes)
            
            # Campo para rótulos en última página
            rotulos_ultima = st.number_input(
                "Rótulos en última página",
                min_value=1,
                max_value=12,
                value=12,
                help="Si la última página no tiene 12 rótulos, indica cuántos tiene"
            )
            st.session_state.rotulos_ultima_pagina = rotulos_ultima
            
            # Calcular y mostrar total de rótulos válidos
            if num_paginas == 1:
                total_validos = rotulos_ultima
            else:
                total_validos = ((num_paginas - 1) * 12) + rotulos_ultima
            
            st.info(f"📊 **Total de rótulos válidos:** {total_validos}")
            
            st.divider()
            st.header("⏰ 4. Configurar Horas")
            
            hora_inicial = st.text_input("Hora inicial (HH:MM)", value="08:00")
            incremento = st.number_input("Incremento (min)", min_value=1, max_value=120, value=5)
            
            # Opción para incrementar cada X etiquetas
            incremento_cada = st.number_input(
                "Incrementar cada X etiquetas",
                min_value=1,
                max_value=12,
                value=1,
                help="Ej: Si pones 2, la hora cambiará cada 2 etiquetas (R01 y R02 tendrán la misma hora)"
            )
            
            if st.button("🚀 Aplicar Horas", type="primary"):
                try:
                    hora_base = datetime.strptime(hora_inicial.strip(), "%H:%M")
                    
                    # Obtener número de rótulos en última página
                    rotulos_ultima = st.session_state.get('rotulos_ultima_pagina', 12)
                    num_paginas = len(st.session_state.imagenes)
                    
                    # Filtrar solo rótulos válidos
                    rotulos_validos = []
                    for rotulo in st.session_state.rotulos:
                        es_ultima_pagina = rotulo['pagina'] == num_paginas
                        if es_ultima_pagina:
                            if rotulo['posicion'] <= rotulos_ultima:
                                rotulos_validos.append(rotulo)
                        else:
                            rotulos_validos.append(rotulo)
                    
                    # Limpiar horas de todos los rótulos primero
                    for rotulo in st.session_state.rotulos:
                        rotulo['hora'] = ''
                    
                    # Aplicar horas solo a rótulos válidos
                    for i, rotulo in enumerate(rotulos_validos):
                        # Calcular el grupo de incremento
                        grupo = i // incremento_cada
                        hora_calc = hora_base + timedelta(minutes=grupo * incremento)
                        rotulo['hora'] = hora_calc.strftime("%H:%M")
                    
                    st.success(f"✅ Horas aplicadas a {len(rotulos_validos)} rótulos")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            
            st.divider()
            total = len(st.session_state.rotulos)
            con_hora = sum(1 for r in st.session_state.rotulos if r.get('hora'))
            rotulos_ultima = st.session_state.get('rotulos_ultima_pagina', 12)
            num_paginas = len(st.session_state.imagenes)
            if num_paginas == 1:
                total_validos = rotulos_ultima
            else:
                total_validos = ((num_paginas - 1) * 12) + rotulos_ultima
            st.metric("Con horas", f"{con_hora}/{total_validos}")

    # === CONTENIDO PRINCIPAL ===
    if not st.session_state.rotulos:
        st.info("👆 Sube un PDF desde el panel lateral")
        return

    # Botón de configuración en la parte superior
    col_title, col_config = st.columns([4, 1])
    
    with col_config:
        if st.button("⚙️ Configuración", help="Calibración manual de posiciones"):
            st.session_state.mostrar_config = not st.session_state.get('mostrar_config', False)
    
    # --- PANEL DE CONFIGURACIÓN (expandible) ---
    if st.session_state.get('mostrar_config', False):
        with st.expander("⚙️ CALIBRACIÓN MANUAL DE POSICIONES", expanded=True):
            st.info("💡 Ajusta los sliders y ve en tiempo real dónde quedará la hora. La posición seleccionada aparece en **AZUL**, las demás en rojo.")
            
            if not any(r.get('hora') for r in st.session_state.rotulos):
                st.warning("⚠️ Primero aplica horas desde el panel lateral (sidebar)")
            else:
                # Dividir en dos columnas: controles y preview
                col_controles, col_preview = st.columns([1, 2])
                
                with col_controles:
                    st.markdown("### 🎛️ Controles")
                    
                    # Seleccionar página
                    paginas = sorted(set(r['pagina'] for r in st.session_state.rotulos))
                    pagina_sel = st.selectbox(
                        "📄 Página", 
                        paginas, 
                        format_func=lambda x: f"Página {x}",
                        key="cal_pag_select"
                    )
                    st.session_state.cal_pagina = pagina_sel
                    
                    # Seleccionar posición (R01-R12)
                    posicion_sel = st.selectbox(
                        "🏷️ Posición del rótulo",
                        range(1, 13),
                        format_func=lambda x: f"R{x:02d} - {'Izquierda' if x % 2 == 1 else 'Derecha'} (Fila {(x-1)//2 + 1})",
                        key="cal_pos_select"
                    )
                    st.session_state.cal_posicion = posicion_sel
                    
                    st.divider()
                    
                    # Obtener coordenadas actuales
                    he_x_actual, hv_x_actual, y_actual = obtener_coordenadas_por_posicion(
                        posicion_sel, 
                        st.session_state.calibraciones,
                        st.session_state.rotulos
                    )
                    
                    st.markdown("### 📍 Coordenadas")
                    
                    # Sliders para ajustar coordenadas
                    new_he_x = st.slider(
                        "**HE X** (Hora Entrada)", 
                        0.0, 1.0, 
                        float(he_x_actual), 
                        0.005,
                        help="Posición horizontal de la hora de entrada",
                        key=f"slider_he_{posicion_sel}"
                    )
                    
                    new_hv_x = st.slider(
                        "**HV X** (Hora Válida)", 
                        0.0, 1.0, 
                        float(hv_x_actual), 
                        0.005,
                        help="Posición horizontal de la hora válida",
                        key=f"slider_hv_{posicion_sel}"
                    )
                    
                    new_y = st.slider(
                        "**Y** (Vertical)", 
                        0.0, 1.0, 
                        float(y_actual), 
                        0.005,
                        help="Posición vertical (desde arriba)",
                        key=f"slider_y_{posicion_sel}"
                    )
                    
                    # Mostrar valores actuales
                    st.markdown(f"""
                    **Valores actuales:**
                    - HE X: `{new_he_x:.1%}`
                    - HV X: `{new_hv_x:.1%}`
                    - Y: `{new_y:.1%}`
                    """)
                    
                    st.divider()
                    
                    # Botones de guardado
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("💾 Guardar", type="primary"):
                            for r in st.session_state.rotulos:
                                r_pos = ((r['posicion'] - 1) % 12) + 1
                                if r_pos == posicion_sel:
                                    st.session_state.calibraciones[r['id']] = {
                                        'he_x': new_he_x,
                                        'hv_x': new_hv_x,
                                        'y': new_y
                                    }
                            st.success(f"✅ R{posicion_sel:02d}")
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("📋 Copiar columna"):
                            for r in st.session_state.rotulos:
                                r_pos = ((r['posicion'] - 1) % 12) + 1
                                col = r_pos % 2
                                
                                if col == (posicion_sel % 2):
                                    st.session_state.calibraciones[r['id']] = {
                                        'he_x': new_he_x,
                                        'hv_x': new_hv_x,
                                        'y': COORDENADAS_DEFAULT[r_pos]['y']
                                    }
                            st.success("✅ Columna")
                            st.rerun()
                    
                    if st.button("🔄 Resetear"):
                        keys_to_delete = []
                        for r in st.session_state.rotulos:
                            r_pos = ((r['posicion'] - 1) % 12) + 1
                            if r_pos == posicion_sel and r['id'] in st.session_state.calibraciones:
                                keys_to_delete.append(r['id'])
                        
                        for key in keys_to_delete:
                            del st.session_state.calibraciones[key]
                        
                        st.success(f"✅ Reset")
                        st.rerun()
                
                with col_preview:
                    st.markdown("### 👁️ Vista Previa en Tiempo Real")
                    
                    rotulos_pag = [r for r in st.session_state.rotulos if r['pagina'] == pagina_sel]
                    img = st.session_state.imagenes[pagina_sel - 1]
                    
                    preview = dibujar_preview_calibracion(
                        img, 
                        posicion_sel, 
                        new_he_x, 
                        new_hv_x, 
                        new_y,
                        rotulos_pag, 
                        st.session_state.calibraciones
                    )
                    
                    st.image(preview, use_column_width=True)
                    st.caption(f"🔵 AZUL = R{posicion_sel:02d} (editando) | 🔴 ROJO = Otras")
        
        st.divider()

    # --- TABS PRINCIPALES (Preview y Generar) ---
    tab1, tab2 = st.tabs(["👁️ Preview", "📄 Generar PDF"])

    # --- TAB PREVIEW ---
    with tab1:
        st.header("👁️ Preview")
        
        if not any(r.get('hora') for r in st.session_state.rotulos):
            st.warning("⚠️ Primero aplica horas (sidebar)")
        else:
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                paginas = sorted(set(r['pagina'] for r in st.session_state.rotulos))
                pag = st.selectbox("Página", paginas, format_func=lambda x: f"Página {x}", key="preview_page")
            
            with col_btn:
                st.write("")  # Espaciado
                generar_preview = st.button("🔄 Actualizar", type="primary")
            
            # Generar preview automáticamente o al presionar botón
            rotulos_pag = [r for r in st.session_state.rotulos if r['pagina'] == pag]
            img = st.session_state.imagenes[pag - 1]
            preview = dibujar_preview_pagina(img, rotulos_pag, st.session_state.calibraciones)
            st.image(preview, use_column_width=True, caption="Horas en ROJO (posiciones finales)")

    # --- TAB GENERAR PDF ---
    with tab2:
        st.header("📄 Generar PDF Final")
        
        if not any(r.get('hora') for r in st.session_state.rotulos):
            st.warning("⚠️ Primero aplica horas (sidebar)")
        else:
            con_hora = sum(1 for r in st.session_state.rotulos if r.get('hora'))
            calibrados = len(st.session_state.calibraciones)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rótulos con horas", con_hora)
            with col2:
                st.metric("Posiciones calibradas", calibrados)
            
            st.divider()
            
            if st.button("📄 GENERAR PDF FINAL", type="primary"):
                with st.spinner("Generando PDF..."):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_out = Path("output") / f"PDF_con_horas_{timestamp}.pdf"
                    pdf_out.parent.mkdir(exist_ok=True)
                    
                    if agregar_horas_a_pdf(
                        st.session_state.pdf_path,
                        st.session_state.rotulos,
                        pdf_out,
                        st.session_state.calibraciones
                    ):
                        if pdf_out.exists():
                            st.success("✅ PDF generado correctamente!")
                            
                            with open(pdf_out, "rb") as f:
                                st.download_button(
                                    "⬇️ DESCARGAR PDF",
                                    f.read(),
                                    f"rotulos_con_horas_{timestamp}.pdf",
                                    "application/pdf",
                                    type="primary"
                                )
                        else:
                            st.error("❌ Error al crear archivo")
                    else:
                        st.error("❌ Error al generar PDF")


if __name__ == "__main__":
    Path("output").mkdir(exist_ok=True)
    main()
