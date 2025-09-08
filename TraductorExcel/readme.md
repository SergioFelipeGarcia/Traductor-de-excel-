# Traductor de Excel Fiable con Streamlit

Esta es una aplicación web interactiva creada con Streamlit que permite traducir ficheros de Excel de forma masiva utilizando la librería `deep-translator`, que a su vez usa el motor de Google Translate.

La aplicación está diseñada para ser robusta, fácil de usar y permitir la reanudación de trabajos de traducción.

## Características

-   **Interfaz Web Interactiva**: Sube y procesa tus ficheros directamente desde el navegador.
-   **Motor de Traducción Fiable**: Utiliza `deep-translator` para evitar los estrictos límites de las APIs de IA y asegurar que el trabajo se complete.
-   **Reanudación Inteligente**: Si traduces una columna y luego quieres traducir otra, la aplicación no retraduce lo que ya está hecho.
-   **Flujo de Trabajo Continuo**: Traduce una columna, descarga el resultado y empieza a traducir otra del mismo fichero sin tener que reiniciar la aplicación.
-   **Vista Previa y Descarga**: Visualiza los resultados directamente en la web y descarga el fichero Excel completo con un solo clic.

## Instalación

1.  **Clona o descarga este proyecto.**

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # En Windows
    # source venv/bin/activate  # En macOS/Linux
    ```

3.  **Instala las dependencias:**
    El fichero `requirements.txt` está simplificado. Instala las librerías necesarias con:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1.  **Inicia la aplicación:**
    Abre tu terminal, navega a la carpeta del proyecto y ejecuta el siguiente comando:
    ```bash
    streamlit run app.py
    ```

2.  **Usa la aplicación en tu navegador:**
    -   Se abrirá una nueva pestaña en tu navegador con la aplicación.
    -   **Sube tu fichero Excel**.
    -   **Configura la traducción**: Elige la columna de origen y los idiomas de destino.
    -   **Inicia el proceso**: Haz clic en "Iniciar Traducción" y observa la barra de progreso.
    -   **Descarga o continúa**: Una vez terminado, puedes descargar el fichero resultante o elegir traducir otra columna.

## Ficheros del Proyecto

-   `app.py`: El código fuente de la aplicación Streamlit.
-   `requirements.txt`: Las librerías de Python necesarias.
-   `traducciones.xls.xlsx`: Un fichero Excel de ejemplo.
-   `Traducido.xls.xlsx`: El fichero de salida que generará el script por defecto.
-   `readme.md`: Este mismo fichero.
