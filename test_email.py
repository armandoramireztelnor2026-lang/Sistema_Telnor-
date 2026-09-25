from notificaciones import disparar_correo

success, message = disparar_correo("armandoramireztelnor2026@gmail.com", "Prueba de Servidor", "<p>Probando si los correos salen.</p>")
print(f"Éxito: {success}, Mensaje: {message}")
