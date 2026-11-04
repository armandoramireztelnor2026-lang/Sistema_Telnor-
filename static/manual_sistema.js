/**
 * =========================================================
 * ARCHIVO: static/manual_sistema.js
 * PROPÓSITO: Manual Operativo Dinámico del Sistema filtrado por Rol.
 *            Documenta exclusivamente los botones de cada rol, su
 *            explicación y cómo se debe realizar cada acción paso a paso.
 * =========================================================
 */

(function () {
    // -------------------------------------------------------------
    // BASE DE CONOCIMIENTO TÉCNICA DEL MANUAL POR PERFIL
    // -------------------------------------------------------------
    const DATOS_MANUAL = {
        "Jefatura": {
            titulo: "Manual Operativo - Jefatura Automotriz",
            badgeClase: "badge-jefa",
            descripcionPerfil: "Como <strong>Jefatura de Automotriz</strong>, posees el máximo nivel jerárquico de control y administración de la plataforma Telnor / RUMN. Cuentas con acceso exclusivo al módulo de <strong>Configuraciones</strong> (Correo y Códigos SMTP, Control Presupuestal y Límite de Cotizaciones Caras), supervisión del cronómetro de <strong>Garantías</strong>, gestión de <strong>Accesos</strong> y auditoría global de la flota.",
            modulos: [
                {
                    id: "jefa-configuraciones",
                    nombre: "Configuraciones del Sistema",
                    icono: "⚙️",
                    descripcion: "Panel de control central exclusivo de Jefatura para credenciales de correo SMTP, cálculo presupuestal de cotizaciones y umbral de cotizaciones extraordinarias.",
                    botones: [
                        {
                            nombre: "Cambiar configuraciones",
                            color: "badge-btn-dark",
                            icono: "⚙️",
                            pantalla: "Barra lateral -> Módulo Configuraciones (Botón negro)",
                            proposito: "Acceder a las 3 actividades de configuración del sistema: Correo y Códigos SMTP, Control Presupuestal y Límite de Cotizaciones Caras.",
                            proceso: "1. En la barra lateral izquierda, localiza el apartado 'Configuraciones'.<br>2. Haz clic sobre el botón negro <strong>'Cambiar configuraciones'</strong>.<br>3. El sistema desplegará la pantalla de configuración con 3 pestañas independientes para cada actividad.",
                            impactoEstado: "Carga y visualiza los parámetros globales activos en el servidor.",
                            reglasNegocio: "Botón reservado únicamente para usuarios con perfil de Jefatura."
                        },
                        {
                            nombre: "Guardar Configuración (SMTP)",
                            color: "badge-btn-verde",
                            icono: "💾",
                            pantalla: "Configuraciones -> Pestaña Correo y Códigos (SMTP)",
                            proposito: "Actualizar la cuenta emisora de Gmail, la contraseña de aplicación de 16 caracteres, el servidor y puerto SMTP para el despacho de alertas y códigos de seguridad.",
                            proceso: "1. En la pestaña 'Correo y Códigos (SMTP)', edita o ingresa la dirección de correo y la contraseña de aplicación.<br>2. Opcionalmente verifica el servidor (ej. <code>smtp.gmail.com</code>) y puerto (<code>587</code>).<br>3. Haz clic en el botón verde <strong>'💾 Guardar Configuración'</strong>.<br>4. Confirma la ventana emergente de validación.",
                            impactoEstado: "Guarda los cambios en <code>configuracion_sistema.json</code>. Todos los correos automáticos futuros se despachan desde esta cuenta.",
                            reglasNegocio: "Requiere confirmación obligatoria. Se debe utilizar una Contraseña de Aplicación generada en la cuenta de Google (no la contraseña habitual de inicio de sesión)."
                        },
                        {
                            nombre: "Activar / Pausar Envíos Automáticos",
                            color: "badge-btn-ambar",
                            icono: "⏸️",
                            pantalla: "Configuraciones -> Pestaña Correo y Códigos (SMTP)",
                            proposito: "Pausar o reanudar el despacho automático de correos electrónicos a talleres, supervisores y choferes.",
                            proceso: "1. En la tarjeta de correo emisor, localiza el botón de estado de envíos.<br>2. Haz clic en <strong>'Pausar Envíos Automáticos'</strong> para suspenderlos temporalmente o en <strong>'Activar Envíos Automáticos'</strong> para reanudarlos.<br>3. Confirma la acción en el cuadro de diálogo.",
                            impactoEstado: "Actualiza la propiedad <code>envio_automatico_activo</code>. Si está pausado, las operaciones del sistema continúan normalmente pero se silencia el envío de correos masivos.",
                            reglasNegocio: "Requiere confirmación obligatoria de seguridad."
                        },
                        {
                            nombre: "+ Agregar Otra Cuenta",
                            color: "badge-btn-azul",
                            icono: "➕",
                            pantalla: "Configuraciones -> Pestaña Correo y Códigos (SMTP)",
                            proposito: "Registrar cuentas secundarias de correo para tener un catálogo de emisores y rotar los envíos en caso necesario.",
                            proceso: "1. Haz clic en el botón azul <strong>'➕ Agregar Otra Cuenta'</strong>.<br>2. En el formulario modal, escribe el correo, la contraseña de aplicación y una etiqueta descriptiva.<br>3. Haz clic en 'Guardar Cuenta' y confirma la ventana de confirmación.",
                            impactoEstado: "Añade la cuenta al listado de credenciales disponibles en el sistema.",
                            reglasNegocio: "Cualquier cuenta secundaria puede activarse como emisora principal con el botón 'Activar como Principal'."
                        },
                        {
                            nombre: "Actualizar Presupuesto Asignado",
                            color: "badge-btn-verde",
                            icono: "💾",
                            pantalla: "Configuraciones -> Pestaña Control Presupuestal",
                            proposito: "Ajustar el monto total de presupuesto financiero asignado para las cotizaciones de la flota. No es un pago, sino un cálculo administrativo de control para limitar el dinero comprometido.",
                            proceso: "1. Selecciona la pestaña <strong>'Control Presupuestal'</strong>.<br>2. En el campo 'Modificar Presupuesto Asignado', digita el monto deseado en pesos (ej. <code>500000</code>).<br>3. Haz clic en el botón verde <strong>'💾 Actualizar'</strong>.<br>4. Confirma el cuadro de diálogo con el monto establecido.",
                            impactoEstado: "Actualiza el presupuesto total en tiempo real, recalcula el saldo disponible y actualiza la barra de progreso de consumo.",
                            reglasNegocio: "<strong>Regla Estricta:</strong> Si el dinero de una cotización excede el presupuesto disponible, el sistema bloqueará la aprobación del supervisor hasta que Jefatura amplíe el fondo."
                        },
                        {
                            nombre: "Resetear Dinero Utilizado",
                            color: "badge-btn-rojo",
                            icono: "🗑️",
                            pantalla: "Configuraciones -> Pestaña Control Presupuestal",
                            proposito: "Reiniciar el cálculo del dinero acumulado en cotizaciones anteriores, restableciendo el saldo disponible al 100% para iniciar un nuevo ciclo o periodo financiero.",
                            proceso: "1. En la pestaña de Presupuesto, ubica el recuadro 'Reiniciar Presupuesto Utilizado'.<br>2. Haz clic en el botón rojo <strong>'🗑️ Resetear Dinero Utilizado'</strong>.<br>3. Lee atentamente la advertencia en pantalla y presiona 'Aceptar' para confirmar.",
                            impactoEstado: "El saldo comprometido se resetea a $0.00 MXN y el disponible regresa al 100%. Las cotizaciones previas se excluyen del cómputo actual.",
                            reglasNegocio: "Requiere confirmación obligatoria. Acción ideal al inicio de cada mes o nuevo ciclo administrativo."
                        },
                        {
                            nombre: "Guardar Nuevo Límite (+10,000)",
                            color: "badge-btn-ambar",
                            icono: "🏷️",
                            pantalla: "Configuraciones -> Pestaña Límite para Cotizaciones Caras",
                            proposito: "Modificar el umbral económico que define si una cotización requiere aprobación obligatoria por Dirección Corporativa.",
                            proceso: "1. Dirígete a la pestaña <strong>'Límite para Cotizaciones Caras'</strong>.<br>2. Elige un monto rápido ($10,000, $15,000, $20,000) o ingresa un monto personalizado en el campo numérico.<br>3. Haz clic en el botón verde <strong>'💾 Guardar Nuevo Límite'</strong>.<br>4. Confirma el cuadro de diálogo.",
                            impactoEstado: "Actualiza el parámetro global <code>limite_cotizaciones_caras</code> y se aplica en automático a los tickets pendientes.",
                            reglasNegocio: "<strong>Reglas del Flujo:</strong> Si una cotización ya está en reparación en taller, no le afecta el cambio. Si el precio de un ticket baja del límite, pasa directo a taller sin requerir Corporativos."
                        }
                    ]
                },
                {
                    id: "jefa-garantias",
                    nombre: "Garantías y Retrabajos",
                    icono: "🛡️",
                    descripcion: "Monitoreo del periodo de garantía de 30 días naturales que inicia al entregar un vehículo reparado.",
                    botones: [
                        {
                            nombre: "Tiempo/Garantía",
                            color: "badge-btn-verde",
                            icono: "🛡️",
                            pantalla: "Barra lateral -> Módulo Garantía (Botón verde)",
                            proposito: "Abrir el panel de monitoreo de unidades cubiertas por garantía tras su reparación física en taller.",
                            proceso: "1. En el menú lateral, localiza la sección verde 'Garantía'.<br>2. Haz clic en el botón verde <strong>'Tiempo/Garantía'</strong>.<br>3. Inspecciona las unidades vigentes, días naturales restantes de cobertura y taller responsable.",
                            impactoEstado: "Muestra la cobertura vigente para certificar si una falla reportada califica como retrabajo sin costo adicional de mano de obra.",
                            reglasNegocio: "La garantía tiene una vigencia legal de 30 días naturales a partir de la validación del PIN de entrega."
                        }
                    ]
                },
                {
                    id: "jefa-operaciones",
                    nombre: "Gestión de Accesos y Padrón",
                    icono: "👥",
                    descripcion: "Control de usuarios, asignación de permisos, estructura de ciudades y centros de trabajo (COPEs).",
                    botones: [
                        {
                            nombre: "Nuevos Registros",
                            color: "badge-btn-azul",
                            icono: "📥",
                            pantalla: "Barra lateral -> Nuevos Registros",
                            proposito: "Revisar, autorizar o rechazar solicitudes de registro de nuevos talleres mecánicos y colaboradores.",
                            proceso: "1. Haz clic en 'Nuevos Registros'.<br>2. Revisa la documentación del solicitante.<br>3. Haz clic en 'Aprobar' para habilitar su acceso o 'Rechazar' para descartar la solicitud.",
                            impactoEstado: "Genera la cuenta activa en <code>usuarios.json</code>.",
                            reglasNegocio: "Ningún taller o colaborador externo puede acceder al portal sin la validación previa de Jefatura."
                        },
                        {
                            nombre: "Accesos (Credenciales)",
                            color: "badge-btn-purple",
                            icono: "🔑",
                            pantalla: "Barra lateral -> Accesos (Credenciales)",
                            proposito: "Consultar credenciales, restablecer contraseñas y administrar los perfiles de todo el personal.",
                            proceso: "1. Haz clic en 'Accesos (Credenciales)'.<br>2. Utiliza el buscador para localizar al usuario.<br>3. Consulta credenciales o presiona editar para cambiar contraseñas y accesos.",
                            impactoEstado: "Mantiene actualizada la seguridad del sistema.",
                            reglasNegocio: "Jefatura tiene visibilidad total de las credenciales del sistema."
                        },
                        {
                            nombre: "Ciudades / COPEs",
                            color: "badge-btn-cyan",
                            icono: "🏢",
                            pantalla: "Barra lateral -> Ciudades / COPEs",
                            proposito: "Estructurar los centros de trabajo (COPEs) y ciudades operativas de Telnor y RUMN.",
                            proceso: "1. Haz clic en 'Ciudades / COPEs'.<br>2. Haz clic en '+ Agregar Ciudad' o '+ Agregar COPE'.<br>3. Captura el nombre y código y confirma con 'Guardar'.",
                            impactoEstado: "Actualiza el catálogo geográfico para asignación de talleres y unidades.",
                            reglasNegocio: "Toda unidad y supervisor debe pertenecer a un COPE válido."
                        },
                        {
                            nombre: "Directorio Talleres / Lista Corp / Lista Admin",
                            color: "badge-btn-azul",
                            icono: "📋",
                            pantalla: "Barra lateral",
                            proposito: "Consultar los directorios completos de proveedores mecánicos, directivos corporativos y supervisores de zona.",
                            proceso: "Haz clic en el directorio deseado desde la barra lateral para consultar contactos, teléfonos, correos y áreas de adscripción.",
                            impactoEstado: "Vista de sólo lectura para control y auditoría.",
                            reglasNegocio: "Permite verificar quiénes son los aprobadores y proveedores autorizados."
                        }
                    ]
                },
                {
                    id: "jefa-analitica-archivo",
                    nombre: "Analítica, Cuadro de Mando y Archivo",
                    icono: "📊",
                    descripcion: "Monitoreo integral de la flota por código de colores, analítica y repositorio histórico.",
                    botones: [
                        {
                            nombre: "Sección de Reportes (Por Colores)",
                            color: "badge-btn-azul",
                            icono: "🎨",
                            pantalla: "Barra lateral -> Sección de Reportes",
                            proposito: "Supervisar todos los vehículos en un cuadro de mando integral organizado por columnas de color según su etapa de servicio.",
                            proceso: "1. Haz clic en 'Sección de Reportes'.<br>2. Consulta las columnas: Amarillo (en cotización/revisión), Negro (en reparación en taller), Verde (reparadas listas para entrega) y Retrabajo (unidades en garantía).<br>3. Utiliza los filtros superiores para auditar la flota.",
                            impactoEstado: "Permite ubicar cualquier vehículo de un vistazo.",
                            reglasNegocio: "Los colores reflejan en tiempo real el avance de cada orden de trabajo."
                        },
                        {
                            nombre: "Descargar Reporte Excel",
                            color: "badge-btn-verde",
                            icono: "📥",
                            pantalla: "Barra lateral -> Vista Analítica",
                            proposito: "Exportar el balance financiero consolidado de reparaciones, gastos por taller, unidades y tiempos de servicio a una hoja de cálculo formal.",
                            proceso: "1. Haz clic en 'Analítica' en la barra lateral.<br>2. Aplica los filtros deseados.<br>3. Haz clic en el botón verde <strong>'Descargar Reporte Excel'</strong>.",
                            impactoEstado: "Genera y descarga en tu equipo el archivo oficial <code>.xlsx</code>.",
                            reglasNegocio: "Procesa los registros vigentes excluyendo reportes cancelados."
                        },
                        {
                            nombre: "Archivo General",
                            color: "badge-btn-dark",
                            icono: "🗄️",
                            pantalla: "Barra lateral -> Archivo General",
                            proposito: "Consultar el repositorio inmutable de expedientes históricos cerrados y liquidados.",
                            proceso: "1. Haz clic en 'Archivo General'.<br>2. Utiliza el buscador para localizar expedientes por número de reporte, unidad, taller o folio fiscal.",
                            impactoEstado: "Permite auditar el historial mecánico y financiero completo de cada auto.",
                            reglasNegocio: "Los registros en archivo histórico son definitivos e inmutables."
                        }
                    ]
                }
            ]
        },

        "Supervisor": {
            titulo: "Manual Operativo - Supervisor Automotriz",
            badgeClase: "badge-super",
            descripcionPerfil: "Como <strong>Supervisor de Zona Automotriz</strong>, eres el responsable técnico y operativo directo de las unidades y talleres de tu centro de trabajo (COPE). Tus atribuciones abarcan la <strong>recepción y asignación de reportes</strong> de los choferes, la <strong>autorización de cotizaciones estándar</strong> con asignación de órdenes de compra, la <strong>validación presencial del PIN de liberación</strong> para la entrega física de los autos, la <strong>revisión fiscal de CFDIs</strong> y la gestión de <strong>Garantías y Retrabajos</strong>.",
            modulos: [
                {
                    id: "super-reportes",
                    nombre: "Bandeja de Reportes",
                    icono: "📥",
                    descripcion: "Recepción de averías levantadas por los operadores en campo y su canalización a talleres mecánicos.",
                    botones: [
                        {
                            nombre: "Asignar Taller",
                            color: "badge-btn-ambar",
                            icono: "🔧",
                            pantalla: "Bandeja de Reportes -> Columna Acciones",
                            proposito: "Evaluar la falla reportada por el chofer y canalizar el vehículo al taller mecánico correspondiente.",
                            proceso: "1. En la tabla de reportes pendientes, ubica el ticket y haz clic en <strong>'Asignar Taller'</strong>.<br>2. Selecciona el taller mecánico autorizado en la lista.<br>3. Selecciona la compañía fiscalizadora (Telnor o RUMN).<br>4. Haz clic en 'Confirmar Asignación'.",
                            impactoEstado: "El reporte cambia a 'Pendiente de Cotización' y envía correo formal con los datos del auto al taller.",
                            reglasNegocio: "Solo se pueden seleccionar talleres autorizados en el COPE del supervisor."
                        },
                        {
                            nombre: "💬 Comentarios",
                            color: "badge-btn-azul",
                            icono: "💬",
                            pantalla: "Bandeja de Reportes / Tabla General",
                            proposito: "Agregar notas técnicas, aclaraciones o historial operativo visible para todo el equipo automotriz.",
                            proceso: "1. Haz clic en el botón de comentarios del ticket.<br>2. Escribe las observaciones en el cuadro de texto.<br>3. Haz clic en 'Guardar Comentario'.",
                            impactoEstado: "Guarda la nota en la bitácora del ticket con autor, fecha y hora.",
                            reglasNegocio: "Cualquier supervisor o administrador puede consultar y agregar comentarios."
                        },
                        {
                            nombre: "Eliminar Reporte",
                            color: "badge-btn-rojo",
                            icono: "🗑️",
                            pantalla: "Bandeja de Reportes -> Columna Acciones",
                            proposito: "Descartar un reporte erróneo, duplicado o generado por equivocación.",
                            proceso: "1. Haz clic en el icono rojo de basura.<br>2. Confirma la eliminación en el mensaje de seguridad.",
                            impactoEstado: "Aplica baja lógica del ticket, ocultándolo de las bandejas operativas.",
                            reglasNegocio: "Solo procede si el reporte aún no ha sido cotizado por un taller."
                        }
                    ]
                },
                {
                    id: "super-cotizaciones",
                    nombre: "Cotizaciones y Órdenes de Trabajo",
                    icono: "📑",
                    descripcion: "Evaluación técnica de costos mecánicos, asignación de órdenes de compra y liberación con PIN.",
                    botones: [
                        {
                            nombre: "Revisar Cotización",
                            color: "badge-btn-cyan",
                            icono: "🔍",
                            pantalla: "Cotizaciones y Órdenes -> Columna Acciones",
                            proposito: "Inspeccionar los precios unitarios de refacciones, costo de mano de obra, fotos de piezas dañadas y el PDF emitido por el taller.",
                            proceso: "Haz clic en 'Revisar Cotización' para abrir el visor técnico con el desglose de conceptos.",
                            impactoEstado: "Permite auditar los conceptos antes de comprometer fondos de la empresa.",
                            reglasNegocio: "Revisa que los trabajos correspondan a la falla reportada por el chofer."
                        },
                        {
                            nombre: "Aprobar Cotización y Asignar Orden",
                            color: "badge-btn-verde",
                            icono: "✅",
                            pantalla: "Modal de Cotización",
                            proposito: "Validar técnicamente los costos e ingresar los Números de Orden de Compra y Pedido oficiales de la empresa.",
                            proceso: "1. Revisa los conceptos del presupuesto.<br>2. Ingresa el Número de Orden y Número de Pedido emitidos por la empresa.<br>3. Adjunta el archivo PDF de la orden oficial.<br>4. Haz clic en el botón verde <strong>'Aprobar Cotización'</strong>.",
                            impactoEstado: "Si el precio es menor o igual al límite global, pasa a 'En Reparación' y notifica al taller. Si es mayor, se turna a Administrador y Corporativos.",
                            reglasNegocio: "<strong>Control Presupuestal Estricto:</strong> El sistema verifica que haya suficiente saldo en el Presupuesto asignado por Jefatura. Si el costo excede el saldo disponible, la aprobación se bloquea y se emite alerta."
                        },
                        {
                            nombre: "Rechazar Cotización con Sugerencias",
                            color: "badge-btn-ambar",
                            icono: "⚠️",
                            pantalla: "Modal de Cotización",
                            proposito: "Solicitar al taller que ajuste precios fuera de tabulador indicando los montos máximos que la empresa pagará.",
                            proceso: "1. En el modal de cotización, haz clic en 'Rechazar Cotización'.<br>2. Llena la tabla con los precios recomendados por concepto.<br>3. Haz clic en 'Enviar Rechazo'.",
                            impactoEstado: "Mueve el ticket a 'Correcciones/Taller' y envía correo al proveedor con la tabla comparativa.",
                            reglasNegocio: "Permite al taller corregir sus costos sin necesidad de cancelar el servicio."
                        },
                        {
                            nombre: "Cancelar por Cotización Cara (Incosteable)",
                            color: "badge-btn-rojo",
                            icono: "🚫",
                            pantalla: "Modal de Cotización",
                            proposito: "Declarar inviable la reparación de una unidad cuando el costo supere el valor comercial del vehículo.",
                            proceso: "1. Haz clic en el botón rojo 'Cancelar por Cotización Cara'.<br>2. Confirma la ventana de diálogo de advertencia.",
                            impactoEstado: "Cancela el ticket y marca automáticamente la unidad como 'Inactiva' en el catálogo vehicular.",
                            reglasNegocio: "Bloquea el vehículo para futuros reportes por obsolescencia patrimonial."
                        },
                        {
                            nombre: "Validar PIN OTP de Entrega",
                            color: "badge-btn-verde",
                            icono: "🔑",
                            pantalla: "Modal Validar PIN OTP",
                            proposito: "Certificar presencialmente la salida del auto del taller cuando el chofer acude a retirarlo.",
                            proceso: "1. Solicita al chofer el código numérico de 8 dígitos que llegó exclusivamente a su correo.<br>2. Ingrésalo en el campo del modal.<br>3. Haz clic en 'Validar PIN'.",
                            impactoEstado: "Al existir coincidencia exacta, marca entregado = 'Sí', libera la unidad físicamente y transiciona a 'Esperando Facturación (Taller)'.",
                            reglasNegocio: "<strong>Seguridad Asimétrica:</strong> Ni el taller ni el supervisor conocen el PIN con anticipación; solo el chofer lo posee en su buzón."
                        }
                    ]
                },
                {
                    id: "super-facturas-unidades",
                    nombre: "Facturas y Gestión de Flota",
                    icono: "🚗",
                    descripcion: "Validación de comprobantes fiscales CFDI del SAT y catálogo de vehículos.",
                    botones: [
                        {
                            nombre: "Aprobar Factura Fiscal",
                            color: "badge-btn-verde",
                            icono: "📑",
                            pantalla: "Bandeja Facturas Finales",
                            proposito: "Validar que la factura electrónica (PDF y XML) concuerda con el importe y conceptos de la orden autorizada.",
                            proceso: "1. Revisa ambos archivos (PDF y XML).<br>2. Verifica razón social, RFC y total.<br>3. Haz clic en 'Aprobar Factura Fiscal'.",
                            impactoEstado: "Transiciona a 'Esperando Num. Contable' para que el Administrador registre el Doc 50 SAP.",
                            reglasNegocio: "Solo procede si el taller cargó satisfactoriamente ambos comprobantes válidos."
                        },
                        {
                            nombre: "+ Agregar Unidad",
                            color: "badge-btn-verde",
                            icono: "➕",
                            pantalla: "Directorio de Unidades",
                            proposito: "Dar de alta un nuevo vehículo en el catálogo automotriz del COPE.",
                            proceso: "1. Haz clic en '+ Agregar Unidad'.<br>2. Captura Número Económico (4 dígitos), Marca, Modelo, Año, Placas y COPE.<br>3. Haz clic en 'Guardar Unidad'.",
                            impactoEstado: "Registra el vehículo con estatus 'Activa' para permitir levantar reportes.",
                            reglasNegocio: "El número económico debe ser único."
                        },
                        {
                            nombre: "Editar / Inactivar Unidad",
                            color: "badge-btn-azul",
                            icono: "✏️",
                            pantalla: "Directorio de Unidades",
                            proposito: "Actualizar datos vehiculares o alternar el estatus entre Activa e Inactiva.",
                            proceso: "Haz clic en 'Editar', modifica las especificaciones y guarda los cambios.",
                            impactoEstado: "Si se marca Inactiva, no se podrán generar nuevos reportes sobre la unidad.",
                            reglasNegocio: "No se puede inactivar una unidad con ticket activo en reparación."
                        }
                    ]
                },
                {
                    id: "super-garantia",
                    nombre: "Garantías y Retrabajos",
                    icono: "🛡️",
                    descripcion: "Gestión de vehículos que presentaron fallas dentro de los 30 días posteriores al servicio.",
                    botones: [
                        {
                            nombre: "Retrabajo (Bandeja)",
                            color: "badge-btn-verde",
                            icono: "🛡️",
                            pantalla: "Barra lateral -> Sección Garantía -> Retrabajo",
                            proposito: "Acceder a la bandeja de unidades canalizadas a garantía para reasignación al taller.",
                            proceso: "Haz clic en 'Retrabajo' en la barra lateral para ver los tickets en garantía.",
                            impactoEstado: "Muestra las fallas reincidentes reportadas.",
                            reglasNegocio: "Aplica dentro de los 30 días naturales de garantía."
                        },
                        {
                            nombre: "Reasignar a Taller (en Retrabajo)",
                            color: "badge-btn-verde",
                            icono: "🔄",
                            pantalla: "Modal Detalle de Retrabajo",
                            proposito: "Reenviar la unidad al taller mecánico responsable para su corrección bajo garantía sin costo de mano de obra.",
                            proceso: "1. En la tabla de Retrabajo, abre el detalle del ticket.<br>2. Haz clic en el botón superior <strong>'Reasignar'</strong>.<br>3. Confirma el cuadro de diálogo.",
                            impactoEstado: "Notifica al taller mecánico para que atienda la unidad con carácter prioritario.",
                            reglasNegocio: "Garantiza que la reparación sea cubierta por el proveedor sin cargo adicional."
                        },
                        {
                            nombre: "Cancelar Reasignación",
                            color: "badge-btn-rojo",
                            icono: "🚫",
                            pantalla: "Modal Detalle de Retrabajo",
                            proposito: "Cancelar una reasignación errónea antes de que el taller comience los trabajos.",
                            proceso: "Haz clic en 'Cancelar Reasignacion' en el modal y confirma la acción.",
                            impactoEstado: "Revierte la reasignación en garantía.",
                            reglasNegocio: "Requiere confirmación de seguridad."
                        },
                        {
                            nombre: "Liberar/Retrabajo",
                            color: "badge-btn-verde",
                            icono: "✅",
                            pantalla: "Barra lateral -> Sección Garantía -> Liberar/Retrabajo",
                            proposito: "Validar y liberar la unidad una vez que el taller mecánico ha concluido la reparación en garantía.",
                            proceso: "1. Ve a la vista 'Liberar/Retrabajo'.<br>2. Localiza la unidad y haz clic en el botón verde <strong>'Liberar Retrabajo'</strong>.<br>3. Confirma la ventana de diálogo.",
                            impactoEstado: "La unidad queda liberada de retrabajo y el ticket regresa a su ciclo operativo normal.",
                            reglasNegocio: "Requiere confirmación previa para evitar liberaciones accidentales."
                        }
                    ]
                },
                {
                    id: "super-cobertura",
                    nombre: "Delegación Por Ausencia (Cobertura)",
                    icono: "🤝",
                    descripcion: "Suplencia temporal de funciones del Administrador ausente.",
                    botones: [
                        {
                            nombre: "Cotizaciones +10000 (en Cobertura)",
                            color: "badge-btn-ambar",
                            icono: "💎",
                            pantalla: "Barra lateral -> Delegación Por Ausencia",
                            proposito: "Aprobar cotizaciones mayores a $10,000 en sustitución temporal del Administrador.",
                            proceso: "Accede desde 'Cotizaciones +10000' en la sección de delegación y revisa o aprueba con sello de suplencia.",
                            impactoEstado: "Registra en bitácora <code>aprobado_por_suplencia = true</code>.",
                            reglasNegocio: "Si el ticket es de ámbito corporativo estricto, el sistema bloquea la acción por seguridad institucional."
                        },
                        {
                            nombre: "Liberar Doc. Contable (en Cobertura)",
                            color: "badge-btn-ambar",
                            icono: "📜",
                            pantalla: "Barra lateral -> Delegación Por Ausencia",
                            proposito: "Capturar el número de póliza SAP y autorizar el pago en suplencia del titular.",
                            proceso: "Captura el número contable y presiona 'Liberar Doc 50' confirmando el diálogo.",
                            impactoEstado: "Desbloquea el ticket para archivo.",
                            reglasNegocio: "Queda estampado el nombre del supervisor suplente en el expediente."
                        }
                    ]
                }
            ]
        },

        "Administrador": {
            titulo: "Manual Operativo - Administrador Central",
            badgeClase: "badge-admin",
            descripcionPerfil: "Como <strong>Administrador Central</strong> de Automotriz, eres la máxima autoridad financiera y de control administrativo. Tienes a tu cargo el filtro previo de <strong>Cotizaciones Mayores a $10,000 MXN</strong>, la <strong>liberación obligatoria del Documento Contable (Doc 50 de SAP)</strong> previa al pago, la cobertura de supervisores y el <strong>archivado definitivo</strong> de los expedientes.",
            modulos: [
                {
                    id: "admin-10k",
                    nombre: "Cotizaciones +10,000",
                    icono: "💎",
                    descripcion: "Auditoría preventiva de presupuestos que rebasan el umbral financiero fijado por Jefatura.",
                    botones: [
                        {
                            nombre: "Revisar Cotización Mayor",
                            color: "badge-btn-azul",
                            icono: "🔍",
                            pantalla: "Bandeja Cotizaciones +10,000 -> Columna Acciones",
                            proposito: "Inspeccionar a detalle el presupuesto técnico-económico elaborado por el taller cuando el monto rebasa el límite global.",
                            proceso: "Haz clic en 'Revisar' para abrir el visor con conceptos, fotos de partes averiadas y archivo PDF del taller.",
                            impactoEstado: "Permite auditar sobrecostos antes de remitir a Dirección Corporativa.",
                            reglasNegocio: "Se activa de forma automática cuando el precio supera el límite fijado por Jefatura."
                        },
                        {
                            nombre: "Aprobar y Canalizar a Corporativos",
                            color: "badge-btn-verde",
                            icono: "✅",
                            pantalla: "Modal de Cotizaciones +10,000",
                            proposito: "Validar técnicamente el presupuesto de alto valor y someterlo a autorización ejecutiva de Dirección Corporativa.",
                            proceso: "1. Revisa los costos y orden.<br>2. Haz clic en el botón verde <strong>'Aprobar y Canalizar a Corporativos'</strong>.<br>3. El sistema valida suficiencia presupuestal y despacha correos automáticos a los directivos corporativos.",
                            impactoEstado: "Mueve el ticket a 'Esperando / Aprob. Cotizacion (Corp)'.",
                            reglasNegocio: "<strong>Control Presupuestal:</strong> Comprueba el saldo disponible de Jefatura. Solo el Administrador Titular puede autorizar tickets de ámbito corporativo."
                        },
                        {
                            nombre: "Rechazar Cotización con Precios Recomendados",
                            color: "badge-btn-rojo",
                            icono: "↩️",
                            pantalla: "Modal de Cotizaciones +10,000",
                            proposito: "Rechazar precios inflados indicando un tabulador de precios tope autorizados.",
                            proceso: "Ingresa los precios recomendados por concepto y presiona 'Enviar Rechazo'.",
                            impactoEstado: "Regresa el ticket a 'Correcciones/Taller' y notifica al proveedor.",
                            reglasNegocio: "Permite al taller ajustar su propuesta sin cancelar la atención del vehículo."
                        }
                    ]
                },
                {
                    id: "admin-doc50",
                    nombre: "Liberación de Doc. Contable (SAP)",
                    icono: "📜",
                    descripcion: "Asociación del asiento contable de SAP y visto bueno financiero previo a la liquidación del servicio.",
                    botones: [
                        {
                            nombre: "Capturar / Guardar Doc 50",
                            color: "badge-btn-azul",
                            icono: "💾",
                            pantalla: "Bandeja Liberar Doc. Contable",
                            proposito: "Ingresar en el expediente el número oficial de Documento Contable (Doc 50 de SAP) generado por Cuentas por Pagar.",
                            proceso: "1. Escribe el número de póliza contable en el campo del ticket.<br>2. Haz clic en <strong>'Guardar Doc 50'</strong>.",
                            impactoEstado: "Asocia el número financiero en <code>facturas.json</code>.",
                            reglasNegocio: "Solo acepta caracteres numéricos correspondientes al registro contable de SAP."
                        },
                        {
                            nombre: "Liberar Documento Contable",
                            color: "badge-btn-verde",
                            icono: "🔓",
                            pantalla: "Bandeja Liberar Doc. Contable",
                            proposito: "Emitir el visto bueno definitivo que confirma que la factura cuenta con suficiencia presupuestal y registro contable, desbloqueando el expediente para su archivado.",
                            proceso: "1. Verifica el número contable.<br>2. Haz clic en <strong>'Liberar Documento Contable'</strong>.<br>3. Confirma la ventana de diálogo.",
                            impactoEstado: "Marca <code>doc50_liberado = true</code> y habilita el botón de archivo definitivo.",
                            reglasNegocio: "<strong>Garantía de Cierre:</strong> Ningún ticket puede ser archivado si no cuenta con la liberación de Doc 50."
                        },
                        {
                            nombre: "Notificar Recordatorio a Corporativos",
                            color: "badge-btn-ambar",
                            icono: "🔔",
                            pantalla: "Bandeja Liberar Doc. Contable",
                            proposito: "Enviar un aviso preventivo por correo a Corporativos si hay tickets detenidos sin póliza contable.",
                            proceso: "Haz clic en el icono de campana/recordatorio para despachar la alerta automática.",
                            impactoEstado: "Envía correo transaccional de seguimiento.",
                            reglasNegocio: "Disponible para facturas validadas fiscalmente con retraso de registro contable."
                        }
                    ]
                },
                {
                    id: "admin-analitica-archivo",
                    nombre: "Analítica y Archivo Definitivo",
                    icono: "📊",
                    descripcion: "Exportación de balances financieros a Excel y cierre formal de tickets.",
                    botones: [
                        {
                            nombre: "Descargar Reporte Excel",
                            color: "badge-btn-verde",
                            icono: "📥",
                            pantalla: "Vista Analítica",
                            proposito: "Generar un libro contable formal en Excel (.xlsx) con los gastos, talleres, órdenes y tiempos de servicio.",
                            proceso: "Haz clic en 'Analítica' en la barra lateral y presiona <strong>'Descargar Reporte Excel'</strong>.",
                            impactoEstado: "Descarga automática del archivo oficial.",
                            reglasNegocio: "Procesa los datos vigentes en memoria mediante Pandas y OpenPyXL."
                        },
                        {
                            nombre: "Archivar Expediente Definitivo",
                            color: "badge-btn-rojo",
                            icono: "🗄️",
                            pantalla: "Vista Archivo General",
                            proposito: "Mover el expediente completado de la base de datos activa a la base histórica inmutable.",
                            proceso: "1. En la tabla de Archivo, localiza el ticket con Doc 50 liberado.<br>2. Haz clic en el botón rojo <strong>'Archivar'</strong>.<br>3. Confirma la acción.",
                            impactoEstado: "Mueve el registro a <code>tickets_archivados.json</code> y cierra definitivamente el expediente.",
                            reglasNegocio: "Requiere obligatoriamente que <code>doc50_liberado == true</code>."
                        }
                    ]
                },
                {
                    id: "admin-cobertura",
                    nombre: "Delegación Por Ausencia (Cobertura)",
                    icono: "🤝",
                    descripcion: "Intervención temporal en supervisión cuando el titular del COPE está ausente.",
                    botones: [
                        {
                            nombre: "Cotizaciones y Órdenes (en Cobertura)",
                            color: "badge-btn-purple",
                            icono: "🛡️",
                            pantalla: "Barra lateral -> Delegación Por Ausencia",
                            proposito: "Aprobar cotizaciones estándar y asignar órdenes de compra en sustitución del supervisor.",
                            proceso: "Accede desde la sección amarilla de cobertura, revisa la cotización y aprueba ingresando los números de orden.",
                            impactoEstado: "Transiciona el ticket a 'En Reparación' con marca de suplencia.",
                            reglasNegocio: "Estampa en bitácora <code>aprobado_por_suplencia = true</code>."
                        },
                        {
                            nombre: "Facturas (en Cobertura)",
                            color: "badge-btn-purple",
                            icono: "📑",
                            pantalla: "Barra lateral -> Delegación Por Ausencia",
                            proposito: "Validar fiscalmente comprobantes CFDI (PDF y XML) de talleres en cobertura.",
                            proceso: "Revisa la factura y haz clic en 'Aprobar Factura Fiscal' con sello de suplencia.",
                            impactoEstado: "Mueve el ticket a 'Esperando Num. Contable'.",
                            reglasNegocio: "Registra el nombre del administrador suplente en la validación fiscal."
                        }
                    ]
                }
            ]
        },

        "Corporativos": {
            titulo: "Manual Operativo - Dirección Corporativa",
            badgeClase: "badge-corp",
            descripcionPerfil: "Como miembro de la <strong>Dirección Corporativa</strong>, ejerces el control de fiscalización y auditoría ejecutiva del gasto de capital de la flota automotriz. Tu intervención se enfoca exclusivamente en <strong>auditar y autorizar los presupuestos extraordinarios (+10,000 MXN)</strong> y consultar el repositorio inmutable de expedientes.",
            modulos: [
                {
                    id: "corp-cotizaciones",
                    nombre: "Autorizaciones Financieras (+10,000)",
                    icono: "💎",
                    descripcion: "Revisión ejecutiva de presupuestos de alto impacto canalizados por el Administrador central.",
                    botones: [
                        {
                            nombre: "Revisar Factura Mayor",
                            color: "badge-btn-azul",
                            icono: "🔍",
                            pantalla: "Bandeja de Cotizaciones -> Columna Acciones",
                            proposito: "Examinar a detalle las refacciones, evidencias fotográficas de piezas dañadas, costo de mano de obra y orden oficial.",
                            proceso: "Haz clic en el botón azul <strong>'Revisar'</strong> en el renglón de la cotización deseada.",
                            impactoEstado: "Abre el modal ejecutivo con la ficha completa del vehículo y desglose de conceptos.",
                            reglasNegocio: "Permite comprobar si el gasto está justificado antes de comprometer el presupuesto corporativo."
                        },
                        {
                            nombre: "Aprobar Gasto Financiero",
                            color: "badge-btn-verde",
                            icono: "✅",
                            pantalla: "Modal Revisión de Factura Mayor",
                            proposito: "Autorizar formalmente el presupuesto de alto valor para que el taller comience los trabajos físicos.",
                            proceso: "1. Revisa los costos y conceptos.<br>2. Haz clic en el botón verde <strong>'Aprobar Gasto Financiero'</strong>.<br>3. Confirma la ventana modal de validación ejecutiva.",
                            impactoEstado: "Marca <code>aprobado_corp = true</code>, mueve el ticket a 'En Reparación (Taller)' y despacha notificación inmediata al taller y al supervisor.",
                            reglasNegocio: "Es el visto bueno final indispensable para que el taller intervenga unidades con presupuestos mayores al límite global."
                        },
                        {
                            nombre: "Rechazar Gasto con Justificación",
                            color: "badge-btn-rojo",
                            icono: "❌",
                            pantalla: "Modal Revisión de Factura Mayor",
                            proposito: "Negar la autorización presupuestal cuando el costo sea excesivo o injustificado.",
                            proceso: "1. Haz clic en el botón rojo <strong>'Rechazar Gasto'</strong>.<br>2. Escribe una justificación ejecutiva formal e ingresa sugerencias de precios.<br>3. Haz clic en 'Confirmar Rechazo'.",
                            impactoEstado: "Regresa el ticket a 'Correcciones/Taller' o deriva a 'Incosteable' según la resolución.",
                            reglasNegocio: "Requiere capturar obligatoriamente un motivo justificado para el historial de auditoría."
                        }
                    ]
                },
                {
                    id: "corp-archivo",
                    nombre: "Repositorio Histórico Corporativo",
                    icono: "🗄️",
                    descripcion: "Consulta inmutable de todos los servicios automotrices concluidos y facturas liquidadas.",
                    botones: [
                        {
                            nombre: "Buscador y Filtro de Expedientes",
                            color: "badge-btn-azul",
                            icono: "🔍",
                            pantalla: "Barra lateral -> Archivo Histórico",
                            proposito: "Localizar expedientes pasados por número de unidad, proveedor, folio fiscal o rango de fechas.",
                            proceso: "1. Haz clic en 'Archivo Histórico' en la barra lateral.<br>2. Teclea en el buscador el número económico o proveedor.<br>3. Consulta importes, pólizas y documentos.",
                            impactoEstado: "Consulta de sólo lectura sin alteración de datos.",
                            reglasNegocio: "Herramienta definitiva para auditorías de capital y seguimiento del ciclo de vida vehicular."
                        }
                    ]
                }
            ]
        },

        "Taller": {
            titulo: "Manual Operativo - Portal Taller / Proveedor",
            badgeClase: "badge-taller",
            descripcionPerfil: "Como <strong>Taller Mecánico Proveedor Autorizado</strong>, eres el eslabón fundamental en la reparación física de los vehículos de Telnor y RUMN. Tu portal te permite <strong>recibir asignaciones de unidades averiadas</strong>, <strong>elaborar y desglosar cotizaciones técnicas</strong>, <strong>descargar órdenes de compra oficiales</strong>, <strong>marcar unidades listas para entrega</strong> (disparando el PIN de seguridad al chofer), atender <strong>Garantías y Retrabajos</strong> y <strong>subir tus comprobantes fiscales CFDI (PDF y XML)</strong> para trámite de pago.",
            modulos: [
                {
                    id: "taller-tickets",
                    nombre: "Tickets de Trabajo Asignados",
                    icono: "🔧",
                    descripcion: "Bandeja de entrada donde aterrizan los vehículos asignados para diagnóstico y cotización.",
                    botones: [
                        {
                            nombre: "Crear Cotización / Presupuesto",
                            color: "badge-btn-ambar",
                            icono: "📝",
                            pantalla: "Bandeja Tickets de Trabajo -> Columna Acciones",
                            proposito: "Formular la propuesta técnico-económica de refacciones y mano de obra tras inspeccionar físicamente el vehículo en tu taller.",
                            proceso: "1. Haz clic en el botón <strong>'Crear Cotización'</strong>.<br>2. Desglosa los conceptos (título, precio, preventivo/correctivo).<br>3. Adjunta tu archivo PDF de presupuesto formal emitido por el taller.<br>4. Sube al menos una fotografía de evidencia de las piezas averiadas.<br>5. Haz clic en 'Enviar Cotización'.",
                            impactoEstado: "Crea el registro formal en <code>facturas.json</code> y mueve el ticket a 'Esperando / Aprob. Cotizacion (Supervisor)'.",
                            reglasNegocio: "<strong>Requisitos Obligatorios:</strong> Es indispensable subir fotografías del daño y adjuntar el archivo PDF de presupuesto formal."
                        },
                        {
                            nombre: "Ver Reporte del Chofer",
                            color: "badge-btn-azul",
                            icono: "📋",
                            pantalla: "Bandeja Tickets de Trabajo -> Columna Acciones",
                            proposito: "Consultar las observaciones, kilometraje y sintomatología reportadas originalmente por el conductor.",
                            proceso: "Haz clic en el icono de reporte para ver la ficha del chofer.",
                            impactoEstado: "Muestra la información de la falla para orientar el diagnóstico mecánico.",
                            reglasNegocio: "Permite verificar el contexto de la avería."
                        }
                    ]
                },
                {
                    id: "taller-cotizaciones",
                    nombre: "Cotizaciones y Reparación Física",
                    icono: "⚙️",
                    descripcion: "Recepción de órdenes de compra, correcciones y notificación de autos concluidos.",
                    botones: [
                        {
                            nombre: "Ver Orden de Compra Aprobada",
                            color: "badge-btn-verde",
                            icono: "📜",
                            pantalla: "Bandeja de Cotizaciones -> Columna Acciones",
                            proposito: "Descargar y visualizar el documento oficial en PDF que ampara el presupuesto autorizado por la empresa.",
                            proceso: "Haz clic en el botón verde <strong>'Ver Orden'</strong> para abrir o descargar el documento con los números oficiales de Orden y Pedido.",
                            impactoEstado: "Confirma que el ticket se encuentra en 'En Reparación (Taller)'.",
                            reglasNegocio: "<strong>Regla de Oro del Proveedor:</strong> NUNCA inicies compras de refacciones ni trabajos mecánicos sin verificar este documento oficial."
                        },
                        {
                            nombre: "Corregir Cotización Rechazada",
                            color: "badge-btn-ambar",
                            icono: "🔄",
                            pantalla: "Cotizaciones en estatus 'Correcciones/Taller'",
                            proposito: "Ajustar los precios unitarios conforme a las recomendaciones de costo enviadas por el supervisor.",
                            proceso: "1. Haz clic en <strong>'Corregir Cotización'</strong>.<br>2. Ajusta los montos observados en la tabla.<br>3. Haz clic en 'Reenviar Cotización Corregida'.",
                            impactoEstado: "Regresa el ticket a 'Esperando / Aprob. Cotizacion (Supervisor)' para su reaprobación.",
                            reglasNegocio: "Permite subsanar observaciones de precio sin perder el folio de servicio."
                        },
                        {
                            nombre: "Marcar Unidad Lista para Entrega",
                            color: "badge-btn-cyan",
                            icono: "🏁",
                            pantalla: "Cotizaciones en estatus 'En Reparación'",
                            proposito: "Notificar formalmente a la empresa que los trabajos físicos han concluido y que el auto está listo para su retiro.",
                            proceso: "1. Verifica que la reparación esté completa al 100%.<br>2. Haz clic en el botón <strong>'Marcar como Lista'</strong>.<br>3. Confirma la advertencia de finalización.",
                            impactoEstado: "El sistema genera de forma criptográfica un <strong>Código PIN OTP de 8 dígitos</strong> y lo envía de inmediato y exclusivamente al correo del chofer para recoger su carro. Notifica al supervisor que la unidad está terminada.",
                            reglasNegocio: "Solo se debe pulsar cuando la unidad esté totalmente armada, probada y lista para circular."
                        }
                    ]
                },
                {
                    id: "taller-facturas",
                    nombre: "Facturas Fiscales y Cobro",
                    icono: "💰",
                    descripcion: "Carga de comprobantes fiscales digitales para radicar el pago del servicio concluido.",
                    botones: [
                        {
                            nombre: "Subir Factura Final (PDF + XML)",
                            color: "badge-btn-verde",
                            icono: "📤",
                            pantalla: "Bandeja Facturas Oficiales",
                            proposito: "Cargar la factura electrónica formal del SAT para tramitar el cobro de la orden terminada.",
                            proceso: "1. En la bandeja de Facturas, localiza el ticket entregado y haz clic en <strong>'Subir Factura'</strong>.<br>2. Adjunta obligatoriamente dos archivos: el archivo <strong>PDF</strong> y el archivo <strong>XML</strong> del CFDI.<br>3. Haz clic en 'Guardar Comprobantes'.",
                            impactoEstado: "Mueve el ticket a 'Esperando Rev/Factura' y notifica al supervisor de zona para su revisión fiscal.",
                            reglasNegocio: "<strong>Requisito Estricto:</strong> Ambos archivos (PDF y XML) son indispensables. El importe fiscal debe coincidir con el monto autorizado en la orden de compra."
                        }
                    ]
                },
                {
                    id: "taller-retrabajos",
                    nombre: "Garantías y Retrabajos",
                    icono: "🛡️",
                    descripcion: "Atención de vehículos reingresados por garantía dentro de los 30 días posteriores al servicio previo.",
                    botones: [
                        {
                            nombre: "Retrabajo (Bandeja)",
                            color: "badge-btn-verde",
                            icono: "🛡️",
                            pantalla: "Barra lateral -> Módulo Garantía -> Retrabajo",
                            proposito: "Consultar las unidades reasignadas a tu taller bajo cobertura de garantía.",
                            proceso: "Haz clic en 'Retrabajo' en la barra lateral para inspeccionar el motivo del reclamo y la fecha de cobertura.",
                            impactoEstado: "Muestra los tickets reasignados para atención inmediata sin costo de mano de obra.",
                            reglasNegocio: "Los trabajos de garantía tienen carácter prioritario conforme a los términos del servicio."
                        },
                        {
                            nombre: "Marcar Unidad Reparada (Retrabajo)",
                            color: "badge-btn-cyan",
                            icono: "🏁",
                            pantalla: "Vista Retrabajo -> Columna Acciones",
                            proposito: "Notificar formalmente a la empresa que la falla en garantía ha sido corregida satisfactoriamente.",
                            proceso: "1. Completa la revisión y compostura del vehículo en garantía.<br>2. Haz clic en el botón <strong>'Marcar como Reparada'</strong>.<br>3. Confirma la acción.",
                            impactoEstado: "Muestra pantalla de carga de confirmación y despacha correos automáticos al supervisor y al chofer con los códigos de seguridad para liberar el auto.",
                            reglasNegocio: "El ticket pasa a la bandeja de Liberar/Retrabajo del supervisor."
                        }
                    ]
                },
                {
                    id: "taller-archivo",
                    nombre: "Archivo Histórico",
                    icono: "🗄️",
                    descripcion: "Consulta de órdenes terminadas y facturas históricas del taller.",
                    botones: [
                        {
                            nombre: "Archivo Histórico",
                            color: "badge-btn-dark",
                            icono: "🗄️",
                            pantalla: "Barra lateral -> Archivo Histórico",
                            proposito: "Consultar el historial completo de órdenes atendidas y comprobantes tramitados por tu taller.",
                            proceso: "Haz clic en 'Archivo Histórico' para buscar servicios concluidos.",
                            impactoEstado: "Consulta de registros pasados.",
                            reglasNegocio: "Permite conciliar pagos y trámites contables con la empresa."
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
        // 1. Revisar subrol-actual (Administración: Jefatura, Supervisor, Administrador)
        const subrolInput = document.getElementById("subrol-actual");
        if (subrolInput && subrolInput.value) {
            const sub = subrolInput.value.trim();
            if (sub === "Jefatura") return "Jefatura";
            if (sub === "Supervisor") return "Supervisor";
            if (sub === "Administrador") return "Administrador";
        }

        // 2. Revisar rol-actual
        const rolInput = document.getElementById("rol-actual");
        if (rolInput && rolInput.value) {
            const rol = rolInput.value.trim();
            if (rol === "proveedores") return "Taller";
            if (rol === "corporativos") return "Corporativos";
            if (rol === "administracion") return "Administrador";
        }

        // 3. Revisar URL
        const path = window.location.pathname;
        if (path.includes("proveedores")) return "Taller";
        if (path.includes("corporativos")) return "Corporativos";
        if (path.includes("administracion")) return "Supervisor";

        return "Supervisor"; // Fallback por defecto
    }

    // -------------------------------------------------------------
    // CONSTRUCCIÓN DEL MODAL DINÁMICO EN EL DOM
    // -------------------------------------------------------------
    let tabActivaId = null;

    function renderizarManual(perfil) {
        const datos = DATOS_MANUAL[perfil] || DATOS_MANUAL["Supervisor"];

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

        datos.modulos.forEach((mod) => {
            const isActive = mod.id === tabActivaId;
            totalBotones += mod.botones.length;

            tabsHtml += `
                <button type="button" class="manual-tab-btn ${isActive ? 'active' : ''}" onclick="window.cambiarTabManual('${mod.id}')">
                    <span>${mod.icono} ${mod.nombre}</span>
                    <span class="manual-tab-count">${mod.botones.length}</span>
                </button>
            `;

            let botonesHtml = "";
            mod.botones.forEach((btn) => {
                botonesHtml += `
                    <div class="manual-card" data-manual-btn="${btn.nombre.toLowerCase()} ${btn.proposito.toLowerCase()} ${btn.proceso.toLowerCase()} ${btn.pantalla.toLowerCase()} ${mod.nombre.toLowerCase()}">
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
                                    <div class="manual-info-label">🎯 ¿Para qué sirve? (Explicación):</div>
                                    <div class="manual-info-desc">${btn.proposito}</div>
                                </div>
                                <div class="manual-info-row">
                                    <div class="manual-info-label">📋 ¿Cómo realizar la acción?:</div>
                                    <div class="manual-info-desc">${btn.proceso}</div>
                                </div>
                                <div class="manual-info-row">
                                    <div class="manual-info-label">🚦 Impacto en el Sistema / Ticket:</div>
                                    <div class="manual-info-desc">
                                        <span class="manual-state-change">${btn.impactoEstado}</span>
                                    </div>
                                </div>
                                <div class="manual-info-row">
                                    <div class="manual-info-label">⚖️ Reglas y Validaciones:</div>
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
                        <span>🔘 Botones de Acción Documentados (${mod.botones.length})</span>
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
                            <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 2px;">Guía Operativa y Catálogo de Botones (Telnor / RUMN)</div>
                        </div>
                        <span class="manual-badge-perfil ${datos.badgeClase}">Rol: ${perfil}</span>
                    </div>
                    <button type="button" class="manual-btn-close" onclick="window.cerrarManualSistema()" title="Cerrar Manual">&times;</button>
                </div>

                <!-- Barra de Búsqueda y Estadísticas -->
                <div class="manual-toolbar">
                    <div class="manual-search-box">
                        <span class="manual-search-icon">🔍</span>
                        <input type="text" id="manual-buscador" placeholder="Buscar botón, acción, regla de negocio o pantalla..." onkeyup="window.filtrarManual(this.value)">
                    </div>
                    <div class="manual-stats-badge">
                        <span>Botones Documentados del Rol: <strong>${totalBotones} botones</strong></span>
                    </div>
                </div>

                <!-- Cuerpo: Tabs a la izquierda y Contenido a la derecha -->
                <div class="manual-body">
                    <div class="manual-tabs-nav">
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; padding: 4px 8px; letter-spacing: 0.5px;">Módulos del Rol</div>
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
                        💡 Haz clic en cualquier botón de la lista para desplegar su ficha con la explicación y el paso a paso.
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

        // Actualizar estado de tabs
        const tabs = document.querySelectorAll(".manual-tab-btn");
        tabs.forEach(t => {
            t.classList.toggle("active", t.getAttribute("onclick").includes(moduloId));
        });

        // Alternar visibilidad de paneles
        const paneles = document.querySelectorAll(".manual-panel-content");
        paneles.forEach(p => p.style.display = "none");

        const target = document.getElementById("manual-panel-" + moduloId);
        if (target) {
            target.style.display = "block";
        }

        // Limpiar buscador si se cambió de tab
        const buscador = document.getElementById("manual-buscador");
        if (buscador && buscador.value) {
            buscador.value = "";
            window.filtrarManual("");
        }
    };

    window.toggleManualAccordion = function (headerEl) {
        const card = headerEl.closest(".manual-card");
        if (!card) return;
        const body = card.querySelector(".manual-card-body");
        const isOpen = card.classList.contains("open");

        if (isOpen) {
            card.classList.remove("open");
            if (body) body.style.maxHeight = null;
        } else {
            card.classList.add("open");
            if (body) body.style.maxHeight = (body.scrollHeight + 40) + "px";
        }
    };

    window.filtrarManual = function (termino) {
        const filtro = termino.toLowerCase().trim();
        const cards = document.querySelectorAll(".manual-card");

        cards.forEach(card => {
            const dataText = card.getAttribute("data-manual-btn") || "";
            if (!filtro || dataText.includes(filtro)) {
                card.style.display = "block";
                // Si hay un término de búsqueda, expandir automáticamente la tarjeta
                if (filtro) {
                    card.classList.add("open");
                    const body = card.querySelector(".manual-card-body");
                    if (body) body.style.maxHeight = (body.scrollHeight + 40) + "px";
                }
            } else {
                card.style.display = "none";
            }
        });
    };

    // Auto-cerrar al hacer clic en el backdrop oscuro
    document.addEventListener("click", function (e) {
        const modal = document.getElementById("modal-ayuda");
        if (modal && e.target === modal) {
            window.cerrarManualSistema();
        }
    });

    // Cerrar con la tecla Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            const modal = document.getElementById("modal-ayuda");
            if (modal && modal.style.display === "flex") {
                window.cerrarManualSistema();
            }
        }
    });

})();
