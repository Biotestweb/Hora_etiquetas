# 🏷️ Sistema de Horas en Rótulos PDF

Aplicación desarrollada en Python con Streamlit para agregar horas automáticamente a rótulos/etiquetas en archivos PDF.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Descripción

Esta aplicación permite:
- Cargar un PDF con rótulos/etiquetas (formato 2 columnas × 6 filas = 12 rótulos por página)
- Asignar horas automáticamente de forma secuencial
- Configurar hora inicial, incremento y frecuencia de cambio
- Calibrar manualmente la posición de las horas con vista previa en tiempo real
- Generar un nuevo PDF con las horas insertadas

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/pdf-rotulos-horas.git
cd pdf-rotulos-horas
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar Poppler (requerido para pdf2image)

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
- Descargar desde: https://github.com/osber/poppler-windows/releases
- Agregar la carpeta `bin` al PATH del sistema

## 💻 Uso

### Ejecutar la aplicación
```bash
streamlit run app.py
```

### Flujo de trabajo

1. **Cargar PDF**: Sube tu archivo PDF con los rótulos
2. **Procesar**: Click en "🔄 Procesar PDF"
3. **Configurar rótulos**: Indica cuántos rótulos tiene la última página (si son menos de 12)
4. **Configurar horas**:
   - Hora inicial (ej: 08:00)
   - Incremento en minutos (ej: 5)
   - Incrementar cada X etiquetas (ej: 2 para que cada par tenga la misma hora)
5. **Aplicar horas**: Click en "🚀 Aplicar Horas"
6. **Preview**: Verifica que las horas estén bien posicionadas
7. **Calibración** (opcional): Si las horas no están bien ubicadas, usa el botón ⚙️ Configuración
8. **Generar PDF**: Descarga el PDF final con las horas

## 📁 Estructura del proyecto

```
pdf-rotulos-horas/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── README.md          # Este archivo
├── .gitignore         # Archivos ignorados por Git
├── LICENSE            # Licencia MIT
└── output/            # Carpeta para PDFs generados (ignorada por Git)
```

## ⚙️ Configuración de coordenadas

Las coordenadas predeterminadas están optimizadas para un formato específico de rótulos. Si necesitas ajustarlas, puedes:

1. Usar el botón **⚙️ Configuración** en la aplicación para calibrar visualmente
2. Modificar el diccionario `COORDENADAS_DEFAULT` en `app.py`

### Coordenadas predeterminadas

| Posición | HE X | HV X | Y |
|----------|------|------|------|
| R01, R03, R05, R07, R09, R11 (Izquierda) | 17.5% | 32.0% | Variable |
| R02, R04, R06, R08, R10, R12 (Derecha) | 59.5% | 73.5% | Variable |

## 🛠️ Tecnologías utilizadas

- **Python 3.9+**
- **Streamlit**: Framework para la interfaz web
- **PyMuPDF (fitz)**: Manipulación de PDFs
- **pdf2image**: Conversión de PDF a imágenes
- **Pillow**: Procesamiento de imágenes

## 📝 Notas

- El sistema usa anotaciones FreeText para insertar las horas, lo que garantiza compatibilidad con PDFs que tienen transformaciones especiales
- Las horas se insertan como texto negro sin fondo
- El preview muestra las horas en rojo para mejor visualización

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

Desarrollado con ❤️ y la asistencia de Claude (Anthropic)

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub