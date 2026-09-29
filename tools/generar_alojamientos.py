#!/usr/bin/env python3
"""
Generador de las páginas individuales de alojamiento de Cabañas Los Pinos.

Uso (desde la raíz del repositorio):
    python3 tools/generar_alojamientos.py

- Los datos de cada alojamiento están en la lista ALOJAMIENTOS (abajo).
- La configuración de Tailwind y los estilos se copian de index.html,
  así las páginas mantienen siempre el mismo tema que la portada.
- Vuelve a ejecutarlo tras editar cualquier dato: sobrescribe los 8 .html.
"""
import html
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WP = 'https://cabanaslospinos.com/wp-content/uploads/2026/06/'
UPLOADS = 'https://cabanaslospinos.com/wp-content/uploads/'
# Carpetas donde se buscan las fotos cuyo nombre no lleva ruta (se prueban
# en este orden en el navegador y se usa la primera que responda).
CARPETAS = ['2026/07', '2026/06', '2026/05', '2026/04', '2026/03']


def rutas(nombre):
    """URL completa -> [URL]; 'AAAA/MM/archivo' -> [uploads/AAAA/MM/archivo];
    'archivo' -> una URL candidata por cada carpeta de CARPETAS."""
    if nombre.startswith('http'):
        return [nombre]
    if '/' in nombre:
        return [UPLOADS + nombre]
    return [f'{UPLOADS}{c}/{nombre}' for c in CARPETAS]


def rutas_foto(foto):
    """'foto' puede ser un nombre o una lista de nombres (se prueban en orden).
    Las portadaN.webp están confirmadas en 2026/06; el resto usa rutas()."""
    lista = foto if isinstance(foto, list) else ([foto] if foto else [])
    out = []
    for f in lista:
        if f.startswith('portada') and '/' not in f:
            # Casi todas las portadas están en 2026/06; si no, se prueban las demás carpetas
            out += [WP + f] + [u for u in rutas(f) if u != WP + f]
        else:
            out += rutas(f)
    return out
LOGO_H = WP + 'logo_clp_trans_horizontal.webp'
LOGO_V = WP + 'logo_clp_vertical.webp'

# ---------------------------------------------------------------------------
# DATOS DE LOS ALOJAMIENTOS (catálogo oficial facilitado por el cliente)
# foto: nombre del archivo en wp-content/uploads/2026/06/ o None si no hay
# registro: nº de registro oficial de turismo (opcional; se muestra si existe)
# lema: título de la sección de texto, como en la web original (opcional)
# cabecera: foto específica para el hero (opcional; si no carga se usa 'foto')
# foto: nombre o lista de nombres de la foto principal (se prueban en orden)
# galeria: lista de fotos (opcional). Si está vacía, la sección 'Galería' no
#          se genera. Admite URL completa, 'AAAA/MM/archivo' o solo 'archivo'
#          (se busca en CARPETAS). Las fotos que no carguen se retiran solas.
# EDITAR: las descripciones pueden sustituirse por los textos originales.
# ---------------------------------------------------------------------------
ALOJAMIENTOS = [
    dict(slug='montemalo', nombre='Montemalo', tipo='Cabaña de madera', foto='portada2.webp',
         max=4, precio='90 – 150 €', habs='2 habitaciones',
         camas=['Habitación 1: cama de matrimonio (135 cm)', 'Habitación 2: cama de matrimonio (135 cm)',
                'Habitaciones separadas'],
         wifi=True, extras=['Baño con bañera y ducha', 'Vistas al jardín', 'Terraza privada', 'Horno-microondas'],
         registro='A/JA/00117',
         # Fotos reales de la web original (pestaña Red de la página de Montemalo)
         cabecera='cabecera_montemalo.webp',
         galeria=['20260521_190342.webp', '20260517_113341.webp', '20260521_190842.webp',
                  '20260521_190629.webp', '20260517_113328.webp', '20260521_190411.webp',
                  '20260521_190420.webp', '20260521_190555.webp', '20260521_190619.webp',
                  '20260521_190722.webp', '20260521_190658.webp', '20260521_190757.webp',
                  '20260521_190423.webp'],
         # Texto REAL de la web original (extraído por Begoña, 29 sept 2026)
         descripcion=['Cabaña ideal para parejas (con opción de alojar a 4 personas en 2 camas de matrimonio '
                      'en 2 habitaciones separadas). Cuenta con 1 baño con bañera y ducha, vistas al jardín, TV, '
                      'nevera, lavadora y horno-microondas, terraza privada y acceso a piscina y barbacoa '
                      'compartidas (en temporada). Dispone de calefacción y aire acondicionado.']),
    dict(slug='las-albercas', nombre='Las Albercas', tipo='Cabaña de madera', foto='portada5.webp',
         max=4, precio='90 – 150 €', habs='2 habitaciones',
         camas=['Habitación 1: cama de matrimonio (135 cm)', 'Habitación 2: cama de matrimonio (135 cm)',
                'Habitaciones separadas'],
         wifi=True, extras=['Baño con bañera y ducha', 'Vistas al jardín', 'Terraza privada', 'Horno-microondas'],
         registro='A/JA/00117',
         lema='Paz y relax para 4 personas',
         # Fotos reales de la web original (pestaña Red de la página de Las Albercas)
         cabecera='cabecera_lasAlbercas.webp',
         galeria=['20260517_112533.webp', '20260517_112643.webp', '20260517_112829.webp',
                  '20260517_112801.webp', '20260521_190928.webp', '20260517_113227.webp',
                  '20260517_113233.webp', '20260517_112837.webp', '20260517_113138.webp',
                  '20260517_112736.webp', '20260517_112943.webp', '20260517_113000.webp',
                  '20260517_113038.webp', '20260517_113157.webp'],
         # Texto REAL de la web original (29 sept 2026)
         descripcion=['Con 2 habitaciones puede alojar a 4 personas en 2 camas de matrimonio en 2 habitaciones '
                      'separadas. Cuenta con 1 baño con bañera y ducha, vistas al jardín, TV, nevera, lavadora y '
                      'horno-microondas, terraza privada, acceso a piscina y barbacoa compartidas (en temporada), '
                      'calefacción y aire acondicionado.']),
    dict(slug='puntal-del-enebrillo', nombre='Puntal del Enebrillo', tipo='Cabaña de madera', foto=['puntal_enebrillo1.webp', 'portada3.webp'],
         max=4, precio='90 – 150 €', habs='2 habitaciones',
         camas=['Habitación 1: cama de 135 cm', 'Habitación 2: cama de 135 cm'],
         wifi=True, extras=[],
         # Fotos reales de la web original (pestaña Red de la página de Puntal del Enebrillo).
         # Su página carga puntal_enebrillo1.webp donde Montemalo carga portada2 y
         # Las Albercas portada5; portada3 queda de respaldo.
         cabecera='cabecera_enebrillo.webp',
         galeria=['20260517_111538.webp', '20260517_111534.webp', '20260517_111517.webp',
                  '20260326_133532.webp', '20260326_133518.webp', '20260326_133158.webp',
                  '20260326_133605.webp', '20260326_133252.webp', '20260326_133422.webp',
                  '20260326_133358.webp', '20260326_133319.webp', '20260326_132954.webp',
                  '20260326_133002.webp', '20260326_133049.webp', '20260326_132951.webp',
                  '20260517_113616.webp', '20260326_132933.webp', '20260517_113623.webp'],
         descripcion=['Puntal del Enebrillo es una cabaña de madera para 4 personas que toma su nombre '
                      'de uno de los parajes de la sierra.',
                      'Dos habitaciones con cama de 135 y todo el equipamiento necesario para disfrutar '
                      'de una escapada tranquila en Arroyo Frío.']),
    dict(slug='barranco-de-las-iglesias', nombre='Barranco de las Iglesias', tipo='Cabaña de madera', foto=['barranco1.webp', 'portada6.webp'],
         max=8, precio='130 – 180 €', habs='2 pisos · 3 habitaciones + buhardilla',
         camas=['3 habitaciones repartidas en 2 pisos', 'Buhardilla con 4 camas individuales'],
         wifi=True, extras=['Dos pisos'],
         # Fotos reales de la web original (pestaña Red de la página de Barranco de las Iglesias).
         # Su página carga barranco1.webp (como Puntal carga puntal_enebrillo1); portada6 de respaldo.
         cabecera='cabecera_barranco.webp',
         galeria=['20260517_111336.webp', '20260517_111431.webp', '20260326_134041.webp',
                  '20260326_134219.webp', '20260326_134329.webp', '20260326_134146.webp',
                  '20260517_111311.webp', '20260326_134215.webp', '20260326_134244.webp',
                  '20260326_134455.webp', '20260326_134424.webp', '20260326_134102.webp',
                  '20260517_111331.webp', '20260326_134325.webp', '20260326_134449.webp',
                  '20260326_134109.webp', '20260326_134008.webp', '20260326_134013.webp'],
         descripcion=['Barranco de las Iglesias es nuestra cabaña más grande: dos pisos pensados para '
                      'grupos y familias numerosas de hasta 8 personas.',
                      'Tres habitaciones y una amplia buhardilla con 4 camas individuales, ideal para que '
                      'los más pequeños tengan su propio espacio.']),
    dict(slug='cabeza-rubia', nombre='Cabeza Rubia', tipo='Cabaña de madera', foto=['principal_cabezarubia.webp', 'portada7.webp'],
         max=2, precio='50 – 80 €', habs='1 habitación',
         camas=['Habitación: cama de 135 cm'],
         wifi=True, extras=[],
         # Fotos reales de la web original (pestaña Red de la página de Cabeza Rubia).
         # Su página carga principal_cabezarubia.webp; portada7 de respaldo.
         cabecera='cabecera_cabezarubia.webp',
         galeria=['20260517_112251.webp', '20260517_111649.webp', '20260517_112049.webp',
                  '20260517_112341.webp', '20260517_112043.webp', '20260517_112007.webp',
                  '20260517_111825.webp', '20260517_112304.webp', '20260517_112227.webp',
                  '20260517_111808.webp', '20260517_111725.webp', '20260517_111904.webp'],
         descripcion=['Cabeza Rubia es una cabaña de madera para 2 personas, perfecta para una escapada '
                      'en pareja entre pinos.',
                      'Una habitación con cama de 135, cocina, baño privado y la tranquilidad de Arroyo Frío '
                      'a las puertas del Parque Natural.']),
    dict(slug='casa-los-pineros', nombre='Los Pineros', tipo='Casa con terraza privada', lema='Casa con terraza privada',
         foto=['principal_losPineros.webp'],
         max=3, precio='65 – 80 €', habs='1 habitación',
         camas=['1 cama de matrimonio', '1 cama individual de 95 cm'],
         wifi=False,
         extras=['Baño con ducha', 'Terraza privada', 'Chimenea de leña (leña no incluida)', 'Horno-microondas'],
         # Texto y fotos REALES de la web original (captura de la pestaña Red, 29 sept 2026)
         cabecera='cabecera_losPineros.webp',
         galeria=['20260521_192323.webp', '20260521_192301.webp', '20260521_192541.webp',
                  '20260521_192331.webp', '20260521_192200.webp', '20260521_192550.webp',
                  '20260521_192540.webp', '20260521_192406.webp', '20260521_192147.webp',
                  '20260521_191955.webp', '20260521_192447.webp'],
         descripcion=['Es una casa en el centro del pueblo, con capacidad para 3 personas, 1 habitación con cama '
                      'de matrimonio y una cama individual. Cuenta con 1 baño con ducha, TV, nevera, lavadora y '
                      'horno-microondas, terraza privada, chimenea de leña (leña no incluida), calefacción y aire '
                      'acondicionado.']),
    dict(slug='mirador-de-las-palomas', nombre='Mirador de las Palomas', tipo='Apartamento con terraza superior', lema='Apartamento con terraza superior',
         foto=['principal_palomas.webp'],
         max=4, precio='90 – 120 €', habs='2 habitaciones',
         camas=['Habitación 1: cama de 135 cm', 'Habitación 2: cama de 135 cm'],
         wifi=False,
         extras=['Baño con ducha', 'Terraza privada con vistas', 'Chimenea de leña (leña no incluida)',
                 'Aire acondicionado (frío/calor) en todas las estancias', 'Horno-microondas'],
         # Texto y fotos REALES de la web original (captura de la pestaña Red, 29 sept 2026)
         cabecera='cabecera_palomas.webp',
         galeria=['20260517_115258.webp', '20260517_120357.webp', '20260517_115603.webp',
                  '20260517_115225.webp', '20260517_115232.webp', '20260517_120011.webp',
                  '20260517_120331.webp', '20260517_115712.webp', '20260517_115803.webp',
                  '20260517_115308.webp', '20260517_115323.webp', '20260517_115250.webp',
                  '20260517_115517.webp', '20260517_115505.webp', '20260517_115419.webp'],
         descripcion=['Apartamento moderno con capacidad para 4 personas en 2 habitaciones, dispone de terraza con '
                      'vistas al Mirador de las Palomas y a la aldea. Cuenta con 1 baño con ducha, TV, nevera, '
                      'lavadora y horno-microondas, terraza privada con vistas, chimenea de leña (leña no incluida) '
                      'y aire acondicionado (frío/calor) en todas las estancias.']),
    dict(slug='el-senderista', nombre='El Senderista', tipo='Dúplex de 3 plantas', lema='Dúplex de gran capacidad',
         # Fotos REALES verificadas en la pestaña Red: su página carga portada8.webp (post-714.css)
         foto=['portada8.webp'],
         max=8, precio='70 – 180 €', habs='3 plantas · 4 habitaciones · 2 baños',
         camas=['2 habitaciones con camas de matrimonio', 'Resto de habitaciones con camas individuales'],
         wifi=False,
         extras=['2 baños con ducha', 'Amplio salón', 'Chimenea de leña (leña no incluida)',
                 'Aire acondicionado (frío/calor) en todas las estancias', 'Horno-microondas'],
         cabecera='cabecera_senderista.webp',
         # Galería REAL de la web original (captura de la pestaña Red, 29 sept 2026)
         galeria=['20260604_131746.webp', '20260604_131644.webp', '20260521_194217.webp',
                  '20260521_194322.webp', '20260521_194334.webp', '20260521_194344.webp',
                  '20260521_194355.webp', '20260604_131608.webp', '20260604_131726.webp',
                  '20260521_194546.webp', '20260604_131733.webp', '20260604_131712.webp',
                  '20260521_194209.webp', '20260521_194551.webp', '20260521_194617.webp',
                  '20260521_194700.webp', '20260521_194713.webp', '20260521_194900.webp',
                  '20260604_131759.webp', '20260604_131812.webp', '20260604_131651.webp',
                  '20260604_131703.webp', '20260508_200052.webp', '20260508_200111.webp',
                  '20260508_200223.webp'],
         # Texto REAL de la web original
         descripcion=['Tiene 3 plantas con 4 habitaciones y 2 baños, con capacidad para 8 personas. Amplio salón '
                      'y ubicado en una zona residencial. Cuenta con 2 baños con ducha, TV, nevera, lavadora y '
                      'horno-microondas, 2 habitaciones con camas de matrimonio, chimenea de leña (leña no '
                      'incluida) y aire acondicionado (frío/calor) en todas las estancias.']),
]

COMUNES = [('🛁', 'Baño privado'), ('🍳', 'Cocina'), ('📺', 'TV'), ('❄️', 'Aire acondicionado'),
           ('🔥', 'Calefacción o chimenea'), ('🧊', 'Nevera'), ('🧺', 'Lavadora'), ('♨️', 'Microondas')]

e = html.escape


def titulo_completo(a):
    """Nombre tal y como aparece en menús y formularios."""
    t = a['tipo'].split()[0]  # Cabaña / Casa / Apartamento / Dúplex
    return f'{t} {a["nombre"]}'


def extraer_tema():
    """Copia de index.html la config de Tailwind y el bloque <style>."""
    idx = (RAIZ / 'index.html').read_text(encoding='utf-8')
    cfg = re.search(r'<script>\s*// Paleta propia.*?</script>', idx, re.S).group(0)
    css = re.search(r'<style>.*?</style>', idx, re.S).group(0)
    return cfg, css


def menu_alojamientos(actual, movil=False):
    items = []
    for a in ALOJAMIENTOS:
        activo = a['slug'] == actual
        cur = ' aria-current="page"' if activo else ''
        if movil:
            cls = 'block py-2' + (' font-semibold text-wood-300' if activo else '')
            items.append(f'            <li><a href="{a["slug"]}.html"{cur} class="{cls}">{e(titulo_completo(a))}</a></li>')
        else:
            cls = 'block rounded-lg px-4 py-2 hover:bg-pine-50' + (' bg-pine-50 font-semibold' if activo else '')
            items.append(f'              <a href="{a["slug"]}.html"{cur} class="{cls}">{e(titulo_completo(a))}</a>')
    return '\n'.join(items)


def cabecera(actual):
    return f'''  <!-- =================== CABECERA (igual que la portada) =================== -->
  <header id="siteHeader" class="fixed inset-x-0 top-0 z-40 transition-all duration-300">
    <nav class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8" aria-label="Principal">
      <a href="index.html" class="flex items-center gap-2 text-cream" aria-label="Cabañas de Madera Los Pinos — Inicio">
        <img data-logo src="{LOGO_H}" alt="Cabañas de Madera Los Pinos" class="hidden h-10 w-auto brightness-0 invert sm:h-12" />
        <svg data-logo-fallback class="h-8 w-8 text-wood-300" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2 6 10h3l-4 6h4l-3 4h12l-3-4h4l-4-6h3z"/><rect x="11" y="19" width="2" height="3"/></svg>
        <span data-logo-fallback class="font-serif text-xl font-semibold leading-tight tracking-wide sm:text-2xl">Cabañas Los Pinos</span>
      </a>

      <ul class="hidden items-center gap-8 text-sm font-medium text-cream/90 lg:flex">
        <li><a href="index.html" class="hover:text-wood-300">Inicio</a></li>
        <li class="group relative">
          <a href="index.html#alojamientos" class="inline-flex items-center gap-1 text-wood-300">Alojamientos
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M5.3 7.3a1 1 0 0 1 1.4 0L10 10.6l3.3-3.3a1 1 0 1 1 1.4 1.4l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 0 1 0-1.4z"/></svg>
          </a>
          <div class="invisible absolute left-1/2 top-full w-80 -translate-x-1/2 pt-3 opacity-0 transition group-hover:visible group-hover:opacity-100 group-focus-within:visible group-focus-within:opacity-100">
            <div class="rounded-xl bg-cream p-2 text-pine-900 shadow-soft">
{menu_alojamientos(actual)}
            </div>
          </div>
        </li>
        <li><a href="index.html#entorno" class="hover:text-wood-300">Entorno</a></li>
        <li><a href="index.html#noticias" class="hover:text-wood-300">Noticias</a></li>
        <li><a href="index.html#contacto" class="hover:text-wood-300">Contacto</a></li>
        <li><button data-open-booking class="rounded-full bg-wood-500 px-5 py-2.5 text-white shadow-lg shadow-wood-700/30 transition hover:bg-wood-600">Reservas</button></li>
      </ul>

      <button id="menuBtn" class="rounded-lg p-2 text-cream lg:hidden" aria-controls="mobileMenu" aria-expanded="false" aria-label="Abrir menú">
        <svg class="h-7 w-7" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
    </nav>

    <div id="mobileMenu" class="hidden max-h-[80svh] overflow-y-auto border-t border-white/10 bg-pine-900/95 backdrop-blur lg:hidden">
      <ul class="space-y-1 px-4 py-4 text-cream">
        <li><a href="index.html" class="block rounded-lg px-3 py-3 hover:bg-white/5">Inicio</a></li>
        <li>
          <a href="index.html#alojamientos" class="block rounded-lg px-3 py-3 hover:bg-white/5">Alojamientos</a>
          <ul class="ml-4 border-l border-white/10 pl-3 text-sm text-cream/80">
{menu_alojamientos(actual, movil=True)}
          </ul>
        </li>
        <li><a href="index.html#entorno" class="block rounded-lg px-3 py-3 hover:bg-white/5">Entorno</a></li>
        <li><a href="index.html#noticias" class="block rounded-lg px-3 py-3 hover:bg-white/5">Noticias</a></li>
        <li><a href="index.html#contacto" class="block rounded-lg px-3 py-3 hover:bg-white/5">Contacto</a></li>
        <li class="pt-2"><button data-open-booking class="w-full rounded-full bg-wood-500 px-5 py-3 font-semibold text-white">Reservar ahora</button></li>
      </ul>
    </div>
  </header>'''


def pagina(a, cfg, css):
    nombre_full = titulo_completo(a)
    fotos_hero = (rutas(a['cabecera']) if a.get('cabecera') else []) + rutas_foto(a['foto'])
    foto = '|'.join(fotos_hero)
    servicios = COMUNES + ([('📶', 'Wi-Fi')] if a['wifi'] else []) \
        + [('✨', x) for x in a['extras']] \
        + [('🏊', 'Piscina (según temporada)'), ('🍖', 'Barbacoa exterior (según temporada)'),
           ('🧭', 'Asesoramiento turístico')]
    li_serv = '\n'.join(
        f'          <li class="flex items-center gap-3 rounded-2xl border border-stone-150 bg-white p-4 shadow-soft">'
        f'<span class="text-2xl" aria-hidden="true">{i}</span><span class="text-sm font-medium">{e(t)}</span></li>'
        for i, t in servicios)
    li_camas = '\n'.join(
        f'            <li class="flex items-start gap-3"><span class="mt-1 text-wood-500">🛏️</span><span>{e(c)}</span></li>'
        for c in a['camas'])
    parrafos = '\n'.join(f'          <p>{e(p)}</p>' for p in a['descripcion'])
    otros = '\n'.join(
        f'''        <a href="{o["slug"]}.html" class="group flex flex-col justify-between rounded-2xl border border-stone-150 bg-white p-5 shadow-soft transition hover:-translate-y-1 hover:border-wood-300">
          <div><p class="text-xs uppercase tracking-widest text-wood-600">{e(o["tipo"])}</p>
          <p class="mt-1 font-serif text-2xl font-semibold leading-tight">{e(o["nombre"])}</p></div>
          <p class="mt-3 text-sm text-pine-700/75">👥 {o["max"]} pers. · {e(o["precio"])}/noche <span class="text-wood-600 transition group-hover:translate-x-1">→</span></p>
        </a>''' for o in ALOJAMIENTOS if o['slug'] != a['slug'])
    datos_js = json.dumps([{'nombre': titulo_completo(o), 'max': o['max'],
                            'info': f'{o["max"]} personas · {o["habs"]} · {o["precio"]}/noche'}
                           for o in ALOJAMIENTOS], ensure_ascii=False)
    registro = a.get('registro')
    fotos_gal = [rutas(u) for u in a.get('galeria', [])]
    items_gal = '\n'.join(
        f'          <a href="{e(c[0])}" target="_blank" rel="noopener" class="block overflow-hidden rounded-lg shadow-md" data-gal>'
        f'<img data-srcs="{e("|".join(c))}" alt="{e(nombre_full)} — foto {i}" loading="lazy" '
        f'class="rounded-lg shadow-md hover:scale-105 transition-transform duration-300 object-cover w-full h-64"></a>'
        for i, c in enumerate(fotos_gal, 1))
    galeria = f'''

    <!-- =================== GALERÍA (fotos reales) =================== -->
    <section id="galeria" class="bg-white py-20 sm:py-24">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-[.25em] text-wood-600">Galería</p>
        <h2 class="mt-2 font-serif text-4xl font-semibold">Fotos de {e(nombre_full)}</h2>
        <div class="mt-10 grid grid-cols-1 gap-4 md:grid-cols-3">
{items_gal}
        </div>
      </div>
    </section>''' if fotos_gal else ''
    reg_aside = (f'\n            <p class="mt-4 border-t border-white/10 pt-4 text-center text-xs uppercase tracking-widest text-cream/60">Nº de registro: {e(registro)}</p>' if registro else '')
    reg_normas = (f'\n        <p class="mt-6 text-sm text-pine-700/70">Número de registro oficial de turismo: <strong class="font-semibold text-pine-800">{e(registro)}</strong></p>' if registro else '')
    descripcion_meta = f'{nombre_full}: {a["tipo"].lower()} para {a["max"]} personas en Arroyo Frío, Sierra de Cazorla. {a["precio"]}/noche.'

    return f'''<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
  <!-- ============================================================
       {nombre_full} — Cabañas de Madera Los Pinos
       Página GENERADA por tools/generar_alojamientos.py:
       edita los datos allí y vuelve a ejecutarlo, no a mano.
       Secciones: cabecera · hero a pantalla completa · datos clave ·
       descripción + reserva · camas · servicios · normas ·
       otros alojamientos · pie · modal de reserva
       ============================================================ -->
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(nombre_full)} · Cabañas de Madera Los Pinos · Arroyo Frío</title>
  <meta name="description" content="{e(descripcion_meta)}" />
  <meta name="theme-color" content="#1a261b" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
  {cfg}
  {css}
</head>

<body class="bg-cream text-pine-900 font-sans antialiased">

{cabecera(a['slug'])}

  <main>
    <!-- =================== HERO: foto a pantalla completa + título centrado =================== -->
    <section class="relative flex min-h-[100svh] items-center justify-center overflow-hidden text-center">
      <div id="heroFoto" class="foto-pendiente absolute inset-0" data-src="{foto}"></div>
      <div class="absolute inset-0 bg-gradient-to-b from-pine-900/60 via-pine-900/35 to-pine-900/80"></div>
      <div class="relative mx-auto max-w-4xl px-4 pt-24">
        <nav aria-label="Ruta" class="mb-6 text-xs uppercase tracking-[.2em] text-cream/70">
          <a href="index.html" class="hover:text-cream">Inicio</a> <span class="mx-2">/</span>
          <a href="index.html#alojamientos" class="hover:text-cream">Alojamientos</a>
        </nav>
        <p class="text-sm font-medium uppercase tracking-[.3em] text-wood-300">{e(a["tipo"])}</p>
        <h1 class="mt-4 font-serif text-5xl font-semibold leading-[1.05] text-white drop-shadow-lg sm:text-7xl lg:text-8xl">{e(a["nombre"])}</h1>
        <div class="mx-auto mt-6 flex items-center justify-center gap-3 text-cream/85" aria-hidden="true">
          <span class="h-px w-12 bg-cream/50"></span><span>🌲</span><span class="h-px w-12 bg-cream/50"></span>
        </div>
        <p class="mt-6 text-lg text-cream/90">👥 {a["max"]} personas · {e(a["habs"])} · <strong class="font-semibold text-white">{e(a["precio"])}</strong> / noche</p>
        <div class="mt-10 flex flex-col justify-center gap-4 sm:flex-row">
          <button data-open-booking class="rounded-full bg-wood-500 px-8 py-4 font-semibold text-white shadow-xl shadow-wood-700/40 transition hover:-translate-y-0.5 hover:bg-wood-600">Reservar ahora</button>
          <a href="#detalles" class="rounded-full border border-cream/40 px-8 py-4 font-medium text-cream transition hover:bg-cream/10">Ver detalles</a>
        </div>
      </div>
      <a href="#detalles" class="absolute bottom-6 left-1/2 -translate-x-1/2 animate-bounce text-cream/70" aria-label="Bajar a los detalles">
        <svg class="h-8 w-8" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6"/></svg>
      </a>
    </section>

    <!-- =================== DATOS CLAVE =================== -->
    <section id="detalles" class="scroll-mt-20 border-b border-stone-150 bg-white">
      <dl class="mx-auto grid max-w-7xl grid-cols-2 divide-stone-150 px-4 sm:px-6 lg:grid-cols-4 lg:divide-x lg:px-8">
        <div class="p-6 text-center"><dt class="text-xs uppercase tracking-widest text-pine-700/60">Capacidad</dt><dd class="mt-1 font-serif text-3xl font-semibold">{a["max"]} personas</dd></div>
        <div class="p-6 text-center"><dt class="text-xs uppercase tracking-widest text-pine-700/60">Distribución</dt><dd class="mt-1 font-serif text-2xl font-semibold">{e(a["habs"])}</dd></div>
        <div class="p-6 text-center"><dt class="text-xs uppercase tracking-widest text-pine-700/60">Precio / noche</dt><dd class="mt-1 font-serif text-3xl font-semibold">{e(a["precio"])}</dd></div>
        <div class="p-6 text-center"><dt class="text-xs uppercase tracking-widest text-pine-700/60">Horario</dt><dd class="mt-1 font-serif text-2xl font-semibold">15:00 → 10:00</dd></div>
      </dl>
    </section>

    <!-- =================== DESCRIPCIÓN + CAMAS + TARJETA DE RESERVA =================== -->
    <section class="py-20 sm:py-24">
      <div class="mx-auto grid max-w-7xl gap-12 px-4 sm:px-6 lg:grid-cols-3 lg:px-8">
        <div class="space-y-12 lg:col-span-2">
          <div class="space-y-4 text-lg leading-relaxed text-pine-700/90">
            <p class="text-sm font-semibold uppercase tracking-[.25em] text-wood-600">El alojamiento</p>
            <h2 class="font-serif text-4xl font-semibold text-pine-900 sm:text-5xl">{e(a.get('lema') or nombre_full)}</h2>
{parrafos}
          </div>
          <div>
            <h3 class="font-serif text-3xl font-semibold">Habitaciones y camas</h3>
            <ul class="mt-5 space-y-3 rounded-3xl border border-stone-150 bg-white p-6 text-pine-800 shadow-soft">
{li_camas}
            </ul>
          </div>
        </div>

        <aside class="lg:sticky lg:top-28 lg:self-start">
          <div class="rounded-3xl bg-pine-800 p-8 text-cream shadow-soft">
            <p class="text-xs uppercase tracking-widest text-cream/60">Precio por noche</p>
            <p class="mt-1 font-serif text-4xl">{e(a["precio"])}</p>
            <p class="mt-1 text-sm text-cream/60">Según temporada · hasta {a["max"]} personas</p>
            <button data-open-booking class="mt-6 w-full rounded-full bg-wood-500 py-4 font-semibold text-white transition hover:bg-wood-600">Reservar ahora</button>
            <a href="https://wa.me/34686235888?text={e('Hola, me interesa ' + nombre_full)}" target="_blank" rel="noopener" class="mt-3 block w-full rounded-full border border-cream/40 py-3 text-center font-medium transition hover:bg-cream/10">WhatsApp directo</a>
            <p class="mt-6 text-center text-sm text-cream/70">o llámanos al <a href="tel:+34686235888" class="font-semibold text-cream underline">686 23 58 88</a></p>{reg_aside}
          </div>
        </aside>
      </div>
    </section>

    {galeria}
    <!-- =================== SERVICIOS =================== -->
    <section class="bg-stone-150 py-20 sm:py-24">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-[.25em] text-wood-600">Servicios</p>
        <h2 class="mt-2 font-serif text-4xl font-semibold">Todo lo que incluye</h2>
        <ul class="mt-10 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
{li_serv}
        </ul>
      </div>
    </section>

    <!-- =================== NORMAS =================== -->
    <section class="py-20 sm:py-24">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="font-serif text-4xl font-semibold">Normas de la casa</h2>
        <div class="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <div class="rounded-3xl border border-stone-150 bg-white p-6 shadow-soft"><p class="text-xs uppercase tracking-widest text-pine-700/60">Entrada</p><p class="font-serif text-3xl font-semibold">15:00 h</p></div>
          <div class="rounded-3xl border border-stone-150 bg-white p-6 shadow-soft"><p class="text-xs uppercase tracking-widest text-pine-700/60">Salida</p><p class="font-serif text-3xl font-semibold">10:00 h</p></div>
          <div class="rounded-3xl border border-red-200 bg-red-50/60 p-6"><p class="text-xs uppercase tracking-widest text-red-800/70">Mascotas</p><p class="font-serif text-2xl font-semibold text-red-900">No se aceptan</p></div>
          <div class="rounded-3xl border border-red-200 bg-red-50/60 p-6"><p class="text-xs uppercase tracking-widest text-red-800/70">Tabaco</p><p class="font-serif text-2xl font-semibold text-red-900">No fumar dentro</p></div>
        </div>{reg_normas}
      </div>
    </section>

    <!-- =================== OTROS ALOJAMIENTOS =================== -->
    <section class="border-t border-stone-150 bg-white py-20 sm:py-24">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="font-serif text-4xl font-semibold">Otros alojamientos</h2>
        <div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
{otros}
        </div>
      </div>
    </section>
  </main>

  <!-- =================== PIE (igual que la portada) =================== -->
  <footer class="bg-pine-900 pb-24 pt-10 text-sm text-cream/60 sm:pb-10">
    <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 text-center sm:flex-row sm:px-6 sm:text-left lg:px-8">
      <img data-logo src="{LOGO_V}" alt="Cabañas de Madera Los Pinos" class="hidden h-20 w-auto opacity-80 brightness-0 invert" />
      <p>© <span id="year"></span> Cabañas de Madera Los Pinos · Arroyo Frío, Sierra de Cazorla</p>
      <p><a href="mailto:info@cabanaslospinos.com" class="hover:text-cream">info@cabanaslospinos.com</a> · <a href="tel:+34686235888" class="hover:text-cream">686 23 58 88</a></p>
    </div>
  </footer>

  <button data-open-booking class="fixed inset-x-4 bottom-4 z-30 rounded-full bg-wood-500 py-4 font-semibold text-white shadow-2xl shadow-wood-700/40 sm:hidden">Reservar {e(a["nombre"])}</button>

  <!-- =================== MODAL DE RESERVA =================== -->
  <div id="bookingModal" class="fixed inset-0 z-50 hidden items-end justify-center bg-pine-900/70 backdrop-blur-sm sm:items-center sm:p-6" role="dialog" aria-modal="true" aria-labelledby="bookingTitle">
    <div class="max-h-[92svh] w-full max-w-lg overflow-y-auto rounded-t-3xl bg-cream p-6 shadow-2xl sm:rounded-3xl sm:p-8">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[.25em] text-wood-600">Solicitud de reserva</p>
          <h2 id="bookingTitle" class="mt-1 font-serif text-3xl font-semibold">Reserva tu estancia</h2>
        </div>
        <button data-close-booking class="rounded-full p-2 text-pine-700 hover:bg-pine-50" aria-label="Cerrar">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </div>
      <form id="bookingForm" class="mt-6 space-y-4" novalidate>
        <label class="block"><span class="text-sm font-medium">Alojamiento</span>
          <select name="alojamiento" id="fAlojamiento" class="mt-1 w-full rounded-xl border border-stone-150 bg-white px-4 py-3 focus:border-wood-500 focus:outline-none focus:ring-2 focus:ring-wood-300"></select>
          <span id="fInfo" class="mt-1 block text-xs text-pine-700/70"></span></label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block"><span class="text-sm font-medium">Entrada</span><input type="date" name="entrada" required class="mt-1 w-full rounded-xl border border-stone-150 bg-white px-3 py-3 focus:border-wood-500 focus:outline-none focus:ring-2 focus:ring-wood-300" /></label>
          <label class="block"><span class="text-sm font-medium">Salida</span><input type="date" name="salida" required class="mt-1 w-full rounded-xl border border-stone-150 bg-white px-3 py-3 focus:border-wood-500 focus:outline-none focus:ring-2 focus:ring-wood-300" /></label>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <label class="block"><span class="text-sm font-medium">Personas</span><input type="number" name="personas" id="fPersonas" min="1" value="2" required class="mt-1 w-full rounded-xl border border-stone-150 bg-white px-4 py-3 focus:border-wood-500 focus:outline-none focus:ring-2 focus:ring-wood-300" /></label>
          <label class="block"><span class="text-sm font-medium">Teléfono</span><input type="tel" name="telefono" required autocomplete="tel" class="mt-1 w-full rounded-xl border border-stone-150 bg-white px-4 py-3 focus:border-wood-500 focus:outline-none focus:ring-2 focus:ring-wood-300" /></label>
        </div>
        <label class="block"><span class="text-sm font-medium">Nombre</span><input type="text" name="nombre" required autocomplete="name" class="mt-1 w-full rounded-xl border border-stone-150 bg-white px-4 py-3 focus:border-wood-500 focus:outline-none focus:ring-2 focus:ring-wood-300" /></label>
        <label class="block"><span class="text-sm font-medium">Comentarios <span class="text-pine-700/50">(opcional)</span></span><textarea name="comentarios" rows="2" class="mt-1 w-full rounded-xl border border-stone-150 bg-white px-4 py-3 focus:border-wood-500 focus:outline-none focus:ring-2 focus:ring-wood-300"></textarea></label>
        <p class="rounded-xl bg-pine-50 px-4 py-3 text-xs text-pine-700">Entrada 15:00 h · Salida 10:00 h · No se aceptan mascotas · No se permite fumar dentro</p>
        <p id="formError" class="hidden text-sm font-medium text-red-700"></p>
        <div class="grid gap-3 pt-2 sm:grid-cols-2">
          <button type="submit" data-via="whatsapp" class="rounded-full bg-pine-700 px-6 py-3.5 font-semibold text-white transition hover:bg-pine-800">Enviar por WhatsApp</button>
          <button type="submit" data-via="email" class="rounded-full bg-wood-500 px-6 py-3.5 font-semibold text-white transition hover:bg-wood-600">Enviar por email</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    const ACTUAL = {json.dumps(nombre_full, ensure_ascii=False)};
    const ALOJAMIENTOS = {datos_js};
    const $ = (s, el = document) => el.querySelector(s);
    const $$ = (s, el = document) => [...el.querySelectorAll(s)];

    // Foto del hero: si no hay foto o no carga, queda la textura de madera con el logo
    (function () {{
      const box = $('#heroFoto'), srcs = box.dataset.src.split('|').filter(Boolean);
      const logo = () => box.innerHTML = `<div class="grid h-full place-items-center"><img src="{LOGO_V}" alt="" class="h-1/3 w-auto opacity-25 brightness-0 invert" onerror="this.remove()"></div>`;
      if (!srcs.length) return logo();
      const img = new Image();
      img.alt = ACTUAL; img.className = 'h-full w-full object-cover';
      img.onload = () => {{ box.classList.remove('foto-pendiente'); box.replaceChildren(img); }};
      img.onerror = () => srcs.length ? img.src = srcs.shift() : logo();  // prueba la siguiente ruta
      img.src = srcs.shift();
    }})();

    // Galería: cada foto prueba sus rutas candidatas; si ninguna carga, se retira
    $$('[data-gal] img').forEach(img => {{
      const srcs = img.dataset.srcs.split('|'), enlace = img.closest('[data-gal]');
      img.onerror = () => {{
        if (srcs.length) return img.src = srcs.shift();
        enlace.remove();
        if (!$$('[data-gal]').length) $('#galeria')?.remove();  // sin fotos: fuera la sección
      }};
      img.onload = () => enlace.href = img.currentSrc || img.src;
      img.src = srcs.shift();
    }});

    // Logos de cabecera y pie: se muestran si cargan; si no, queda el texto
    $$('img[data-logo]').forEach(img => {{
      const ok = () => {{ img.classList.remove('hidden'); img.parentElement.querySelectorAll('[data-logo-fallback]').forEach(x => x.classList.add('hidden')); }};
      if (img.complete && img.naturalWidth) ok(); else {{ img.onload = ok; img.onerror = () => img.remove(); }}
    }});

    // Menú móvil y cabecera al hacer scroll
    const menuBtn = $('#menuBtn'), mobileMenu = $('#mobileMenu'), header = $('#siteHeader');
    menuBtn.addEventListener('click', () => menuBtn.setAttribute('aria-expanded', !mobileMenu.classList.toggle('hidden')));
    const onScroll = () => header.classList.toggle('scrolled', scrollY > 40);
    addEventListener('scroll', onScroll, {{ passive: true }}); onScroll();

    // Modal de reserva (preseleccionado con este alojamiento)
    const sel = $('#fAlojamiento'), modal = $('#bookingModal');
    sel.innerHTML = ALOJAMIENTOS.map(a => `<option>${{a.nombre}}</option>`).join('');
    const sync = () => {{ const a = ALOJAMIENTOS.find(x => x.nombre === sel.value); $('#fInfo').textContent = a.info; $('#fPersonas').max = a.max; }};
    sel.value = ACTUAL; sync(); sel.addEventListener('change', sync);
    const abrir = () => {{ mobileMenu.classList.add('hidden'); modal.classList.replace('hidden', 'flex'); document.body.style.overflow = 'hidden'; }};
    const cerrar = () => {{ modal.classList.replace('flex', 'hidden'); document.body.style.overflow = ''; }};
    document.addEventListener('click', ev => {{
      if (ev.target.closest('[data-open-booking]')) {{ ev.preventDefault(); abrir(); }}
      if (ev.target.closest('[data-close-booking]') || ev.target === modal) cerrar();
    }});
    document.addEventListener('keydown', ev => {{ if (ev.key === 'Escape') cerrar(); }});
    const now = new Date(), hoy = new Date(now - now.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
    $$('#bookingForm input[type="date"]').forEach(i => i.min = hoy);
    $('#bookingForm').addEventListener('submit', ev => {{
      ev.preventDefault();
      const d = Object.fromEntries(new FormData(ev.target));
      const max = ALOJAMIENTOS.find(x => x.nombre === d.alojamiento).max;
      let err = '';
      if (!d.entrada || !d.salida || d.salida <= d.entrada) err = 'Indica fechas válidas: la salida debe ser posterior a la entrada.';
      else if (!(+d.personas >= 1 && +d.personas <= max)) err = `Este alojamiento admite hasta ${{max}} personas.`;
      else if (!d.nombre.trim() || !d.telefono.trim()) err = 'Indica tu nombre y teléfono.';
      $('#formError').textContent = err; $('#formError').classList.toggle('hidden', !err);
      if (err) return;
      const msg = `Hola, me gustaría reservar:\\n• Alojamiento: ${{d.alojamiento}}\\n• Entrada: ${{d.entrada}} (15:00 h)\\n• Salida: ${{d.salida}} (10:00 h)\\n• Personas: ${{d.personas}}\\n• Nombre: ${{d.nombre}}\\n• Teléfono: ${{d.telefono}}` + (d.comentarios ? `\\n• Comentarios: ${{d.comentarios}}` : '');
      if (ev.submitter && ev.submitter.dataset.via === 'whatsapp') window.open(`https://wa.me/34686235888?text=${{encodeURIComponent(msg)}}`, '_blank', 'noopener');
      else location.href = `mailto:info@cabanaslospinos.com?subject=${{encodeURIComponent('Solicitud de reserva – ' + d.alojamiento)}}&body=${{encodeURIComponent(msg)}}`;
    }});
    $('#year').textContent = new Date().getFullYear();
  </script>
</body>
</html>
'''


def main():
    cfg, css = extraer_tema()
    for a in ALOJAMIENTOS:
        (RAIZ / f'{a["slug"]}.html').write_text(pagina(a, cfg, css), encoding='utf-8')
        print('✓', f'{a["slug"]}.html')


if __name__ == '__main__':
    main()
