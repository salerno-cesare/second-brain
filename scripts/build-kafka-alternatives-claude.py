# -*- coding: utf-8 -*-
"""Kafka alternatives deck - built directly with python-pptx (no template,
full creative freedom on visual design). Content mirrors
reports/kafka-alternatives-slides.md, redesigned as clean cards/diagrams
instead of plain bullet lists."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

OUT = r"reports\kafka-alternatives-claude.pptx"
LOGO_DARK = r"reports\assets\ntt-logo-dark.png"   # for light-background slides
LOGO_LIGHT = r"reports\assets\ntt-logo-light.png"  # for navy/dark-background slides
LOGO_ASPECT = 116 / 400

# ---------------------------------------------------------------- palette --
NAVY = RGBColor(0x0B, 0x1F, 0x3A)
NAVY2 = RGBColor(0x12, 0x2B, 0x4F)
INK = RGBColor(0x11, 0x18, 0x27)
MUTED = RGBColor(0x64, 0x74, 0x8B)
ACCENT = RGBColor(0x25, 0x63, 0xEB)
TEAL = RGBColor(0x06, 0xB6, 0xD4)
AMBER = RGBColor(0xF5, 0x9E, 0x0B)
GOOD = RGBColor(0x16, 0xA3, 0x4A)
BAD = RGBColor(0xDC, 0x26, 0x26)
BG = RGBColor(0xF7, 0xF9, 0xFC)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xE2, 0xE8, 0xF0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Segoe UI"
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def add_logo(slide, light=False, w=1.0):
    h = w * LOGO_ASPECT
    x = 12.78 - w
    y = 7.5 - 0.30 - h
    path = LOGO_LIGHT if light else LOGO_DARK
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))


def new_slide(bg=BG):
    s = prs.slides.add_slide(BLANK)
    rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    rect.fill.solid()
    rect.fill.fore_color.rgb = bg
    rect.line.fill.background()
    rect.shadow.inherit = False
    _send_to_back(s, rect)
    add_logo(s, light=(bg == NAVY))
    return s


def _send_to_back(slide, shape):
    spTree = slide.shapes._spTree
    spTree.remove(shape._element)
    spTree.insert(2, shape._element)


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.0, round_=False, shadow=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    if round_:
        try:
            sh.adjustments[0] = 0.06
        except Exception:
            pass
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    return sh


def oval(slide, x, y, d, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.25)
    sh.shadow.inherit = False
    return sh


def text(slide, x, y, w, h, s, size=14, color=INK, bold=False, italic=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=FONT, line_spacing=None,
         wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    if line_spacing:
        p.line_spacing = line_spacing
    r = p.add_run()
    r.text = s
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font
    return box


def bulleted(slide, x, y, w, h, lines, size=13, color=INK, dot_color=ACCENT,
             gap=8, anchor=MSO_ANCHOR.TOP, bold_lines=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        r_dot = p.add_run()
        r_dot.text = u"\u25CF  "
        r_dot.font.size = Pt(size - 2)
        r_dot.font.color.rgb = dot_color
        r_dot.font.name = FONT
        r_txt = p.add_run()
        r_txt.text = line
        r_txt.font.size = Pt(size)
        r_txt.font.color.rgb = color
        r_txt.font.name = FONT
        r_txt.font.bold = bool(bold_lines and i in bold_lines)
    return box


def line(slide, x1, y1, x2, y2, color=NAVY, weight=1.5, arrow=False, dash=None):
    conn = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(weight)
    if arrow:
        ln = conn.line._get_or_add_ln()
        tail = ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
        ln.append(tail)
    if dash:
        ln = conn.line._get_or_add_ln()
        d = ln.makeelement(qn('a:prstDash'), {'val': dash})
        ln.append(d)
    conn.shadow.inherit = False
    return conn


def set_dash(shape, val="dash"):
    ln = shape.line._get_or_add_ln()
    d = ln.makeelement(qn('a:prstDash'), {'val': val})
    ln.append(d)


def header(slide, kicker, title, subtitle=None, badge_letter=None, badge_color=ACCENT):
    if badge_letter:
        oval(slide, 0.55, 0.42, 0.62, badge_color)
        text(slide, 0.55, 0.42, 0.62, 0.62, badge_letter, size=22, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        tx = 1.35
    else:
        tx = 0.55
    if kicker:
        text(slide, tx, 0.38, 11.5, 0.3, kicker.upper(), size=12, color=ACCENT, bold=True)
        ty = 0.68
    else:
        ty = 0.42
    text(slide, tx, ty, 11.6, 0.55, title, size=26, color=NAVY, bold=True)
    if subtitle:
        text(slide, tx, ty + 0.56, 11.6, 0.4, subtitle, size=14, color=MUTED, italic=True)
    line(slide, 0.55, 1.55, 12.78, 1.55, color=BORDER, weight=1.0)
    footer(slide)


def footer(slide):
    text(slide, 0.55, 7.12, 6, 0.3, "Legacy Data Bridge - Pilot Apache Flink", size=9, color=MUTED)


def card(slide, x, y, w, h, accent_color, kicker, lines, kicker_bg=None, size=12.5):
    rect(slide, x, y, w, h, fill=CARD, line=BORDER, line_w=1.0, round_=True)
    rect(slide, x, y, 0.09, h, fill=accent_color, round_=False)
    text(slide, x + 0.28, y + 0.16, w - 0.5, 0.32, kicker, size=13, color=accent_color, bold=True)
    bulleted(slide, x + 0.28, y + 0.58, w - 0.5, h - 0.78, lines, size=size, color=INK,
             dot_color=accent_color, gap=7)


# ============================================================= SLIDE 1 ====
s = new_slide(bg=NAVY)
oval(s, 10.4, -2.2, 6.2, NAVY2)
oval(s, 11.7, 4.6, 4.4, NAVY2)
rect(s, 0.75, 2.55, 0.55, 0.10, fill=TEAL)
text(s, 0.75, 2.85, 11.5, 0.35, "ALTERNATIVE A KAFKA - PILOT LEGACY DATA BRIDGE", size=14,
     color=TEAL, bold=True)
text(s, 0.75, 3.25, 11.6, 1.5, "Ridurre il costo della coda,\nsenza perdere scalabilita e semplicita",
     size=34, color=WHITE, bold=True)
text(s, 0.75, 4.85, 10.8, 0.5, "Sette opzioni a confronto per il Pilot Apache Flink su Kubernetes",
     size=16, color=RGBColor(0xC7, 0xD4, 0xE8))
panel = rect(s, 0.75, 5.55, 11.83, 1.55, fill=NAVY2, round_=True)
bulleted(s, 1.05, 5.75, 11.2, 1.2, [
    "Il Pilot riceve eventi CDC che vivono sulla coda solo pochi istanti, prima di essere consumati da Flink.",
    "Oggi il flusso passa da AWS MSK: affidabile, ma troppo costoso per questo volume di messaggi.",
    "Qualsiasi alternativa deve restare compatibile con Debezium/Kafka Connect, i connettori Flink e Splunk.",
], size=12.5, color=RGBColor(0xE5, 0xEC, 0xF7), dot_color=TEAL, gap=6)

# ============================================================= SLIDE 2 ====
s = new_slide()
header(s, "Metodo", "Criteri di valutazione", "Come confrontiamo le sette opzioni")
criteria = [
    ("Costo", GOOD, "Non solo il broker: anche compute, storage, traffico in uscita e tempo del team dedicato alla gestione."),
    ("Scalabilita", ACCENT, "Il volume di eventi CDC puo crescere: serve poter scalare orizzontalmente senza ripensare l'architettura."),
    ("Semplicita operativa", TEAL, "Operator maturi, upgrade prevedibili e osservabilita pronta all'uso, senza richiedere nuove competenze."),
    ("Compatibilita", AMBER, "Protocollo Kafka, Debezium e connettori Flink: da questo dipende quanto lavoro di migrazione servira."),
    ("Affidabilita", RGBColor(0x7C, 0x3A, 0xED), "Durabilita, replica e semantica di consegna, almeno at-least-once."),
    ("Footprint", RGBColor(0x0D, 0x94, 0x88), "Risorse extra richieste oltre a JobManager e ai due TaskManager gia previsti."),
]
cx, cy, cw, ch, gx, gy = 0.55, 1.65, 3.95, 2.55, 0.19, 0.25
for i, (title_, color_, body) in enumerate(criteria):
    col = i % 3
    row = i // 3
    x = cx + col * (cw + gx)
    y = cy + row * (ch + gy)
    rect(s, x, y, cw, ch, fill=CARD, line=BORDER, line_w=1.0, round_=True)
    rect(s, x, y, cw, 0.09, fill=color_)
    text(s, x + 0.22, y + 0.24, cw - 0.4, 0.35, title_, size=15, color=NAVY, bold=True)
    text(s, x + 0.22, y + 0.68, cw - 0.44, ch - 0.9, body, size=11.5, color=MUTED)

# ================================================== OPTION SLIDES 3-8 =====
DIAGRAM_Y = 1.65
DIAGRAM_H = 1.05


def option_slide(letter, title_, subtitle_, nodes, broker_idx, pro_lines, con_lines,
                  direct_mode=False):
    s = new_slide()
    header(s, f"Opzione {letter}", title_, subtitle_, badge_letter=letter,
           badge_color=ACCENT if not direct_mode else TEAL)

    # ---- flow diagram ----
    n = len(nodes)
    x0, x1 = 0.55, 12.78
    box_w = 2.35 if n == 3 else 1.72
    gap = ((x1 - x0) - n * box_w) / (n - 1)
    xs = [x0 + i * (box_w + gap) for i in range(n)]
    mid_y = DIAGRAM_Y + DIAGRAM_H / 2

    for i, label in enumerate(nodes):
        is_broker = (i == broker_idx)
        fill_ = RGBColor(0xFF, 0xF3, 0xD9) if is_broker else CARD
        border_ = AMBER if is_broker else BORDER
        bw = 2.2 if (direct_mode and i == 1) else 2.0
        rect(s, xs[i], DIAGRAM_Y, box_w, DIAGRAM_H, fill=fill_, line=border_,
             line_w=2.2 if is_broker else 1.0, round_=True)
        text(s, xs[i] + 0.05, DIAGRAM_Y + 0.30, box_w - 0.1, 0.4, label, size=12.5,
             color=NAVY if not is_broker else RGBColor(0x92, 0x64, 0x0E), bold=True,
             align=PP_ALIGN.CENTER)
        if is_broker:
            text(s, xs[i], DIAGRAM_Y + DIAGRAM_H + 0.05, box_w, 0.22, "CODA / BROKER",
                 size=8.5, color=AMBER, bold=True, align=PP_ALIGN.CENTER)

    if direct_mode:
        # ghost box where the queue used to be: dashed outline, no fill, no crossing lines
        gx0 = xs[0] + box_w
        gx1 = xs[1]
        gw = gx1 - gx0
        pad = 0.18
        gxc, gwc = gx0 + pad, gw - 2 * pad
        ghost = rect(s, gxc, DIAGRAM_Y, gwc, DIAGRAM_H, fill=None, line=MUTED, line_w=1.25, round_=True)
        set_dash(ghost)
        text(s, gxc, DIAGRAM_Y + 0.38, gwc, 0.3, "nessuna coda", size=9.5, color=MUTED,
             bold=True, align=PP_ALIGN.CENTER, italic=True)
        line(s, xs[0] + box_w, mid_y, xs[1], mid_y, color=ACCENT, weight=3.0, arrow=True)
        text(s, xs[0] + box_w, DIAGRAM_Y + DIAGRAM_H + 0.05, gw, 0.22, "DIRETTO - NO BROKER",
             size=8.5, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)
        line(s, xs[1] + box_w, mid_y, xs[2], mid_y, color=NAVY, weight=1.5, arrow=True)
    else:
        for i in range(n - 1):
            line(s, xs[i] + box_w, mid_y, xs[i + 1], mid_y, color=NAVY, weight=1.5, arrow=True)

    # ---- pro / con cards ----
    card_y = DIAGRAM_Y + DIAGRAM_H + 0.55
    card_h = 7.02 - card_y
    card_w = (12.78 - 0.55 - 0.24) / 2
    card(s, 0.55, card_y, card_w, card_h, GOOD, "Perche sceglierla", pro_lines, size=12.5)
    card(s, 0.55 + card_w + 0.24, card_y, card_w, card_h, AMBER, "Attenzione a", con_lines, size=12.5)
    return s


option_slide(
    "A", "AWS MSK (baseline attuale)", "Kafka managed su AWS",
    ["SQL Server", "Debezium Connect", "AWS MSK", "Flink (EKS)", "Aurora PG"], 2,
    pro_lines=[
        "AWS MSK e la versione Kafka completamente gestita da Amazon: patching, alta disponibilita e integrazione IAM/PrivateLink a carico del provider.",
        "Il team infrastrutturale non deve occuparsi della gestione dei broker; l'integrazione con il resto dell'ecosistema AWS e naturale.",
        "Resta un'opzione sensata se in futuro servissero SLA molto stringenti con un team infrastrutturale piccolo.",
    ],
    con_lines=[
        "Il costo e alto: si pagano i nodi broker in tripla replica, lo storage EBS e il traffico cross-AZ, anche a bassi volumi.",
        "Per messaggi CDC che vivono sulla coda pochi secondi, questo costo fisso e sproporzionato rispetto al valore che offre.",
        "Non e la scelta piu efficiente per il Pilot attuale.",
    ],
)

option_slide(
    "B", "Strimzi (Kafka self-managed su EKS)", "Stesso Kafka, gestito con operator Kubernetes",
    ["SQL Server", "Debezium Connect", "Kafka Strimzi", "Flink (EKS)", "Aurora PG"], 2,
    pro_lines=[
        "Kafka gira sul cluster EKS gia esistente, gestito da un operator Kubernetes invece che da un servizio cloud a pagamento.",
        "Debezium e i connettori Flink restano invariati: zero refactor, zero licenze aggiuntive.",
        "Gestione dichiarativa via CRD (Kafka, KafkaTopic, KafkaUser) con upgrade rolling automatici.",
    ],
    con_lines=[
        "Il team infrastrutturale si assume broker, consenso KRaft/ZooKeeper e tuning JVM: un lavoro prima delegato ad AWS.",
        "Si paga solo compute EKS + storage, con un risparmio stimato del 50-70% rispetto a MSK.",
        "Effort di setup medio, che si riduce a regime grazie all'operator.",
    ],
)

option_slide(
    "C", "Redpanda (Kafka-compatible, senza JVM)", "Broker C++ single-binary, protocollo Kafka nativo",
    ["SQL Server", "Debezium Connect", "Redpanda Operator", "Flink (EKS)", "Aurora PG"], 2,
    pro_lines=[
        "Riscrive il broker Kafka in C++, eliminando JVM e ZooKeeper, ma mantenendo piena compatibilita con l'API Kafka.",
        "Bastano circa un terzo delle risorse di un broker Kafka tradizionale, con latenze piu basse e meno tuning.",
        "La Community Edition (BSL) e open source e piu che sufficiente per i volumi del Pilot.",
    ],
    con_lines=[
        "Ecosistema piu piccolo di Kafka: alcune feature enterprise (tiered storage, RBAC avanzato) sono a pagamento.",
        "La maggiore densita dei broker permette pero di usare meno nodi EKS, abbassando ulteriormente il costo.",
        "Effort basso: operator semplice e documentazione lineare.",
    ],
)

option_slide(
    "D", "NATS JetStream", "Messaging leggero cloud-native, non Kafka",
    ["SQL Server", "Debezium Server", "NATS JetStream", "Flink (EKS)", "Aurora PG"], 2,
    pro_lines=[
        "Abbandona il protocollo Kafka per un pub/sub nativo cloud: singolo binario Go, footprint minimo (<100 MB RAM/nodo).",
        "Scaling orizzontale semplice, replica RAFT integrata e retention ideale per messaggi a vita brevissima.",
        "Operativita quotidiana molto semplice, con osservabilita Prometheus nativa.",
    ],
    con_lines=[
        "Non parla Kafka: serve sostituire il sink Debezium e la sorgente Flink con connettori nuovi.",
        "Ecosistema CDC meno maturo: spesso richiede un connettore custom o Debezium Server.",
        "Costo minimo della lista, ma effort di migrazione alto (gestione poi molto semplice).",
    ],
)

option_slide(
    "E", "RabbitMQ Cluster Operator (opzionale)", "Message broker maturo, protocollo AMQP",
    ["SQL Server", "Debezium Connect", "RabbitMQ Operator", "Flink (EKS)", "Aurora PG"], 2,
    pro_lines=[
        "Broker maturo su AMQP, distribuibile su EKS con il Cluster Operator ufficiale.",
        "Il plugin Streams introduce code append-only vicine alla semantica Kafka, con retention breve.",
        "Buona scelta per messaggi transitori, gestione semplice tramite custom resource.",
    ],
    con_lines=[
        "Non compatibile Kafka: richiede comunque un refactoring di Debezium e dei connettori Flink.",
        "Su volumi molto alti il throughput resta inferiore a Kafka o Redpanda.",
        "Costo basso e footprint contenuto, ma sforzo medio per riscrivere i connettori.",
    ],
)

option_slide(
    "F", "Connessione diretta, nessuna coda in mezzo", "Flink CDC Connector con Debezium embedded",
    ["SQL Server", "Flink CDC Connector", "Aurora PG"], None,
    pro_lines=[
        "Il connettore Flink CDC integra un motore Debezium nel job stesso e legge il transaction log senza alcun broker intermedio.",
        "Costo minimo assoluto: nessuna infrastruttura di messaggistica da gestire o pagare.",
        "Architettura essenziale: meno componenti da monitorare, meno hop di rete, latenza end-to-end piu bassa.",
    ],
    con_lines=[
        "Nessun disaccoppiamento: un rallentamento di Flink scarica pressione diretta sul transaction log di SQL Server.",
        "Nessun fan-out: un solo consumer per stream, niente replay indipendente ne piu consumatori.",
        "Il lag di coda sparisce dall'osservabilita; adatto solo a flussi non critici e a basso volume.",
    ],
    direct_mode=True,
)

option_slide(
    "G", "Amazon Kinesis Data Streams", "Streaming AWS-native, alternativa gestita ma non Kafka",
    ["SQL Server", "Debezium (Kinesis sink)", "Kinesis Data Streams", "Flink (EKS)", "Aurora PG"], 2,
    pro_lines=[
        "Amazon Kinesis Data Streams e completamente gestito da AWS: nessun cluster da patchare, si paga solo per shard-hour e dati trasferiti.",
        "Il connettore Kinesis di Flink e maturo e nativo, e la retention (fino a 365 giorni) puo essere impostata bassa per messaggi CDC di vita breve.",
        "Puo costare meno di MSK a bassi volumi, perche non servono broker dedicati ma solo shard proporzionati al throughput.",
    ],
    con_lines=[
        "Non parla il protocollo Kafka: Debezium non scrive nativamente su Kinesis, serve un sink dedicato (Kafka Connect Kinesis o produttore custom).",
        "La capacita scala a shard: resharding e limiti di velocita richiedono pianificazione, e il fan-out avanzato per piu consumer ha un costo extra.",
        "Resta un servizio AWS a consumo: utile per chi vuole restare nell'ecosistema AWS, meno se l'obiettivo e uscire dai costi variabili cloud.",
    ],
)

# ============================================================= SLIDE 9 ====
s = new_slide()
header(s, "Sintesi", "Matrice di confronto", "Le sette opzioni fianco a fianco")

rows_data = [
    ("AWS MSK", "Alto", GOOD, "Molto basso", "Totale", "Si"),
    ("Strimzi su EKS", "Medio-basso", ACCENT, "Medio", "Totale", "Si"),
    ("Redpanda Operator", "Basso", ACCENT, "Basso", "Kafka API", "Si"),
    ("NATS JetStream", "Molto basso", GOOD, "Alto (migr.)", "Non-Kafka", "Si"),
    ("RabbitMQ Operator", "Basso", ACCENT, "Medio", "Non-Kafka", "Si"),
    ("Kinesis Data Streams", "Basso-medio", ACCENT, "Medio", "Non-Kafka", "Si"),
    ("Connessione diretta (F)", "Minimo", GOOD, "Alto (migr.)", "No broker", "No"),
]
headers = ["Opzione", "Costo", "Effort infra", "Compat. Kafka", "Disaccoppiamento"]
tx, ty, tw, th = 0.55, 1.65, 12.23, 4.50
rows = len(rows_data) + 1
cols = len(headers)
gtable = s.shapes.add_table(rows, cols, Inches(tx), Inches(ty), Inches(tw), Inches(th)).table
col_w = [3.2, 2.2, 2.4, 2.4, 2.03]
for i, w in enumerate(col_w):
    gtable.columns[i].width = Inches(w)
for c, htext in enumerate(headers):
    cell = gtable.cell(0, c)
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    cell.text_frame.paragraphs[0].text = htext
    r = cell.text_frame.paragraphs[0].runs[0]
    r.font.bold = True
    r.font.size = Pt(12.5)
    r.font.color.rgb = WHITE
    r.font.name = FONT
for ridx, row in enumerate(rows_data, start=1):
    name, cost, cost_color, effort, compat, decoupled = row
    values = [name, cost, effort, compat, decoupled]
    band = CARD if ridx % 2 else RGBColor(0xEE, 0xF2, 0xF8)
    for c, val in enumerate(values):
        cell = gtable.cell(ridx, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = band
        cell.text_frame.paragraphs[0].text = val
        r = cell.text_frame.paragraphs[0].runs[0]
        r.font.size = Pt(12)
        r.font.name = FONT
        r.font.color.rgb = cost_color if c == 1 else INK
        r.font.bold = (c == 1)

rect(s, 0.55, 6.20, 12.23, 0.78, fill=NAVY, round_=True)
text(s, 0.85, 6.36, 11.7, 0.5,
     "Miglior rapporto valore/rischio: Strimzi (quick win) o Redpanda (piu densita); "
     "la connessione diretta solo se il rischio di accoppiamento e accettabile.",
     size=13, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================ SLIDE 10 ====
s = new_slide()
header(s, "Piano d'azione", "Raccomandazione", "Percorso a due passi, piu un'opzione radicale")

steps = [
    ("1", "Quick win: Strimzi su EKS", "Stesso protocollo Kafka, nessun refactor Debezium/Flink: riduzione costi quasi immediata, sforzo concentrato nel setup iniziale."),
    ("2", "Evoluzione: Redpanda", "Stesso client Kafka, meno risorse, upgrade non piu disruptivi: da valutare per densificare ulteriormente i broker."),
]
step_y = 1.75
step_w = 5.85
for i, (num, title_, body) in enumerate(steps):
    x = 0.55 + i * (step_w + 0.3)
    oval(s, x, step_y, 0.62, ACCENT)
    text(s, x, step_y, 0.62, 0.62, num, size=22, color=WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.78, step_y + 0.02, step_w - 0.8, 0.4, title_, size=15, color=NAVY, bold=True)
    text(s, x + 0.78, step_y + 0.46, step_w - 0.8, 1.0, body, size=12, color=MUTED)
    if i == 0:
        line(s, x + 0.62, step_y + 0.31, x + step_w + 0.3, step_y + 0.31, color=BORDER, weight=2.0)

bulleted(s, 0.55, 3.35, 12.0, 2.3, [
    "NATS e RabbitMQ restano opzioni valide solo se in futuro si decidesse di uscire completamente dall'ecosistema Kafka.",
    "Kinesis Data Streams e un'alternativa da considerare se si vuole restare nell'ecosistema AWS senza gestire cluster, accettando un modello a consumo e un sink dedicato per Debezium.",
    "La connessione diretta (Opzione F) va considerata solo per flussi non critici e a basso volume, dove il costo zero della coda vale il rischio di accoppiamento con la sorgente.",
], size=13.5, color=INK, dot_color=AMBER, gap=9)

rect(s, 0.55, 6.20, 12.23, 0.78, fill=NAVY, round_=True)
text(s, 0.85, 6.36, 11.7, 0.5,
     "Prossima azione: PoC Strimzi nel namespace del Pilot | benchmark throughput/latenza | stima costi EKS",
     size=13, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================ SLIDE 11 ====
s = new_slide()
header(s, "Prossimi passi", "Dubbi aperti e verifiche necessarie", "Da confermare prima della decisione")

open_items = [
    "Volumi reali di eventi CDC al secondo e dimensione media dei messaggi.",
    "Retention richiesta, SLO di disponibilita del broker e vincoli di sicurezza/compliance (patching, audit).",
    "Compatibilita tra la versione di Debezium/Kafka Connect in uso e Redpanda.",
    "Costo effettivo su EKS: nodi dedicati o condivisi, storage EBS necessario.",
    "Integrazione del nuovo broker con l'osservabilita Splunk gia in uso.",
    "Per la connessione diretta: tolleranza al rischio di accoppiamento e capacita del transaction log SQL Server.",
]
y = 1.75
for i, item in enumerate(open_items):
    rowy = y + i * 0.78
    rect(s, 0.55, rowy, 0.32, 0.32, fill=None, line=ACCENT, line_w=1.75, round_=True)
    text(s, 1.05, rowy - 0.06, 11.4, 0.6, item, size=13.5, color=INK)

text(s, 0.55, 6.95, 12.2, 0.35, "Owner: Team Infrastruttura - Pilot Legacy Data Bridge MVP 1",
     size=10.5, color=MUTED, italic=True, align=PP_ALIGN.RIGHT)

prs.save(OUT)
print("Saved:", OUT, "-", len(prs.slides), "slides")
