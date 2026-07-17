# quinielaJoanSantos · Apertura 2026

Aplicación Streamlit con calendario precargado, pronósticos, tabla general, duelos 3-1-0, Survivor con tres vidas y selección final de campeón por turnos.

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Administrador: `ADMIN` / PIN `2026`.

Los PIN individuales aparecen únicamente en el panel del administrador y pueden descargarse como CSV.

## Publicar como app

Sube esta carpeta a un repositorio privado de GitHub y publícala con Streamlit Community Cloud. En iPhone abre el enlace en Safari, toca Compartir y luego **Agregar a pantalla de inicio**. En Android abre el enlace en Chrome y selecciona **Instalar aplicación** o **Agregar a pantalla principal**.

Para uso real con datos permanentes y varios usuarios simultáneos se recomienda sustituir SQLite por Supabase/PostgreSQL antes del torneo.
