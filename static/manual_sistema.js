/**
 * =========================================================
 * ARCHIVO: static/manual_sistema.js
 * PROPÓSITO: Manual del Sistema específico por Rol.
 *            Muestra y explica únicamente los botones presentes
 *            en la interfaz del rol activo, indicando a quién o
 *            a qué paso continúa el flujo cuando maneja tickets,
 *            o su función básica cuando no maneja tickets.
 * =========================================================
 */

(function () {
    const DATOS_MANUAL = {
        "Jefatura": {
            titulo: "Manual de Usuario — Jefatura",
            badgeClase: "badge-jefa",
            descripcionPerfil: "Esta guía muestra únicamente los botones disponibles en tu interfaz de <strong>Jefatura</strong> y explica para qué sirve cada uno.",
            modulos: [
                {
                    id: "jefa-admin",
                    nombre: "Sección Administración",
                    icono: "📋",
                    descripcion: "Botones del menú lateral para administrar registros, accesos, catálogos y reportes del sistema.",
                    botones: [
                        {
                            nombre: "Nuevos Registros (Aprobar / Rechazar)",
                            color: "badge-btn-dark",
                            icono: "📥",
                            funcion: "Muestra las solicitudes de cuenta enviadas desde la pantalla de inicio por talleres o personal. Con el botón <strong>Aprobar</strong> creas su usuario y contraseña (enviándolos por correo), y con <strong>Rechazar</strong> descartas la solicitud.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Accesos (Credenciales)",
                            color: "badge-btn-dark",
                            icono: "🔑",
                            funcion: "Permite consultar los usuarios y contraseñas registrados en el sistema, así como editar sus datos o eliminar cuentas.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Ciudades / COPEs",
                            color: "badge-btn-dark",
                            icono: "🏢",
                            funcion: "Permite agregar o eliminar ciudades y edificios (COPEs) del catálogo oficial que se usa en los formularios del sistema.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Directorio Talleres",
                            color: "badge-btn-dark",
                            icono: "🔧",
                            funcion: "Muestra el listado de talleres mecánicos registrados con su encargado, teléfono, correo, dirección y ciudad base.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Lista de Corporativos",
                            color: "badge-btn-dark",
                            icono: "👔",
                            funcion: "Muestra el directorio de usuarios con rol Corporativo registrados en la plataforma.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Lista Automotriz",
                            color: "badge-btn-dark",
                            icono: "👥",
                            funcion: "Muestra el directorio del personal administrativo (Supervisores, Administrador y Jefatura) con su área y ciudad.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Panel de Control",
                            color: "badge-btn-dark",
                            icono: "📈",
                            funcion: "Abre el tablero visual con indicadores rápidos y gráficas sobre la actividad general del sistema.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Flujo de Trabajo",
                            color: "badge-btn-dark",
                            icono: "🔄",
                            funcion: "Muestra el diagrama informativo paso a paso de cómo avanza un ticket normal y un ticket en garantía dentro del sistema.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Analítica (y botón Descargar Reporte Excel)",
                            color: "badge-btn-verde",
                            icono: "📊",
                            funcion: "Muestra estadísticas de costos, tiempos y talleres. Incluye el botón <strong>Descargar Reporte Excel</strong> para exportar la información filtrada a un archivo <code>.xlsx</code>.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Sección de Reportes (Filtros, Detalles y Eliminar)",
                            color: "badge-btn-azul",
                            icono: "🗂️",
                            funcion: "Concentra todos los tickets con botones de filtro rápido (<em>Todos los Tickets, En Taller, Aprobación Pendiente, Facturación y Pago, Finalizados, Cotizaciones +10000, Garantía / Retrabajo, Cancelados</em>), botón <strong>Exportar a Excel</strong>, <strong>Ver Detalles</strong> para consultar el expediente y <strong>Eliminar</strong> para borrar un ticket del sistema.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Archivo General",
                            color: "badge-btn-dark",
                            icono: "🗄️",
                            funcion: "Muestra el historial de tickets finalizados y permite abrir o descargar su reporte completo en PDF, orden de compra y factura.",
                            flujoSiguiente: null
                        }
                    ]
                },
                {
                    id: "jefa-garantia-config",
                    nombre: "Garantía y Configuraciones",
                    icono: "⚙️",
                    descripcion: "Botones exclusivos de Jefatura para ajustar tiempos de garantía y parámetros globales del sistema.",
                    botones: [
                        {
                            nombre: "Tiempo/Garantía (y botón Ajustar Tiempo)",
                            color: "badge-btn-verde",
                            icono: "🛡️",
                            funcion: "Muestra el tiempo de garantía que ofrece cada taller y los tickets con garantía activa o vencida. Con el botón <strong>Ajustar Tiempo</strong> puedes modificar los días, horas, minutos y segundos de garantía de cualquier taller.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Cambiar configuraciones — Correo y Códigos (SMTP)",
                            color: "badge-btn-azul",
                            icono: "📧",
                            funcion: "Permite cambiar el correo emisor y contraseña de aplicación para el envío de notificaciones y códigos, agregar cuentas secundarias o pausar/activar los envíos automáticos.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Cambiar configuraciones — Control Presupuestal",
                            color: "badge-btn-verde",
                            icono: "💰",
                            funcion: "Permite actualizar el monto de presupuesto disponible para aprobar cotizaciones o usar el botón <strong>Resetear Dinero Utilizado</strong> para reiniciar la cuenta del dinero comprometido a $0.00.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Cambiar configuraciones — Límite para Cotizaciones Caras",
                            color: "badge-btn-ambar",
                            icono: "🏷️",
                            funcion: "Permite definir el monto límite (por defecto $10,000) a partir del cual una cotización se considera cara y requiere aprobación de Administrador y Corporativos.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Foto de Perfil / Cerrar Sesión",
                            color: "badge-btn-rojo",
                            icono: "👤",
                            funcion: "Al hacer clic en tu foto se abre tu ficha de perfil con opción a descargarla en PDF. El botón <strong>Cerrar Sesión</strong> finaliza tu sesión actual.",
                            flujoSiguiente: null
                        }
                    ]
                }
            ]
        },

        "Supervisor": {
            titulo: "Manual de Usuario — Supervisor",
            badgeClase: "badge-super",
            descripcionPerfil: "Esta guía muestra únicamente los botones disponibles en tu interfaz de <strong>Supervisor</strong>, explicando su función y a qué paso o rol continúa cada ticket.",
            modulos: [
                {
                    id: "super-flujo",
                    nombre: "Flujo del Ticket",
                    icono: "🔄",
                    descripcion: "Botones azules del menú lateral y acciones dentro de cada bandeja que hacen avanzar los tickets.",
                    botones: [
                        {
                            nombre: "Bandeja de Reportes → Asignar Taller",
                            color: "badge-btn-ambar",
                            icono: "🔧",
                            funcion: "Abre los reportes recién levantados por los choferes y permite elegir el taller mecánico y la compañía (Telnor o RUMN) que atenderá la unidad.",
                            flujoSiguiente: "Al confirmar la asignación, el ticket pasa a la bandeja <strong>Tickets de Trabajo</strong> del <strong>Taller (Proveedor)</strong> seleccionado para que revise la unidad y suba su cotización."
                        },
                        {
                            nombre: "Bandeja de Reportes → Comentarios (💬) y Eliminar (🗑️)",
                            color: "badge-btn-gray",
                            icono: "💬",
                            funcion: "El botón <strong>💬</strong> permite guardar o borrar una nota interna en el ticket. El botón <strong>🗑️</strong> elimina el reporte del sistema si fue capturado por error.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Cotizaciones y Órdenes → Aprobar Cotización (Orden y Pedido)",
                            color: "badge-btn-verde",
                            icono: "✅",
                            funcion: "Permite revisar el desglose enviado por el taller, registrar el Número de Orden y Número de Pedido con sus archivos PDF y aprobar la cotización.",
                            flujoSiguiente: "• Si ninguna cotización individual supera los $10,000: el ticket pasa directo a la bandeja <strong>Cotizaciones (En Reparación)</strong> del <strong>Taller</strong> para que inicie el trabajo.<br>• Si alguna cotización individual supera los $10,000: el ticket pasa a <strong>Cotizaciones +10000</strong> del <strong>Administrador</strong> y después a <strong>Corporativos</strong> antes de que el taller pueda reparar."
                        },
                        {
                            nombre: "Cotizaciones y Órdenes → Rechazar y Sugerir Precios",
                            color: "badge-btn-ambar",
                            icono: "⚠️",
                            funcion: "Permite devolver la cotización al taller indicando precios sugeridos cuando algún monto es elevado.",
                            flujoSiguiente: "El ticket regresa a la bandeja <strong>Cotizaciones</strong> del <strong>Taller (Proveedor)</strong> en estado <em>Correcciones/Taller</em> para que ajuste los precios y la reenvíe al Supervisor."
                        },
                        {
                            nombre: "Cotizaciones y Órdenes → Solicitar Rehacer Cotización",
                            color: "badge-btn-rojo",
                            icono: "🔄",
                            funcion: "Elimina la cotización actual cuando tiene errores de captura o faltan evidencias, enviando el motivo al taller.",
                            flujoSiguiente: "El ticket regresa al paso inicial en la bandeja <strong>Tickets de Trabajo</strong> del <strong>Taller (Proveedor)</strong> para que elabore la cotización nuevamente desde cero."
                        },
                        {
                            nombre: "Cotizaciones y Órdenes → Cancelar Ticket (Cotización Cara)",
                            color: "badge-btn-rojo",
                            icono: "✖",
                            funcion: "Cancela definitivamente el ticket cuando la reparación es incosteable para la unidad.",
                            flujoSiguiente: "El ticket queda en estado <strong>Cancelado por Cotización Cara</strong> y la unidad se marca como <strong>Inactiva</strong>."
                        },
                        {
                            nombre: "Cotizaciones y Órdenes → Validar Código de Liberación (PIN)",
                            color: "badge-btn-azul",
                            icono: "🔑",
                            funcion: "Cuando el taller marca la unidad como lista, este botón permite ingresar el código de 8 dígitos que recibió el chofer en su correo para confirmar la entrega del vehículo.",
                            flujoSiguiente: "La unidad queda entregada (iniciando su periodo de garantía) y el ticket avanza a la bandeja <strong>Facturas</strong> del <strong>Taller (Proveedor)</strong> para que suba su factura fiscal (PDF y XML)."
                        },
                        {
                            nombre: "Facturas → Revisar Factura (Aprobar / No Aprobar)",
                            color: "badge-btn-verde",
                            icono: "📑",
                            funcion: "Abre el visor con el PDF y XML de la factura fiscal subida por el taller para verificar que los datos e importes sean correctos.",
                            flujoSiguiente: "• Al presionar <strong>Aprobar Factura</strong>: el ticket pasa a <strong>Liberar Doc. Contable</strong> del <strong>Administrador</strong> (y a tu bandeja de <strong>Documentos Contables</strong>).<br>• Al presionar <strong>No Aprobar</strong>: la factura se devuelve a la bandeja <strong>Facturas</strong> del <strong>Taller</strong> para que suba los archivos corregidos."
                        },
                        {
                            nombre: "Documentos Contables → Guardar Números y Archivar Ticket",
                            color: "badge-btn-verde",
                            icono: "📜",
                            funcion: "Una vez que el Administrador liberó el ticket para documento contable, permite capturar el número de Documento Contable de cada cotización.",
                            flujoSiguiente: "Al guardar los números, el ciclo del ticket concluye y pasa definitivamente a <strong>Archivo General / Histórico</strong> como finalizado."
                        }
                    ]
                },
                {
                    id: "super-garantia-delegacion",
                    nombre: "Garantía y Delegación",
                    icono: "🛡️",
                    descripcion: "Botones verdes de Garantía/Retrabajo y botones amarillos de Delegación por Ausencia.",
                    botones: [
                        {
                            nombre: "Retrabajo → Ver Detalles (Reasignar / Cancelar Reasignación)",
                            color: "badge-btn-verde",
                            icono: "🛡️",
                            funcion: "Muestra los tickets reportados en garantía (Sección 1 del chofer y Sección 2 del taller previo). Desde el detalle puedes presionar <strong>Reasignar</strong> para enviarlo al taller o <strong>Cancelar Reasignación</strong> si no procede la garantía.",
                            flujoSiguiente: "• Al presionar <strong>Reasignar</strong>: el ticket pasa a la bandeja <strong>Retrabajo</strong> del <strong>Taller (Proveedor)</strong> para que repare la falla sin costo.<br>• Al presionar <strong>Cancelar Reasignación</strong>: se notifica el motivo al chofer por correo y la garantía se cierra."
                        },
                        {
                            nombre: "Retrabajo → Aplicar garantía/Cotizaciones Caras",
                            color: "badge-btn-verde",
                            icono: "💰",
                            funcion: "Permite al Supervisor buscar un ticket de cotización cara (+$10,000) que requiera garantía, escribir la falla que persiste y generar el retrabajo.",
                            flujoSiguiente: "El ticket aparece en tu bandeja de <strong>Retrabajo</strong> listo para reasignarlo al <strong>Taller</strong>; cuando el taller termina la reparación, el código de liberación llega <strong>únicamente al Supervisor</strong> para validarlo en <strong>Liberar/Retrabajo</strong>."
                        },
                        {
                            nombre: "Liberar/Retrabajo → Validar y Liberar Unidad",
                            color: "badge-btn-verde",
                            icono: "🔐",
                            funcion: "Cuando el taller marca como reparada una unidad en garantía, este botón permite ingresar el código de 6 dígitos para liberar la unidad.",
                            flujoSiguiente: "Al validar el código, el retrabajo queda <strong>Finalizado / Liberado</strong> y la unidad regresa a estar activa en circulación."
                        },
                        {
                            nombre: "Delegación Por Ausencia → Cotizaciones +10000",
                            color: "badge-btn-ambar",
                            icono: "🤝",
                            funcion: "Permite cubrir temporalmente al Administrador ausente para revisar y aprobar cotizaciones mayores a $10,000 (si eliges Cancelar en la alerta inicial, se mantiene seleccionado el botón en el que estabas).",
                            flujoSiguiente: "Al aprobar la cotización en suplencia, el ticket avanza al portal de <strong>Corporativos (Cotizaciones)</strong> para su autorización ejecutiva."
                        },
                        {
                            nombre: "Delegación Por Ausencia → Liberar Doc. Contable",
                            color: "badge-btn-ambar",
                            icono: "🤝",
                            funcion: "Permite cubrir temporalmente al Administrador ausente para autorizar la liberación previa al registro del documento contable.",
                            flujoSiguiente: "Al liberar el ticket en suplencia, queda habilitado en <strong>Documentos Contables</strong> para capturar el número contable y archivarlo."
                        }
                    ]
                },
                {
                    id: "super-admin",
                    nombre: "Sección Administración",
                    icono: "📋",
                    descripcion: "Botones de consulta, catálogos de unidades y reportes que no alteran el flujo activo de los tickets.",
                    botones: [
                        {
                            nombre: "Directorio Talleres / Lista de Corporativos / Lista Automotriz",
                            color: "badge-btn-dark",
                            icono: "📋",
                            funcion: "Permiten consultar los datos de contacto de los talleres proveedores, directivos corporativos y personal de administración automotriz.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Unidades (Filtros de Flota, + Agregar Unidad, Editar, Inactivar, Jurídicos)",
                            color: "badge-btn-azul",
                            icono: "🚘",
                            funcion: "Permite filtrar las unidades por su estado (<em>Todas, En Circulación, En Taller, Garantía / Retrabajo, Inhabilitadas, Jurídicos</em>), dar de alta nuevas unidades, editar su marca/modelo, activarlas/inactivarlas o ponerlas en estado de Jurídicos.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Accesos (Credenciales)",
                            color: "badge-btn-dark",
                            icono: "🔑",
                            funcion: "Permite consultar las credenciales de acceso de los usuarios registrados.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Flujo de Trabajo",
                            color: "badge-btn-dark",
                            icono: "🔄",
                            funcion: "Muestra la guía visual con todos los pasos del flujo normal y del flujo de garantías.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Analítica / Sección de Reportes / Archivo General",
                            color: "badge-btn-dark",
                            icono: "📊",
                            funcion: "<strong>Analítica</strong> muestra gráficas y exporta reportes a Excel; <strong>Sección de Reportes</strong> permite filtrar tickets por etapa (incluyendo <em>Cotizaciones +10000</em> y <em>Garantía/Retrabajo</em>); <strong>Archivo General</strong> muestra los expedientes cerrados y sus PDFs.",
                            flujoSiguiente: null
                        }
                    ]
                }
            ]
        },

        "Administrador": {
            titulo: "Manual de Usuario — Administrador",
            badgeClase: "badge-admin",
            descripcionPerfil: "Esta guía muestra únicamente los botones disponibles en tu interfaz de <strong>Administrador</strong>, explicando su función y a quién continúa el proceso en cada paso.",
            modulos: [
                {
                    id: "admin-flujo",
                    nombre: "Flujo del Ticket",
                    icono: "🔄",
                    descripcion: "Botones principales del Administrador para validar cotizaciones mayores a $10,000 y liberar documentos contables.",
                    botones: [
                        {
                            nombre: "Cotizaciones +10000 → Revisar y Aprobar Cotización Mayor",
                            color: "badge-btn-verde",
                            icono: "💎",
                            funcion: "Muestra los tickets donde alguna cotización individual supera los $10,000 (y que ya fueron revisados por el Supervisor). Permite inspeccionar el desglose y aprobar su envío a nivel ejecutivo.",
                            flujoSiguiente: "Al aprobar la cotización, el ticket se envía a la bandeja <strong>Cotizaciones</strong> del rol <strong>Corporativos (Dirección)</strong> para su autorización ejecutiva final."
                        },
                        {
                            nombre: "Cotizaciones +10000 → Rechazar Cotización Mayor",
                            color: "badge-btn-rojo",
                            icono: "↩️",
                            funcion: "Permite rechazar una cotización mayor indicando el motivo o precios sugeridos cuando el presupuesto no procede.",
                            flujoSiguiente: "El ticket regresa a la bandeja <strong>Cotizaciones (Correcciones/Taller)</strong> del <strong>Taller (Proveedor)</strong> para que ajuste su propuesta."
                        },
                        {
                            nombre: "Liberar Doc. Contable → Liberar / Guardar Doc. Contable",
                            color: "badge-btn-azul",
                            icono: "📜",
                            funcion: "Muestra las facturas fiscales que ya fueron validadas por el Supervisor. Permite autorizar la liberación contable o ingresar los números de documento contable.",
                            flujoSiguiente: "Al liberar el ticket pasa a <strong>Documentos Contables</strong> del <strong>Supervisor</strong> para el registro de los folios contables (o si registras directamente los números de documento contable, el ticket se cierra y pasa a <strong>Archivo General / Histórico</strong>)."
                        }
                    ]
                },
                {
                    id: "admin-delegacion",
                    nombre: "Delegación Por Ausencia",
                    icono: "🤝",
                    descripcion: "Botones amarillos para cubrir funciones del Supervisor únicamente en caso de ausencia o contingencia.",
                    botones: [
                        {
                            nombre: "Cotizaciones y Órdenes (Delegación)",
                            color: "badge-btn-ambar",
                            icono: "🛡️",
                            funcion: "Permite cubrir al Supervisor ausente para aprobar cotizaciones estándar con Orden/Pedido o validar el código PIN de entrega de una unidad (si cancelas la alerta inicial, se conserva seleccionado tu botón anterior).",
                            flujoSiguiente: "• Al aprobar una cotización estándar: pasa al <strong>Taller (En Reparación)</strong>.<br>• Al validar el PIN de entrega: pasa a la bandeja <strong>Facturas</strong> del <strong>Taller</strong>."
                        },
                        {
                            nombre: "Facturas (Delegación)",
                            color: "badge-btn-ambar",
                            icono: "📑",
                            funcion: "Permite cubrir al Supervisor ausente para revisar y aprobar los archivos PDF y XML de las facturas fiscales subidas por los talleres.",
                            flujoSiguiente: "Al aprobar la factura fiscal en suplencia, el ticket avanza a tu bandeja <strong>Liberar Doc. Contable</strong>."
                        }
                    ]
                },
                {
                    id: "admin-consulta",
                    nombre: "Sección Administración",
                    icono: "📋",
                    descripcion: "Botones de consulta, reportes, analítica y archivo que no alteran el flujo de tickets.",
                    botones: [
                        {
                            nombre: "Flujo de Trabajo",
                            color: "badge-btn-dark",
                            icono: "🔄",
                            funcion: "Muestra el diagrama explicativo con todas las etapas de un ticket normal y de las garantías.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Analítica (y botón Descargar Reporte Excel)",
                            color: "badge-btn-verde",
                            icono: "📊",
                            funcion: "Permite consultar gráficas de costos y desempeño de talleres, y descargar el reporte en formato Excel (<code>.xlsx</code>).",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Sección de Reportes",
                            color: "badge-btn-azul",
                            icono: "🗂️",
                            funcion: "Permite consultar y filtrar todos los tickets por etapa (<em>Todos los Tickets, En Taller, Aprobación Pendiente, Facturación y Pago, Finalizados, Cotizaciones +10000, Garantía / Retrabajo, Cancelados</em>), ver detalles y exportar a Excel.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Archivo General",
                            color: "badge-btn-dark",
                            icono: "🗄️",
                            funcion: "Consulta de todos los expedientes finalizados con acceso a su PDF de reporte, orden de compra y factura fiscal.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Foto de Perfil / Cerrar Sesión",
                            color: "badge-btn-rojo",
                            icono: "👤",
                            funcion: "Al pulsar tu foto puedes ver tu perfil y descargarlo en PDF. El botón <strong>Cerrar Sesión</strong> sale de tu cuenta.",
                            flujoSiguiente: null
                        }
                    ]
                }
            ]
        },

        "Corporativos": {
            titulo: "Manual de Usuario — Dirección Corporativa",
            badgeClase: "badge-corp",
            descripcionPerfil: "Esta guía muestra únicamente los botones disponibles en tu interfaz de <strong>Dirección Corporativa</strong>, explicando su función y hacia quién continúa el ticket.",
            modulos: [
                {
                    id: "corp-flujo",
                    nombre: "Flujo del Ticket (Cotizaciones)",
                    icono: "💎",
                    descripcion: "Botones para revisar y autorizar o rechazar cotizaciones individuales mayores a $10,000.",
                    botones: [
                        {
                            nombre: "Cotizaciones → Revisar",
                            color: "badge-btn-azul",
                            icono: "🔍",
                            funcion: "Abre la ventana de revisión con los detalles completos de la cotización mayor a $10,000 (desglose de precios, evidencias fotográficas, PDF del taller y datos del vehículo).",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Modal de Revisión → Aprobar Cotización Mayor",
                            color: "badge-btn-verde",
                            icono: "✅",
                            funcion: "Otorga la autorización ejecutiva final para que proceda el gasto de la cotización mayor a $10,000.",
                            flujoSiguiente: "Al aprobarse, el ticket pasa a la bandeja <strong>Cotizaciones (En Reparación)</strong> del <strong>Taller (Proveedor)</strong> para que inicie la reparación física de la unidad (o si falta adjuntar la Orden/Pedido, se habilita al <strong>Supervisor</strong> para subirla y pasar al Taller)."
                        },
                        {
                            nombre: "Modal de Revisión → Rechazar Cotización",
                            color: "badge-btn-rojo",
                            icono: "❌",
                            funcion: "Permite rechazar el presupuesto mayor escribiendo el motivo exacto del rechazo.",
                            flujoSiguiente: "El ticket regresa a la bandeja <strong>Cotizaciones (Correcciones/Taller)</strong> del <strong>Taller (Proveedor)</strong> y se notifica por correo para que ajuste su cotización."
                        }
                    ]
                },
                {
                    id: "corp-admin",
                    nombre: "Administración y Perfil",
                    icono: "🗄️",
                    descripcion: "Botones de consulta histórica y perfil del directivo.",
                    botones: [
                        {
                            nombre: "Archivo Histórico",
                            color: "badge-btn-dark",
                            icono: "🗄️",
                            funcion: "Muestra el listado histórico de tickets cerrados con su folio fiscal, unidad, proveedor y precio, permitiendo abrir el expediente completo en PDF.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Foto de Perfil / Cerrar Sesión",
                            color: "badge-btn-rojo",
                            icono: "👤",
                            funcion: "Al hacer clic en tu foto de perfil se muestra tu expediente de usuario con el botón <strong>Confirmar y Descargar PDF</strong>. El botón <strong>Cerrar Sesión</strong> finaliza la sesión actual.",
                            flujoSiguiente: null
                        }
                    ]
                }
            ]
        },

        "Taller": {
            titulo: "Manual de Usuario — Portal de Proveedores (Taller)",
            badgeClase: "badge-taller",
            descripcionPerfil: "Esta guía muestra únicamente los botones disponibles en tu interfaz de <strong>Proveedor / Taller</strong>, explicando para qué sirve cada uno y a quién pasa el ticket.",
            modulos: [
                {
                    id: "taller-flujo",
                    nombre: "Flujo del Ticket",
                    icono: "🔧",
                    descripcion: "Botones del menú lateral y de las tablas para cotizar, reparar, entregar unidades y subir facturas.",
                    botones: [
                        {
                            nombre: "Tickets de Trabajo → Crear Cotización / Diagnóstico",
                            color: "badge-btn-ambar",
                            icono: "📝",
                            funcion: "Permite capturar el diagnóstico mecánico de la unidad asignada, agregar una o más cotizaciones con su título y precio sin IVA, adjuntar el PDF del presupuesto y subir fotos o video de evidencia.",
                            flujoSiguiente: "Al enviar la cotización, el ticket pasa a la bandeja <strong>Cotizaciones y Órdenes</strong> del <strong>Supervisor</strong> para su revisión (y si alguna cotización individual supera los $10,000, pasará también al <strong>Administrador</strong> y a <strong>Corporativos</strong>)."
                        },
                        {
                            nombre: "Cotizaciones → Ver Orden / Detalles",
                            color: "badge-btn-azul",
                            icono: "📄",
                            funcion: "Permite consultar el desglose enviado y, una vez aprobada la cotización, visualizar y descargar el PDF con los números oficiales de Orden y Pedido.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Cotizaciones → Corregir Cotización",
                            color: "badge-btn-ambar",
                            icono: "🔄",
                            funcion: "Aparece cuando el Supervisor o Corporativos solicitan ajustar precios. Permite modificar los importes conforme a los precios sugeridos y volver a enviar la cotización.",
                            flujoSiguiente: "Al reenviar la cotización corregida, el ticket regresa a la bandeja <strong>Cotizaciones y Órdenes</strong> del <strong>Supervisor</strong> para su aprobación."
                        },
                        {
                            nombre: "Cotizaciones → Marcar como Lista (Unidad Reparada)",
                            color: "badge-btn-cyan",
                            icono: "🏁",
                            funcion: "Se presiona cuando el taller ya terminó físicamente la reparación del vehículo y la unidad está lista para entregarse.",
                            flujoSiguiente: "El sistema envía un código PIN de 8 dígitos al correo del <strong>Chofer</strong> y habilita al <strong>Supervisor</strong> en <strong>Cotizaciones y Órdenes</strong> para validar ese PIN al entregar la unidad; una vez validado el PIN, el ticket pasa a tu bandeja de <strong>Facturas</strong>."
                        },
                        {
                            nombre: "Facturas → Subir Factura Fiscal (PDF y XML)",
                            color: "badge-btn-verde",
                            icono: "📤",
                            funcion: "Permite ingresar el Folio Fiscal y adjuntar los archivos PDF y XML de la factura una vez que la unidad ya fue entregada.",
                            flujoSiguiente: "Al guardar la factura, el ticket pasa a la bandeja <strong>Facturas</strong> del <strong>Supervisor</strong> para su validación fiscal (y posteriormente al <strong>Administrador</strong> para Documento Contable)."
                        }
                    ]
                },
                {
                    id: "taller-garantia-archivo",
                    nombre: "Garantía y Administración",
                    icono: "🛡️",
                    descripcion: "Botones para atender unidades en garantía/retrabajo, configurar el tiempo de garantía y consultar el archivo.",
                    botones: [
                        {
                            nombre: "Retrabajo → Detalles y Ver Fotos/Video",
                            color: "badge-btn-azul",
                            icono: "🔍",
                            funcion: "Permite revisar la Sección 1 (reporte original del chofer), la Sección 2 (cotización y trabajo previo realizado) y el motivo por el cual la unidad reingresó por garantía.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Retrabajo → Marcar como Reparada (Finalizar Retrabajo)",
                            color: "badge-btn-verde",
                            icono: "✅",
                            funcion: "Se presiona cuando el taller ya corrigió la falla reportada en garantía.",
                            flujoSiguiente: "El sistema envía el código de liberación de 6 dígitos (al <strong>Supervisor</strong> y al <strong>Chofer</strong> en garantía normal, o únicamente al <strong>Supervisor</strong> si es garantía de cotización cara) y el ticket pasa a la bandeja <strong>Liberar/Retrabajo</strong> del <strong>Supervisor</strong> para liberar la unidad."
                        },
                        {
                            nombre: "Archivo Histórico (y botón ⏱️ Tiempo/Garantía)",
                            color: "badge-btn-dark",
                            icono: "🗄️",
                            funcion: "Muestra el historial de todos tus tickets finalizados. En la esquina superior derecha incluye el botón <strong>⏱️ Tiempo/Garantía</strong> para configurar cuántos días, horas, minutos y segundos de garantía ofrece tu taller y notificarlo a Jefatura.",
                            flujoSiguiente: null
                        },
                        {
                            nombre: "Logo de Perfil / Cerrar Sesión",
                            color: "badge-btn-rojo",
                            icono: "👤",
                            funcion: "Al pulsar el logo de tu taller puedes ver tu expediente y descargarlo en PDF. El botón <strong>Cerrar Sesión</strong> cierra tu sesión actual.",
                            flujoSiguiente: null
                        }
                    ]
                }
            ]
        }
    };

    function detectarPerfilActual() {
        const subrolInput = document.getElementById("subrol-actual");
        if (subrolInput && subrolInput.value) {
            const sub = subrolInput.value.trim();
            if (sub === "Jefatura") return "Jefatura";
            if (sub === "Supervisor") return "Supervisor";
            if (sub === "Administrador") return "Administrador";
        }

        const rolInput = document.getElementById("rol-actual");
        if (rolInput && rolInput.value) {
            const rol = rolInput.value.trim();
            if (rol === "proveedores") return "Taller";
            if (rol === "corporativos") return "Corporativos";
            if (rol === "administracion") return "Administrador";
        }

        const path = window.location.pathname;
        if (path.includes("proveedores")) return "Taller";
        if (path.includes("corporativos")) return "Corporativos";
        if (path.includes("administracion")) return "Supervisor";

        return "Supervisor";
    }

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
                const textoBusqueda = `${btn.nombre} ${btn.funcion} ${btn.flujoSiguiente || ''} ${mod.nombre}`.toLowerCase();
                const bloqueFlujo = btn.flujoSiguiente
                    ? `<div class="manual-btn-flow"><strong>➡️ ¿A quién o a qué paso continúa el ticket?:</strong><br>${btn.flujoSiguiente}</div>`
                    : ``;

                botonesHtml += `
                    <div class="manual-card" data-manual-btn="${textoBusqueda.replace(/"/g, '&quot;')}">
                        <div class="manual-card-top" onclick="window.toggleManualAccordion(this)">
                            <div class="manual-card-top-left">
                                <span class="manual-badge-accion ${btn.color}">
                                    <span>${btn.icono}</span>
                                    <span>${btn.nombre}</span>
                                </span>
                            </div>
                            <span class="manual-card-arrow">▼</span>
                        </div>
                        <div class="manual-card-body">
                            <p class="manual-btn-desc"><strong>¿Qué hace y para qué sirve?:</strong> ${btn.funcion}</p>
                            ${bloqueFlujo}
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
                    <div class="manual-cards-list">
                        ${botonesHtml}
                    </div>
                </div>
            `;
        });

        modalExistente.innerHTML = `
            <div class="manual-container" onclick="event.stopPropagation()">
                <!-- Fondo Azul Marino con Imágenes Sutiles -->
                <div class="manual-bg-decor">
                    <img src="/static/telnor_logo.png" alt="" class="manual-bg-img-telnor">
                    <img src="/static/RUMN_logo.png" alt="" class="manual-bg-img-rumn">
                    <img src="/static/telnor_nombre.jpg" alt="" class="manual-bg-img-nombre">
                </div>

                <!-- Header -->
                <div class="manual-header">
                    <div class="manual-header-title">
                        <span style="font-size: 1.4rem;">📖</span>
                        <h3>${datos.titulo}</h3>
                        <span class="manual-badge-perfil ${datos.badgeClase}">Rol: ${perfil}</span>
                    </div>
                    <button type="button" class="manual-btn-close" onclick="window.cerrarManualSistema()" title="Cerrar">&times;</button>
                </div>

                <!-- Buscador -->
                <div class="manual-toolbar">
                    <div class="manual-search-box">
                        <span class="manual-search-icon">🔍</span>
                        <input type="text" id="manual-buscador" placeholder="Buscar botón o función de tu rol..." onkeyup="window.filtrarManual(this.value)">
                    </div>
                    <div class="manual-stats-badge">
                        <span>Botones de tu rol: <strong>${totalBotones}</strong></span>
                    </div>
                </div>

                <!-- Cuerpo -->
                <div class="manual-body">
                    <div class="manual-tabs-nav">
                        ${tabsHtml}
                    </div>
                    <div class="manual-content-area" id="manual-content-area">
                        <div class="manual-role-summary">
                            ${datos.descripcionPerfil}
                        </div>
                        ${modulosHtml}
                    </div>
                </div>

                <!-- Footer -->
                <div class="manual-footer">
                    <div class="manual-footer-note">
                        💡 Haz clic sobre cualquier botón de la lista para desplegar su explicación.
                    </div>
                    <button type="button" class="manual-btn-done" onclick="window.cerrarManualSistema()">Cerrar manual</button>
                </div>
            </div>
        `;
    }

    window.toggleManualAccordion = function (headerEl) {
        const card = headerEl.closest(".manual-card");
        if (!card) return;
        card.classList.toggle("open");
    };

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

        const tabs = document.querySelectorAll(".manual-tab-btn");
        tabs.forEach(t => {
            t.classList.toggle("active", t.getAttribute("onclick").includes(moduloId));
        });

        const paneles = document.querySelectorAll(".manual-panel-content");
        paneles.forEach(p => p.style.display = "none");

        const target = document.getElementById("manual-panel-" + moduloId);
        if (target) {
            target.style.display = "block";
        }

        const buscador = document.getElementById("manual-buscador");
        if (buscador && buscador.value) {
            buscador.value = "";
            window.filtrarManual("");
        }
    };

    window.filtrarManual = function (termino) {
        const filtro = termino.toLowerCase().trim();
        const paneles = document.querySelectorAll(".manual-panel-content");
        const cards = document.querySelectorAll(".manual-card");

        if (filtro) {
            paneles.forEach(p => p.style.display = "block");
        } else {
            paneles.forEach(p => {
                p.style.display = (p.id === "manual-panel-" + tabActivaId) ? "block" : "none";
            });
        }

        cards.forEach(card => {
            const dataText = card.getAttribute("data-manual-btn") || "";
            card.style.display = (!filtro || dataText.includes(filtro)) ? "block" : "none";
        });
    };

    document.addEventListener("click", function (e) {
        const modal = document.getElementById("modal-ayuda");
        if (modal && e.target === modal) {
            window.cerrarManualSistema();
        }
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            const modal = document.getElementById("modal-ayuda");
            if (modal && modal.style.display === "flex") {
                window.cerrarManualSistema();
            }
        }
    });
})();
