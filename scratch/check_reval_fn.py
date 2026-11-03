import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('rutas_facturas.py', 'r', encoding='utf-8') as f:
    code = f.read()

pos_reval = code.find('def revaluar_cotizaciones_por_limite')
print(code[pos_reval:pos_reval+2000])

