import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('templates/administracion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Reemplazar barra superior de pasos por actividades independientes
pos_tabs_start = html.find('<!-- PESTAÑAS PASO A PASO')
if pos_tabs_start == -1:
    pos_tabs_start = html.find('id="tab-btn-cfg-correo"')
    pos_tabs_start = html.rfind('<!--', 0, pos_tabs_start)

pos_tabs_end = html.find('id="seccion-cfg-correo"')
pos_tabs_end = html.rfind('<!--', 0, pos_tabs_end)

new_tabs_html = """<!-- ACTIVIDADES INDEPENDIENTES DE CONFIGURACIÓN -->
                    <div style="background: #0b1523; border: 1px solid #1e293b; border-radius: 12px; padding: 6px; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin-bottom: 6px;">
                        <button type="button" id="tab-btn-cfg-correo" onclick="cambiarTabConfiguracion('correo')" style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; border: 1px solid #38bdf8; font-weight: 700; padding: 12px 20px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.25s ease; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35); font-size: 0.95rem;">
                            <span style="font-size: 1.15rem;">📧</span> <span>Correo y Códigos (SMTP)</span>
                        </button>
                        <button type="button" id="tab-btn-cfg-presupuesto" onclick="cambiarTabConfiguracion('presupuesto')" style="background: #0f172a; color: #94a3b8; border: 1px solid #1e293b; font-weight: 600; padding: 12px 20px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.25s ease; font-size: 0.95rem;">
                            <span style="font-size: 1.15rem;">💰</span> <span>Control Presupuestal</span>
                        </button>
                        <button type="button" id="tab-btn-cfg-limite" onclick="cambiarTabConfiguracion('limite')" style="background: #0f172a; color: #94a3b8; border: 1px solid #1e293b; font-weight: 600; padding: 12px 20px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.25s ease; font-size: 0.95rem;">
                            <span style="font-size: 1.15rem;">🏷️</span> <span>Cotizaciones Caras</span>
                        </button>
                    </div>

                    """

html = html[:pos_tabs_start] + new_tabs_html + html[pos_tabs_end:]
print("Pestañas de actividades independientes actualizadas.")

# 2. Reemplazar Sección 1 (Correo) con simetría perfecta y sin pie de paso
pos_sec1_start = html.find('id="seccion-cfg-correo"')
pos_sec1_div = html.rfind('<div', 0, pos_sec1_start)
pos_sec2_start = html.find('id="seccion-cfg-presupuesto"')
pos_sec2_comment = html.rfind('<!--', 0, pos_sec2_start)

new_sec1_html = """<div id="seccion-cfg-correo" style="background: linear-gradient(145deg, #0b1c30, #081422); border: 1px solid #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px; margin-bottom: 22px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 14px;">
                            <div>
                                <h3 style="margin: 0; color: #38bdf8; font-size: 1.25rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    <span>📧</span> Correo y Código de Envío de Notificaciones (SMTP)
                                </h3>
                                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                                    Configuración de la cuenta emisora para generar y despachar códigos PIN al chofer, órdenes al taller y avisos a supervisores.
                                </p>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="color: #94a3b8; font-size: 0.85rem;">Emisor Activo:</span>
                                <span id="cfg-badge-correo-activo" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">
                                    Cargando...
                                </span>
                            </div>
                        </div>

                        <!-- Formulario de Configuración del Emisor con Simetría Rigurosa -->
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 24px;">
                            <!-- Cuadro 1: Correo Remitente -->
                            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <label style="display: flex; align-items: center; justify-content: space-between; color: #cbd5e1; font-size: 0.88rem; font-weight: 600; margin-bottom: 8px; min-height: 22px;">
                                    <span>Correo Remitente Oficial:</span>
                                    <span style="color: #64748b; font-size: 0.75rem; font-weight: 400;">(Gmail / Institucional)</span>
                                </label>
                                <input type="email" id="cfg-correo-emisor" class="buscador-pildora" placeholder="ejemplo@gmail.com" style="width: 100%; height: 44px; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 0 14px; border-radius: 8px; font-size: 0.92rem;">
                            </div>

                            <!-- Cuadro 2: Contraseña de Aplicación -->
                            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <label style="display: flex; align-items: center; justify-content: space-between; color: #cbd5e1; font-size: 0.88rem; font-weight: 600; margin-bottom: 8px; min-height: 22px;">
                                    <span>Contraseña / Código de Aplicación:</span>
                                    <span style="color: #64748b; font-size: 0.75rem; font-weight: 400;">(16 dígitos de Google)</span>
                                </label>
                                <div style="position: relative; width: 100%; height: 44px; display: flex; align-items: center;">
                                    <input type="password" id="cfg-codigo-emisor" class="buscador-pildora" placeholder="zgdhbgcpuobszybi" style="width: 100%; height: 44px; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 0 44px 0 14px; border-radius: 8px; font-size: 0.92rem;">
                                    <button type="button" onclick="toggleMostrarPassword('cfg-codigo-emisor', this)" style="position: absolute; right: 8px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: transparent; border: none; cursor: pointer; font-size: 1.15rem; color: #94a3b8;" title="Mostrar / Ocultar código">👁️</button>
                                </div>
                            </div>

                            <!-- Cuadro 3: Servidor SMTP -->
                            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <label style="display: flex; align-items: center; justify-content: space-between; color: #cbd5e1; font-size: 0.88rem; font-weight: 600; margin-bottom: 8px; min-height: 22px;">
                                    <span>Servidor SMTP (Host):</span>
                                    <span style="color: #64748b; font-size: 0.75rem; font-weight: 400;">(Default: smtp.gmail.com)</span>
                                </label>
                                <input type="text" id="cfg-servidor-smtp" class="buscador-pildora" value="smtp.gmail.com" style="width: 100%; height: 44px; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 0 14px; border-radius: 8px; font-size: 0.92rem;">
                            </div>

                            <!-- Cuadro 4: Puerto SMTP -->
                            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <label style="display: flex; align-items: center; justify-content: space-between; color: #cbd5e1; font-size: 0.88rem; font-weight: 600; margin-bottom: 8px; min-height: 22px;">
                                    <span>Puerto SMTP (TLS / SSL):</span>
                                    <span style="color: #64748b; font-size: 0.75rem; font-weight: 400;">(Default: 587)</span>
                                </label>
                                <input type="number" id="cfg-puerto-smtp" class="buscador-pildora" value="587" style="width: 100%; height: 44px; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 0 14px; border-radius: 8px; font-size: 0.92rem;">
                            </div>
                        </div>

                        <!-- Botones de Acción de Correo (Simétricos y Balanceados) -->
                        <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px; align-items: center;">
                            <button type="button" class="btn-success" onclick="guardarCorreoEmisor()" style="background: #10b981; color: white; border: none; height: 42px; padding: 0 22px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);">
                                <span>💾</span> <span>Guardar Credenciales de Correo</span>
                            </button>
                            <button type="button" class="btn-secondary" onclick="abrirModalProbarCorreo()" style="background: #0284c7; color: white; border: none; height: 42px; padding: 0 20px; border-radius: 8px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);">
                                <span>✉️</span> <span>Enviar Correo de Prueba</span>
                            </button>
                            <button type="button" class="btn-secondary" onclick="abrirModalAgregarCuenta()" style="background: #1e293b; color: #f8fafc; border: 1px solid #334155; height: 42px; padding: 0 18px; border-radius: 8px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px;">
                                <span>➕</span> <span>Agregar Otra Cuenta</span>
                            </button>
                        </div>

                        <!-- Tabla de Cuentas Configuradas -->
                        <div style="margin-top: 20px;">
                            <h4 style="margin: 0 0 10px 0; color: #cbd5e1; font-size: 0.95rem; font-weight: 600;">
                                Cuentas de Correo Registradas para el Sistema:
                            </h4>
                            <div class="table-responsive" style="max-height: 280px; overflow-y: auto; border: 1px solid #1e293b; border-radius: 8px;">
                                <table>
                                    <thead>
                                        <tr style="background: #0f172a; position: sticky; top: 0; z-index: 2;">
                                            <th>Nombre / Alias</th>
                                            <th>Correo Electrónico</th>
                                            <th>Servidor : Puerto</th>
                                            <th style="text-align: center;">Estado</th>
                                            <th>Fecha Registro</th>
                                            <th style="text-align: center;">Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody id="tabla-cuentas-correo">
                                        <tr><td colspan="6" style="text-align:center; padding:15px; color:#94a3b8;">Cargando cuentas...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    """

html = html[:pos_sec1_div] + new_sec1_html + html[pos_sec2_comment:]
print("Sección 1 (Correo) actualizada con simetría y sin pasos.")

# 3. Reemplazar Sección 2 (Presupuesto) sin detalle de quién utiliza el presupuesto
pos_sec2_start = html.find('id="seccion-cfg-presupuesto"')
pos_sec2_div = html.rfind('<div', 0, pos_sec2_start)
pos_sec3_start = html.find('id="seccion-cfg-limite"')
pos_sec3_comment = html.rfind('<!--', 0, pos_sec3_start)

new_sec2_html = """<div id="seccion-cfg-presupuesto" style="display: none; background: linear-gradient(145deg, #0b1c30, #081422); border: 1px solid #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px; margin-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 14px;">
                            <div>
                                <h3 style="margin: 0; color: #10b981; font-size: 1.25rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    <span>💰</span> Control Presupuestal y Seguimiento de Cotizaciones
                                </h3>
                                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                                    Cálculo estricto en tiempo real del dinero comprometido en cotizaciones confirmadas y saldo disponible.
                                </p>
                            </div>
                        </div>

                        <!-- Aclaración: NO ES PAGO -->
                        <div style="background: rgba(14, 165, 233, 0.1); border-left: 4px solid #0284c7; padding: 12px 18px; border-radius: 6px; margin-bottom: 22px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 1.3rem;">ℹ️</span>
                                <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.45;">
                                    <strong style="color: #38bdf8;">Cálculo Administrativo de Presupuesto:</strong>
                                    Este módulo <strong>NO realiza pagos bancarios ni cargos automáticos</strong>. Su propósito exclusivo es llevar el cálculo de cuánto dinero va comprometido en cotizaciones confirmadas y cuánto saldo queda disponible.
                                </div>
                            </div>
                        </div>

                        <!-- Tarjetas Métricas de Presupuesto (Simétricas) -->
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 24px;">
                            <!-- Presupuesto Asignado -->
                            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                                <div style="color: #94a3b8; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Presupuesto Asignado</div>
                                <div id="cfg-presupuesto-total-txt" style="color: #ffffff; font-size: 1.7rem; font-weight: 800; line-height: 1.2;">$ 0.00 MXN</div>
                            </div>
                            <!-- Dinero en Cotizaciones Confirmadas -->
                            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                                <div style="color: #f59e0b; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Dinero en Cotizaciones Confirmadas</div>
                                <div id="cfg-comprometido-txt" style="color: #f59e0b; font-size: 1.7rem; font-weight: 800; line-height: 1.2;">$ 0.00 MXN</div>
                            </div>
                            <!-- Saldo Disponible -->
                            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                                <div style="color: #10b981; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">Presupuesto Disponible</div>
                                <div id="cfg-restante-txt" style="color: #10b981; font-size: 1.7rem; font-weight: 800; line-height: 1.2;">$ 0.00 MXN</div>
                            </div>
                        </div>

                        <!-- Barra de Progreso Presupuestal -->
                        <div style="margin-bottom: 24px; background: #0f172a; padding: 18px; border-radius: 10px; border: 1px solid #1e293b;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span style="color: #cbd5e1; font-size: 0.9rem; font-weight: 600;">Consumo Presupuestal Acumulado:</span>
                                <span id="cfg-progreso-presupuesto-txt" style="color: #38bdf8; font-size: 0.9rem; font-weight: 700;">0.00% Utilizado</span>
                            </div>
                            <div style="width: 100%; height: 14px; background: #1e293b; border-radius: 8px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);">
                                <div id="cfg-progreso-presupuesto" style="height: 100%; width: 0%; background: linear-gradient(90deg, #10b981, #059669); transition: width 0.6s ease, background 0.6s ease; border-radius: 8px;"></div>
                            </div>
                        </div>

                        <!-- Formulario para Modificar Presupuesto Total -->
                        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px;">
                            <h4 style="margin: 0 0 12px 0; color: #ffffff; font-size: 1rem; font-weight: 700;">Modificar Presupuesto Asignado:</h4>
                            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                                <div style="position: relative; max-width: 320px; width: 100%;">
                                    <span style="position: absolute; left: 14px; top: 11px; color: #94a3b8; font-weight: bold;">$</span>
                                    <input type="number" id="cfg-input-presupuesto" min="0" step="1000" placeholder="500000" style="width: 100%; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 10px 14px 10px 28px; border-radius: 8px; font-size: 1rem; font-weight: 700;">
                                </div>
                                <button type="button" class="btn-success" onclick="guardarPresupuestoTotal()" style="background: #10b981; color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);">
                                    <span>💾</span> <span>Actualizar Presupuesto</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    """

html = html[:pos_sec2_div] + new_sec2_html + html[pos_sec3_comment:]
print("Sección 2 (Presupuesto) actualizada sin detalle de quién utiliza el presupuesto.")

# 4. Reemplazar Sección 3 (Cotizaciones Caras) con explicación de las 3 reglas y sin pie de paso
pos_sec3_start = html.find('id="seccion-cfg-limite"')
pos_sec3_div = html.rfind('<div', 0, pos_sec3_start)
pos_modal_start = html.find('id="modal-agregar-cuenta-correo"')
pos_modal_comment = html.rfind('<!--', 0, pos_modal_start)
# Encontrar los divs de cierre antes del modal
pos_div_admin_close = html.rfind('</div>', 0, pos_modal_comment) # vista-configuraciones
pos_div_admin_close = html.rfind('</div>', 0, pos_div_admin_close) # admin-container
pos_div_sec3_close = html.rfind('</div>', 0, pos_div_admin_close) # seccion-cfg-limite

new_sec3_html = """<div id="seccion-cfg-limite" style="display: none; background: linear-gradient(145deg, #0b1c30, #081422); border: 1px solid #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px; margin-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 14px;">
                            <div>
                                <h3 style="margin: 0; color: #f59e0b; font-size: 1.25rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                    <span>🏷️</span> Límite para Cotizaciones Caras (+10000 / Extraordinarias)
                                </h3>
                                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                                    Ajuste del umbral que determina si una cotización requiere aprobación obligatoria de Corporativos.
                                </p>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="color: #94a3b8; font-size: 0.85rem;">Límite Actual:</span>
                                <span id="cfg-badge-limite-actual" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid #f59e0b; padding: 4px 14px; border-radius: 20px; font-weight: 800; font-size: 1rem;">
                                    $ 10,000.00 MXN
                                </span>
                            </div>
                        </div>

                        <!-- Reglas de Funcionamiento de Cotizaciones Caras -->
                        <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #f59e0b; padding: 14px 18px; border-radius: 6px; margin-bottom: 22px;">
                            <h4 style="margin: 0 0 6px 0; color: #fbbf24; font-size: 0.95rem; font-weight: 700;">Reglas del Flujo de Cotizaciones:</h4>
                            <ul style="margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">
                                <li><strong>Unidades en taller o trabajadas:</strong> Si un ticket ya fue aprobado por el supervisor para que empiece a trabajar el taller, ya no le afecta si la cotización era cara o no.</li>
                                <li><strong>Reevaluación automática:</strong> Si se modifica este límite o el costo de una cotización en proceso de aprobación, el cambio se aplica de inmediato enviando a Corporativos o no según corresponda.</li>
                                <li><strong>Paso directo a taller:</strong> Si una cotización cara estaba aprobada por el supervisor y pendiente de administrador, y el precio pasa a ser menor al límite global, se despacha directo al taller sin requerir Corporativos.</li>
                            </ul>
                        </div>

                        <!-- Formulario para Ajustar Límite -->
                        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 20px;">
                            <label style="display: block; color: #ffffff; font-size: 0.95rem; font-weight: 700; margin-bottom: 8px;">
                                Ingresa el Nuevo Monto Límite ($ MXN):
                            </label>

                            <!-- Acciones rápidas de montos predefinidos -->
                            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px;">
                                <span style="color: #94a3b8; font-size: 0.8rem; align-self: center; margin-right: 5px;">Valores rápidos:</span>
                                <button type="button" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.82rem; font-weight: 600;" onclick="seleccionarLimiteRapido(5000)">$ 5,000</button>
                                <button type="button" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.82rem; font-weight: 600;" onclick="seleccionarLimiteRapido(8000)">$ 8,000</button>
                                <button type="button" style="background: #1e293b; color: #38bdf8; border: 1px solid #0284c7; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.82rem; font-weight: 700;" onclick="seleccionarLimiteRapido(10000)">$ 10,000 (Default)</button>
                                <button type="button" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.82rem; font-weight: 600;" onclick="seleccionarLimiteRapido(12000)">$ 12,000</button>
                                <button type="button" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.82rem; font-weight: 600;" onclick="seleccionarLimiteRapido(15000)">$ 15,000</button>
                                <button type="button" style="background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.82rem; font-weight: 600;" onclick="seleccionarLimiteRapido(20000)">$ 20,000</button>
                            </div>

                            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                                <div style="position: relative; max-width: 320px; width: 100%;">
                                    <span style="position: absolute; left: 14px; top: 11px; color: #94a3b8; font-weight: bold;">$</span>
                                    <input type="number" id="cfg-input-limite" min="1000" step="500" value="10000" style="width: 100%; box-sizing: border-box; background: #1e293b; border: 1px solid #334155; color: #ffffff; padding: 10px 14px 10px 28px; border-radius: 8px; font-size: 1rem; font-weight: 700;">
                                </div>
                                <button type="button" class="btn-success" onclick="guardarLimiteCotizacionesCaras()" style="background: #f59e0b; color: #0f172a; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.25);">
                                    <span>💾</span> <span>Guardar Nuevo Límite</span>
                                </button>
                            </div>
                        </div>
                    </div>"""

html = html[:pos_sec3_div] + new_sec3_html + html[pos_div_sec3_close+6:]
print("Sección 3 (Cotizaciones Caras) actualizada con las 3 reglas.")

# 5. Cache buster
html = html.replace('configuraciones_jefatura.js?v=2', 'configuraciones_jefatura.js?v=3')

with open('templates/administracion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Plantilla templates/administracion.html actualizada con éxito!")

