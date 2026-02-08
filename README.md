# Ask a Manager – Salary Survey (Visualization & Storytelling)

## Descripción del proyecto
Este proyecto realiza un análisis exploratorio de datos (EDA) y un proceso de modelado sobre la base de datos **Ask a Manager Salary Survey**, una encuesta pública que recopila información salarial de profesionales de distintas industrias y países.

El objetivo principal es **limpiar, estandarizar y modelar los datos** para permitir su análisis y visualización, así como construir un **dashboard interactivo** que facilite la exploración de patrones salariales desde una perspectiva comparativa.

---

## Dashboard
El dashboard fue desarrollado en **Looker Studio** y presenta indicadores clave sobre salarios, industrias y localización geográfica.

[Acceso al dashboard](https://lookerstudio.google.com/reporting/a6bdd84d-40bb-450f-adc7-3293629c10de)  


### Módulos incluidos:
1. Contador total de respuestas.
2. Mapa geográfico por país.
3. Relación entre industria y salario promedio (en COP).
4. Relación entre trabajo y salario promedio (en COP).
5. Relación entre experiencia y salario promedio (en COP).
6. Relación entre genero y salario promedio (en COP).

---

## Fuentes de datos

- **Ask a Manager Salary Survey** [link](https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/export?format=csv&gid=1625408792)  
  Dataset alojado en Google Sheets y actualizado constantemente.

- **Frankfurter API** [link](https://www.frankfurter.app)
    
  Utilizada para obtener las tasas de cambio oficiales publicadas por el Banco Central Europeo.

**Fecha de extracción del dataset:** 2026-02-07  
**Fecha de las tasas de cambio:** 2026-02-07  

---

## 🛠️ Proceso de modelado de datos

El modelado se realizó en Python utilizando principalmente `pandas` y `numpy`. Los pasos principales fueron:

1. **Extracción de datos**  
   - Descarga directa del Google Sheets público en formato CSV.

2. **Renombrado de variables**  
   - Se simplificaron los nombres de columnas para facilitar su uso en análisis y visualización.

3. **Limpieza de salarios (`salary`)**  
   - Eliminación de símbolos y separadores.
   - Conversión a valores numéricos.
   - Aplicación de una heurística mínima para interpretar valores abreviados (por ejemplo, `80` → `80,000`).

4. **Limpieza de compensaciones adicionales (`bonus`)**  
   - Conversión a valores numéricos.
   - Reemplazo de valores nulos por cero, al tratarse de un campo opcional.

5. **Estandarización de ubicación geográfica**
   - `country`: normalización de variantes ortográficas y abreviaciones (por ejemplo, `US`, `USA`, `United States of America` → `United States`).
   - `city`: normalización básica y mapeo explícito de variantes frecuentes (por ejemplo, `NYC` → `New York`, `Washington DC` → `Washington, DC`).

6. **Conversión de monedas**
   - Se excluyeron registros con moneda categorizada como `Other`.
   - Se obtuvieron tasas de cambio desde Frankfurter API.
   - Se convirtieron salarios y compensaciones a pesos colombianos (COP).

7. **Creación de variables modeladas**
   - `salario_anual_cop`
   - `compensaciones_cop`
   - `total_compensacion_cop`

---

## Diccionario de variables (resumen)

### A. Variables originales (base Ask a Manager)

*Nota*: Los nombres de las variables se mantienen en inglés, tal como aparecen en la base de datos original. Las descripciones están en español para facilitar su comprensión.

---

date_created
- Tipo: fecha y hora (datetime)
-	Descripción: Fecha y hora en la que la persona respondió la encuesta.

---

age
	-	Tipo: texto (categoría)
	-	Descripción: Rango etario en el que se encuentra la persona encuestada (por ejemplo, 25-34, 35-44).

---

What industry do you work in?
	-	Tipo: texto (categoría)
	-	Descripción: Industria o sector económico en el que trabaja la persona encuestada, reportado de forma categórica.

---

job
	-	Tipo: texto
	-	Descripción: Cargo o título del puesto de trabajo desempeñado por la persona encuestada.

---

If your job title needs additional context, please clarify here:
	-	Tipo: texto
	-	Descripción: Campo opcional donde la persona puede agregar contexto adicional sobre su cargo o responsabilidades.

---

salary
	-	Tipo: numérico
	-	Descripción: Salario anual reportado por la persona encuestada, previamente limpiado y convertido a formato numérico. El valor se expresa en la moneda indicada en el campo currency.

---

bonus
	-	Tipo: numérico
	-	Descripción: Compensación monetaria adicional anual (bonos, horas extra, etc.). Los valores nulos se interpretan como ausencia de compensación adicional y se reemplazan por cero.

---

currency
	-	Tipo: texto (categoría)
	-	Descripción: Moneda en la que la persona reportó su salario y compensaciones.

---

If "Other," please indicate the currency here:
	-	Tipo: texto
	-	Descripción: Campo opcional para especificar la moneda cuando se selecciona la opción “Other”.

---

If your income needs additional context, please provide it here:
	-	Tipo: texto
	-	Descripción: Campo opcional donde la persona puede agregar aclaraciones sobre su salario o esquema de compensación.

---

country
	-	Tipo: texto
	-	Descripción: País donde la persona encuestada trabaja actualmente. Este campo se utiliza como base para la variable estandarizada de país.

---

state_US
	-	Tipo: texto
	-	Descripción: Estado dentro de Estados Unidos donde trabaja la persona, cuando aplica.

---

city
	-	Tipo: texto
	-	Descripción: Ciudad donde trabaja la persona encuestada. Campo de texto libre, posteriormente normalizado para análisis y visualización.

---

years_of_experience
	-	Tipo: texto (categoría)
	-	Descripción: Rango de años de experiencia profesional total de la persona encuestada.

---

years_of_experience_in_field
	-	Tipo: texto (categoría)
	-	Descripción: Rango de años de experiencia profesional de la persona dentro de su campo o industria actual.

---

highest_level_of_education
	-	Tipo: texto (categoría)
	-	Descripción: Nivel educativo más alto alcanzado por la persona encuestada.

---

gender
	-	Tipo: texto (categoría)
	-	Descripción: Identidad de género reportada por la persona encuestada.

---

race
	-	Tipo: texto
	-	Descripción: Categoría(s) de raza o etnicidad seleccionadas por la persona encuestada.

---

### B. Variables modeladas y derivadas

---

fx_to_cop
	-	Tipo: numérico
	-	Descripción: Tasa de conversión utilizada para transformar valores monetarios desde la moneda original reportada a pesos colombianos (COP), obtenida desde Frankfurter API en la fecha del análisis.

---

salario_anual_cop
	-	Tipo: numérico
	-	Descripción: Salario anual convertido a pesos colombianos (COP) a partir del campo salary y la tasa de cambio correspondiente.

---

compensaciones_cop
	-	Tipo: numérico
	-	Descripción: Compensaciones monetarias adicionales convertidas a pesos colombianos (COP) a partir del campo bonus.

---

total_compensacion_cop
	-	Tipo: numérico
	-	Descripción: Suma del salario anual y las compensaciones adicionales, ambas expresadas en pesos colombianos (COP). Esta variable se utiliza como métrica principal para el análisis comparativo de ingresos.

---

## Cómo actualizar los datos (paso a paso)

1. Acceder al Google Sheets público del Salary Survey.
2. Ejecutar el script de Python incluido en este repositorio.
3. El script:
   - Descarga la versión más reciente del dataset.
   - Aplica el proceso de limpieza y modelado.
   - Obtiene automáticamente las tasas de cambio.
4. Exportar el dataset final en formato CSV o Google Sheets.
5. Actualizar la fuente de datos en Looker Studio.
6. Verificar que el dashboard se actualice correctamente.

