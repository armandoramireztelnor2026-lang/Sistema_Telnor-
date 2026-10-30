with open('static/seccion_reportes.js', 'r', encoding='utf-8') as f:
    content = f.read()

target_operando = """        let isOperando = true;
        if (f.is_unassigned) {
            isOperando = !f.asignado_a;
        } else {
            isOperando = (f.entregado === 'Sí');
        }
        let statusUnidad = isOperando"""

new_operando = """        let isOperando = true;
        if (f.is_unassigned) {
            isOperando = !f.asignado_a;
        } else {
            isOperando = (f.entregado === 'Sí');
        }

        // Si la unidad está en retrabajo / reasignación, su estado operativo es No Operando
        let estRetNorm = String(f.estado_retrabajo || '').trim().toLowerCase();
        let estTicketNorm = String(estado || f.estado || f.estado_calculado || '').trim().toLowerCase();
        let rawRetNorm = String(f.retrabajo || f.es_retrabajo || '').trim().toLowerCase();

        let estaEnRetrabajoActivo = (
            estTicketNorm.includes('retrabajo') ||
            estRetNorm === 'reasignado' ||
            estRetNorm === 'pendiente' ||
            rawRetNorm === 'sí' ||
            rawRetNorm === 'si' ||
            rawRetNorm === 'pendiente' ||
            rawRetNorm === 'reasignado'
        );
        if (estRetNorm === 'finalizado') {
            estaEnRetrabajoActivo = false;
        }
        if (estaEnRetrabajoActivo) {
            isOperando = false;
        }

        let statusUnidad = isOperando"""

if target_operando in content:
    content = content.replace(target_operando, new_operando)
    print("Replaced statusUnidad logic (LF)")
else:
    to_crlf = target_operando.replace('\n', '\r\n')
    no_crlf = new_operando.replace('\n', '\r\n')
    if to_crlf in content:
        content = content.replace(to_crlf, no_crlf)
        print("Replaced statusUnidad logic (CRLF)")
    else:
        print("Warning: target_operando not found in seccion_reportes.js")

with open('static/seccion_reportes.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated static/seccion_reportes.js successfully")

