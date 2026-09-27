import json

def remove_ghost_ticket():
    try:
        with open('facturas.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        facturas = data.get('facturas', [])
        
        # Filtramos la factura fantasma
        new_facturas = [f for f in facturas if f.get('id') != '20260924125352']
        
        if len(new_facturas) < len(facturas):
            data['facturas'] = new_facturas
            with open('facturas.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Ticket fantasma eliminado exitosamente.")
        else:
            print("No se encontró el ticket fantasma en facturas.json.")
            
    except Exception as e:
        print(f"Error: {e}")

remove_ghost_ticket()
