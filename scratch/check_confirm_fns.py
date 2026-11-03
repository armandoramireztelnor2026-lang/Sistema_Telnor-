import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/configuraciones_jefatura.js', 'r', encoding='utf-8') as f:
    js = f.read()

def show_snippet(fn_name, length=500):
    pos = js.find(fn_name)
    if pos != -1:
        print(f"\n=== {fn_name} ===")
        print(js[pos:pos+length])

show_snippet('window.guardarCorreoEmisor')
show_snippet('window.guardarNuevaCuentaCorreo')
show_snippet('window.activarCuentaCorreo')
show_snippet('window.guardarPresupuestoTotal')
show_snippet('window.guardarLimiteCotizacionesCaras')
show_snippet('window.cambiarTabConfiguracion')

