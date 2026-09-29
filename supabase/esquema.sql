-- =============================================================================
-- Gestor de reservas · Cabañas de Madera Los Pinos
-- Esquema para Supabase (PostgreSQL). Ejecutar entero en: Supabase → SQL Editor.
-- Es idempotente: se puede volver a ejecutar sin perder datos.
--
-- Contenido:
--   1. Tablas: alojamientos, temporadas, tarifas, reservas
--   2. Regla anti-solape: dos reservas CONFIRMADAS del mismo alojamiento no
--      pueden coincidir en fechas
--   3. Funciones para el gestor y el agente de WhatsApp:
--        precio_estancia(alojamiento, entrada, salida)
--        disponibilidad(entrada, salida, personas)
--        crear_solicitud(...)            ← para la web y el agente IA
--   4. Seguridad (RLS):
--        · usuarios autenticados (el propietario) → acceso completo
--        · público (web) → solo puede crear solicitudes vía crear_solicitud()
--          y consultar disponibilidad; nunca leer datos de huéspedes
--   5. Datos iniciales: los 8 alojamientos y dos temporadas de ejemplo
-- =============================================================================

create extension if not exists btree_gist;

-- -----------------------------------------------------------------------------
-- 1. TABLAS
-- -----------------------------------------------------------------------------
create table if not exists public.alojamientos (
  id           text primary key,                 -- slug, igual que la web: 'montemalo'…
  nombre       text not null,                    -- 'Cabaña Montemalo'
  tipo         text not null,                    -- 'Cabaña de madera', 'Casa', …
  capacidad    int  not null check (capacidad > 0),
  precio_base  numeric(8,2) not null check (precio_base >= 0),  -- €/noche fuera de temporada
  orden        int  not null default 0,
  activo       boolean not null default true
);

create table if not exists public.temporadas (
  id      bigint generated always as identity primary key,
  nombre  text not null,                         -- 'Temporada alta', 'Puente de diciembre'…
  desde   date not null,
  hasta   date not null,                         -- incluido
  color   text not null default '#b07a45',
  check (hasta >= desde)
);

create table if not exists public.tarifas (
  alojamiento_id  text   not null references public.alojamientos(id) on delete cascade,
  temporada_id    bigint not null references public.temporadas(id)  on delete cascade,
  precio_noche    numeric(8,2) not null check (precio_noche >= 0),
  primary key (alojamiento_id, temporada_id)
);

do $$ begin
  create type public.estado_reserva as enum ('pendiente', 'confirmada', 'cancelada');
exception when duplicate_object then null; end $$;

do $$ begin
  create type public.origen_reserva as enum ('web', 'whatsapp', 'agente', 'telefono', 'email', 'manual');
exception when duplicate_object then null; end $$;

create table if not exists public.reservas (
  id              uuid primary key default gen_random_uuid(),
  alojamiento_id  text not null references public.alojamientos(id),
  entrada         date not null,
  salida          date not null,
  personas        int  not null check (personas > 0),
  nombre          text not null,
  telefono        text,
  email           text,
  origen          public.origen_reserva not null default 'manual',
  estado          public.estado_reserva not null default 'pendiente',
  precio_total    numeric(8,2),
  pagado          numeric(8,2) not null default 0,
  notas           text,
  creado_en       timestamptz not null default now(),
  actualizado_en  timestamptz not null default now(),
  check (salida > entrada)
);

-- Documento de identidad del huésped (registro de viajeros en España). Se valida en el gestor.
alter table public.reservas add column if not exists tipo_documento text check (tipo_documento in ('DNI', 'NIE', 'Pasaporte'));
alter table public.reservas add column if not exists documento text;

-- Registro de viajeros SES.Hospedajes (RD 933/2021). Los datos de cada viajero van en
-- 'viajeros' (jsonb: nombre, apellido1, apellido2, sexo, nacimiento, nacionalidad,
-- tipo_documento, documento, soporte, expedicion, direccion, cp, localidad, pais,
-- telefono, email, parentesco). El gestor valida que estén completos.
alter table public.reservas add column if not exists viajeros jsonb not null default '[]'::jsonb;
alter table public.reservas add column if not exists referencia text;
alter table public.reservas add column if not exists fecha_contrato date;
alter table public.reservas add column if not exists habitaciones int check (habitaciones > 0);
alter table public.reservas add column if not exists internet boolean;
alter table public.reservas add column if not exists pago_tipo text check (pago_tipo in ('EFECT', 'TARJT', 'TRANS', 'MOVIL', 'PLATF', 'TREG', 'DESTI', 'OTRO'));
alter table public.reservas add column if not exists pago_titular text;
alter table public.reservas add column if not exists pago_medio text;      -- solo últimos dígitos, nunca la tarjeta completa
alter table public.reservas add column if not exists pago_caducidad text;  -- MM/AA
alter table public.reservas add column if not exists pago_fecha date;
alter table public.reservas add column if not exists parte_comunicado_en date;
create unique index if not exists reservas_referencia_idx on public.reservas (referencia) where referencia is not null;

create index if not exists reservas_fechas_idx on public.reservas (entrada, salida);
create index if not exists reservas_estado_idx on public.reservas (estado);

-- Gastos (módulo Finanzas): limpieza, lavandería, leña, mantenimiento, suministros, otros.
-- Opcionalmente vinculados a un alojamiento y a la reserva cuya salida originó la limpieza.
create table if not exists public.gastos (
  id              uuid primary key default gen_random_uuid(),
  fecha           date not null,
  categoria       text not null check (categoria in ('limpieza', 'lavanderia', 'lena', 'mantenimiento', 'suministros', 'otros')),
  concepto        text not null,
  importe         numeric(8,2) not null check (importe > 0),
  alojamiento_id  text references public.alojamientos(id) on delete set null,
  reserva_id      uuid references public.reservas(id) on delete set null,
  creado_en       timestamptz not null default now()
);
create index if not exists gastos_fecha_idx on public.gastos (fecha);

-- -----------------------------------------------------------------------------
-- 2. REGLA ANTI-SOLAPE (solo entre reservas confirmadas)
--    daterange '[)' → el día de salida queda libre para la siguiente entrada.
-- -----------------------------------------------------------------------------
do $$ begin
  alter table public.reservas
    add constraint reservas_sin_solape
    exclude using gist (alojamiento_id with =, daterange(entrada, salida, '[)') with &&)
    where (estado = 'confirmada');
exception when duplicate_object or duplicate_table then null; end $$;

create or replace function public.tocar_actualizado() returns trigger
language plpgsql as $$
begin
  new.actualizado_en := now();
  return new;
end $$;

drop trigger if exists reservas_actualizado on public.reservas;
create trigger reservas_actualizado before update on public.reservas
  for each row execute function public.tocar_actualizado();

-- -----------------------------------------------------------------------------
-- 3. FUNCIONES
-- -----------------------------------------------------------------------------

-- Precio total de una estancia: suma noche a noche la tarifa de la temporada que
-- contiene esa noche (si hay varias, la más cara); si no hay temporada, precio_base.
create or replace function public.precio_estancia(p_alojamiento text, p_entrada date, p_salida date)
returns numeric
language sql stable security definer set search_path = public as $$
  select coalesce(sum(
           coalesce(
             (select max(t.precio_noche)
                from tarifas t join temporadas s on s.id = t.temporada_id
               where t.alojamiento_id = p_alojamiento
                 and noche between s.desde and s.hasta),
             a.precio_base)
         ), 0)
    from alojamientos a,
         generate_series(p_entrada, p_salida - 1, interval '1 day') as g(noche_ts),
         lateral (select noche_ts::date as noche) n
   where a.id = p_alojamiento;
$$;

-- Alojamientos libres para unas fechas y nº de personas, con su precio total.
-- Pensada para el agente de WhatsApp y para una futura búsqueda en la web.
-- No expone datos de huéspedes.
create or replace function public.disponibilidad(p_entrada date, p_salida date, p_personas int default 1)
returns table (alojamiento_id text, nombre text, capacidad int, noches int, precio_total numeric)
language sql stable security definer set search_path = public as $$
  select a.id, a.nombre, a.capacidad,
         (p_salida - p_entrada) as noches,
         public.precio_estancia(a.id, p_entrada, p_salida)
    from alojamientos a
   where a.activo
     and a.capacidad >= p_personas
     and p_salida > p_entrada
     and not exists (
       select 1 from reservas r
        where r.alojamiento_id = a.id
          and r.estado = 'confirmada'
          and daterange(r.entrada, r.salida, '[)') && daterange(p_entrada, p_salida, '[)'))
   order by a.orden;
$$;

-- Crea una SOLICITUD (estado 'pendiente') desde la web o el agente IA.
-- Valida capacidad y fechas; calcula el precio orientativo. El propietario la
-- confirma después desde el gestor.
create or replace function public.crear_solicitud(
  p_alojamiento text, p_entrada date, p_salida date, p_personas int,
  p_nombre text, p_telefono text default null, p_email text default null,
  p_notas text default null, p_origen text default 'web')
returns uuid
language plpgsql security definer set search_path = public as $$
declare
  v_id uuid;
  v_cap int;
begin
  select capacidad into v_cap from alojamientos where id = p_alojamiento and activo;
  if v_cap is null then raise exception 'Alojamiento no válido: %', p_alojamiento; end if;
  if p_salida <= p_entrada then raise exception 'La salida debe ser posterior a la entrada'; end if;
  if p_entrada < current_date then raise exception 'La fecha de entrada ya ha pasado'; end if;
  if p_personas < 1 or p_personas > v_cap then raise exception 'Este alojamiento admite hasta % personas', v_cap; end if;
  if coalesce(trim(p_nombre), '') = '' then raise exception 'Falta el nombre'; end if;
  if p_origen not in ('web', 'whatsapp', 'agente') then p_origen := 'web'; end if;

  insert into reservas (alojamiento_id, entrada, salida, personas, nombre, telefono, email, notas,
                        origen, estado, precio_total)
  values (p_alojamiento, p_entrada, p_salida, p_personas, trim(p_nombre), p_telefono, p_email, p_notas,
          p_origen::origen_reserva, 'pendiente', precio_estancia(p_alojamiento, p_entrada, p_salida))
  returning id into v_id;
  return v_id;
end $$;

-- -----------------------------------------------------------------------------
-- 4. SEGURIDAD (Row Level Security)
-- -----------------------------------------------------------------------------
alter table public.alojamientos enable row level security;
alter table public.temporadas   enable row level security;
alter table public.tarifas      enable row level security;
alter table public.reservas     enable row level security;
alter table public.gastos       enable row level security;

-- El propietario (cualquier usuario autenticado de este proyecto) gestiona todo.
-- Crear los usuarios SOLO desde Supabase → Authentication (desactivar el registro público).
do $$
declare t text;
begin
  foreach t in array array['alojamientos', 'temporadas', 'tarifas', 'reservas', 'gastos'] loop
    execute format('drop policy if exists "propietario_todo" on public.%I', t);
    execute format('create policy "propietario_todo" on public.%I for all to authenticated using (true) with check (true)', t);
  end loop;
end $$;

-- El público puede ver alojamientos, temporadas y tarifas (no son datos personales).
drop policy if exists "publico_lee_alojamientos" on public.alojamientos;
create policy "publico_lee_alojamientos" on public.alojamientos for select to anon using (activo);
drop policy if exists "publico_lee_temporadas" on public.temporadas;
create policy "publico_lee_temporadas" on public.temporadas for select to anon using (true);
drop policy if exists "publico_lee_tarifas" on public.tarifas;
create policy "publico_lee_tarifas" on public.tarifas for select to anon using (true);
-- Reservas y gastos: el público NO tiene ninguna política → no puede leer ni escribir directamente.
-- Solo puede crear solicitudes a través de crear_solicitud().

revoke all on function public.crear_solicitud(text, date, date, int, text, text, text, text, text) from public;
grant execute on function public.crear_solicitud(text, date, date, int, text, text, text, text, text) to anon, authenticated;
grant execute on function public.disponibilidad(date, date, int) to anon, authenticated;
grant execute on function public.precio_estancia(text, date, date) to anon, authenticated;

-- -----------------------------------------------------------------------------
-- 5. DATOS INICIALES (catálogo oficial). Precio base = mínimo del rango;
--    la temporada alta de ejemplo usa el máximo. Ajustar desde el gestor.
-- -----------------------------------------------------------------------------
insert into public.alojamientos (id, nombre, tipo, capacidad, precio_base, orden) values
  ('montemalo',                'Cabaña Montemalo',                   'Cabaña de madera', 4,  90, 1),
  ('las-albercas',             'Cabaña Las Albercas',                'Cabaña de madera', 4,  90, 2),
  ('puntal-del-enebrillo',     'Cabaña Puntal del Enebrillo',        'Cabaña de madera', 4,  90, 3),
  ('barranco-de-las-iglesias', 'Cabaña Barranco de las Iglesias',    'Cabaña de madera', 8, 130, 4),
  ('cabeza-rubia',             'Cabaña Cabeza Rubia',                'Cabaña de madera', 2,  50, 5),
  ('casa-los-pineros',         'Casa Los Pineros',                   'Casa',             3,  65, 6),
  ('mirador-de-las-palomas',   'Apartamento Mirador de las Palomas', 'Apartamento',      4,  90, 7),
  ('el-senderista',            'Dúplex El Senderista',               'Dúplex',           8,  70, 8)
on conflict (id) do nothing;

do $$
declare v_alta bigint;
begin
  if not exists (select 1 from public.temporadas) then
    insert into public.temporadas (nombre, desde, hasta, color)
      values ('Temporada alta (verano)', make_date(extract(year from current_date)::int, 7, 1),
              make_date(extract(year from current_date)::int, 8, 31), '#b07a45')
      returning id into v_alta;
    insert into public.tarifas (alojamiento_id, temporada_id, precio_noche) values
      ('montemalo', v_alta, 150), ('las-albercas', v_alta, 150), ('puntal-del-enebrillo', v_alta, 150),
      ('barranco-de-las-iglesias', v_alta, 180), ('cabeza-rubia', v_alta, 80), ('casa-los-pineros', v_alta, 80),
      ('mirador-de-las-palomas', v_alta, 120), ('el-senderista', v_alta, 180);
  end if;
end $$;
