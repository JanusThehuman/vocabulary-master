import sys
import os
import csv
import random
import pygame

# --- INICIALIZACE ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.DOUBLEBUF)
pygame.display.set_caption("Vocabulary Master")
is_fullscreen = False

# --- SATUROVANÁ, MODERNÍ BAREVNÁ PALETA ---
BG_LIGHT = (235, 240, 248)
SURFACE = (255, 255, 255)
SURFACE_HOVER = (246, 250, 255)
SHADOW = (180, 195, 215)
PRIMARY = (25, 95, 215)
PRIMARY_HOVER = (45, 120, 240)
PRIMARY_LIGHT = (225, 236, 255)
GREEN = (20, 165, 85)
RED = (215, 45, 60)
LIGHT_RED = (255, 232, 236)
GRAY_BTN = (120, 135, 155)
TEXT_DARK = (22, 32, 50)
TEXT_SUB = (90, 105, 125)
WHITE = (255, 255, 255)

# --- DETEKCE NEJLEPŠÍHO SYSTÉMOVÉHO PÍSMA A CACHE ---
def najdi_nejlepsi_font():
    dostupne = pygame.font.get_fonts()
    preferovane = ['segoeui', 'calibri', 'verdana', 'arial', 'roboto', 'dejavusans']
    for f in preferovane:
        if f in dostupne:
            return f
    return None

FONT_NAME = najdi_nejlepsi_font()
font_cache = {}
text_cache = {}
shadow_cache = {}

# --- SOUBORY ---
CSV_FILE = "otazky.csv"
LEADERBOARD_FILE = "zebricek.csv"

def vytvor_vychozi_csv():
    """
    45 didaktických okruhů (15x Úroveň 1, 15x Úroveň 2, 15x Úroveň 3).
    Každý okruh má 3 jednoznačné kontextové věty (celkem 135 vět) a 5 distraktorů.
    """
    vychozi_otazky = [
        ["Tema", "Spravne", "Spatne", "Body", "Vety_oddelene_svislickou"],

        # ==================== ÚROVEŇ 1 (1 bod - 15 okruhů) ====================
        ["Fyzika / Teplota", "freezing, cold, icy", "boiling, hot, warm, tropical, burning", "1",
         "Water turns into solid ice when the temperature drops and it becomes extremely ____.|Put on your heavy winter coat and gloves, because it is ____ outside!|Polar bears have a thick layer of fat to survive in the ____ Arctic climate."],
        ["Biologie / Spánek", "tired, exhausted, sleepy", "energetic, awake, fresh, active, lively", "1",
         "Without enough sleep at night, the human brain functions poorly and you feel ____.|After running the forty-kilometer marathon, all the athletes were completely ____.|He worked twelve hours without a break, so he was too ____ to cook dinner."],
        ["Ekologie / Voda", "polluted, dirty, contaminated", "clean, pure, fresh, drinkable, sterile", "1",
         "Throwing plastic and chemical waste into the ocean makes the water ____.|You must filter the river water before drinking it, because it is too ____.|Factories without ecological filters leave the local air and rivers heavily ____."],
        ["Fyzika / Rychlost", "fast, quick, rapid", "slow, delayed, sluggish, late, gradual", "1",
         "Light travels at an incredibly ____ speed of 300,000 kilometers per second.|Cheetahs are famous for being the most ____ land predators on Earth.|Modern fiber-optic cables allow for a very ____ internet connection."],
        ["Zdravověda / Výživa", "healthy, nutritious, beneficial", "harmful, toxic, poisonous, unhealthy, junk", "1",
         "Eating a balanced diet full of fresh vegetables and vitamins is ____ for your body.|Doctors strongly recommend regular exercise as part of a ____ lifestyle.|Fresh fruit is a much more ____ snack than potato chips and candy."],
        ["Psychologie / Emoce", "happy, joyful, cheerful", "sad, depressed, miserable, angry, upset", "1",
         "Releasing dopamine and endorphins in the brain makes a person feel ____.|The little girl was ____ when she finally received a puppy for her birthday.|Everyone at the wedding was smiling and in a very ____ mood."],
        ["Fyzika / Hmotnost", "heavy, massive, weighty", "light, weightless, airy, tiny, featherlight", "1",
         "Due to Earth's gravity, objects made of solid iron and lead feel very ____.|He could not lift the ____ wardrobe up the stairs without his friend's help.|An adult elephant is so ____ that it can weigh up to six tons."],
        ["Ekonomika / Ceny", "expensive, costly, pricey", "cheap, free, inexpensive, affordable, bargain", "1",
         "Because pure gold is rare and difficult to mine, it is very ____ to buy.|Dining in a luxury five-star restaurant in Paris is usually quite ____.|Brand-new sports cars are too ____ for an average student to afford."],
        ["Astronomie / Vesmír", "empty, vacant, void", "full, crowded, packed, busy, overflowing", "1",
         "Beyond the Earth's atmosphere, outer space is mostly an ____ vacuum without air.|When all the students went home for the holidays, the school building was completely ____.|He opened the fridge to make breakfast, but it was completely ____."],
        ["Sociologie / Prostředí", "quiet, silent, peaceful", "loud, noisy, deafening, chaotic, roaring", "1",
         "To focus and study effectively, the human brain usually requires a ____ environment.|The university library must remain ____ so that students can read without distraction.|At midnight, the small village streets were completely ____ and calm."],
        ["Geografie / Vlhkost", "dry, arid, parched", "wet, humid, rainy, soaked, flooded", "1",
         "Cacti are special plants that can survive in the extremely ____ desert climate.|Because it had not rained forthree months, the soil in the garden was completely ____.|Use a towel to make sure your hair is ____ before going outside in winter."],
        ["Bezpečnost / Riziko", "dangerous, unsafe, risky", "safe, secure, harmless, protected, gentle", "1",
         "Swimming in the ocean during a violent thunderstorm is extremely ____.|Walking alone on thin ice in the middle of a lake is very ____.|Electricians wear rubber gloves because working with high voltage is ____."],
        ["Fyzika / Optika", "bright, shining, luminous", "dark, dim, shadowy, gloomy, black", "1",
         "Never look directly at the sun, because its light is too ____ and can damage your eyes.|A lighthouse uses a ____ lamp to warn ships about rocks in the night.|The full moon was so ____ that we could walk in the forest without a flashlight."],
        ["Biologie / Svaly", "strong, powerful, muscular", "weak, feeble, powerless, fragile, frail", "1",
         "Ants are incredibly ____ insects because they can carry objects ten times their own weight.|Regular weightlifting makes your bones and muscles much more ____.|A ____ wind blew down several old trees in the city park."],
        ["Historie / Čas", "ancient, old, historic", "modern, new, futuristic, recent, current", "1",
         "The pyramids in Egypt are ____ monuments built more than four thousand years ago.|In Rome, tourists can walk through the ruins of ____ buildings from the Roman Empire.|Archaeologists found an ____ coin buried deep under the medieval castle."],

        # ==================== ÚROVEŇ 2 (2 body - 15 okruhů) ====================
        ["Ekologie / Energetika", "sustainable, renewable, eco-friendly", "destructive, finite, polluting, toxic, harmful", "2",
         "Solar and wind power are ____ sources of energy that do not deplete natural resources.|We must adopt ____ farming methods to protect the soil for future generations.|Recycling paper and glass is a key part of a ____ lifestyle."],
        ["Občanská výchova / Právo", "mandatory, compulsory, required", "optional, voluntary, elective, unnecessary, free", "2",
         "In most modern countries, paying income taxes is a ____ duty for working citizens.|Wearing a protective helmet on a construction site is strictly ____ by safety laws.|School attendance is ____ for all children in the Czech Republic."],
        ["Informatika / Pokrok", "innovative, groundbreaking, revolutionary", "outdated, obsolete, old-fashioned, traditional, primitive", "2",
         "The invention of the internet was an ____ step that changed global communication forever.|Marie Curie's ____ research on radioactivity earned her two Nobel Prizes.|Tech companies compete to create the most ____ artificial intelligence tools."],
        ["Geografie / Zdroje", "scarce, rare, limited", "abundant, plentiful, common, unlimited, excessive", "2",
         "In the middle of the Sahara Desert, fresh drinking water is extremely ____.|During the harsh winter famine, food became ____ and expensive.|Natural diamonds are valuable because they are ____ minerals in the Earth's crust."],
        ["Fyzika / Vlastnosti látek", "fragile, delicate, breakable", "sturdy, durable, unbreakable, tough, solid", "2",
         "Glass laboratory equipment is very ____, so students must handle it with care.|Coral reefs are ____ marine ecosystems that die if the ocean temperature rises.|The ____ wings of a butterfly can be easily damaged by human touch."],
        ["Biologie / Imunita", "vulnerable, susceptible, exposed", "immune, protected, invincible, resistant, shielded", "2",
         "Newborn babies have underdeveloped immune systems, making them ____ to infections.|Without a strong firewall and password, a computer network is ____ to hackers.|Coastal cities built at sea level are highly ____ to flooding and hurricanes."],
        ["Ekonomika / Podnikání", "lucrative, profitable, rewarding", "unprofitable, losing, bankrupt, failing, worthless", "2",
         "Developing popular mobile software can be a highly ____ business in the digital age.|Selling cold drinks on a crowded beach during a summer heatwave is very ____.|Because of high demand, the pharmaceutical industry remains extremely ____."],
        ["Technologie / Vývoj", "obsolete, outdated, antiquated", "modern, cutting-edge, advanced, current, futuristic", "2",
         "Because everyone uses smartphones today, public telephone booths have become ____.|Floppy disks and VHS tapes are ____ technologies that nobody uses to store data anymore.|Steam locomotives became ____ after electric and diesel trains were invented."],
        ["Psychologie / Chování", "stubborn, obstinate, inflexible", "flexible, adaptable, open-minded, compliant, cooperative", "2",
         "A ____ person refuses to admit a mistake even when shown clear scientific evidence.|Mules and donkeys have a reputation for being ____ animals that refuse to move.|Negotiations failed because the manager was too ____ to accept any compromise."],
        ["Fyzika / Přístroje", "accurate, precise, exact", "inaccurate, wrong, rough, faulty, mistaken", "2",
         "Atomic clocks are the most ____ timekeeping devices ever built by scientists.|A GPS satellite requires ____ timing to calculate your position on Earth.|Before building a bridge, engineers must make ____ mathematical calculations."],
        ["Geografie / Osídlení", "remote, isolated, distant", "central, nearby, accessible, crowded, urban", "2",
         "Antarctica is the most ____ continent on Earth, far away from major cities.|The mountain village is so ____ that it can only be reached by helicopter in winter.|Astronomers build telescopes in ____ deserts to avoid city light pollution."],
        ["Ekologie / Zemědělství", "abundant, plentiful, ample", "scarce, lacking, rare, insufficient, empty", "2",
         "Thanks to warm weather and regular rain, farmers enjoyed an ____ harvest of wheat.|Oxygen and silicon are the most ____ chemical elements in the Earth's crust.|Tropical rainforests have an ____ variety of plant and animal species."],
        ["Chemie / Bezpečnost", "hazardous, toxic, dangerous", "harmless, safe, nontoxic, healthy, benign", "2",
         "Radioactive waste and lead paint are ____ materials that require special disposal.|Breathing in carbon monoxide gas is extremadamente ____ to human health.|Chemical laboratories use warning symbols to mark ____ substances."],
        ["Právo / Soukromí", "anonymous, unnamed, unidentified", "famous, named, public, known, identified", "2",
         "To protect the witness from danger, their testimony in court remained completely ____.|The hospital received a million-dollar donation from a generous ____ benefactor.|Cybercriminals often use special software to stay ____ on the internet."],
        ["Literatura / Argumentace", "persuasive, convincing, compelling", "unconvincing, weak, doubtful, illogical, poor", "2",
         "The defense lawyer gave a ____ speech that convinced the jury of the man's innocence.|A good academic essay requires ____ arguments supported by verified data.|The advertisement was so ____ that thousands of people bought the product immediately."],

        # ==================== ÚROVEŇ 3 (3 body - 15 okruhů) ====================
        ["Biochemie / Život", "essential, vital, indispensable", "trivial, optional, unnecessary, minor, useless", "3",
         "Liquid water and carbon are ____ for the existence of all known biological life.|Critical thinking is an ____ competence for evaluating information on the internet.|Sleep is ____ for consolidating memory and repairing cells in the human body."],
        ["Lingvistika / Význam", "ambiguous, vague, unclear", "explicit, clear, obvious, definite, transparent", "3",
         "Because the legal contract was written in an ____ way, both companies interpreted it differently.|The politician gave an intentionally ____ answer to avoid making a clear promise.|Scientific definitions must be exact and never ____, so researchers avoid confusion."],
        ["Historie / Dopad", "profound, significant, far-reaching", "superficial, trivial, minor, negligible, slight", "3",
         "The invention of the printing press had a ____ impact on education and literacy in Europe.|The discovery of penicillin brought a ____ transformation to modern medicine.|Experiencing a different culture can lead to a ____ change in a person's worldview."],
        ["Právo / Spravedlnost", "impartial, unbiased, neutral", "biased, prejudiced, corrupt, unfair, one-sided", "3",
         "In a democratic court of law, a judge must remain strictly ____ toward both sides.|Scientific peer review requires ____ experts who evaluate research objectively.|A good referee must be completely ____ and follow the rules regardless of who is playing."],
        ["Ekologie / Adaptace", "resilient, adaptable, tough", "fragile, vulnerable, delicate, weak, sensitive", "3",
         "Tardigrades are microscopic animals so ____ that they can survive even in outer space.|A ____ ecosystem can recover quickly after a natural disaster such as a forest fire.|Developing a ____ mindset helps students overcome academic failure and stress."],
        ["Fyzika / Determinismus", "predictable, foreseeable, expected", "random, chaotic, unpredictable, shocking, erratic", "3",
         "Because planets obey strict gravitational laws, solar eclipses are mathematically ____.|When a country prints too much money, rising inflation is a completely ____ economic result.|The plot of the action movie was so ____ that everyone knew how it would end."],
        ["Astronomie / Kosmologie", "inevitable, unavoidable, inescapable", "preventable, avoidable, unlikely, doubtful, impossible", "3",
         "When a massive star exhausts its nuclear fuel, its gravitational collapse is physically ____.|Without brakes on a steep hill, a collision is ____.|Change and aging are ____ biological processes for all living organisms."],
        ["Psychologie / Rozhodování", "reluctant, hesitant, unwilling", "eager, enthusiastic, willing, keen, ready", "3",
         "Due to the high risk of financial loss, banks were ____ to approve the loan.|Patients are often ____ to try experimental medicine if the side effects are unknown.|Because he was afraid of heights, he was ____ to step onto the glass balcony."],
        ["Věda / Metodologie", "meticulous, thorough, rigorous", "careless, sloppy, negligent, hasty, superficial", "3",
         "Forensic scientists must be ____ when collecting DNA evidence at a crime scene.|Restoring a Renaissance painting requires ____ attention to the smallest details.|A ____ proofreader checks every single comma and spelling rule in the manuscript."],
        ["Sociologie / Technologie", "ubiquitous, omnipresent, widespread", "rare, scarce, absent, unusual, isolated", "3",
         "Smartphones and Wi-Fi networks have become ____ in modern urban society.|Microplastics have become so ____ that scientists find them even in Arctic snow.|In the digital era, cameras and sensors are ____ in public spaces."],
        ["Kultura / Pomíjivost", "ephemeral, fleeting, short-lived", "permanent, eternal, everlasting, enduring, immortal", "3",
         "Viral internet trends are usually ____ and are forgotten within a few weeks.|Mayflies are insects known for their ____ lifespan, which lasts only a single day.|Rainbows are ____ optical phenomena that disappear as soon as the sun or rain shifts."],
        ["Inženýrství / Konstrukce", "sophisticated, advanced, complex", "primitive, crude, basic, simple, rudimentary", "3",
         "The James Webb Space Telescope uses ____ infrared sensors to observe distant galaxies.|Modern passenger airplanes rely on ____ autopilot systems for safe navigation.|The human brain is the most ____ biological structure known to science."],
        ["Politologie / Veřejná správa", "transparent, open, accountable", "secretive, hidden, opaque, corrupt, concealed", "3",
         "To prevent corruption, government budgets and public contracts must be completely ____.|Pure optical glass is ____, allowing almost all visible light to pass through.|Scientists share their raw data so that their research process remains ____."],
        ["Makroekonomie / Zdroje", "sufficient, adequate, enough", "insufficient, inadequate, lacking, deficient, scarce", "3",
         "Plants require ____ sunlight and water to perform photosynthesis effectively.|Before launching a rocket, engineers verify that there is ____ fuel for the mission.|A score of sixty percent is ____ to pass the university qualification exam."],
        ["Medicína / Prevence", "detrimental, harmful, damaging", "beneficial, helpful, healthy, advantageous, healing", "3",
         "Chronic sleep deprivation is ____ to both cognitive performance and immune health.|Smoking tobacco has a proven ____ effect on the human cardiovascular system.|Excessive screen time before bed is ____ to the quality of your natural sleep."]
    ]
    with open(CSV_FILE, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(vychozi_otazky)

def nacti_databazi_slovicek():
    if not os.path.exists(CSV_FILE):
        vytvor_vychozi_csv()
    databaze = []
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader, None)
            for row in reader:
                if len(row) >= 5:
                    spravne = [x.strip() for x in str(row[1]).split(',') if x.strip()]
                    spatne = [x.strip() for x in str(row[2]).split(',') if x.strip()]
                    body = int(row[3].strip())
                    vety = [x.strip() for x in str(row[4]).split('|') if x.strip()]
                    if spravne and spatne and vety:
                        databaze.append({
                            "tema": row[0].strip(),
                            "spravne_pool": spravne,
                            "spatne_pool": spatne,
                            "body": body,
                            "vety": vety
                        })
    except Exception:
        vytvor_vychozi_csv()
        return nacti_databazi_slovicek()

    # Automatický upgrade starší databáze na novou (45 okruhů / 135 vět)
    if len(databaze) < 45:
        vytvor_vychozi_csv()
        return nacti_databazi_slovicek()
    return databaze

def uloz_skore(jmeno, skore, cas_sekund):
    with open(LEADERBOARD_FILE, mode='a', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([jmeno, skore, cas_sekund])

def nacti_osobni_historii(hrac_jmeno):
    if not os.path.exists(LEADERBOARD_FILE):
        return [], None

    zaznamy_hrace = []
    pocet_pokusu_vsech = {}

    try:
        with open(LEADERBOARD_FILE, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                if len(row) >= 2:
                    jmeno = row[0].strip()
                    try:
                        skore = int(row[1])
                        cas = int(row[2]) if len(row) >= 3 else 0
                    except ValueError:
                        continue

                    pocet_pokusu_vsech[jmeno] = pocet_pokusu_vsech.get(jmeno, 0) + 1
                    cislo_pokusu = pocet_pokusu_vsech[jmeno]

                    if jmeno == hrac_jmeno:
                        zaznamy_hrace.append((jmeno, skore, cas, cislo_pokusu))
    except Exception:
        return [], None

    if not zaznamy_hrace:
        return [], None

    nejlepsi_pokus = max(zaznamy_hrace, key=lambda x: (x[1], -x[2] if x[2] > 0 else -999999))
    zaznamy_hrace.remove(nejlepsi_pokus)
    zaznamy_hrace.reverse()
    vysledny_seznam = [nejlepsi_pokus] + zaznamy_hrace

    return vysledny_seznam[:8], nejlepsi_pokus

# --- VYKRESLOVÁNÍ S 3X SUPERSAMPLINGEM A CACHINGEM ---
def draw_soft_shadow(surface, rect, radius=15, offset_y=4):
    key = (rect.width, rect.height, radius, offset_y)
    if key not in shadow_cache:
        shadow_surf = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
        for i, alpha in zip([12, 8, 4, 0], [4, 7, 11, 16]):
            r = pygame.Rect(8 - i // 2, 8 - i // 2 + offset_y, rect.width + i, rect.height + i)
            pygame.draw.rect(shadow_surf, (15, 25, 45, alpha), r, border_radius=radius)
        shadow_cache[key] = shadow_surf
    surface.blit(shadow_cache[key], (rect.x - 8, rect.y - 8))

def get_font(size, is_bold):
    key = (size, is_bold)
    if key not in font_cache:
        font_cache[key] = pygame.font.SysFont(FONT_NAME, size, bold=is_bold)
    return font_cache[key]

def render_crisp_text(text, base_size, color, max_width, is_bold=False):
    """
    3x Supersampling s ukládáním do paměti (cache).
    Zajišťuje dokonale hladké hrany písma bez ztráty FPS.
    """
    cache_key = (text, base_size, color, max_width, is_bold)
    if cache_key in text_cache:
        return text_cache[cache_key]

    scale = 3
    size = base_size
    font = get_font(size * scale, is_bold)
    surf = font.render(text, True, color)

    while (surf.get_width() // scale) > max_width and size > 11:
        size -= 1
        font = get_font(size * scale, is_bold)
        surf = font.render(text, True, color)

    target_w = max(1, surf.get_width() // scale)
    target_h = max(1, surf.get_height() // scale)
    crisp_surf = pygame.transform.smoothscale(surf, (target_w, target_h))

    if len(text_cache) > 600:
        text_cache.clear()
    text_cache[cache_key] = crisp_surf
    return crisp_surf

# --- OŽIVENÁ GRAFIKA POZADÍ ---
class ModernBackground:
    def __init__(self):
        self.size = (0, 0)
        self.surf = None

    def bezier_curve(self, p0, p1, p2, steps=45):
        pts = []
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t)**2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
            y = (1 - t)**2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
            pts.append((x, y))
        return pts

    def draw_blob(self, surface, color, A, B, C, ctrl_A, ctrl_B, ctrl_C):
        pts = []
        pts.extend(self.bezier_curve(A, ctrl_A, B))
        pts.extend(self.bezier_curve(B, ctrl_B, C))
        pts.extend(self.bezier_curve(C, ctrl_C, A))
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.aalines(surface, color, True, pts)

    def draw(self, surface):
        w, h = surface.get_size()
        if self.size != (w, h):
            self.size = (w, h)
            self.surf = pygame.Surface((w, h))
            self.surf.fill(BG_LIGHT)

            shape_layer = pygame.Surface((w, h), pygame.SRCALPHA)
            self.draw_blob(shape_layer, (0, 190, 230, 45), (-w * 0.1, h * 0.4), (w * 0.25, h * 1.1), (-w * 0.2, h * 1.1), (w * 0.15, h * 0.5), (w * 0.2, h * 0.9), (-w * 0.3, h * 0.8))
            self.draw_blob(shape_layer, (240, 40, 110, 35), (w * 0.15, h * 0.3), (w * 0.25, h * 0.45), (w * 0.1, h * 0.5), (w * 0.22, h * 0.35), (w * 0.18, h * 0.55), (w * 0.08, h * 0.4))
            self.draw_blob(shape_layer, (110, 40, 220, 40), (w * 0.7, -h * 0.1), (w * 1.1, h * 0.4), (w * 1.2, -h * 0.2), (w * 0.9, h * 0.2), (w * 1.15, h * 0.1), (w * 0.8, -h * 0.3))
            self.draw_blob(shape_layer, (255, 140, 0, 45), (w * 0.75, h * 0.6), (w * 1.2, h * 1.1), (w * 0.6, h * 1.2), (w * 0.88, h * 0.8), (w * 0.92, h * 1.2), (w * 0.52, h * 0.9))
            self.draw_blob(shape_layer, (30, 200, 110, 35), (w * 0.85, h * 0.4), (w * 1.1, h * 0.7), (w * 1.1, h * 0.3), (w * 0.92, h * 0.52), (w * 1.15, h * 0.58), (w * 0.98, h * 0.22))

            self.surf.blit(shape_layer, (0, 0))
        surface.blit(self.surf, (0, 0))

bg_modern = ModernBackground()

# --- HLAVNÍ TŘÍDA HRY ---
class Game:
    def __init__(self):
        self.player_name = ""
        self.state = "NAME_INPUT"

        self.current_question = 0
        self.score = 0
        self.stats_correct = 0
        self.stats_wrong = 0

        self.wrong_guesses = set()
        self.correct_guess = None
        self.first_attempt = True

        # Neblokující časovače (v milisekundách)
        self.active_quiz_ms = 0
        self.transition_ms = 0
        self.elapsed_seconds = 0

        self.databaze_slovicek = nacti_databazi_slovicek()
        self.active_questions = []

        self.menu_buttons = []
        self.quiz_buttons = []
        self.end_buttons = []
        self.leaderboard_buttons = []

        self.btn_change_player = None
        self.btn_confirm_name = None
        self.end_quiz_button = None

    def vygeneruj_kviz(self):
        """Vybere 9 otázek: 3x 1 bod, 3x 2 body, 3x 3 body (Max = 18 bodů)."""
        self.active_questions = []

        level_1 = [w for w in self.databaze_slovicek if w['body'] == 1]
        level_2 = [w for w in self.databaze_slovicek if w['body'] == 2]
        level_3 = [w for w in self.databaze_slovicek if w['body'] == 3]

        vybrana_slova = random.sample(level_1, min(3, len(level_1))) + \
                        random.sample(level_2, min(3, len(level_2))) + \
                        random.sample(level_3, min(3, len(level_3)))

        for data in vybrana_slova:
            veta = random.choice(data["vety"]).replace("____", "[ _____ ]")
            spravne_slovo = random.choice(data["spravne_pool"])

            pool_spatnych = data["spatne_pool"]
            spatna_slova = random.sample(pool_spatnych, min(3, len(pool_spatnych)))

            vsechny_moznosti = spatna_slova + [spravne_slovo]
            random.shuffle(vsechny_moznosti)
            spravny_index = vsechny_moznosti.index(spravne_slovo)

            self.active_questions.append({
                "otazka": veta,
                "tema": data["tema"],
                "moznosti": vsechny_moznosti,
                "spravne": spravny_index,
                "body": data["body"]
            })

    def start_new_game(self):
        self.current_question = 0
        self.score = 0
        self.stats_correct = 0
        self.stats_wrong = 0
        self.active_quiz_ms = 0
        self.elapsed_seconds = 0
        self.reset_question_state()

        self.databaze_slovicek = nacti_databazi_slovicek()
        self.vygeneruj_kviz()
        self.state = "QUIZ"

    def reset_question_state(self):
        self.wrong_guesses.clear()
        self.correct_guess = None
        self.first_attempt = True
        self.transition_ms = 0

    def next_question(self):
        if self.current_question < len(self.active_questions) - 1:
            self.current_question += 1
            self.reset_question_state()
        else:
            uloz_skore(self.player_name, self.score, max(1, self.elapsed_seconds))
            self.state = "END"

    def vyhodnot_volbu(self, index):
        if self.correct_guess is not None or index in self.wrong_guesses:
            return
        q_data = self.active_questions[self.current_question]
        if index == q_data["spravne"]:
            if self.first_attempt:
                self.score += q_data["body"]
                self.stats_correct += 1
            self.correct_guess = index
            self.transition_ms = 0
        else:
            if self.first_attempt:
                self.stats_wrong += 1
            self.first_attempt = False
            self.wrong_guesses.add(index)

    def update(self, dt):
        """Neblokující aktualizace herního času a animace přechodu."""
        if self.state == "QUIZ":
            if self.correct_guess is None:
                self.active_quiz_ms += dt
                self.elapsed_seconds = self.active_quiz_ms // 1000
            else:
                self.transition_ms += dt
                if self.transition_ms >= 700:
                    self.next_question()

    def handle_input(self, event):
        pos = pygame.mouse.get_pos()

        if self.state == "NAME_INPUT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_RETURN and self.player_name.strip() != "":
                    self.player_name = self.player_name.strip()
                    self.state = "MENU"
                elif len(self.player_name) < 15 and event.unicode.isprintable() and event.unicode != ";":
                    self.player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_confirm_name and self.btn_confirm_name.collidepoint(pos) and self.player_name.strip() != "":
                    self.player_name = self.player_name.strip()
                    self.state = "MENU"

        elif self.state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_change_player and self.btn_change_player.collidepoint(pos):
                    self.player_name = ""
                    self.state = "NAME_INPUT"
                    return
                for btn in self.menu_buttons:
                    if btn['rect'].collidepoint(pos):
                        if btn['text'] == "Nová Hra":
                            self.start_new_game()
                        elif btn['text'] == "Moje historie pokusů":
                            self.state = "LEADERBOARD"
                        elif btn['text'] == "Ukončit":
                            pygame.quit()
                            sys.exit()

        elif self.state == "QUIZ":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.end_quiz_button and self.end_quiz_button.collidepoint(pos):
                    uloz_skore(self.player_name, self.score, max(1, self.elapsed_seconds))
                    self.state = "END"
                    return

                if self.correct_guess is not None:
                    return

                for i, btn in enumerate(self.quiz_buttons):
                    if btn['rect'].collidepoint(pos):
                        self.vyhodnot_volbu(i)
                        break

            # Podpora klávesnice (1-4 nebo A-D) pro rychlé odpovídání
            elif event.type == pygame.KEYDOWN and self.correct_guess is None:
                key_map = {
                    pygame.K_1: 0, pygame.K_KP1: 0, pygame.K_a: 0,
                    pygame.K_2: 1, pygame.K_KP2: 1, pygame.K_b: 1,
                    pygame.K_3: 2, pygame.K_KP3: 2, pygame.K_c: 2,
                    pygame.K_4: 3, pygame.K_KP4: 3, pygame.K_d: 3
                }
                if event.key in key_map and key_map[event.key] < len(self.quiz_buttons):
                    self.vyhodnot_volbu(key_map[event.key])

        elif self.state == "END":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.end_buttons[0]['rect'].collidepoint(pos):
                    self.state = "MENU"
                elif self.end_buttons[1]['rect'].collidepoint(pos):
                    self.state = "LEADERBOARD"

        elif self.state == "LEADERBOARD":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.leaderboard_buttons[0]['rect'].collidepoint(pos):
                    self.state = "MENU"
                    return

    def draw_modern_button(self, surface, rect, text, is_hovered, base_color, text_color=WHITE):
        draw_soft_shadow(surface, rect, radius=25)
        color = PRIMARY_HOVER if (is_hovered and base_color == PRIMARY) else base_color
        pygame.draw.rect(surface, color, rect, border_radius=25)
        text_surf = render_crisp_text(text, 30, text_color, rect.width - 40, is_bold=True)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def draw_quiz_button(self, surface, rect, index, text, state, is_hovered):
        draw_soft_shadow(surface, rect, radius=20, offset_y=3)
        labels = ["A", "B", "C", "D"]
        label_char = labels[index] if index < 4 else str(index + 1)

        if state == "wrong":
            bg_color, text_color = LIGHT_RED, RED
            badge_bg, badge_fg = RED, WHITE
        elif state == "correct":
            bg_color, text_color = GREEN, WHITE
            badge_bg, badge_fg = WHITE, GREEN
        else:
            bg_color = SURFACE_HOVER if is_hovered else SURFACE
            text_color = PRIMARY if is_hovered else TEXT_DARK
            badge_bg = PRIMARY if is_hovered else PRIMARY_LIGHT
            badge_fg = WHITE if is_hovered else PRIMARY

        pygame.draw.rect(surface, bg_color, rect, border_radius=20)

        # Decentní kroužek s písmenem A, B, C, D vlevo
        badge_rect = pygame.Rect(rect.x + 16, rect.centery - 17, 34, 34)
        pygame.draw.rect(surface, badge_bg, badge_rect, border_radius=12)
        badge_surf = render_crisp_text(label_char, 18, badge_fg, 30, is_bold=True)
        surface.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

        # Samotný text odpovědi
        text_surf = render_crisp_text(text, 26, text_color, rect.width - 110, is_bold=(state == "correct"))
        surface.blit(text_surf, text_surf.get_rect(center=(rect.centerx + 12, rect.centery)))

    def draw(self):
        w, h = screen.get_size()
        bg_modern.draw(screen)
        mouse_pos = pygame.mouse.get_pos()

        if self.state == "NAME_INPUT":
            title_surf = render_crisp_text("Zadej své jméno pro uložení profilu:", 42, TEXT_DARK, w - 100, is_bold=True)
            screen.blit(title_surf, title_surf.get_rect(center=(w // 2, h // 3 - 20)))

            name_rect = pygame.Rect(w // 2 - 250, h // 2 - 40, 500, 76)
            draw_soft_shadow(screen, name_rect, radius=20)
            pygame.draw.rect(screen, SURFACE, name_rect, border_radius=20)
            pygame.draw.rect(screen, PRIMARY, name_rect, 3, border_radius=20)

            # Blikající kurzor
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
            display_name = self.player_name + cursor if len(self.player_name) < 15 else self.player_name
            name_surf = render_crisp_text(display_name, 36, PRIMARY, name_rect.width - 40, is_bold=True)
            screen.blit(name_surf, name_surf.get_rect(center=name_rect.center))

            self.btn_confirm_name = pygame.Rect(w // 2 - 140, h // 2 + 65, 280, 55)
            can_continue = len(self.player_name.strip()) > 0
            btn_color = PRIMARY if can_continue else GRAY_BTN
            is_hov = self.btn_confirm_name.collidepoint(mouse_pos) and can_continue
            self.draw_modern_button(screen, self.btn_confirm_name, "Pokračovat", is_hov, btn_color)

            hint_surf = render_crisp_text("(Nebo stiskni klávesu ENTER)", 17, TEXT_SUB, w)
            screen.blit(hint_surf, hint_surf.get_rect(center=(w // 2, h // 2 + 145)))

        elif self.state == "MENU":
            prof_surf = render_crisp_text(f"Přihlášen jako: {self.player_name}", 21, TEXT_DARK, w, is_bold=True)
            screen.blit(prof_surf, prof_surf.get_rect(topleft=(40, 35)))

            self.btn_change_player = pygame.Rect(40, 72, 150, 36)
            ch_hover = self.btn_change_player.collidepoint(mouse_pos)
            pygame.draw.rect(screen, PRIMARY if ch_hover else SURFACE, self.btn_change_player, border_radius=15)
            if not ch_hover:
                pygame.draw.rect(screen, GRAY_BTN, self.btn_change_player, 2, border_radius=15)
            ch_surf = render_crisp_text("Změnit hráče", 16, WHITE if ch_hover else TEXT_DARK, 130, is_bold=True)
            screen.blit(ch_surf, ch_surf.get_rect(center=self.btn_change_player.center))

            title_surf = render_crisp_text("Vocabulary Master", 70, TEXT_DARK, w - 80, is_bold=True)
            screen.blit(title_surf, title_surf.get_rect(center=(w // 2, h // 4 - 25)))

            desc_surf = render_crisp_text("Didaktická hra pro procvičování slovní zásoby napříč předměty.", 23, TEXT_SUB, w - 100)
            screen.blit(desc_surf, desc_surf.get_rect(center=(w // 2, h // 4 + 42)))

            btn_w, btn_h = 360, 65
            start_y = h // 2 - 10
            self.menu_buttons = [
                {'rect': pygame.Rect(w // 2 - btn_w // 2, start_y, btn_w, btn_h), 'text': "Nová Hra"},
                {'rect': pygame.Rect(w // 2 - btn_w // 2, start_y + 85, btn_w, btn_h), 'text': "Moje historie pokusů"},
                {'rect': pygame.Rect(w // 2 - btn_w // 2, start_y + 170, btn_w, btn_h), 'text': "Ukončit"}
            ]
            for btn in self.menu_buttons:
                is_hovered = btn['rect'].collidepoint(mouse_pos)
                self.draw_modern_button(screen, btn['rect'], btn['text'], is_hovered, PRIMARY)

            footer_surf = render_crisp_text("Univerzita Palackého v Olomouci 2026", 16, TEXT_SUB, 400)
            screen.blit(footer_surf, footer_surf.get_rect(bottomright=(w - 25, h - 20)))

        elif self.state == "QUIZ":
            q_data = self.active_questions[self.current_question]

            # Horní vizuální lišta postupu (Progress bar)
            bar_bg = pygame.Rect(0, 0, w, 6)
            prog_ratio = (self.current_question + 1) / len(self.active_questions)
            bar_fg = pygame.Rect(0, 0, int(w * prog_ratio), 6)
            pygame.draw.rect(screen, SHADOW, bar_bg)
            pygame.draw.rect(screen, PRIMARY, bar_fg)

            quiz_label = render_crisp_text(f"OKRUH: {q_data['tema'].upper()}", 18, PRIMARY, w - 350, is_bold=True)
            screen.blit(quiz_label, quiz_label.get_rect(center=(w // 2, 42)))

            progress_surf = render_crisp_text(f"Otázka {self.current_question + 1} z {len(self.active_questions)}", 19, TEXT_DARK, 200, is_bold=True)
            screen.blit(progress_surf, progress_surf.get_rect(topright=(w - 40, 28)))

            m = self.elapsed_seconds // 60
            s = self.elapsed_seconds % 60
            timer_surf = render_crisp_text(f"Čas: {m:02d}:{s:02d}", 19, TEXT_SUB, 200)
            screen.blit(timer_surf, timer_surf.get_rect(topright=(w - 40, 56)))

            # Zalamování věty s využitím měření na základním fontu
            words = q_data["otazka"].split(' ')
            lines, current_line = [], []
            measure_font = get_font(30, False)
            max_line_w = min(820, w - 140)
            for word in words:
                current_line.append(word)
                if measure_font.size(' '.join(current_line))[0] > max_line_w:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            total_text_h = len(lines) * 44
            y_offset = (h // 4 + 10) - (total_text_h // 2)
            for line in lines:
                ls = render_crisp_text(line, 30, TEXT_DARK, max_line_w + 40, is_bold=False)
                screen.blit(ls, ls.get_rect(center=(w // 2, y_offset)))
                y_offset += 44

            self.quiz_buttons = []
            btn_w, btn_h = 560, 56
            start_y = h // 2 - 25

            for i, opt in enumerate(q_data["moznosti"]):
                rect = pygame.Rect(w // 2 - btn_w // 2, start_y + i * (btn_h + 15), btn_w, btn_h)
                self.quiz_buttons.append({'rect': rect, 'text': opt})

            for i, btn in enumerate(self.quiz_buttons):
                is_hovered = btn['rect'].collidepoint(mouse_pos) and self.correct_guess is None
                btn_state = "normal"
                if self.correct_guess == i:
                    btn_state = "correct"
                elif i in self.wrong_guesses:
                    btn_state = "wrong"
                self.draw_quiz_button(screen, btn['rect'], i, btn['text'], btn_state, is_hovered)

            body_val = q_data["body"]
            body_text = "1 bod" if body_val == 1 else f"{body_val} body"
            info_text = f"Skóre: {self.score} / 18   |   Hodnota otázky: {body_text}   |   Správně: {self.stats_correct}   Špatně: {self.stats_wrong}"
            info_surf = render_crisp_text(info_text, 18, TEXT_SUB, w - 260)
            screen.blit(info_surf, info_surf.get_rect(center=(w // 2, h - 45)))

            self.end_quiz_button = pygame.Rect(40, h - 65, 125, 40)
            end_hovered = self.end_quiz_button.collidepoint(mouse_pos)
            draw_soft_shadow(screen, self.end_quiz_button, radius=20, offset_y=2)
            pygame.draw.rect(screen, LIGHT_RED if end_hovered else SURFACE, self.end_quiz_button, border_radius=20)
            end_surf = render_crisp_text("Ukončit", 18, RED if end_hovered else TEXT_SUB, 100, is_bold=True)
            screen.blit(end_surf, end_surf.get_rect(center=self.end_quiz_button.center))

        elif self.state == "END":
            end_surf = render_crisp_text("Výborně!", 68, TEXT_DARK, w - 100, is_bold=True)
            screen.blit(end_surf, end_surf.get_rect(center=(w // 2, h // 4 - 20)))

            m = self.elapsed_seconds // 60
            s = self.elapsed_seconds % 60
            cas_text = f"Čas: {m:02d}:{s:02d}"

            score_surf = render_crisp_text(f"{self.player_name}  |  Získané body: {self.score} / 18  |  {cas_text}", 34, PRIMARY, w - 100, is_bold=True)
            screen.blit(score_surf, score_surf.get_rect(center=(w // 2, h // 2 - 30)))

            uspesnost = int((self.score / 18) * 100)
            sub_surf = render_crisp_text(f"Celková úspěšnost: {uspesnost} %  (Správně napoprvé: {self.stats_correct} z 9)", 22, TEXT_SUB, w - 100)
            screen.blit(sub_surf, sub_surf.get_rect(center=(w // 2, h // 2 + 25)))

            btn_w, btn_h = 330, 65
            self.end_buttons = [
                {'rect': pygame.Rect(w // 2 - btn_w - 15, h - 200, btn_w, btn_h), 'text': "Hlavní menu"},
                {'rect': pygame.Rect(w // 2 + 15, h - 200, btn_w, btn_h), 'text': "Moje historie pokusů"}
            ]
            for btn in self.end_buttons:
                is_hovered = btn['rect'].collidepoint(mouse_pos)
                self.draw_modern_button(screen, btn['rect'], btn['text'], is_hovered, PRIMARY)

        elif self.state == "LEADERBOARD":
            title_surf = render_crisp_text(f"Historie Pokusů ({self.player_name})", 52, TEXT_DARK, w - 100, is_bold=True)
            screen.blit(title_surf, title_surf.get_rect(center=(w // 2, h // 6 - 10)))

            zaznamy, nejlepsi_pokus = nacti_osobni_historii(self.player_name)

            start_y = h // 4 + 25
            table_rect = pygame.Rect(w // 2 - 400, start_y - 25, 800, 470)

            draw_soft_shadow(screen, table_rect, radius=20)
            pygame.draw.rect(screen, SURFACE, table_rect, border_radius=20)

            if not zaznamy:
                emp_surf = render_crisp_text("Zatím žádné výsledky k zobrazení.", 26, TEXT_SUB, 500)
                screen.blit(emp_surf, emp_surf.get_rect(center=(w // 2, start_y + 60)))
            else:
                for i, zaznam in enumerate(zaznamy):
                    jmeno, skore, cas, pokus = zaznam
                    is_best = (zaznam == nejlepsi_pokus)

                    row_y = start_y + i * 55
                    if is_best:
                        best_bg = pygame.Rect(w // 2 - 385, row_y - 8, 770, 46)
                        pygame.draw.rect(screen, PRIMARY_LIGHT, best_bg, border_radius=12)

                    text_barva = PRIMARY if is_best else (TEXT_DARK if i < 3 else TEXT_SUB)

                    jmeno_text = f"Pokus číslo {pokus}"
                    if is_best:
                        jmeno_text += "   (NEJLEPŠÍ POKUS)"

                    row_surf = render_crisp_text(jmeno_text, 24, text_barva, 450, is_bold=is_best)

                    sc_t = f"{skore} / 18 bodů   |   Čas: {cas}s" if cas > 0 else f"{skore} / 18 bodů"
                    score_surf = render_crisp_text(sc_t, 24, text_barva, 300, is_bold=True)

                    screen.blit(row_surf, row_surf.get_rect(topleft=(w // 2 - 365, row_y)))
                    screen.blit(score_surf, score_surf.get_rect(topright=(w // 2 + 365, row_y)))

                    if i < len(zaznamy) - 1 and not is_best:
                        pygame.draw.line(screen, SHADOW, (w // 2 - 365, row_y + 44), (w // 2 + 365, row_y + 44), 1)

            self.leaderboard_buttons = [{'rect': pygame.Rect(w // 2 - 160, h - 85, 320, 50), 'text': "Zpět do Menu"}]
            is_hovered = self.leaderboard_buttons[0]['rect'].collidepoint(mouse_pos)
            self.draw_modern_button(screen, self.leaderboard_buttons[0]['rect'], self.leaderboard_buttons[0]['text'], is_hovered, GRAY_BTN)

game = Game()
clock = pygame.time.Clock()

while True:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            is_fullscreen = not is_fullscreen
            if is_fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            else:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.DOUBLEBUF)
        game.handle_input(event)

    game.update(dt)
    game.draw()
    pygame.display.flip()
