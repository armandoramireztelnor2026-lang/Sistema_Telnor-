# scratch/test_chat_photos_and_edits.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from app import app

def test_chat_photos():
    client = app.test_client()
    
    # Login as an admin (e.g. Samuel Giron)
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "Samuel_Giron-RUMN-2026-admin",
            "rol": "administracion",
            "nombre": "Samuel Giron",
            "datos_perfil": {
                "nombres": "Samuel",
                "apellido_paterno": "Giron",
                "subrol": "Supervisor"
            }
        }
    
    # 1. Test mi_perfil
    res_perfil = client.get('/api/chat/mi_perfil')
    assert res_perfil.status_code == 200, f"Error mi_perfil {res_perfil.status_code}"
    p_data = res_perfil.get_json()
    print("Mi Perfil:", p_data)
    assert p_data["status"] == "success"
    assert p_data["foto_ruta"] != "", "foto_ruta no debe estar vacia para Samuel Giron"
    assert os.path.exists(p_data["foto_ruta"].lstrip('/')), f"Archivo {p_data['foto_ruta']} debe existir en disco"
    print(">> /api/chat/mi_perfil OK - Foto:", p_data["foto_ruta"])

    # 2. Test contactos
    res_contactos = client.get('/api/chat/contactos')
    assert res_contactos.status_code == 200
    c_data = res_contactos.get_json()
    contactos = c_data.get("contactos", [])
    print(f"Total contactos retornados: {len(contactos)}")
    assert len(contactos) > 0, "Debe haber contactos permitidos para Supervisor"
    
    for c in contactos:
        foto = c.get("foto_ruta", "")
        print(f"  Contacto: {c.get('nombre')} ({c.get('rol')}) -> Foto: {foto}")
        if foto:
            assert os.path.exists(foto.lstrip('/')), f"La foto {foto} de {c.get('nombre')} debe existir físicamente en disco"
    print(">> /api/chat/contactos OK - Todas las fotos resueltas existen")

    # 3. Test conversacion
    contacto_taller = next((c for c in contactos if c.get("rol") == "Taller"), contactos[0])
    cid = contacto_taller["usuario"]
    res_conv = client.get(f'/api/chat/conversacion/{cid}')
    assert res_conv.status_code == 200
    conv_data = res_conv.get_json()
    assert conv_data["status"] == "success"
    assert conv_data["contacto"]["foto_ruta"] != "", "El contacto debe tener foto_ruta"
    assert os.path.exists(conv_data["contacto"]["foto_ruta"].lstrip('/'))
    print(">> /api/chat/conversacion OK - Contacto foto:", conv_data["contacto"]["foto_ruta"])
    
    msgs = conv_data.get("mensajes", [])
    print(f"Total mensajes en conversacion: {len(msgs)}")
    for m in msgs:
        assert "emisor_foto" in m, "Debe incluir emisor_foto"
        assert "receptor_foto" in m, "Debe incluir receptor_foto"
        assert "emisor_nombre" in m, "Debe incluir emisor_nombre"
        print(f"  Mensaje ID: {m.get('id')} - De: {m.get('emisor_nombre')} (Foto: {m.get('emisor_foto')}) -> Para: {m.get('receptor_nombre')} (Foto: {m.get('receptor_foto')})")

    print(">> Mensajes enriquecidos con foto y nombre en tiempo real OK")

def test_dynamic_edit_reflection():
    print("\n--- Probando reflejo dinámico al editar usuario ---")
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["usuario"] = {
            "usuario": "Samuel_Giron-RUMN-2026-admin",
            "rol": "administracion",
            "datos_perfil": {"subrol": "Supervisor"}
        }

    # Leer nombre original de Manuel Alejandro Marquez
    with open("usuarios.json", "r", encoding="utf-8") as f:
        u_data = json.load(f)
    
    target_user = next((u for u in u_data["usuarios"] if u["usuario"] == "ManuelAlejandro_Marquez-RUMN-2026-admin"), None)
    orig_nombres = target_user["datos_perfil"]["nombres"]
    
    try:
        # 1. Simular edicion de nombre
        target_user["datos_perfil"]["nombres"] = "Manuel Alejandro TEST"
        with open("usuarios.json", "w", encoding="utf-8") as f:
            json.dump(u_data, f, indent=4, ensure_ascii=False)
            
        # 2. Consultar contactos y verificar que sale el nuevo nombre
        res = client.get('/api/chat/contactos')
        data = res.get_json()
        c_marquez = next((c for c in data["contactos"] if c["usuario"] == "ManuelAlejandro_Marquez-RUMN-2026-admin"), None)
        assert c_marquez is not None
        print(f"Nombre de contacto tras edición: {c_marquez['nombre']}")
        assert "TEST" in c_marquez["nombre"], "El nuevo nombre debe reflejarse en el chat"
        print(">> El cambio de nombre se reflejó inmediatamente en el chat!")
        
    finally:
        # Restaurar nombre original
        target_user["datos_perfil"]["nombres"] = orig_nombres
        with open("usuarios.json", "w", encoding="utf-8") as f:
            json.dump(u_data, f, indent=4, ensure_ascii=False)
        print(">> Nombre original restaurado correctamente.")

if __name__ == "__main__":
    test_chat_photos()
    test_dynamic_edit_reflection()
    print("\n==========================================")
    print("TODAS LAS PRUEBAS DE CHAT PASARON AL 100%")
    print("==========================================")

