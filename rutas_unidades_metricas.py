import json
import os
import re

def leer_json_seguro(archivo):
    if not os.path.exists(archivo): 
        return {}
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        try:
            with open(archivo, 'r', encoding='latin-1') as f:
                return json.load(f)
        except Exception:
            return {}

def obtener_metricas_flota():
    unidades_data = leer_json_seguro("unidades.json")
    facturas_data = leer_json_seguro("facturas.json").get("facturas", [])
    reportes_data = leer_json_seguro("reportes.json").get("reportes", [])

    # Mapeo de reportes vinculados a facturas
    facturas_report_ids = set()
    unidades_en_caras = set()
    unidades_en_taller = set()

    for f in facturas_data:
        r_id = f.get("id_reporte") or f.get("numero_reporte")
        if not r_id:
            retro = f.get("retro", "")
            match = re.search(r"\[TICKET:(.*?)\]", retro)
            if match:
                r_id = match.group(1).strip()
        if r_id:
            facturas_report_ids.add(str(r_id))

        u_raw = str(f.get("unidad", "")).replace("8090-", "").strip()
        if len(u_raw) >= 4:
            u4 = u_raw[-4:]
            st = f.get("estado", "")
            entregado = str(f.get("entregado", "")).strip().lower()

            # En cotizaciones caras:
            if st == "Cancelado_Cotizacion_Cara":
                unidades_en_caras.add(u4)
            # En taller: desde que inicia el reporte hasta que se entrega la unidad (entregado == "Sí")
            elif entregado not in ["sí", "si"] and st not in ["Rechazado", "Eliminado"]:
                unidades_en_taller.add(u4)

    # Revisar reportes originales del chofer que aún no se convierten en factura
    for r in reportes_data:
        r_id = str(r.get("id", "")).strip()
        r_st = r.get("estado", "")
        if r_st != "Eliminado" and r_id not in facturas_report_ids:
            u_raw = str(r.get("unidad", "")).replace("8090-", "").strip()
            if len(u_raw) >= 4:
                u4 = u_raw[-4:]
                unidades_en_taller.add(u4)

    # Si una unidad está en caras, su estado prioritario es inhabilitada (caras)
    unidades_en_taller = unidades_en_taller - unidades_en_caras

    estados_por_unidad = {}
    totales = {
        "circulacion": 0,
        "taller": 0,
        "juridicos": 0,
        "inhabilitadas": 0,
        "total": len(unidades_data)
    }

    for uid, info in unidades_data.items():
        u4 = str(uid)[-4:]
        
        if info.get("Estado") == "Inactiva" or u4 in unidades_en_caras:
            estado = "Inhabilitada"
            totales["inhabilitadas"] += 1
        elif info.get("Juridicos") is True:
            estado = "En Jurídicos"
            totales["juridicos"] += 1
        elif u4 in unidades_en_taller:
            estado = "En Taller"
            totales["taller"] += 1
        else:
            estado = "En Circulación"
            totales["circulacion"] += 1

        estados_por_unidad[uid] = estado

    total = totales["total"]
    porcentajes = {
        "circulacion": round((totales["circulacion"] / total * 100), 1) if total else 0,
        "taller": round((totales["taller"] / total * 100), 1) if total else 0,
        "juridicos": round((totales["juridicos"] / total * 100), 1) if total else 0,
        "inhabilitadas": round((totales["inhabilitadas"] / total * 100), 1) if total else 0
    }

    return {
        "totales": totales,
        "porcentajes": porcentajes,
        "estados_por_unidad": estados_por_unidad,
        "unidades_data": unidades_data
    }
