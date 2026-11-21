"""
Módulo de Base de Datos SQLite para el Chatbot de Plantas (FloraBot).
Almacena fichas botánicas completas, cuidados, plagas, requerimientos y propiedades.
"""

import os
import sqlite3
import re

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plantas.db")

def get_db_connection():
    """Crea y devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea las tablas e inserta los datos botánicos iniciales si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plantas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_comun TEXT NOT NULL,
        nombre_cientifico TEXT NOT NULL,
        tipo TEXT NOT NULL,                -- Interior, Exterior, Suculenta, Aromática, Huerto
        luz TEXT NOT NULL,                 -- Requerimientos de iluminación
        riego TEXT NOT NULL,               -- Frecuencia y método de riego
        humedad TEXT NOT NULL,             -- Necesidad de humedad ambiental
        temperatura TEXT NOT NULL,         -- Rango ideal de temperatura
        suelo TEXT NOT NULL,               -- Tipo de sustrato y drenaje
        toxicidad TEXT NOT NULL,           -- Información de toxicidad para perros/gatos/humanos
        dificultad TEXT NOT NULL,          -- Fácil, Moderada, Exigente
        cuidados TEXT NOT NULL,            -- Consejos clave de mantenimiento y poda
        problemas_comunes TEXT NOT NULL,   -- Plagas, hongos, hojas amarillas o caídas
        propiedades TEXT NOT NULL,         -- Purificadora, aromática, medicinal, etc.
        icono TEXT DEFAULT '🌿'
    );
    """)

    # Verificar si ya existen registros
    cursor.execute("SELECT COUNT(*) as total FROM plantas;")
    row = cursor.fetchone()
    if row and row["total"] > 0:
        conn.close()
        return

    plantas_iniciales = [
        (
            "Monstera Deliciosa (Costilla de Adán)",
            "Monstera deliciosa",
            "Interior",
            "Luz indirecta brillante o media. Evitar sol directo que queme sus hojas.",
            "Moderado. Regar cada 7-10 días en primavera/verano y cada 12-15 días en invierno. Dejar secar el primer tercio del sustrato antes de volver a regar.",
            "Media a alta (50-70%). Pulverizar hojas o usar humidificador si el ambiente es muy seco.",
            "18°C a 27°C. No tolera heladas ni temperaturas bajo 12°C.",
            "Sustrato suelto y aireado con turba, fibra de coco, corteza de pino y perlita para excelente drenaje.",
            "Tóxica para perros, gatos y humanos si se mastica (contiene cristales de oxalato de calcio).",
            "Fácil a Moderada",
            "Limpiar el polvo de las hojas con un paño húmedo para facilitar la fotosíntesis. Colocar un tutor de musgo para trepar a medida que crece.",
            "Hojas amarillas: Exceso de riego. Puntas marrones y crujientes: Falta de humedad ambiental. Sin agujeros (fenestraciones): Falta de luz.",
            "Purificadora de aire, reduce el estrés visual y aporta estética tropical.",
            "🪴"
        ),
        (
            "Sansevieria (Lengua de Suegra / Planta Serpiente)",
            "Sansevieria trifasciata (Dracaena trifasciata)",
            "Interior / Exterior protegido",
            "Muy adaptable. Crece bien desde sombra y poca luz hasta luz solar brillante.",
            "Escaso. Regar solo cuando el sustrato esté 100% seco (cada 2 a 3 semanas en verano, mensual en invierno). El exceso de agua la pudre.",
            "Tolera ambientes muy secos (30-40%). No necesita pulverización.",
            "15°C a 30°C. Proteger de heladas prolongadas.",
            "Sustrato para cactus y suculentas con mucha perlita o arena gruesa. Drenaje impecable.",
            "Levemente tóxica para perros y gatos si se ingiere (contiene saponinas que causan malestar estomacal).",
            "Muy Fácil (Casi indestructible)",
            "Es la planta ideal para principiantes y personas ocupadas. Limpiar hojas esporádicamente y fertilizar solo 1 vez al año en primavera.",
            "Hojas blandas y amarillentas desde la base: Pudrición por encharcamiento. Manchas secas: Quemadura solar directa repentina.",
            "Purificadora de aire de élite según la NASA (elimina benceno, formaldehído y produce oxígeno por la noche).",
            "🌿"
        ),
        (
            "Pothos (Potus / Poto)",
            "Epipremnum aureum",
            "Interior (Colgante o trepadora)",
            "Luz indirecta brillante a media. Sobrevive en luz artificial de oficina.",
            "Moderado. Regar cuando los primeros 3 cm de tierra estén secos (aprox. 1 vez por semana). Si las hojas decaen levemente, pide agua.",
            "Media. Agradece pulverizaciones ocasionales en verano.",
            "16°C a 26°C. Evitar corrientes de aire frío.",
            "Sustrato universal ligero mezclado con perlita.",
            "Tóxica para gatos y perros por oxalatos insolubles.",
            "Muy Fácil",
            "Fácil de propagar por esquejes en agua. Se puede guiar como enredadera o dejar caer en cascada.",
            "Hojas amarillas generalizadas: Riego excesivo. Pérdida de matices variegados: Falta de luz. Puntas marrones: Ambiente muy seco.",
            "Excelente eliminadora de toxinas del aire interior (monóxido de carbono y xileno).",
            "🌱"
        ),
        (
            "Cuna de Moisés (Lirio de la Paz / Espatifilo)",
            "Spathiphyllum wallisii",
            "Interior",
            "Luz indirecta media a baja. No exponer a sol directo bajo ninguna circunstancia.",
            "Frecuente. Mantener el sustrato ligeramente húmedo pero no encharcado (aprox. 1 a 2 veces por semana). Te avisa bajando sus hojas si tiene sed.",
            "Alta (60-80%). Pulverizar agua tibia sobre las hojas regularmente sin mojar en exceso las flores blancas.",
            "18°C a 25°C. Muy sensible al frío intenso.",
            "Sustrato rico en materia orgánica, turba y perlita.",
            "Tóxica para gatos y perros (oxalato de calcio). Mantener en sitios elevados.",
            "Fácil",
            "Florece varias veces al año con brácteas blancas elegantes. Cortar las flores marchitas desde la base del tallo para estimular nuevas floraciones.",
            "Hojas marchitas y caídas: Sed extrema (se recupera al regar en pocas horas). Puntas negras: Agua con exceso de cloro o sales (usar agua reposada).",
            "Capacidad sobresaliente para absorber humedad ambiental y filtrar esporas de moho y químicos.",
            "🕊️"
        ),
        (
            "Aloe Vera (Sábila)",
            "Aloe barbadensis Miller",
            "Suculenta / Exterior e Interior muy luminoso",
            "Pleno sol o luz brillante directa por al menos 4-6 horas diarias.",
            "Muy escaso. Regar profundamente cada 15 a 20 días solo cuando el sustrato esté completamente seco. En invierno reducir a una vez al mes.",
            "Baja. No requiere humedad en el follaje.",
            "18°C a 32°C. No tolera heladas ni suelo mojado frío.",
            "Sustrato poroso específico para suculentas o tierra con arena gruesa y grava volcánica.",
            "El gel interior es seguro y medicinal en humanos; la corteza amarilla (aloína) es laxante y tóxica para mascotas.",
            "Muy Fácil",
            "Usar macetas de barro cocido con orificio de drenaje amplio. Retirar hijuelos de la base para multiplicarla.",
            "Hojas delgadas y cóncavas: Falta de riego. Hojas marrones y blandas: Exceso mortal de humedad. Color pardo/rojizo: Estrés por sol intenso (normal si no se quema).",
            "Gel hidratante y cicatrizante para quemaduras superficiales de la piel, antiséptico natural.",
            "🌵"
        ),
        (
            "Ficus Lyrata (Higuera Hoja de Violín)",
            "Ficus lyrata",
            "Interior",
            "Luz indirecta muy abundante y brillante. Tolera un poco de sol suave de la mañana.",
            "Moderado y regular. Esperar a que los primeros 5 cm de tierra estén secos antes de regar (cada 8-12 días). El agua estancada es su peor enemigo.",
            "Media a alta (50-60%). Limpiar sus grandes hojas con paño suave periódicamente.",
            "18°C a 24°C. Detesta los cambios bruscos de ubicación y las corrientes de aire.",
            "Sustrato premium aireado con corteza, perlita y compost orgánico.",
            "Tóxica para gatos y perros si muerden sus hojas o tallos.",
            "Moderada a Exigente",
            "Girar la maceta un cuarto de vuelta cada mes para que crezca erguida y pareja hacia la luz. No cambiar de sitio una vez adaptada.",
            "Caída repentina de hojas: Corrientes de aire frío o exceso de agua. Manchas marrones centrales: Hongo por raíces asfixiadas.",
            "Gran presencia escénica y purificación de partículas de aire en interiores.",
            "🌳"
        ),
        (
            "Ficus Elástica (Gomero / Árbol del Caucho)",
            "Ficus elastica",
            "Interior / Exterior protegido",
            "Luz indirecta brillante. Tolera sol suave matutino que intensifica el brillo de sus hojas granate o verdes.",
            "Moderado. Regar cuando los primeros 3-4 cm de tierra se sientan secos al tacto (cada 7-10 días).",
            "Media. Agradece que le pulvericen las hojas en climas muy secos.",
            "16°C a 28°C.",
            "Sustrato con buen drenaje, mezcla de tierra negra con perlita y humus de lombriz.",
            "Tóxica para animales (su látex lechoso causa dermatitis e irritación digestiva).",
            "Fácil",
            "Limpiar hojas con frecuencia. Podar el ápice si se desea fomentar ramas laterales y un porte más tupido.",
            "Hojas inferiores amarillas que caen: Regar con demasiada frecuencia. Hojas arrugadas: Falta de hidratación.",
            "Filtra toxinas como formaldehído; follaje llamativo y resistente.",
            "🍃"
        ),
        (
            "Lavanda (Lavandula)",
            "Lavandula angustifolia",
            "Exterior / Balcón soleado",
            "Pleno sol directo obligatorio (mínimo 6 horas diarias de sol directo).",
            "Bajo. Muy tolerante a la sequía. Regar moderadamente cada 7-10 días en maceta, evitando siempre mojar las ramas y flores.",
            "Baja. Prefiere ambientes secos y con buena ventilación.",
            "Resiste heladas moderadas (-10°C) y calor extremo veraniego.",
            "Suelo calcáreo, alcalino o neutro, muy arenoso y con drenaje instantáneo.",
            "No tóxica para humanos. El aceite concentrado en grandes dosis no debe administrarse a mascotas.",
            "Fácil en exteriores soleados",
            "Podar suavemente tras la floración en otoño para mantener la mata compacta y estimular flores la siguiente temporada.",
            "Ramas leñosas caídas y ennegrecidas: Suelo arcilloso encharcado o falta de drenaje. Falta de flores: Insuficiente sol.",
            "Aroma relajante natural, ahuyenta mosquitos y polillas, atrae abejas y polinizadores beneficiosos.",
            "🪻"
        ),
        (
            "Romero",
            "Salvia rosmarinus (Rosmarinus officinalis)",
            "Exterior / Terraza",
            "Pleno sol directo continuo (al menos 6 a 8 horas).",
            "Muy bajo. Dejar secar la tierra por completo entre riegos. En invierno regar muy poco.",
            "Baja. Los climas húmedos y cerrados favorecen hongos como el oídio.",
            "Muy rústico. Soporta calor, sequía y heladas de hasta -8°C.",
            "Suelos pobres, pedregosos o arenosos con drenaje perfecto.",
            "Completamente no tóxica y comestible.",
            "Fácil",
            "Cosechar brotes tiernos para la cocina cortando con tijera limpia. No abusar del fertilizante nitrogenado.",
            "Manchas blancas polvorientas: Oídio por exceso de humedad o poco aire. Pudrición radicular: Maceta sin orificio de salida.",
            "Hierba culinaria deliciosa, estimulante digestivo y antioxidante natural.",
            "🌿"
        ),
        (
            "Calathea Orbifolia",
            "Calathea orbifolia (Goeppertia orbifolia)",
            "Interior",
            "Luz indirecta suave o semisombra. El sol directo decolora y quema sus hojas rayadas.",
            "Frecuente con agua de lluvia o filtrada (sin cal ni cloro). Mantener el sustrato húmedo como una esponja escurrida.",
            "Muy alta (65-85%). Requiere humidificador ambiental o bandeja con guijarros y agua.",
            "18°C a 24°C. Muy sensible a corrientes frías y estufas.",
            "Sustrato ácido y poroso: Turba, fibra de coco, perlita y corteza fina.",
            "Completamente NO tóxica (100% Pet Friendly para perros y gatos).",
            "Moderada a Difícil (Requiere atención a la humedad)",
            "Sus hojas se mueven y cierran hacia arriba por la noche (planta de oración). Nunca usar abrillantadores químicos en sus hojas.",
            "Bordes marrones y curvados hacia adentro: Falta de humedad ambiental o agua de grifo pesada. Araña roja: Por aire excesivamente seco.",
            "Segura para hogares con mascotas y de belleza botánica sobresaliente.",
            "🪴"
        ),
        (
            "Planta ZZ (Zamioculca)",
            "Zamioculcas zamiifolia",
            "Interior",
            "Extremadamente tolerante. Prospera en luz indirecta brillante pero sobrevive en rincones con sombra o poca luz.",
            "Mínimo. Posee rizomas subterráneos que almacenan agua. Regar cada 2 a 4 semanas. Mejor olvidar regarla que regar de más.",
            "Tolera aire seco de calefacción y aire acondicionado.",
            "18°C a 30°C.",
            "Sustrato bien suelto y permeable (mezcla para cactus o universal con 40% perlita).",
            "Tóxica por ingestión (oxalatos de calcio). Mantener fuera del alcance de cachorros curiosos.",
            "Ultra Fácil (Prácticamente inmortal)",
            "Hojas de un brillo verde esmeralda encerado natural. No requiere fertilización frecuente (1 vez cada 3 meses).",
            "Hojas amarillas que se desprenden del tallo: Exceso letal de riego.",
            "Purificadora y estética moderna minimalista.",
            "🌱"
        ),
        (
            "Orquídea Phalaenopsis (Orquídea Mariposa)",
            "Phalaenopsis spp.",
            "Interior luminoso",
            "Luz indirecta brillante abundante. Jamás sol directo sobre flores u hojas.",
            "Riego por inmersión semanal durante 10 minutos cuando las raíces dentro de la maceta transparente se vean plateadas/grises (si están verdes, no regar).",
            "Media a alta (55-75%). Pulverizar raíces aéreas en verano.",
            "18°C a 26°C. Requiere una ligera caída de temperatura nocturna (15°C) para inducir nueva floración.",
            "No usa tierra común: Corteza de pino, carbón vegetal y musgo sphagnum en maceta transparente.",
            "NO tóxica para gatos y perros (Pet Friendly).",
            "Moderada",
            "Dejar las raíces expuestas a la luz en su maceta transparente porque hacen fotosíntesis. Cortar la vara floral por encima del tercer nudo tras marchitarse.",
            "Raíces marrones y huecas: Pudrición por agua acumulada en la base. Caída de botones florales: Corrientes de aire o falta de luz.",
            "Floración espectacular que dura hasta 3 meses consecutivos.",
            "🌸"
        ),
        (
            "Cinta (Mala Madre / Lazo de Amor)",
            "Chlorophytum comosum",
            "Interior / Exterior en sombra",
            "Luz indirecta brillante a moderada. Tolera sol suave de primeras horas de la mañana.",
            "Moderado. 1 a 2 veces por semana en verano, cada 10-14 días en invierno. Sus raíces tubulares almacenan agua.",
            "Media. Se adapta bien al hogar promedio.",
            "13°C a 27°C. Tolera descensos esporádicos a 2°C.",
            "Sustrato estándar con buen drenaje.",
            "Totalmente NO tóxica (100% Pet Friendly para perros y gatos).",
            "Muy Fácil",
            "Emite tallos con pequeñas flores blancas y numerosos 'hijuelos' colgantes que se pueden enraizar en agua o tierra muy fácilmente.",
            "Puntas marrones: Ambiente muy seco o acumulación de flúor/cloro del agua de grifo. Hojas descoloridas: Falta de luz.",
            "Gran purificadora de monóxido de carbono según la NASA; ideal para dormitorios y colgar.",
            "🌿"
        ),
        (
            "Menta",
            "Mentha spicata / Mentha piperita",
            "Exterior o ventana luminosa (Maceta independiente)",
            "Semisombra a sol moderado.",
            "Frecuente. Necesita suelo constantemente fresco y húmedo. No dejar que se seque completamente la tierra.",
            "Media a alta.",
            "Muy resistente al frío y heladas. En invierno rebrota con fuerza en primavera.",
            "Tierra fértil rica en materia orgánica y con retención moderada de humedad.",
            "Segura para humanos. En mascotas, grandes cantidades de aceites de menta pueden causar vómito.",
            "Muy Fácil",
            "IMPORTANTE: Plantar siempre en maceta individual porque sus raíces rizomatosas son invasivas y asfixiarán a otras plantas en el mismo recipiente.",
            "Hojas con telarañas o puntitos amarillos: Araña roja por sequedad. Hojas ennegrecidas: Hongos por falta de ventilación.",
            "Infusiones digestivas, coctelería, aromatizante fresco y repelente natural de plagas e insectos.",
            "🍃"
        ),
        (
            "Tomate (Planta Tomatera)",
            "Solanum lycopersicum",
            "Huerto / Terraza muy soleada",
            "Pleno sol directo obligatorio (mínimo 6 a 8 horas diarias sin sombra).",
            "Abundante y regular. Regar directo a la raíz sin mojar las hojas ni las flores para prevenir hongos.",
            "Media. Buena ventilación indispensable.",
            "20°C a 30°C. Las flores no cuajan con temperaturas inferiores a 12°C o superiores a 35°C.",
            "Suelo muy fértil, abonado con compost maduro o humus, profundo y permeable.",
            "El fruto maduro es comestible y saludable. Las hojas y tallos verdes contienen solanina y no deben ingerirse.",
            "Moderada",
            "Requiere tutor o estaca para sostener el peso de los tomates. Podar los brotes axilares ('chupones') para concentrar la energía en frutos grandes.",
            "Hojas con manchas marrones circulares: Mildiu o tizón por mojar las hojas. Fondo del tomate negro y hundido: Podredumbre apical (falta de calcio o riegos irregulares).",
            "Frutos deliciosos ricos en licopeno, vitamina C y antioxidantes.",
            "🍅"
        ),
        (
            "Árbol de Jade (Planta del Dinero)",
            "Crassula ovata",
            "Interior luminoso / Exterior soleado",
            "Luz solar directa o semisombra muy luminosa.",
            "Muy bajo. Regar a fondo solo cuando la tierra esté completamente seca y las hojas comiencen a sentirse ligeramente menos carnosas.",
            "Baja. No pulverizar agua.",
            "18°C a 25°C. Proteger de heladas fuertes bajo 5°C.",
            "Sustrato arenoso para crasas con excelente drenaje en maceta de terracota.",
            "Tóxica para perros y gatos si se ingiere.",
            "Fácil",
            "Forma un tronco leñoso estilo bonsái con los años. Símbolo tradicional de buena fortuna y prosperidad en el Feng Shui.",
            "Caída masiva de hojas verdes: Riego excesivo o falta dramática de luz. Hojas arrugadas: Falta de agua.",
            "Longevidad notable, fácil multiplicación a partir de una sola hoja.",
            "🪙"
        )
    ]

    cursor.executemany("""
    INSERT INTO plantas (
        nombre_comun, nombre_cientifico, tipo, luz, riego, humedad,
        temperatura, suelo, toxicidad, dificultad, cuidados,
        problemas_comunes, propiedades, icono
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, plantas_iniciales)

    conn.commit()
    conn.close()
    print("✓ Base de datos botánica inicializada con éxito.")

STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a",
    "en", "para", "por", "con", "sin", "sobre", "entre", "mi", "mis", "tu",
    "tus", "su", "sus", "como", "que", "cual", "cuales", "donde", "cuando",
    "cuanto", "cuanta", "porque", "hola", "bot", "planta", "plantas", "cuido",
    "cuidar", "riego", "regar", "tengo", "hojas", "flor", "flores", "dime",
    "sobre", "quiero", "saber", "algo", "buenas", "dias", "tardes"
}

def clean_search_terms(query):
    """Extrae palabras clave significativas de la consulta del usuario."""
    words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]{3,}\b', query.lower())
    terms = [w for w in words if w not in STOPWORDS]
    return terms if terms else words

def search_plants(query, limit=3):
    """
    Busca plantas en la base de datos acumulando puntuación por coincidencia
    en nombres, toxicidad, cuidados, tipo y problemas comunes.
    """
    if not os.path.exists(DB_PATH):
        init_db()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plantas")
    all_plants = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not all_plants:
        return []

    query_clean = query.strip().lower()
    terms = clean_search_terms(query)

    plant_scores = {}
    for p in all_plants:
        pid = p["id"]
        plant_scores[pid] = 0
        name_common = p["nombre_comun"].lower()
        name_sci = p["nombre_cientifico"].lower()
        toxicity = p["toxicidad"].lower()
        problems = p["problemas_comunes"].lower()
        care = p["cuidados"].lower()
        p_type = p["tipo"].lower()
        light = p["luz"].lower()
        water = p["riego"].lower()
        props = p["propiedades"].lower()

        # Coincidencia exacta o frase completa en nombres
        if query_clean in name_common or name_common in query_clean:
            plant_scores[pid] += 60
        if query_clean in name_sci or name_sci in query_clean:
            plant_scores[pid] += 50

        # Ponderación por palabras clave
        for term in terms:
            t = term.lower()
            if t in name_common:
                plant_scores[pid] += 25
            if t in name_sci:
                plant_scores[pid] += 20
            if t in toxicity:
                plant_scores[pid] += 12
            if t in problems:
                plant_scores[pid] += 10
            if t in care:
                plant_scores[pid] += 8
            if t in p_type:
                plant_scores[pid] += 8
            if t in light or t in water:
                plant_scores[pid] += 7
            if t in props:
                plant_scores[pid] += 6

    # Filtrar solo plantas con coincidencias positivas y ordenar
    ranked = [p for p in all_plants if plant_scores[p["id"]] > 0]
    ranked.sort(key=lambda x: plant_scores[x["id"]], reverse=True)

    # Si ninguna coincide directamente con los términos, devolver top plantas representativas
    if not ranked:
        return all_plants[:limit]

    return ranked[:limit]

def get_all_plants():
    """Devuelve todas las plantas registradas en la base de datos."""
    if not os.path.exists(DB_PATH):
        init_db()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plantas ORDER BY nombre_comun ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_plant_by_id(plant_id):
    """Devuelve una planta por su ID único."""
    if not os.path.exists(DB_PATH):
        init_db()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plantas WHERE id = ?;", (plant_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_plant(data):
    """Inserta una nueva planta en la base de datos."""
    if not os.path.exists(DB_PATH):
        init_db()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO plantas (
        nombre_comun, nombre_cientifico, tipo, luz, riego, humedad,
        temperatura, suelo, toxicidad, dificultad, cuidados,
        problemas_comunes, propiedades, icono
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        data.get("nombre_comun"),
        data.get("nombre_cientifico", "Desconocido"),
        data.get("tipo", "Interior"),
        data.get("luz", "Luz indirecta"),
        data.get("riego", "Moderado"),
        data.get("humedad", "Media"),
        data.get("temperatura", "18-25°C"),
        data.get("suelo", "Sustrato universal drenante"),
        data.get("toxicidad", "Consultar veterinario"),
        data.get("dificultad", "Fácil"),
        data.get("cuidados", "Riego regular y buena luz"),
        data.get("problemas_comunes", "Evitar encharcamiento"),
        data.get("propiedades", "Decorativa"),
        data.get("icono", "🌱")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_botanical_context_for_prompt(user_query):
    """
    Genera un bloque de contexto enriquecido desde la base de datos SQLite
    para alimentar al modelo Gemini antes de responder.
    """
    matches = search_plants(user_query, limit=2)
    if not matches:
        return "", []

    context_lines = [
        "### DATOS OFICIALES DE LA BASE DE DATOS BOTÁNICA (SQLITE) ###",
        "Utiliza la siguiente información verificada para fundamentar tu respuesta al usuario:"
    ]

    for p in matches:
        context_lines.append(f"""
[PLANTA: {p['nombre_comun']} | Científico: {p['nombre_cientifico']}]
- Tipo: {p['tipo']} | Dificultad: {p['dificultad']}
- Iluminación: {p['luz']}
- Riego: {p['riego']}
- Humedad: {p['humedad']} | Temperatura ideal: {p['temperatura']}
- Sustrato: {p['suelo']}
- Toxicidad (Mascotas y Humanos): {p['toxicidad']}
- Cuidados esenciales: {p['cuidados']}
- Diagnóstico de problemas comunes: {p['problemas_comunes']}
- Propiedades: {p['propiedades']}
""")

    context_lines.append("FIN DE LOS DATOS DE LA BASE DE DATOS.\n")
    return "\n".join(context_lines), matches
