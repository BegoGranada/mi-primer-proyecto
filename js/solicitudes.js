/* =============================================================================
   Envío de solicitudes de reserva de la web al gestor (Supabase)

   Si config.js tiene los datos de Supabase, los formularios de la web llaman a
   la función crear_solicitud() de la base de datos: la solicitud aparece en el
   gestor como "pendiente". Si no, los formularios siguen enviando por email o
   WhatsApp como siempre.

   La web solo puede CREAR solicitudes (nunca leer reservas): lo garantizan las
   políticas RLS de supabase/esquema.sql.
   ============================================================================= */
(function () {
  const C = window.LOSPINOS_CONFIG || {};
  const activo = !!(C.supabaseUrl && C.supabaseAnonKey);

  async function enviar(d) {
    const url = C.supabaseUrl.replace(/\/+$/, '') + '/rest/v1/rpc/crear_solicitud';
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: C.supabaseAnonKey, Authorization: 'Bearer ' + C.supabaseAnonKey },
      body: JSON.stringify({
        p_alojamiento: d.alojamiento, p_entrada: d.entrada, p_salida: d.salida, p_personas: +d.personas,
        p_nombre: d.nombre, p_telefono: d.telefono || null, p_email: d.email || null,
        p_notas: d.comentarios || null, p_origen: d.origen || 'web'
      })
    });
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      throw new Error(j.message || 'No se ha podido enviar la solicitud. Inténtalo por WhatsApp o teléfono.');
    }
    return true;
  }

  window.LosPinosSolicitudes = { activo, enviar };
})();
