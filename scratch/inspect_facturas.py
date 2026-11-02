import json

facts = json.load(open('facturas.json', encoding='utf-8')).get('facturas', [])
print(f'Total facturas: {len(facts)}')
for i, f in enumerate(facts):
    print(f"{i}: ID={f.get('id')} Estado={f.get('estado')} EstadoPrevio={f.get('estado_previo')} ValFiscal={f.get('validacion_fiscal')} Retrabajo={f.get('retrabajo')} EstadoRet={f.get('estado_retrabajo')}")

