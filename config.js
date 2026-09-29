/* =============================================================================
   Configuración de Cabañas Los Pinos (la usan la web y el gestor de reservas)

   · Con los dos campos VACÍOS, todo funciona en MODO DEMOSTRACIÓN:
       - el gestor (gestor.html) usa datos de ejemplo guardados en el navegador
       - los formularios de la web envían la solicitud por email / WhatsApp
   · Rellenándolos con tu proyecto de Supabase:
       - el gestor lee y guarda las reservas en la base de datos
       - las solicitudes de la web entran en el gestor como "pendientes"

   Dónde encontrarlos: Supabase → Project Settings → API
     supabaseUrl      → "Project URL" (en autoalojado: la URL pública de Kong/API)
     supabaseAnonKey  → clave "anon public". Es pública por diseño: la seguridad
                        la dan las políticas RLS de supabase/esquema.sql.
   ⚠️ NUNCA pongas aquí la clave "service_role".
   ============================================================================= */
window.LOSPINOS_CONFIG = {
  supabaseUrl: '',
  supabaseAnonKey: ''
};
