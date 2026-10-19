/**
 * =========================================================
 * ARCHIVO: static/manual_sistema.js
 * PROPÓSITO: Motor del Manual Dinámico del Sistema filtrado por perfil.
 *            Documenta pantallas y botones de acción exhaustivamente.
 * =========================================================
 */

(function () {
    // -------------------------------------------------------------
    // BASE DE CONOCIMIENTO TÉCNICA DEL MANUAL POR PERFIL
    // -------------------------------------------------------------
    const DATOS_MANUAL = {
        "Administrador": {
            titulo: "Manual Operativo - Administrador Central",
            badgeClase: "badge-admin",
            descripcionPerfil: "Como <strong>Administrador Central</strong> de Automotriz, eres la máxima autoridad financiera y de control operativo sobre los recursos de mantenimiento. Tienes a tu cargo el filtro exclusivo de <strong>Cotizaciones Mayores a $10,000 MXN</strong>, la facultad de <strong>asumir procesos en cobertura</strong> de supervisores ausentes, la <strong>liberación obligatoria del Documento Contable (Doc 50 de SAP)</strong> previa al pago, y el <strong>archivado definitivo</strong> de los expedientes en el histórico.",
            modulos: [
                {
                    id: "admin-10k",
                    nombre: "Cotizaciones +10,000",
                    icono: "💎",
                    descripcion: "Bandeja neurálgica exclusiva del Administrador. Filtra preventivamente cualquier presupuesto automotriz que exceda los $10,000 MXN para evitar gastos no autorizados por Dirección Corporativa.",
                    botones: [
                        {
                            nombre: "Revisar Cotización Mayor",
                            color: "badge-btn-azul",
                            icono: "🔍",
                            pantalla: "Bandeja Cotizaciones +10,000",
                            proposito: "Inspeccionar a detalle el presupuesto técnico-económico elaborado por el taller mecánico cuando el monto rebasa el umbral financiero de $10,000 MXN.",
                            proceso: "Abre el visor modal donde se visualiza el desglose concepto por concepto, piezas y refacciones requeridas, costo de mano de obra, archivo PDF de presupuesto formal emitido por el taller y la galería de fotografías de evidencia física.",
                            impactoEstado: "Mantiene el ticket en 'Esperando / Aprob. Cotizacion (Admin)' mientras se realiza la auditoría previa.",
                            reglasNegocio: "Se activa de forma automática cuando el campo <code>precio</code> de la factura es mayor o igual a $10,001.00 MXN. Permite al Administrador detectar sobrecostos o piezas innecesarias antes de comprometer el presupuesto corporativo."
                        },
                        {
                            nombre: "Aprobar y Canalizar a Corporativos",
                            color: "badge-btn-verde",
                            icono: "✅",
                            pantalla: "Modal de Cotizaciones +10,000",
                            proposito: "Validar técnicamente el presupuesto de alto valor y someterlo formalmente a la autorización ejecutiva de Dirección Corporativa.",
                            proceso: "Ejecuta una petición <code>POST /api/facturas/aprobar_10k</code>. Modifica el registro marcando <code>aprobado_admin_10k = true</code> y dispara notificaciones masivas por correo electrónico con enlace directo a todos los ejecutivos con rol 'corporativos' (<code>enviar_correo_admin_aprobado_a_corp</code>).",
                            impactoEstado: "Transiciona el ticket del estado 'Esperando / Aprob. Cotizacion (Admin)' a 'Esperando / Aprob. Cotizacion (Corp)'.",
                            reglasNegocio: "<strong>🔒 Regla Crítica de Flujo Estricto:</strong> Si la cotización pertenece al ámbito de Corporativos (identificado por <code>es_ticket_corporativo</code>) y el monto es $\\ge \\$10,001$, esta acción queda estrictamente reservada para el <strong>Administrador Titular</strong>. Si un usuario con subrol de Supervisor intenta aprobar bajo suplencia, el backend rechaza la transacción con código <strong>HTTP 403 Prohibido</strong>."
                        },
                        {
                            nombre: "Rechazar Cotización con Recomendaciones",
                            color: "badge-btn-rojo",
                            icono: "↩️",
                            pantalla: "Modal de Cotizaciones +10,000",
                            proposito: "Rechazar los costos propuestos por el proveedor cuando se consideren inflados o fuera de tabulador, indicando sugerencias de precios tope por concepto.",
                            proceso: "Envía una solicitud <code>POST /api/facturas/rechazar_super</code> registrando el array de precios recomendados. El sistema envía un correo formal al taller con la tabla comparativa de precios autorizables (<code>enviar_correo_factura_rechazada_super</code>).",
                            impactoEstado: "Mueve el ticket a 'Correcciones/Taller'. El taller debe corregir los montos para poder continuar.",
                            reglasNegocio: "Permite preservar la relación con el taller evitando cancelar el servicio, dándole la oportunidad de apegarse a los costos de mercado de la empresa."
                        }
                    ]
                },
                {
                    id: "admin-doc50",
                    nombre: "Liberación de Doc. Contable",
                    icono: "📜",
                    descripcion: "Módulo donde radica la responsabilidad financiera final. Tras la entrega del auto y validación fiscal, el Administrador asocia el asiento contable de SAP y emite la autorización formal de pago.",
                    botones: [
                        {
                            nombre: "Capturar / Guardar Doc 50",
                            color: "badge-btn-azul",
                            icono: "💾",
                            pantalla: "Bandeja Documentos Contables",
                            proposito: "Ingresar en el expediente el número oficial de Documento Contable (Doc 50 / SAP) emitido por el departamento de Cuentas por Pagar.",
                            proceso: "Dispara <code>POST /api/facturas/doc50</code>. Guarda los metadatos <code>numero_doc50</code> y la fecha de asignación <code>doc50_fecha</code> en <code>facturas.json</code>.",
                            impactoEstado: "Mantiene el ticket en 'Esperando Num. Contable' hasta que se formalice la liberación.",
                            reglasNegocio: "El campo solo acepta caracteres numéricos correspondientes a la póliza o documento financiero de SAP."
                        },
                        {
                            nombre: "Liberar Documento Contable (Liberar Doc 50)",
                            color: "badge-btn-verde",
                            icono: "🔓",
                            pantalla: "Bandeja Documentos Contables",
                            proposito: "Emitir el visto bueno definitivo que confirma que la factura cuenta con suficiencia presupuestal y registro contable, desbloqueando el expediente para su archivado.",
                            proceso: "Ejecuta <code>POST /api/facturas/liberar_doc50</code>. Graba <code>doc50_liberado = true</code> y <code>liberado_por = '[Nombre] (Administrador)'</code>. Dispara correo de notificación al Supervisor titular de la plaza.",
                            impactoEstado: "Habilita la transición final hacia el estado 'Finalizado / Histórico'.",
                            reglasNegocio: "<strong>Garantía de Cierre:</strong> Ningún ticket puede ser archivado ni cerrado contablemente si el Administrador no ha ejecutado previamente este botón."
                        },
                        {
                            nombre: "Notificar Recordatorio a Corporativos",
                            color: "badge-btn-ambar",
                            icono: "🔔",
                            pantalla: "Bandeja Documentos Contables",
                            proposito: "Enviar un aviso preventivo por correo electrónico a Dirección Corporativa cuando una orden de alto valor esté pendiente de registro contable.",
                            proceso: "Ejecuta <code>POST /api/facturas/notificar_recordatorio_doc_contable</code> disparando <code>enviar_correo_recordatorio_doc_contable</code>.",
                            impactoEstado: "No muta el estado; genera una alerta transaccional para acelerar la gestión contable.",
                            reglasNegocio: "Solo disponible para facturas aprobadas fiscalmente que carecen de número contable tras 48 horas de la entrega."
                        }
                    ]
                },
                {
                    id: "admin-cobertura",
                    nombre: "Cobertura de Supervisión (Suplencia)",
                    icono: "🤝",
                    descripcion: "Herramienta de continuidad operativa. Permite al Administrador intervenir directamente en la bandeja de supervisión cuando el titular de la plaza se encuentra ausente o de vacaciones.",
                    botones: [
                        {
                            nombre: "Asumir Proceso / Aprobar en Cobertura",
                            color: "badge-btn-purple",
                            icono: "🛡️",
                            pantalla: "Cotizaciones y Órdenes (Modo Cobertura)",
                            proposito: "Aprobar cotizaciones estándar ($\le \$10,000$ MXN) y asignar Números de Orden de Compra y Pedido en sustitución temporal del Supervisor.",
                            proceso: "Ejecuta <code>POST /api/facturas/confirmar_admin</code>. Genera la orden oficial y notifica al taller mecánico para que inicie la compra de refacciones e intervención física.",
                            impactoEstado: "Transiciona el ticket a 'En Reparación (Taller)'.",
                            reglasNegocio: "<strong>Trazabilidad Obligatoria:</strong> El sistema estampa en base de datos: <code>aprobado_por_suplencia = true</code> y <code>supervisor_aprobador = '[Nombre] (Administrador en Cobertura)'</code>. <br><strong>Bloqueo Estricto:</strong> Si el ticket supera $10,000 y pertenece a Corporativos, el botón se bloquea automáticamente mostrando el candado <code>🔒 Flujo Estricto Corp (Sin Cobertura)</code>."
                        },
                        {
                            nombre: "Validar PIN de Entrega (en Cobertura)",
                            color: "badge-btn-cyan",
                            icono: "🔑",
                            pantalla: "Modal Validar PIN OTP",
                            proposito: "Recibir el código confidencial de 8 dígitos presentado por el chofer y certificar la salida de la unidad del taller mecánico.",
                            proceso: "Ejecuta <code>POST /api/facturas/validar_codigo</code>. Compara el PIN ingresado contra el <code>codigo_liberacion</code> en <code>facturas.json</code>. Si coincide, marca <code>entregado = 'Sí'</code>.",
                            impactoEstado: "Transiciona de 'Validación / Pin (Chofer)' a 'Esperando Facturación (Taller)'.",
                            reglasNegocio: "Requiere coincidencia exacta de los 8 dígitos. La unidad queda habilitada de inmediato en el catálogo vehicular."
                        },
                        {
                            nombre: "Revisar y Validar CFDI (en Cobertura)",
                            color: "badge-btn-verde",
                            icono: "📑",
                            pantalla: "Bandeja Facturas Finales",
                            proposito: "Cotejar la factura electrónica emitida ante el SAT (PDF y XML) contra los conceptos autorizados en la orden de compra.",
                            proceso: "Ejecuta <code>POST /api/facturas/validar_fiscal</code>, estampando <code>validado_fiscal_por = 'Administrador en Cobertura: [Nombre]'</code>.",
                            impactoEstado: "Transiciona de 'Esperando Rev/Factura' a 'Esperando Num. Contable'.",
                            reglasNegocio: "Solo procede si el taller ya subió satisfactoriamente ambos archivos (PDF y XML válidos)."
                        }
                    ]
                },
                {
                    id: "admin-analitica-archivo",
                    nombre: "Analítica, Auditoría y Archivo",
                    icono: "📊",
                    descripcion: "Control gerencial y cierre del ciclo de vida de los tickets de servicio.",
                    botones: [
                        {
                            nombre: "Descargar Reporte Excel",
                            color: "badge-btn-verde",
                            icono: "📥",
                            pantalla: "Vista Analítica",
                            proposito: "Generar un libro de cálculo formal en Excel (.xlsx) con el desglose acumulado de gastos, talleres, órdenes y tiempos de atención.",
                            proceso: "Invoca al backend en <code>/api/analitica/exportar_excel</code>. Procesa los registros en memoria mediante <strong>Pandas y OpenPyXL</strong> y descarga el archivo automáticamente.",
                            impactoEstado: "No muta la base de datos; genera un informe ejecutivo para auditoría contable.",
                            reglasNegocio: "Aplica filtros automáticos excluyendo tickets eliminados lógicamente o cancelados."
                        },
                        {
                            nombre: "Archivar Expediente Definitivo",
                            color: "badge-btn-rojo",
                            icono: "🗄️",
                            pantalla: "Vista Archivo General",
                            proposito: "Mover el ticket completado de la colección activa a la base de datos histórica inmutable.",
                            proceso: "Ejecuta <code>POST /api/facturas/archivar_final</code>. Retira el ticket de <code>facturas.json</code> y lo almacena de manera permanente en <code>tickets_archivados.json</code> estampando <code>archivado_por</code> y fecha exacta.",
                            impactoEstado: "Pasa al estado final 'Finalizado / Histórico'. Cierra definitivamente el expediente.",
                            reglasNegocio: "<strong>Requisito Indispensable:</strong> Solo se puede archivar si <code>doc50_liberado == true</code>. Si falta el documento contable, la acción queda bloqueada por el sistema."
                        }
                    ]
                }
            ]
        },

        "Supervisor": {
            titulo: "Manual Operativo - Supervisor Automotriz",
            badgeClase: "badge-super",
            descripcionPerfil: "Como <strong>Supervisor de Zona Automotriz</strong>, eres el responsable técnico y operativo directo de las unidades y talleres de tu centro de trabajo (COPE). Tus atribuciones abarcan la <strong>recepción y asignación de reportes</strong> de los choferes, la <strong>autorización de cotizaciones estándar ($\le \$10,000$ MXN)</strong> con asignación de órdenes de compra, la <strong>validación presencial del PIN de liberación</strong> para la entrega física de los autos, la <strong>revisión fiscal de CFDIs</strong> y la gestión del catálogo de unidades vehiculares.",
            modulos: [
                {
                    id: "super-reportes",
                    nombre: "Bandeja de Reportes",
                    icono: "📥",
                    descripcion: "Recepción de averías levantadas por los operadores en campo y su correspondiente canalización a talleres mecánicos externos.",
                    botones: [
                        {
                            nombre: "Revisar y Asignar Taller",
                            color: "badge-btn-ambar",
                            icono: "🔧",
                            pantalla: "Bandeja de Reportes",
                            proposito: "Evaluar la falla reportada por el chofer y canalizar el vehículo averiado al taller mecánico más adecuado de la cobertura territorial.",
                            proceso: "Abre el modal <code>modal-asignar-taller</code>. El supervisor selecciona el taller proveedor de su lista autorizada y define la compañía fiscalizadora (<strong>Telnor</strong> o <strong>RUMN</strong>). Al confirmar, ejecuta <code>POST /api/reportes/asignar</code> y envía correo formal con los datos de la unidad al taller (<code>enviar_correo_nueva_orden</code>).",
                            impactoEstado: "El reporte cambia de 'Pendiente / Asig. Taller' a 'Pendiente de Cotización'.",
                            reglasNegocio: "Solo se pueden seleccionar talleres que tengan cobertura activa en la ciudad y COPE del supervisor. La compañía asignada rige la facturación final."
                        },
                        {
                            nombre: "💬 Comentarios del Ticket",
                            color: "badge-btn-azul",
                            icono: "💬",
                            pantalla: "Bandeja de Reportes / Tabla General",
                            proposito: "Agregar notas internas, aclaraciones o historial operativo visible para todo el equipo automotriz.",
                            proceso: "Abre el modal de notas y guarda el texto en el campo <code>comentarios</code> junto con el autor y la fecha.",
                            impactoEstado: "No altera el estado del ticket; añade trazabilidad operativa.",
                            reglasNegocio: "Cualquier supervisor o administrador del COPE puede consultar y actualizar los comentarios."
                        },
                        {
                            nombre: "Eliminar Reporte (Baja Lógica)",
                            color: "badge-btn-rojo",
                            icono: "🗑️",
                            pantalla: "Bandeja de Reportes",
                            proposito: "Descartar un reporte erróneo, duplicado o levantado por equivocación por un chofer.",
                            proceso: "Ejecuta <code>POST /api/reportes/eliminar</code>, estampando <code>eliminado_por</code> con el nombre del usuario y la fecha.",
                            impactoEstado: "El ticket se oculta de las bandejas operativas y no computa en las métricas de gasto.",
                            reglasNegocio: "Solo aplica a reportes que aún no han sido asignados ni cotizados por un taller."
                        }
                    ]
                },
                {
                    id: "super-cotizaciones",
                    nombre: "Cotizaciones y Órdenes de Trabajo",
                    icono: "📑",
                    descripcion: "Evaluación técnica de costos mecánicos, asignación de números de orden de compra y entrega física controlada.",
                    botones: [
                        {
                            nombre: "Revisar / Desglosar Cotización",
                            color: "badge-btn-cyan",
                            icono: "🔎",
                            pantalla: "Cotizaciones y Órdenes",
                            proposito: "Inspeccionar las refacciones, costo de mano de obra y presupuesto PDF enviado por el taller mecánico.",
                            proceso: "Despliega el modal de detalle con precios unitarios, evidencias fotográficas subidas por el taller y el desglose de conceptos.",
                            impactoEstado: "Mantiene el ticket en 'Esperando / Aprob. Cotizacion (Supervisor)'.",
                            reglasNegocio: "Permite al supervisor evaluar si el costo de refacciones es razonable y si la falla amerita las piezas presupuestadas."
                        },
                        {
                            nombre: "Aprobar Cotización y Asignar Orden",
                            color: "badge-btn-verde",
                            icono: "✅",
                            pantalla: "Modal de Aprobación de Cotización",
                            proposito: "Validar técnicamente los costos e ingresar los Números de Orden de Compra y Pedido de la empresa.",
                            proceso: "Ejecuta <code>POST /api/facturas/confirmar_admin</code> capturando <code>numero_orden</code>, <code>numero_cotizacion_asignacion</code> y el PDF de orden oficial.",
                            impactoEstado: "<strong>Si el precio es $\le \$10,000$:</strong> Transiciona directo a 'En Reparación (Taller)' y notifica al taller para iniciar trabajos físicos (<code>enviar_correo_taller_aprobado</code>).<br><strong>Si el precio es $> \$10,000$:</strong> Guarda la orden preliminar y transiciona a 'Esperando / Aprob. Cotizacion (Admin)' notificando al Administrador.",
                            reglasNegocio: "Garantiza que ningún trabajo mecánico inicie sin un número formal de orden de compra emitido por la empresa."
                        },
                        {
                            nombre: "Rechazar Cotización con Sugerencias",
                            color: "badge-btn-ambar",
                            icono: "⚠️",
                            pantalla: "Modal de Cotización",
                            proposito: "Solicitar al taller que ajuste sus precios a los tabuladores autorizados de la empresa.",
                            proceso: "Abre tabla donde el supervisor ingresa precios máximos autorizables por concepto y despacha correo al taller con las observaciones (<code>POST /api/facturas/rechazar_super</code>).",
                            impactoEstado: "El ticket pasa a 'Correcciones/Taller'.",
                            reglasNegocio: "El taller recibe las sugerencias y puede modificar sus costos para someter a segunda revisión sin cancelar la orden."
                        },
                        {
                            nombre: "Cancelar por Cotización Cara (Incosteable)",
                            color: "badge-btn-rojo",
                            icono: "🚫",
                            pantalla: "Modal de Cotización",
                            proposito: "Declarar inviable la reparación de una unidad cuando el costo supere el valor comercial del vehículo o el límite patrimonial.",
                            proceso: "Ejecuta <code>POST /api/facturas/cancelar_cotizacion</code>. Marca el estado de la factura como <code>Cancelado_Cotizacion_Cara</code> y actualiza automáticamente <code>unidades.json</code> marcando la unidad con <code>Estado: 'Inactiva'</code>.",
                            impactoEstado: "Transiciona al estado 'Incosteable'. El vehículo queda bloqueado en el sistema para futuros reportes.",
                            reglasNegocio: "Inhabilita patrimonialmente la unidad para evitar gastos mayores en vehículos obsoletos."
                        },
                        {
                            nombre: "Validar PIN de Entrega (Match de Seguridad)",
                            color: "badge-btn-verde",
                            icono: "🔑",
                            pantalla: "Modal Validar PIN OTP",
                            proposito: "Verificar presencialmente el retiro del vehículo del taller cuando el chofer acude por él.",
                            proceso: "El chofer proporciona su código numérico confidencial de 8 dígitos recibido en su correo. El supervisor lo introduce en el modal y el sistema ejecuta <code>POST /api/facturas/validar_codigo</code>.",
                            impactoEstado: "Al existir coincidencia exacta, <code>entregado</code> pasa a 'Sí'. La unidad se libera físicamente y el ticket transiciona a 'Esperando Facturación (Taller)'.",
                            reglasNegocio: "<strong>Seguridad Asimétrica:</strong> El supervisor nunca conoce el código PIN con anticipación; solo el chofer lo recibe. Esto evita retiros no autorizados de vehículos."
                        }
                    ]
                },
                {
                    id: "super-fiscal-unidades",
                    nombre: "Facturas Fiscales y Gestión de Flota",
                    icono: "🚗",
                    descripcion: "Validación de comprobantes fiscales digitales del SAT y administración del parque vehicular.",
                    botones: [
                        {
                            nombre: "Aprobar Factura Fiscal",
                            color: "badge-btn-verde",
                            icono: "📑",
                            pantalla: "Bandeja Facturas Finales",
                            proposito: "Validar que los archivos PDF y XML emitidos por el taller coinciden con el importe y conceptos de la orden autorizada.",
                            proceso: "Ejecuta <code>POST /api/facturas/validar_fiscal</code> marcando <code>validacion_fiscal = 'Aprobada'</code> y estampando el nombre del supervisor.",
                            impactoEstado: "Transiciona de 'Esperando Rev/Factura' a 'Esperando Num. Contable'.",
                            reglasNegocio: "Revisa que la factura esté a nombre de la razón social asignada (Telnor o RUMN) y que el RFC emisor concuerde con el taller."
                        },
                        {
                            nombre: "+ Agregar Unidad",
                            color: "badge-btn-verde",
                            icono: "➕",
                            pantalla: "Directorio de Unidades",
                            proposito: "Dar de alta un nuevo vehículo en el catálogo del parque automotriz.",
                            proceso: "Abre modal para capturar Número Económico, Marca, Modelo, Año, Placas y COPE de adscripción en <code>unidades.json</code>.",
                            impactoEstado: "La unidad queda registrada inmediatamente con estado 'Activa'.",
                            reglasNegocio: "El número económico debe ser único y de 4 dígitos."
                        },
                        {
                            nombre: "Editar Unidad / Cambiar Estatus",
                            color: "badge-btn-azul",
                            icono: "✏️",
                            pantalla: "Directorio de Unidades",
                            proposito: "Modificar especificaciones vehiculares o alternar el estado entre Activa / Inactiva.",
                            proceso: "Actualiza el registro en <code>unidades.json</code> vía <code>POST /api/unidades/guardar</code>.",
                            impactoEstado: "Si se marca Inactiva, el sistema bloquea inmediatamente cualquier nuevo reporte para ese vehículo.",
                            reglasNegocio: "No se puede editar ni inactivar una unidad que tenga un ticket abierto en proceso activo en taller."
                        }
                    ]
                }
            ]
        },

        "Taller": {
            titulo: "Manual Operativo - Portal Taller / Proveedor",
            badgeClase: "badge-taller",
            descripcionPerfil: "Como <strong>Taller Mecánico Proveedor Autorizado</strong>, eres el eslabón operativo fundamental en la reparación física de los vehículos de Telnor y RUMN. Tu portal te permite <strong>recibir asignaciones de unidades averiadas</strong>, <strong>elaborar y desglosar cotizaciones técnicas</strong> con evidencias fotográficas, <strong>descargar órdenes de compra oficiales</strong>, <strong>marcar unidades listas para entrega</strong> (disparando el PIN de seguridad al chofer) y <strong>subir tus comprobantes fiscales CFDI (PDF y XML)</strong> para trámite de pago.",
            modulos: [
                {
                    id: "taller-tickets",
                    nombre: "Tickets de Trabajo (Asignaciones)",
                    icono: "🔧",
                    descripcion: "Bandeja de entrada donde aterrizan los vehículos que la administración te ha canalizado para diagnóstico y reparación.",
                    botones: [
                        {
                            nombre: "Crear Cotización / Presupuesto",
                            color: "badge-btn-ambar",
                            icono: "📝",
                            pantalla: "Bandeja Tickets de Trabajo",
                            proposito: "Formular la propuesta técnico-económica de refacciones y mano de obra tras inspeccionar físicamente el vehículo en tu taller.",
                            proceso: "Abre el formulario modal de cotización. Permite agregar múltiples conceptos (título, precio, mantenimiento preventivo/correctivo), adjuntar tu archivo formal de presupuesto en PDF y subir fotografías de evidencia de las piezas dañadas. Al enviar, ejecuta <code>POST /api/facturas/nueva</code>.",
                            impactoEstado: "Crea el registro formal en <code>facturas.json</code> y mueve el ticket a 'Esperando / Aprob. Cotizacion (Supervisor)'. Notifica por correo al Supervisor.",
                            reglasNegocio: "Todos los campos de costo deben ser numéricos y es obligatorio adjuntar al menos una evidencia fotográfica del daño."
                        },
                        {
                            nombre: "Ver Reporte de Falla del Chofer",
                            color: "badge-btn-azul",
                            icono: "📋",
                            pantalla: "Bandeja Tickets de Trabajo",
                            proposito: "Consultar las observaciones originales registradas por el conductor que entregó el vehículo averiado.",
                            proceso: "Despliega una tarjeta con los datos de kilometraje, celular del empleado, departamento, tipo de falla descrita y firma digital del chofer.",
                            impactoEstado: "Solo lectura; no modifica estados.",
                            reglasNegocio: "Permite al mecánico orientar su diagnóstico inicial basándose en la sintomatología descrita por el chofer."
                        }
                    ]
                },
                {
                    id: "taller-cotizaciones",
                    nombre: "Cotizaciones en Proceso y Reparación",
                    icono: "⚙️",
                    descripcion: "Seguimiento de autorizaciones, recepción de órdenes de compra y notificación de conclusión de trabajos.",
                    botones: [
                        {
                            nombre: "Ver Orden de Compra Aprobada",
                            color: "badge-btn-verde",
                            icono: "📜",
                            pantalla: "Bandeja de Cotizaciones",
                            proposito: "Descargar y visualizar el documento oficial que ampara el presupuesto autorizado por la empresa.",
                            proceso: "Abre o descarga el archivo PDF de orden oficial emitido por la administración con el Número de Orden y de Pedido autorizados.",
                            impactoEstado: "Confirma que el ticket se encuentra en 'En Reparación (Taller)'.",
                            reglasNegocio: "<strong>Regla de Oro del Proveedor:</strong> NUNCA inicies compras de refacciones ni trabajos mecánicos hasta ver el botón verde de Orden Aprobada."
                        },
                        {
                            nombre: "Corregir Cotización Rechazada",
                            color: "badge-btn-ambar",
                            icono: "🔄",
                            pantalla: "Cotizaciones Rechazadas",
                            proposito: "Ajustar los precios unitarios de los conceptos observados conforme a las recomendaciones enviadas por el supervisor.",
                            proceso: "Abre modal precargado con los montos anteriores y las sugerencias del supervisor. Al guardar, ejecuta <code>POST /api/facturas/corregir_cotizacion_rechazada</code>.",
                            impactoEstado: "Regresa el ticket a 'Esperando / Aprob. Cotizacion (Supervisor)' para su reaprobación.",
                            reglasNegocio: "Permite corregir el presupuesto sin necesidad de crear un ticket nuevo desde cero."
                        },
                        {
                            nombre: "Marcar Unidad Lista para Entrega",
                            color: "badge-btn-cyan",
                            icono: "🏁",
                            pantalla: "Cotizaciones en Reparación",
                            proposito: "Notificar oficialmente a la empresa que los trabajos físicos han concluido y que el auto está listo para su retiro.",
                            proceso: "Ejecuta <code>POST /api/facturas/marcar_lista</code>. El sistema genera de forma criptográfica un <strong>Código PIN OTP de 8 dígitos</strong> y lo despacha de inmediato y exclusivamente al correo del chofer (<code>enviar_correo_liberacion</code>).",
                            impactoEstado: "Transiciona el ticket a 'Validación / Pin (Chofer)'. Notifica al Supervisor que el auto está terminado (sin revelarle el PIN).",
                            reglasNegocio: "Solo se puede pulsar una vez completada la reparación al 100%. Desencadena el protocolo de seguridad de entrega física."
                        }
                    ]
                },
                {
                    id: "taller-facturacion",
                    nombre: "Facturación Fiscal y Cobranza",
                    icono: "💰",
                    descripcion: "Carga de comprobantes fiscales digitales tras la entrega presencial de la unidad al conductor.",
                    botones: [
                        {
                            nombre: "Subir Factura Final (PDF + XML)",
                            color: "badge-btn-verde",
                            icono: "📤",
                            pantalla: "Bandeja de Facturas",
                            proposito: "Cargar la factura formal emitida ante el SAT para radicar el trámite de cobro del servicio concluido.",
                            proceso: "Abre modal de carga de archivos binarios vía <code>FormData</code>. Requiere seleccionar obligatoriamente dos archivos: el comprobante en formato PDF y el archivo fiscal en XML. Ejecuta <code>POST /api/facturas/subir_factura_final</code>.",
                            impactoEstado: "Mueve el ticket a 'Esperando Rev/Factura' y notifica al Supervisor de la plaza para su validación fiscal.",
                            reglasNegocio: "<strong>Requisito Estricto:</strong> Ambos archivos son indispensables. El sistema rechaza cargas que solo incluyan el PDF o solo el XML. El folio fiscal y montos deben coincidir con la orden de compra."
                        },
                        {
                            nombre: "Confirmar y Descargar PDF (Credencial)",
                            color: "badge-btn-azul",
                            icono: "🪪",
                            pantalla: "Modal Mi Perfil",
                            proposito: "Generar la credencial oficial y cédula de registro del taller mecánico en el sistema.",
                            proceso: "Utiliza la librería cliente <code>html2pdf.js</code> para renderizar y descargar una credencial digital en formato PDF con los datos y logo del taller.",
                            impactoEstado: "No altera estados de tickets; sirve para acreditación física ante choferes.",
                            reglasNegocio: "Disponible permanentemente en el encabezado del perfil de proveedor."
                        }
                    ]
                }
            ]
        },

        "Chofer": {
            titulo: "Manual Operativo - Chofer / Operador de Vehículo",
            badgeClase: "badge-chofer",
            descripcionPerfil: "Como <strong>Chofer u Operador de Flota</strong> de Telnor y RUMN, tu rol es el punto de partida del mantenimiento automotriz. Eres el encargado de <strong>reportar cualquier avería mecánica o solicitar servicios preventivos</strong> a través del formulario oficial. Tu <strong>correo electrónico es estrictamente obligatorio</strong>, ya que ahí recibirás el folio de seguimiento y el <strong>Código Secreto de 8 dígitos (PIN OTP)</strong> con el cual podrás recoger tu unidad físicamente una vez reparada en el taller.",
            modulos: [
                {
                    id: "chofer-reporte",
                    nombre: "Levantamiento de Reporte de Falla",
                    icono: "⚠️",
                    descripcion: "Proceso público de notificación de averías mecánicas y solicitud de servicio para vehículos oficiales.",
                    botones: [
                        {
                            nombre: "Campo No. Económico (Unidad)",
                            color: "badge-btn-azul",
                            icono: "🚗",
                            pantalla: "Formulario de Reporte (/reportar)",
                            proposito: "Identificar el vehículo de la empresa que presenta la avería o requiere mantenimiento preventivo.",
                            proceso: "Al ingresar los 4 dígitos del número económico (ej. '1212'), el formulario consulta automáticamente <code>/api/estado_unidad/<eco></code>. Rellena de forma inteligente la Marca, Modelo y Año desde la base de datos oficial.",
                            impactoEstado: "Si el vehículo está en taller o inactivo, alerta de inmediato en pantalla.",
                            reglasNegocio: "<strong>Filtros de Seguridad:</strong> El sistema rechaza reportes si el vehículo está marcado en 'Jurídicos', si está en estatus 'Inactiva/Incosteable', o si ya tiene una orden activa en reparación."
                        },
                        {
                            nombre: "Campo Email (Correo Electrónico Obligatorio)",
                            color: "badge-btn-ambar",
                            icono: "📧",
                            pantalla: "Formulario de Reporte (/reportar)",
                            proposito: "Garantizar la entrega de acuses de recibo y del código de seguridad para retirar el auto reparado.",
                            proceso: "Validado en 3 capas: atributo HTML <code>required</code>, validador JavaScript con expresión regular estándar, y validación estricta en el servidor Python que rechaza campos vacíos o valores nulos.",
                            impactoEstado: "Sin correo válido, el reporte no es admitido en la base de datos.",
                            reglasNegocio: "Debe ser un correo con formato válido (ej. <code>usuario@dominio.com</code>). <strong>Crítico:</strong> En esta dirección recibirás el PIN de 8 dígitos para recoger tu carro."
                        },
                        {
                            nombre: "Seleccionar Tipo de Mantenimiento",
                            color: "badge-btn-cyan",
                            icono: "🔄",
                            pantalla: "Formulario de Reporte (/reportar)",
                            proposito: "Clasificar si el servicio es un Preventivo programado (afinación, frenos, aceite) o un Correctivo por falla imprevista.",
                            proceso: "Tarjetas interactivas de color azul (Preventivo) o rojo (Correctivo) que asignan el valor correspondiente al reporte.",
                            impactoEstado: "Define la prioridad y categorización del ticket en las bandejas de supervisión.",
                            reglasNegocio: "Selección obligatoria para enviar el formulario."
                        },
                        {
                            nombre: "Limpiar Firma (HTML5 Canvas)",
                            color: "badge-btn-gray",
                            icono: "🧹",
                            pantalla: "Lienzo de Firma Manuscrita",
                            proposito: "Borrar el trazo del lienzo táctil si cometiste un error para volver a firmar limpiamente.",
                            proceso: "Ejecuta <code>limpiarFirma()</code> reseteando el canvas bidimensional.",
                            impactoEstado: "No muta la base de datos.",
                            reglasNegocio: "El formulario exige obligatoriamente una firma dibujada antes de habilitar el envío."
                        },
                        {
                            nombre: "Enviar Reporte de Falla",
                            color: "badge-btn-verde",
                            icono: "🚀",
                            pantalla: "Formulario de Reporte (/reportar)",
                            proposito: "Transmitir formalmente el reporte al departamento de Automotriz y generar el ticket oficial de servicio.",
                            proceso: "Envía los datos a <code>POST /api/reportes/nuevo</code>. Genera el folio único <code>REP-YYYYMMDDHHMMSS</code>, codifica tu firma en Base64 y despacha un correo de confirmación a tu buzón y una alerta al supervisor de tu COPE.",
                            impactoEstado: "Crea el ticket en estado 'Pendiente / Asig. Taller' dentro de <code>reportes.json</code>.",
                            reglasNegocio: "Valida que el COPE territorial cuente con Administrador y Supervisor registrados para asegurar que tu vehículo reciba atención inmediata."
                        }
                    ]
                },
                {
                    id: "chofer-entrega",
                    nombre: "Proceso de Recolección y Código PIN OTP",
                    icono: "🔐",
                    descripcion: "Procedimiento obligatorio para recoger tu vehículo reparado en las instalaciones del taller.",
                    botones: [
                        {
                            nombre: "Código de Liberación de 8 Dígitos (PIN OTP)",
                            color: "badge-btn-purple",
                            icono: "📱",
                            pantalla: "Buzón de Correo / SMS del Chofer",
                            proposito: "Clave criptográfica única y confidencial que autoriza la salida física del vehículo reparado.",
                            proceso: "Cuando el taller termina el trabajo y presiona 'Marcar como Lista', el servidor genera automáticamente este código secreto y te lo envía únicamente a tu correo y teléfono.",
                            impactoEstado: "Al presentarlo en el taller ante el supervisor, se realiza el 'Match' y el auto pasa a estado entregado.",
                            reglasNegocio: "<strong>Privacidad Absoluta:</strong> Ni el taller mecánico ni el supervisor conocen este PIN. Solo tú lo posees en tu correo. Preséntalo físicamente al retirar tu unidad."
                        }
                    ]
                }
            ]
        },

        "Corporativos": {
            titulo: "Manual Operativo - Dirección Corporativa",
            badgeClase: "badge-corp",
            descripcionPerfil: "Como miembro de la <strong>Dirección Corporativa</strong>, funges como el <strong>Filtro de Fiscalización Financiera y Auditoría Ejecutiva</strong>. Tu intervención se enfoca exclusivamente en auditar y autorizar los presupuestos de reparación de alto impacto que superan los <strong>$10,000 MXN</strong>, consultar el repositorio inmutable de expedientes y supervisar el destino del gasto de capital de la flota.",
            modulos: [
                {
                    id: "corp-cotizaciones",
                    nombre: "Bandeja de Autorizaciones Mayores (+10,000)",
                    icono: "💎",
                    descripcion: "Revisión ejecutiva de presupuestos extraordinarios canalizados por el Administrador central.",
                    botones: [
                        {
                            nombre: "Aprobar Gasto Financiero",
                            color: "badge-btn-verde",
                            icono: "✅",
                            pantalla: "Bandeja de Cotizaciones",
                            proposito: "Autorizar formalmente el presupuesto de alto valor para que el taller comience los trabajos físicos.",
                            proceso: "Ejecuta <code>POST /api/facturas/confirmar_corp</code> marcando <code>aprobado_corp = true</code>. Se completa la triple autorización requerida.",
                            impactoEstado: "Mueve el ticket a 'En Reparación (Taller)' y despacha notificación formal a taller y supervisor.",
                            reglasNegocio: "Indispensable para cualquier servicio automotriz mayor a $10,000 MXN."
                        },
                        {
                            nombre: "Rechazar Gasto con Justificación",
                            color: "badge-btn-rojo",
                            icono: "❌",
                            pantalla: "Bandeja de Cotizaciones",
                            proposito: "Negar la autorización del presupuesto cuando el costo sea financieramente desproporcionado.",
                            proceso: "Ejecuta <code>POST /api/facturas/rechazar_corp</code> solicitando un motivo explícito que se envía por correo al Administrador.",
                            impactoEstado: "Regresa el ticket a 'Correcciones/Taller' o deriva a 'Incosteable'.",
                            reglasNegocio: "Exige capturar una justificación ejecutiva que queda grabada en el historial de auditoría."
                        }
                    ]
                },
                {
                    id: "corp-archivo",
                    nombre: "Repositorio Gerencial y Auditoría",
                    icono: "🗄️",
                    descripcion: "Consulta inmutable de todos los servicios automotrices concluidos y facturas pagadas históricamente.",
                    botones: [
                        {
                            nombre: "Buscador y Filtro de Expedientes",
                            color: "badge-btn-azul",
                            icono: "🔍",
                            pantalla: "Archivo General",
                            proposito: "Rastrear antecedentes mecánicos, folios fiscales y costos acumulados por número de unidad o taller proveedor.",
                            proceso: "Filtra en tiempo real los registros de <code>tickets_archivados.json</code>.",
                            impactoEstado: "Consulta de sólo lectura sin alteración de datos.",
                            reglasNegocio: "Herramienta definitiva para auditorías de compras y seguimiento del ciclo de vida del parque vehicular."
                        }
                    ]
                }
            ]
        }
    };

    // -------------------------------------------------------------
    // DETECCIÓN DINÁMICA DEL PERFIL AUTENTICADO
    // -------------------------------------------------------------
    function detectarPerfilActual() {
        // 1. Revisar si estamos en reporte.html (Chofer)
        if (document.getElementById("form-reporte-externo") || window.location.pathname.includes("reportar")) {
            return "Chofer";
        }

        // 2. Revisar si hay un subrol-actual (Administración: Administrador, Supervisor, Jefatura)
        const subrolInput = document.getElementById("subrol-actual");
        if (subrolInput && subrolInput.value) {
            const sub = subrolInput.value.trim();
            if (sub === "Supervisor") return "Supervisor";
            if (sub === "Administrador") return "Administrador";
            if (sub === "Jefatura") return "Administrador"; // Jefatura tiene acceso al manual administrativo
        }

        // 3. Revisar rol-actual
        const rolInput = document.getElementById("rol-actual");
        if (rolInput && rolInput.value) {
            const rol = rolInput.value.trim();
            if (rol === "proveedores") return "Taller";
            if (rol === "corporativos") return "Corporativos";
            if (rol === "administracion") return "Administrador";
        }

        // 4. Revisar la URL como respaldo
        const path = window.location.pathname;
        if (path.includes("proveedores")) return "Taller";
        if (path.includes("corporativos")) return "Corporativos";
        if (path.includes("administracion")) return "Supervisor";

        return "Chofer"; // Fallback por defecto
    }

    // -------------------------------------------------------------
    // CONSTRUCCIÓN DEL MODAL DINÁMICO EN EL DOM
    // -------------------------------------------------------------
    let tabActivaId = null;

    function renderizarManual(perfil) {
        const datos = DATOS_MANUAL[perfil] || DATOS_MANUAL["Chofer"];

        let modalExistente = document.getElementById("modal-ayuda");
        if (!modalExistente) {
            modalExistente = document.createElement("div");
            modalExistente.id = "modal-ayuda";
            modalExistente.className = "manual-overlay";
            document.body.appendChild(modalExistente);
        } else {
            modalExistente.className = "manual-overlay";
        }

        // Configurar tab inicial
        if (!tabActivaId || !datos.modulos.some(m => m.id === tabActivaId)) {
            tabActivaId = datos.modulos[0]?.id || "";
        }

        let tabsHtml = "";
        let modulosHtml = "";
        let totalBotones = 0;

        datos.modulos.forEach((mod, idx) => {
            const isActive = mod.id === tabActivaId;
            totalBotones += mod.botones.length;

            tabsHtml += `
                <button type="button" class="manual-tab-btn ${isActive ? 'active' : ''}" onclick="window.cambiarTabManual('${mod.id}')">
                    <span>${mod.icono} ${mod.nombre}</span>
                    <span class="manual-tab-count">${mod.botones.length}</span>
                </button>
            `;

            let botonesHtml = "";
            mod.botones.forEach((btn, bIdx) => {
                botonesHtml += `
                    <div class="manual-card" data-manual-btn="${btn.nombre.toLowerCase()} ${btn.proposito.toLowerCase()} ${mod.nombre.toLowerCase()}">
                        <div class="manual-card-header" onclick="window.toggleManualAccordion(this)">
                            <div class="manual-btn-meta">
                                <span class="manual-badge-accion ${btn.color}">
                                    <span>${btn.icono}</span>
                                    <span>${btn.nombre}</span>
                                </span>
                                <span class="manual-btn-screen-tag">📍 ${btn.pantalla}</span>
                            </div>
                            <span class="manual-card-arrow">▼</span>
                        </div>
                        <div class="manual-card-body">
                            <div class="manual-card-content">
                                <div class="manual-info-row">
                                    <div class="manual-info-label">🎯 Propósito Operativo:</div>
                                    <div class="manual-info-desc">${btn.proposito}</div>
                                </div>
                                <div class="manual-info-row">
                                    <div class="manual-info-label">⚙️ Proceso Técnico:</div>
                                    <div class="manual-info-desc">${btn.proceso}</div>
                                </div>
                                <div class="manual-info-row">
                                    <div class="manual-info-label">🚦 Impacto en Ticket:</div>
                                    <div class="manual-info-desc">
                                        <span class="manual-state-change">${btn.impactoEstado}</span>
                                    </div>
                                </div>
                                <div class="manual-info-row">
                                    <div class="manual-info-label">⚖️ Reglas & Validaciones:</div>
                                    <div class="manual-info-desc">
                                        <div class="manual-rule-callout">${btn.reglasNegocio}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            modulosHtml += `
                <div id="manual-panel-${mod.id}" class="manual-panel-content" style="display: ${isActive ? 'block' : 'none'};">
                    <div class="manual-panel-intro">
                        <h4>${mod.icono} ${mod.nombre}</h4>
                        <p>${mod.descripcion}</p>
                    </div>
                    <div class="manual-section-title">
                        <span>🔘 Botones de Acción y Controles (${mod.botones.length})</span>
                    </div>
                    <div class="manual-accordion">
                        ${botonesHtml}
                    </div>
                </div>
            `;
        });

        modalExistente.innerHTML = `
            <div class="manual-container" onclick="event.stopPropagation()">
                <!-- Header -->
                <div class="manual-header">
                    <div class="manual-header-title">
                        <span style="font-size: 1.6rem;">📖</span>
                        <div>
                            <h3>${datos.titulo}</h3>
                            <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 2px;">Sistema de Facturación Central (Telnor / RUMN)</div>
                        </div>
                        <span class="manual-badge-perfil ${datos.badgeClase}">Rol: ${perfil}</span>
                    </div>
                    <button type="button" class="manual-btn-close" onclick="window.cerrarManualSistema()" title="Cerrar Manual">&times;</button>
                </div>

                <!-- Barra de Búsqueda y Estadísticas -->
                <div class="manual-toolbar">
                    <div class="manual-search-box">
                        <span class="manual-search-icon">🔍</span>
                        <input type="text" id="manual-buscador" placeholder="Buscar botón, regla de negocio, endpoint o pantalla..." onkeyup="window.filtrarManual(this.value)">
                    </div>
                    <div class="manual-stats-badge">
                        <span>Total de Controles Documentados: <strong>${totalBotones} botones</strong></span>
                    </div>
                </div>

                <!-- Cuerpo: Tabs a la izquierda y Contenido a la derecha -->
                <div class="manual-body">
                    <div class="manual-tabs-nav">
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; padding: 4px 8px; letter-spacing: 0.5px;">Módulos del Perfil</div>
                        ${tabsHtml}
                    </div>
                    <div class="manual-content-area" id="manual-content-area">
                        <div style="background: rgba(30, 41, 59, 0.4); border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; font-size: 0.92rem; border-left: 4px solid #38bdf8; line-height: 1.6;">
                            ${datos.descripcionPerfil}
                        </div>
                        ${modulosHtml}
                    </div>
                </div>

                <!-- Footer -->
                <div class="manual-footer">
                    <div class="manual-footer-note">
                        💡 Haz clic en cualquier tarjeta de botón para desplegar u ocultar su ficha técnica completa.
                    </div>
                    <button type="button" class="manual-btn-done" onclick="window.cerrarManualSistema()">Entendido, cerrar manual</button>
                </div>
            </div>
        `;
    }

    // -------------------------------------------------------------
    // CONTROLADORES DE INTERACCIÓN UI
    // -------------------------------------------------------------
    window.abrirManualSistema = function (perfilForzado) {
        const perfil = perfilForzado || detectarPerfilActual();
        renderizarManual(perfil);
        const modal = document.getElementById("modal-ayuda");
        if (modal) {
            modal.style.display = "flex";
            // Prevenir scroll en el fondo
            document.body.style.overflow = "hidden";
        }
    };

    window.cerrarManualSistema = function () {
        const modal = document.getElementById("modal-ayuda");
        if (modal) {
            modal.style.display = "none";
            document.body.style.overflow = "";
        }
    };

    window.cambiarTabManual = function (moduloId) {
        tabActivaId = moduloId;
        // Actualizar clases de botones
        const tabs = document.querySelectorAll(".manual-tab-btn");
        tabs.forEach(btn => btn.classList.remove("active"));
        event?.currentTarget?.classList?.add("active");

        // Alternar paneles de contenido
        const paneles = document.querySelectorAll(".manual-panel-content");
        paneles.forEach(p => p.style.display = "none");

        const target = document.getElementById("manual-panel-" + moduloId);
        if (target) target.style.display = "block";

        // Resetear buscador
        const buscador = document.getElementById("manual-buscador");
        if (buscador) buscador.value = "";
        window.filtrarManual("");
    };

    window.toggleManualAccordion = function (headerEl) {
        const card = headerEl.closest(".manual-card");
        if (!card) return;
        const body = card.querySelector(".manual-card-body");
        if (!body) return;

        const isOpen = card.classList.contains("open");

        if (isOpen) {
            card.classList.remove("open");
            body.style.maxHeight = "0px";
        } else {
            card.classList.add("open");
            body.style.maxHeight = body.scrollHeight + 30 + "px";
        }
    };

    window.filtrarManual = function (termino) {
        const query = (termino || "").toLowerCase().trim();
        const cards = document.querySelectorAll(".manual-card");

        cards.forEach(card => {
            const dataText = card.getAttribute("data-manual-btn") || "";
            if (!query || dataText.includes(query)) {
                card.style.display = "block";
                // Si hay un término de búsqueda, abrir automáticamente para ver detalles
                if (query.length > 2) {
                    card.classList.add("open");
                    const body = card.querySelector(".manual-card-body");
                    if (body) body.style.maxHeight = body.scrollHeight + 30 + "px";
                }
            } else {
                card.style.display = "none";
            }
        });
    };

    // Cerrar al hacer clic fuera del contenedor o con tecla Escape
    document.addEventListener("click", function (e) {
        const modal = document.getElementById("modal-ayuda");
        if (modal && modal.style.display === "flex" && e.target === modal) {
            window.cerrarManualSistema();
        }
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            window.cerrarManualSistema();
        }
    });

    // Sobrescribir listeners en caso de que botones antiguos utilicen onclick directo
    window.addEventListener("DOMContentLoaded", function () {
        const botonesAyuda = document.querySelectorAll('button[title="Ayuda"], button[title*="Manual"]');
        botonesAyuda.forEach(btn => {
            btn.setAttribute("title", "Manual del Sistema");
            btn.onclick = function (e) {
                e.preventDefault();
                window.abrirManualSistema();
            };
        });
    });

})();
