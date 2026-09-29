# Gestor de reservas · Cabañas Los Pinos

App para el propietario (`gestor.html`), pensada para el móvil. Se entra desde el botón **🔒 Propietarios** de la cabecera de la web (en el móvil, el candado junto al menú), desde el menú móvil o desde el pie de cualquier página.

| Pantalla | Para qué sirve |
|---|---|
| **📅 Calendario** | Ocupación del mes de los 8 alojamientos. Resumen de entradas, salidas y pendientes de hoy. Tocar un día libre crea una reserva; tocar una barra la abre. |
| **📋 Reservas** | Listas: Pendientes · Hoy · Próximas · Pasadas · Canceladas · Todas. Buscador por nombre o teléfono. Las solicitudes pendientes se confirman o rechazan con un toque y se puede escribir al huésped por WhatsApp. |
| **＋ Nueva** | Ficha de reserva: alojamiento, fechas, personas (con el máximo de cada alojamiento), huésped, origen, estado, precio (calculado solo con las tarifas), pagado, datos del pago, **registro de viajeros** y notas. Avisa si se solapa con otra reserva. |
| **💶 Precios** | Precio base por noche, temporadas con su precio por alojamiento y una calculadora de presupuestos. Todo se guarda al momento. |
| **📊 Finanzas** | Beneficio neto real del mes (ingresos de reservas confirmadas − gastos), margen y ocupación; gráfica de ingresos vs gastos de 6 meses (tocar un mes lo abre); gastos por categoría (limpieza, lavandería, leña, mantenimiento de piscina/jardín, suministros, otros); control de **limpiezas tras cada salida** con «+ Apuntar» en un toque; resultado por alojamiento. Cada gasto lleva fecha, concepto, categoría, importe y, opcionalmente, alojamiento. |

**Navegación:** barra inferior con las 5 pestañas, deslizar el dedo a izquierda/derecha para cambiar de pestaña, flecha ← en la cabecera y botón «atrás» del móvil (primero cierra la ficha abierta, luego vuelve a la pestaña anterior; desde Calendario, la flecha lleva a la web). La casita de la cabecera abre la web.

## Registro de viajeros (SES.Hospedajes · RD 933/2021)

En la ficha de cada reserva hay una tarjeta por viajero (la 1.ª es el titular) con todos los datos que exige el parte: nombre y apellidos (el 2.º obligatorio con DNI), sexo, fecha de nacimiento, nacionalidad, tipo y número de documento (se comprueba la letra de DNI/NIE), **nº de soporte** (DNI/NIE), fecha de expedición, dirección de residencia habitual con código postal, localidad y país, teléfono o email y, para menores, parentesco con el titular. Los menores de 14 años no necesitan documento.

También se guardan los datos del contrato (referencia automática `LP-AAAA-0001`, fecha de contrato, nº de habitaciones, acceso a internet) y del pago (forma de pago, titular, identificación del medio —solo los 4 últimos dígitos de la tarjeta—, caducidad y fecha).

- El DNI del titular es obligatorio para confirmar. El parte completo, para marcarlo como **comunicado a SES.Hospedajes**.
- Las reservas confirmadas con huéspedes ya llegados y parte sin comunicar aparecen en rojo, en el aviso del calendario y en el filtro **Partes SES** (plazo: 24 h desde la entrada; conservar 3 años).
- **📄 Parte de viajeros** abre el parte listo para imprimir o guardar en PDF (con línea de firma por viajero) y **⬇️ CSV** descarga los datos en una hoja de cálculo para pasarlos a SES.Hospedajes. La comunicación al Ministerio sigue haciéndose en la sede de SES.Hospedajes: el gestor no la envía.

Sin configurar, funciona en **modo demostración** (datos de ejemplo guardados solo en el navegador), útil para enseñárselo al cliente.

---

## Puesta en marcha con Supabase (autoalojado en el VPS o supabase.com)

1. **Crear la base de datos.** Supabase Studio → *SQL Editor* → pegar el contenido de [`supabase/esquema.sql`](../supabase/esquema.sql) → *Run*.
   Se puede volver a ejecutar sin perder datos. Crea las tablas, la seguridad y los 8 alojamientos con una temporada alta de ejemplo (julio–agosto).
2. **Crear el usuario del propietario.** Studio → *Authentication → Users → Add user* (correo y contraseña, marcando *Auto confirm*).
3. **Cerrar el registro público.** *Authentication → Providers → Email*: desactivar *Allow new users to sign up*. En autoalojado equivale a `DISABLE_SIGNUP=true` / `GOTRUE_DISABLE_SIGNUP=true` en el `.env`.
   ⚠️ Es importante: cualquier usuario autenticado tiene acceso completo a las reservas.
4. **Conectar la web.** Editar [`config.js`](../config.js):
   ```js
   window.LOSPINOS_CONFIG = {
     supabaseUrl: 'https://api.tudominio.com',   // Project URL (en autoalojado: la URL pública de Kong)
     supabaseAnonKey: 'eyJ…'                     // clave "anon public"
   };
   ```
   La clave *anon* es pública por diseño; lo que protege los datos son las políticas RLS. **Nunca** poner aquí la clave *service_role*.
5. **CORS** (solo autoalojado): el dominio donde se publica la web debe estar permitido en la API (Kong) para que el navegador pueda llamar a Supabase.

A partir de ese momento:
- el gestor pide correo y contraseña y trabaja con la base de datos real;
- los formularios de la web registran la solicitud como **pendiente** (origen *web* o *whatsapp*) y muestran «Solicitud recibida»; si el visitante elige WhatsApp, además se abre el chat.

---

## Modelo de datos

| Tabla | Contenido |
|---|---|
| `alojamientos` | `id` (slug, igual que las páginas de la web: `montemalo`, `las-albercas`…), nombre, tipo, capacidad, precio base, orden, activo |
| `temporadas` | nombre, desde, hasta (incluidos), color |
| `tarifas` | precio por noche de cada alojamiento en cada temporada |
| `gastos` | fecha, categoría (limpieza · lavanderia · lena · mantenimiento · suministros · otros), concepto, importe, alojamiento y reserva (opcionales) |
| `reservas` | alojamiento, entrada, salida, personas, huésped (nombre, teléfono, email, `tipo_documento` DNI · NIE · Pasaporte y `documento`, obligatorio para confirmar), `viajeros` (jsonb con el parte de cada viajero), referencia, fecha de contrato, habitaciones, internet, datos del pago (`pago_*`), `parte_comunicado_en`, `origen` (web · whatsapp · agente · telefono · email · manual), `estado` (pendiente · confirmada · cancelada), precio total, pagado, notas |

**Reglas que garantiza la base de datos** (aunque falle la app):
- Dos reservas **confirmadas** del mismo alojamiento no pueden solaparse (el día de salida queda libre para la siguiente entrada).
- La salida debe ser posterior a la entrada y las personas, mayor que 0.
- El público (web) no puede leer ni modificar reservas: solo crear solicitudes con `crear_solicitud()`.

**Precio de una estancia:** noche a noche, la tarifa de la temporada que contiene esa noche (si coinciden varias, la más alta); fuera de temporada, el precio base. Es la misma regla en SQL (`precio_estancia`) y en el gestor.

---

## Conexión con el agente de WhatsApp (n8n)

El agente usa la API REST de Supabase. Hay dos niveles:

### 1. Operaciones públicas (clave *anon*, sin datos de huéspedes)

| Acción | Llamada | Cuerpo JSON |
|---|---|---|
| **¿Qué hay libre?** | `POST {URL}/rest/v1/rpc/disponibilidad` | `{"p_entrada":"2026-10-10","p_salida":"2026-10-12","p_personas":4}` |
| **¿Cuánto cuesta?** | `POST {URL}/rest/v1/rpc/precio_estancia` | `{"p_alojamiento":"montemalo","p_entrada":"2026-10-10","p_salida":"2026-10-12"}` |
| **Registrar solicitud** | `POST {URL}/rest/v1/rpc/crear_solicitud` | `{"p_alojamiento":"montemalo","p_entrada":"2026-10-10","p_salida":"2026-10-12","p_personas":4,"p_nombre":"Ana","p_telefono":"600123123","p_notas":"Llegan tarde","p_origen":"agente"}` |

Cabeceras: `apikey: <anon>` y `Authorization: Bearer <anon>`.
`disponibilidad` devuelve `[{alojamiento_id, nombre, capacidad, noches, precio_total}]` y ya descarta los alojamientos ocupados o sin capacidad. `crear_solicitud` devuelve el `id` de la reserva, o un error con mensaje en español («Este alojamiento admite hasta 2 personas», «La fecha de entrada ya ha pasado»…) que el agente puede repetir al cliente.

Con estas tres funciones el agente puede: consultar disponibilidad → dar el precio → dejar la solicitud **pendiente**. El propietario la ve en el gestor (pestaña *Pendientes*, con la etiqueta 🤖 Agente IA) y la confirma con un toque.

### 2. Operaciones internas (clave *service_role*, SOLO en credenciales de n8n)

Si más adelante el agente debe consultar o gestionar reservas existentes (por ejemplo «¿a qué hora es mi entrada?»), usar la clave *service_role* guardada como credencial de n8n, nunca en la web:
- Reservas de un huésped: `GET {URL}/rest/v1/reservas?telefono=eq.600123123&estado=neq.cancelada&order=entrada`
- Confirmar automáticamente (si el propietario lo decide): `PATCH {URL}/rest/v1/reservas?id=eq.<id>` con `{"estado":"confirmada"}` — la regla anti-solape de la base de datos sigue impidiendo dobles reservas.

### Herramientas sugeridas para el agente

| Herramienta | Llama a | Cuándo |
|---|---|---|
| `consultar_disponibilidad(entrada, salida, personas)` | `rpc/disponibilidad` | El cliente pregunta por fechas |
| `calcular_precio(alojamiento, entrada, salida)` | `rpc/precio_estancia` | El cliente pregunta cuánto cuesta un alojamiento concreto |
| `crear_solicitud(alojamiento, entrada, salida, personas, nombre, telefono, notas)` | `rpc/crear_solicitud` con `p_origen: "agente"` | El cliente quiere reservar (siempre queda pendiente de confirmar por el propietario) |

Ids de alojamiento: `montemalo`, `las-albercas`, `puntal-del-enebrillo`, `barranco-de-las-iglesias`, `cabeza-rubia`, `casa-los-pineros`, `mirador-de-las-palomas`, `el-senderista`.
