import sys
import json
import urllib.request

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Ejecutando pruebas de verificación de leyendas duales ---")

# 1. Probar que el servidor Flask responde
base_url = "http://127.0.0.1:5000"
try:
    with urllib.request.urlopen(f"{base_url}/") as res:
        print(f"✓ Servidor Flask responde HTTP {res.status}")
except Exception as e:
    print(f"✗ Error al conectar con servidor: {e}")

# 2. Verificar que los archivos JS contengan ambas leyendas en las tablas correspondientes
checks = [
    ("static/seccion_reportes.js", "${ticket}</span>${badgeCaras}${badgeRetrabajo}"),
    ("static/facturas_principal.js", "${r.id}</span>${badgeCaras}${badgeRetrabajo}"),
    ("static/facturas_principal.js", "${r.id}</strong>${badgeCarasP}${badgeRetrabajoP}"),
    ("static/facturas_principal.js", "${idRepForTable}</span>${badgeCaras}${badgeRetrabajo}"),
    ("static/facturas_principal.js", "${idRepTable}</span>${badgeCarasDoc}${badgeRetrabajoDoc}"),
    ("static/facturas_principal.js", "${idRepTableLib}</span>${badgeCarasDocLib}${badgeRetrabajoDocLib}"),
    ("static/facturas_principal.js", "${idReporteAsociado}</span>${badgeCarasArch}${badgeRetrabajoArch}"),
    ("static/script.js", "${ticketId}</strong>${badgeCarasAdmin}${badgeRetrabajoAdmin}"),
    ("static/script.js", "${ticketId}</strong>${badgeCarasProv}${badgeRetrabajoProv}"),
    ("static/script.js", "${ticketId}</strong>${badgeCarasLib}${badgeRetrabajoLib}"),
    ("static/cotizaciones_10k.js", "${idRepForTable}</span>${badgeCaras}${badgeRetrabajo}"),
    ("static/facturas_pdf.js", "r.id + badgeStr + badgeRetrabajo")
]

all_passed = True
for filepath, needle in checks:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if needle in content:
        print(f"✓ {filepath}: contiene '{needle}'")
    else:
        print(f"✗ {filepath}: NO contiene '{needle}'")
        all_passed = False

if all_passed:
    print("\n🎉 TODAS LAS VERIFICACIONES DE LEYENDAS PASARON SATISFACTORIAMENTE (100%)")
else:
    print("\n⚠️ ALGUNAS VERIFICACIONES FALLARON")

