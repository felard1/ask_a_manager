# %%
import pandas as pd
import numpy as np
import requests
from datetime import date, timedelta

# %%
url = "https://docs.google.com/spreadsheets/d/1IPS5dBSGtwYVbjsfbaMCYIWnOuRmJcbequohNxCyGVw/export?format=csv&gid=1625408792"

df = pd.read_csv(url)
print(df.head())

df_copy = df.copy()

# %%
df.rename(
    columns={
        "Timestamp": "date_created",
        "How old are you?": "age",
        "Job title": "job",
        "What is your annual salary? (You'll indicate the currency in a later question. If you are part-time or hourly, please enter an annualized equivalent -- what you would earn if you worked the job 40 hours a week, 52 weeks a year.)": "salary",
        "How much additional monetary compensation do you get, if any (for example, bonuses or overtime in an average year)? Please only include monetary compensation here, not the value of benefits.": "bonus",
        "Please indicate the currency": "currency",
        "What country do you work in?": "country",
        "If you're in the U.S., what state do you work in?": "state_US",
        "What city do you work in?": "city",
        "How many years of professional work experience do you have overall?": "years_of_experience",
        "How many years of professional work experience do you have in your field?": "years_of_experience_in_field",
        "What is your highest level of education completed?": "highest_level_of_education",
        "What is your gender?": "gender",
        "What is your race? (Choose all that apply.)": "race",
    },
    inplace=True,
)
# %%
df["date_created"] = pd.to_datetime(df["date_created"])


# %%
def clean_salary(x):
    if pd.isna(x):
        return np.nan

    s = str(x).strip().lower()
    if s in {"", "na", "n/a", "none"}:
        return np.nan

    # quitar símbolos comunes
    s = s.replace(",", "").replace("$", "")

    try:
        val = float(s)
    except ValueError:
        return np.nan

    # heurística mínima: 80 -> 80000
    if val < 1000:
        val *= 1000

    return val


df["salary"] = df["salary"].apply(clean_salary)

df["bonus"] = df["bonus"].replace({None: 0, "": 0}).fillna(0)

# %%
df["currency"] = df["currency"].astype(str).str.strip().str.upper()
df = df[df["currency"] != "OTHER"].copy()

# %%

currencies = [c for c in df["currency"].unique() if c != "OTHER"]
# Extraemos símbolos individuales (por si hay combos tipo AUD/NZD)
symbols_set = set()
for c in currencies:
    for sub in c.split("/"):
        symbols_set.add(sub)

# Endpoint para el día de hoy
url = "https://api.frankfurter.app/latest"
params = {"from": "USD", "to": ",".join(symbols_set)}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    rates = data.get("rates", {})

    # IMPORTANTE: Si Frankfurter NO tiene COP, el código fallará aquí.
    # Como salvaguarda, si no está, podrías usar un valor hardcodeado o lanzar error claro.
    if "COP" not in rates:
        # Valor aproximado si la API falla en dar COP (ajustar según realidad)
        print("⚠️ COP no encontrado en API. Usando TRM referencial de 3,661.")
        usd_to_cop = 3661.0
    else:
        usd_to_cop = rates["COP"]

    fx_to_cop = {}
    for c in currencies:
        try:
            if "/" in c:
                parts = c.split("/")
                # Usamos .get() para evitar que el script se rompa si falta una moneda
                val = sum([(usd_to_cop / rates.get(p, 1)) for p in parts]) / len(parts)
                fx_to_cop[c] = val
            elif c == "USD":
                fx_to_cop["USD"] = usd_to_cop
            else:
                # 1 Moneda X = (1 / tasa_X_vs_USD) * tasa_COP_vs_USD
                tasa_vs_usd = rates.get(c)
                if tasa_vs_usd:
                    fx_to_cop[c] = usd_to_cop / tasa_vs_usd
                else:
                    fx_to_cop[c] = np.nan
        except Exception as e:
            fx_to_cop[c] = np.nan
            print(f"Error procesando {c}: {e}")

    # 4. Mapeo y cálculos (Tu lógica original que está perfecta)
    df["fx_to_cop"] = df["currency"].map(fx_to_cop)

    # Validar si alguna moneda quedó fuera
    missing = df[df["fx_to_cop"].isna()]["currency"].unique()
    if len(missing) > 0:
        print(f"⚠️ Alerta: No se encontraron tasas para: {missing}")

    df["salario_anual_cop"] = df["salary"] * df["fx_to_cop"]
    df["compensaciones_cop"] = df["bonus"] * df["fx_to_cop"]
    df["total_compensacion_cop"] = df["salario_anual_cop"] + df["compensaciones_cop"]

    print(f"✅ Procesado exitoso. TRM USD/COP hoy: {usd_to_cop:,.2f}")
else:
    print(f"❌ Error al conectar con Frankfurter: {response.status_code}")

# %%
df["country"] = df["country"].astype(str).str.strip().str.lower()

country_map = {
    # Estados Unidos
    "united states": "United States",
    "united states of america": "United States",
    "united states ": "United States",
    "united state": "United States",
    "unites states": "United States",
    "america": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s": "United States",
    "u.s.a.": "United States",
    "usa": "United States",
    "usa ": "United States",
    "united stated ": "United States",
    "u.s.a": "United States",
    "united stated": "United States",
    "the united states": "United States",
    "u. s.": "United States",
    "united sates": "United States",
    "🇺🇸": "United States",
    "United Sttes ": "United States",
    # Reino Unido
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "england": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    # Otros (tal como aparecen)
    "canada": "Canada",
    "australia": "Australia",
    "germany": "Germany",
    "the netherlands": "netherlands",
    "ireland": "Ireland",
    "new zealand": "New Zealand",
    "nz": "New Zealand",
    "Remote (Philippines)": "Philippines",
}
df["country"] = df["country"].replace(country_map)
df["country"] = df["country"].str.title()
# %%
df["city"] = df["city"].astype(str).str.strip().str.lower()


city_map = {
    # New York
    "nyc": "New York",
    "new york city": "New York",
    # Washington DC
    "washington dc": "Washington, DC",
    "washington, dc": "Washington, DC",
    "dc": "Washington, DC",
    "d.c.": "Washington, DC",
    "washington": "Washington, DC",  # decisión explícita
    # San Francisco
    "sf": "San Francisco",
    "s.f.": "San Francisco",
    "bay area": "San Francisco",
    # Los Angeles
    "la": "Los Angeles",
    "l.a.": "Los Angeles",
    # St Louis
    "saint louis": "St. Louis",
    "st louis": "St. Louis",
    # St Paul
    "st. paul": "Saint Paul",
    # Remote / no geográfico
    "remote": np.nan,
    "nan": np.nan,
}


df["city"] = df["city"].replace(city_map)
# %%
df["city"] = df["city"].str.title()


def smart_city_title(s):
    if pd.isna(s):
        return s
    if s.isupper() and len(s) <= 4:
        return s
    return s.title()


df["city"] = df["city"].apply(smart_city_title)

# Arreglo explícito por seguridad
df["city"] = df["city"].str.replace("Washington, Dc", "Washington, DC", regex=False)
# %%
df.to_csv("ask_a_manager_modelado.csv", index=False, encoding="utf-8")
print("Finalizo con la recación de: ask_a_manager_modelado.csv ")
