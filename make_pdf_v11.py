from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Register Inter font ───────────────────────────────────────
# Font files are loaded from the uploads directory.
# Change these paths if running locally.
FONT_DIR = "."
pdfmetrics.registerFont(TTFont("Inter",      f"{FONT_DIR}/Inter_Regular.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Bold", f"{FONT_DIR}/Inter-Bold.ttf"))

# ── Font aliases — single point of control ────────────────────
BODY_FONT = "Inter"
BOLD_FONT = "Inter-Bold"

OUTPUT = "Claude_AI_Study_Notes_Final_v11.pdf"

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=15*mm,  bottomMargin=16*mm,
)
W, H = A4
DW = doc.width

# ── Palette ───────────────────────────────────────────────────
BLACK     = colors.black
DARK      = colors.HexColor("#0d0c1e")
ACCENT    = colors.HexColor("#2e5490")
ACCENT2   = colors.HexColor("#c4860e")
MID       = colors.HexColor("#1e1d38")
LIGHT_BG  = colors.HexColor("#e4ebf5")   # slightly more saturated alt-row tint
RULE_CLR  = colors.HexColor("#7888a8")
C_GREEN   = colors.HexColor("#1E6B3F")   # rich forest green — LOW
C_RED     = colors.HexColor("#8B1C2E")   # deep dark red — HIGH (visually heavy/serious)
C_ORANGE  = colors.HexColor("#FF8C00")   # brighter, more contrast
BG_GREEN  = colors.HexColor("#c0ecd8")
BG_ORANGE = colors.HexColor("#fde0b0")
BG_RED    = colors.HexColor("#f5c8cc")
BG_BLUE   = colors.HexColor("#cce0f8")
BG_SOFT   = colors.HexColor("#d4e4fc")
BG_AMBER  = colors.HexColor("#ffe070")

def S(name, **kw):
    return ParagraphStyle(name, **kw)

# ── Type scale — Inter throughout ────────────────────────────
# Inter is a modern humanist sans-serif designed for screen readability.
# All content styles use pure black; only decorative/cover elements use colour.
sTitle    = S("T",  fontName=BOLD_FONT, fontSize=28,   textColor=colors.white,  alignment=TA_CENTER, leading=34, spaceAfter=0)
sSubtitle = S("St", fontName=BODY_FONT, fontSize=12,   textColor=colors.HexColor("#dde8fc"), alignment=TA_CENTER, leading=17, spaceAfter=0)
sMeta     = S("Me", fontName=BODY_FONT, fontSize=9,    textColor=colors.HexColor("#b0c0d8"), alignment=TA_CENTER, leading=13, spaceAfter=0)
sH1       = S("H1", fontName=BOLD_FONT, fontSize=13,   textColor=colors.white,  leading=18, spaceAfter=0, spaceBefore=0)
sH2       = S("H2", fontName=BOLD_FONT, fontSize=11.5, textColor=ACCENT,        leading=16, spaceAfter=7, spaceBefore=8)
sH3       = S("H3", fontName=BOLD_FONT, fontSize=10.5, textColor=BLACK,         leading=15, spaceAfter=4, spaceBefore=5)

# Body / bullets: Inter 10.5pt, pure black — leading = fontSize * 1.55 ≈ 17
sBody   = S("Bo", fontName=BODY_FONT, fontSize=10.7, textColor=BLACK, leading=17.5, spaceAfter=6, alignment=TA_JUSTIFY)
sBullet = S("Bu", fontName=BODY_FONT, fontSize=10.7, textColor=BLACK, leading=17.5, spaceAfter=5, leftIndent=14)

# Table header + cells: Inter, pure black, 10pt leading 16
sTHdr  = S("TH",  fontName=BOLD_FONT, fontSize=9.5,  textColor=colors.white, alignment=TA_CENTER, leading=13)
sTC    = S("TC",  fontName=BODY_FONT, fontSize=10.2,   textColor=BLACK,        leading=16.5)
sTCB   = S("TCB", fontName=BOLD_FONT, fontSize=10,   textColor=BLACK,        leading=16)

sCallout = S("Ca", fontName=BOLD_FONT, fontSize=10.5, textColor=colors.HexColor("#0a0920"), leading=16, alignment=TA_CENTER)
sTocL    = S("TL", fontName=BOLD_FONT, fontSize=10.5, textColor=ACCENT,  leading=16)
sTocR    = S("TR", fontName=BODY_FONT, fontSize=10.5, textColor=BLACK,   leading=16)
sFoot    = S("Fo", fontName=BODY_FONT, fontSize=9,    textColor=BLACK,   alignment=TA_CENTER)

# Risk pills — clearly distinct colours, bold Inter, white text, generous padding
# HIGH: dark red (#8B1C2E) — feels heavy and serious
# MEDIUM: bright orange (#E67E22) — warm and visually very different from red
# LOW: forest green (#1E6B3F) — clean positive signal
sRISK = {
    "HIGH":   S("RH", fontName=BOLD_FONT, fontSize=9.5, textColor=colors.white, backColor=C_RED,    alignment=TA_CENTER, leading=12, borderPadding=(5,6,5,6)),
    "MEDIUM": S("RM", fontName=BOLD_FONT, fontSize=9.5, textColor=colors.white, backColor=C_ORANGE, alignment=TA_CENTER, leading=12, borderPadding=(5,6,5,6)),
    "LOW":    S("RL", fontName=BOLD_FONT, fontSize=9.5, textColor=colors.white, backColor=C_GREEN,  alignment=TA_CENTER, leading=12, borderPadding=(5,6,5,6)),
}

# ── Helpers ───────────────────────────────────────────────────
def sp(h=6):  return Spacer(1, h)
def hr(c=RULE_CLR, t=0.7):
    return HRFlowable(width="100%", thickness=t, color=c, spaceBefore=2, spaceAfter=6)

def bullet(text): return Paragraph(f"\u2022\u2002{text}", sBullet)
def cell(t):      return Paragraph(t, sTC)
def bcell(t):     return Paragraph(t, sTCB)
def hdr(*cols):   return [Paragraph(c, sTHdr) for c in cols]

def section_start(num, title):
    banner = Table([[Paragraph(f"{num}.  {title}", sH1)]], colWidths=[DW])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), ACCENT),
        ("TOPPADDING",    (0,0),(-1,-1), 9),
        ("BOTTOMPADDING", (0,0),(-1,-1), 9),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
    ]))
    return [PageBreak(), banner, sp(9)]

def callout_box(text, bg=LIGHT_BG, border=ACCENT):
    t = Table([[Paragraph(text, sCallout)]], colWidths=[DW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
        ("LINEBEFORE",    (0,0),(0,-1),  4, border),
        ("LINEAFTER",     (0,0),(0,-1),  4, border),
        ("LINEABOVE",     (0,0),(-1,0),  0.6, RULE_CLR),
        ("LINEBELOW",     (0,-1),(-1,-1),0.6, RULE_CLR),
    ]))
    return [sp(4), t, sp(6)]

def std_table(rows, widths, pad=11):
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
        ("GRID",          (0,0),(-1,-1), 0.5, RULE_CLR),
        ("TOPPADDING",    (0,0),(-1,-1), pad),
        ("BOTTOMPADDING", (0,0),(-1,-1), pad),
        ("LEFTPADDING",   (0,0),(-1,-1), 11),
        ("RIGHTPADDING",  (0,0),(-1,-1), 11),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t

# ═════════════════════════════════════════════════════════════
story = []

# ── COVER ─────────────────────────────────────────────────────
def banner_table(content, bg, tp=0, bp=0):
    t = Table([[content]], colWidths=[DW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("TOPPADDING",    (0,0),(-1,-1), tp),
        ("BOTTOMPADDING", (0,0),(-1,-1), bp),
    ]))
    return t

story.append(banner_table(Paragraph("CLAUDE AI", sTitle), DARK, tp=34, bp=10))
story.append(banner_table(Paragraph("Practical Notes, Uses, Limitations &amp; Workflow", sSubtitle), MID, tp=9, bp=9))
story.append(banner_table(Paragraph("Internship Study Notes  \u00b7  Day 1  \u00b7  April 2026", sMeta), colors.HexColor("#0a0918"), tp=6, bp=6))
story.append(sp(14))

story.append(Paragraph(
    "These notes summarise everything you need to know about Claude AI as a practical, "
    "professional tool. Written in plain English and suitable for daily revision.",
    sBody))
story.append(sp(3))
story.append(hr(ACCENT, 1.8))

# ── TOC ───────────────────────────────────────────────────────
story.append(Paragraph("Contents",
    S("TH2", fontName=BOLD_FONT, fontSize=12, textColor=ACCENT, spaceAfter=6, spaceBefore=4)))

toc_items = [
    ("1.",  "What is Claude?"),
    ("2.",  "What Claude Does Well"),
    ("3.",  "Claude's Weaknesses"),
    ("4.",  "Trust vs Verify"),
    ("5.",  "Best Prompt Techniques"),
    ("6.",  "Common User Mistakes"),
    ("7.",  "Real Use Cases"),
    ("8.",  "Daily Workflow"),
    ("9.",  "Key Things to Remember"),
    ("10.", "Day 1 Internship Learning Summary"),
]
toc_rows = [[Paragraph(n, sTocL), Paragraph(t, sTocR)] for n, t in toc_items]
toc_t = Table(toc_rows, colWidths=[16*mm, DW-16*mm])
toc_t.setStyle(TableStyle([
    ("TOPPADDING",    (0,0),(-1,-1), 3),
    ("BOTTOMPADDING", (0,0),(-1,-1), 3),
    ("LINEBELOW",     (0,0),(-1,-1), 0.4, RULE_CLR),
]))
story.append(toc_t)

# ═══════════════════════════════════════════════════════
# S1 — WHAT IS CLAUDE?
# ═══════════════════════════════════════════════════════
story += section_start("1", "What is Claude?")

story.append(Paragraph(
    "Claude is an AI assistant created by <b>Anthropic</b>, an AI safety company. "
    "Its design prioritises honesty, calibrated uncertainty, and helpfulness — it aims to "
    "push back when appropriate rather than simply agreeing. Claude expresses uncertainty "
    "openly rather than guessing with false confidence.",
    sBody))
story.append(sp(7))

story.append(Paragraph("Model and Version", sH2))
story.append(Paragraph(
    "The Claude 4 family includes Sonnet and Opus tiers. The model available to you depends "
    "on your platform, plan, and configuration. Anthropic releases updates regularly — "
    "check Anthropic's documentation for the latest model information.",
    sBody))
story.append(sp(7))

story.append(Paragraph("Key Technical Facts", sH2))
tech_rows = [
    hdr("Feature", "How it works"),
    [bcell("Knowledge cutoff"),  cell("Training has a cutoff date. Claude may not know recent events. Enable web search for current information.")],
    [bcell("Session memory"),    cell("Not retained between separate conversations by default. Some platforms support memory features — check your environment.")],
    [bcell("Internet access"),   cell("Not available by default. Web search can be enabled as a tool in supported environments such as Claude.ai.")],
    [bcell("Code execution"),    cell("Standard Claude does not run code. Certain platform configurations may support this — check if enabled.")],
    [bcell("Image generation"),  cell("Not a native capability in standard Claude. Image generation may be available in specific integrations.")],
]
story.append(std_table(tech_rows, [44*mm, DW-44*mm]))
story.append(sp(7))
story += callout_box(
    "Claude is a reasoning and writing tool — not a search engine, fact database, or substitute for professional expertise.",
    bg=BG_BLUE, border=ACCENT)

# ═══════════════════════════════════════════════════════
# S2 — WHAT CLAUDE DOES WELL
# ═══════════════════════════════════════════════════════
story += section_start("2", "What Claude Does Well")

story.append(Paragraph(
    "Claude performs consistently well across the following tasks. "
    "These strengths are most reliable when given clear context, specific constraints, and a well-defined task.",
    sBody))
story.append(sp(7))

strengths = [
    ("Writing and Editing",       "Cover letters, emails, reports, essays, press releases. Consistently Claude's strongest area."),
    ("Tone and Style Matching",   "Rewrites content to match a specific voice, register, or audience with precision."),
    ("Explaining Complex Topics", "Breaks down difficult concepts into clear, plain language without oversimplifying."),
    ("Code Understanding",        "Reads code, identifies logical errors, explains what went wrong, and suggests fixes."),
    ("Document Analysis",         "Reads long pasted documents and answers specific questions about them accurately."),
    ("Brainstorming",             "Generates ideas, options, angles, and frameworks you may not have considered."),
    ("Structuring Information",   "Organises scattered thoughts into coherent outlines, plans, and structured sections."),
    ("Summarising",               "Extracts key points from long content quickly and accurately."),
    ("Research Synthesis",        "When given source material to work with, compares, contrasts, and summarises well."),
    ("Interview Preparation",     "Asks practice questions, evaluates answers honestly, and suggests improvements."),
    ("First Drafts",              "Produces solid first versions of almost any written document quickly."),
    ("Thought Partnership",       "Challenges assumptions, finds weak points in arguments, and stress-tests reasoning."),
]
rows = [hdr("Capability", "What it means in practice")]
for cap, desc in strengths:
    rows.append([bcell(cap), cell(desc)])
story.append(std_table(rows, [52*mm, DW-52*mm]))

# ═══════════════════════════════════════════════════════
# S3 — WEAKNESSES
# ═══════════════════════════════════════════════════════
story += section_start("3", "Claude's Weaknesses")

story.append(Paragraph(
    "Claude can generate text that sounds accurate and well-reasoned but contains factual errors. "
    "This is called <b>hallucination</b> — a known limitation of language models. "
    "Claude's confident tone does not indicate that a claim is correct. "
    "Understanding these weaknesses is essential for using Claude safely.",
    sBody))
story.append(sp(7))

weaknesses = [
    ("Hallucination",        "Can generate plausible-sounding but inaccurate facts, names, or figures.",                                                   "HIGH"),
    ("Unverified citations", "May produce references that appear credible but have not been verified. Always check independently.",                         "HIGH"),
    ("Knowledge cutoff",     "Unaware of events after its training cutoff. May present outdated information as current.",                                   "HIGH"),
    ("Session memory",       "Does not retain information between separate sessions unless a memory feature is enabled.",                                   "HIGH"),
    ("Cannot run code",      "In standard mode, Claude cannot execute code. Output must be tested independently.",                                         "MEDIUM"),
    ("Over-caution",         "May add unnecessary caveats or decline requests that are genuinely harmless.",                                               "MEDIUM"),
    ("Context drift",        "In very long conversations, early instructions can be deprioritised or forgotten.",                                          "MEDIUM"),
    ("Inconsistency",        "The same prompt in a new session may produce a somewhat different response.",                                                "LOW"),
    ("Assumption-filling",   "When instructions are vague, Claude makes assumptions to complete the task — which may not match what was intended.",         "MEDIUM"),
]
rows3 = [hdr("Weakness", "What it means in practice", "Risk")]
for wk, desc, risk in weaknesses:
    rows3.append([bcell(wk), cell(desc), Paragraph(risk, sRISK[risk])])

# Risk column 24 mm — accommodates 9pt Inter-Bold "MEDIUM" without wrapping
t3 = Table(rows3, colWidths=[40*mm, DW-64*mm, 24*mm])
t3.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
    ("GRID",          (0,0),(-1,-1), 0.5, RULE_CLR),
    ("TOPPADDING",    (0,0),(-1,-1), 9),
    ("BOTTOMPADDING", (0,0),(-1,-1), 9),
    ("LEFTPADDING",   (0,0),(-1,-1), 11),
    ("RIGHTPADDING",  (0,0),(-1,-1), 11),
    ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ("ALIGN",         (2,0),(2,-1),  "CENTER"),
]))
story.append(t3)
story.append(sp(7))
story += callout_box(
    "Confident phrasing from Claude does not mean the information is accurate. Always verify specific facts, numbers, and sources.",
    bg=BG_RED, border=C_RED)

# ═══════════════════════════════════════════════════════
# S4 — TRUST VS VERIFY
# ═══════════════════════════════════════════════════════
story += section_start("4", "Trust vs Verify")

story.append(Paragraph(
    "Use this framework to decide when to act on Claude's output directly "
    "and when to verify it with an independent source first.",
    sBody))
story.append(sp(7))

def mk_trust_hdr(txt):
    s = S("tth", fontName=BOLD_FONT, fontSize=10, textColor=colors.white,
          alignment=TA_CENTER, leading=14)
    return Paragraph(txt, s)

def trust_col_table(items_str, sep_color):
    item_s = S("tci", fontName=BODY_FONT, fontSize=10, textColor=BLACK,
               leading=16, leftIndent=4, spaceAfter=0)
    lines  = [i.strip() for i in items_str.split("\n\n") if i.strip()]
    rows   = [[Paragraph(f"\u2022  {ln}", item_s)] for ln in lines]
    inner  = Table(rows, colWidths=[DW/3 - 6*mm])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 3),
        ("RIGHTPADDING",  (0,0),(-1,-1), 3),
        ("LINEBELOW",     (0,0),(-1,-2), 0.5, sep_color),
    ]))
    return inner

g_items = "Writing, editing, rewording\n\nExplaining concepts clearly\n\nBrainstorming and ideation\n\nStructuring information\n\nIdentifying code logic errors\n\nFirst drafts of any document"
o_items = "Newly generated code\n\nSynthesis of pasted sources\n\nGeneral knowledge claims\n\nSalary and market data\n\nIndustry-specific advice"
r_items = "Specific statistics or figures\n\nAny citation or reference\n\nLegal guidance\n\nMedical information\n\nFinancial advice\n\nCurrent or live information\n\nProduction-ready code"

col = DW / 3
trust_t = Table([
    [mk_trust_hdr("TRUST\nHigh Confidence"),
     mk_trust_hdr("VERIFY\nMedium Confidence"),
     mk_trust_hdr("NEVER USE ALONE\nLow Confidence")],
    [trust_col_table(g_items, colors.HexColor("#70aa88")),
     trust_col_table(o_items, colors.HexColor("#c09050")),
     trust_col_table(r_items, colors.HexColor("#b86070"))],
], colWidths=[col, col, col])
trust_t.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(0,0), C_GREEN),
    ("BACKGROUND",    (1,0),(1,0), C_ORANGE),
    ("BACKGROUND",    (2,0),(2,0), C_RED),
    ("BACKGROUND",    (0,1),(0,1), BG_GREEN),
    ("BACKGROUND",    (1,1),(1,1), BG_ORANGE),
    ("BACKGROUND",    (2,1),(2,1), BG_RED),
    ("BOX",           (0,0),(-1,-1), 1.2, RULE_CLR),
    ("LINEAFTER",     (0,0),(1,-1), 2.5,  colors.white),
    ("TOPPADDING",    (0,0),(-1,0),  10),
    ("BOTTOMPADDING", (0,0),(-1,0),  10),
    ("TOPPADDING",    (0,1),(-1,1),  12),
    ("BOTTOMPADDING", (0,1),(-1,1),  12),
    ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ("VALIGN",        (0,0),(-1,-1), "TOP"),
]))
story.append(trust_t)
story.append(sp(7))
story += callout_box(
    "Core rule: Trust Claude's thinking, structure, and writing. Verify Claude's facts, figures, and references.",
    bg=BG_SOFT, border=ACCENT)

story.append(sp(7))
story.append(KeepTogether([
    Paragraph("A Note on Citations and References", sH2),
    Paragraph(
        "Claude may produce references that sound credible but have not been independently verified. "
        "In some cases a cited source may be inaccurate, incomplete, or unverifiable. "
        "This is a known limitation of language models and does not mean every reference is wrong — "
        "but all references should be checked before use.",
        sBody),
    sp(4),
    bullet("Search for any source Claude mentions using Google, Google Scholar, or the publisher's website."),
    bullet("Only use a reference if you can confirm it exists and accurately supports the claim being made."),
    bullet("It is safer to ask Claude to explain a concept and then source supporting references yourself."),
]))

# ═══════════════════════════════════════════════════════
# S5 — PROMPT TECHNIQUES
# ═══════════════════════════════════════════════════════
story += section_start("5", "Best Prompt Techniques")

story.append(Paragraph(
    "The quality of Claude's output depends heavily on the quality of your instructions. "
    "A well-structured prompt consistently produces better, more useful responses.",
    sBody))
story.append(sp(7))

story.append(Paragraph("The Prompt Formula", sH2))
pf_data = [[
    Paragraph("CONTEXT",         sTHdr),
    Paragraph("+ TASK",          sTHdr),
    Paragraph("+ CONSTRAINTS",   sTHdr),
    Paragraph("+ FORMAT",        sTHdr),
    Paragraph("+ QUALITY CHECK", sTHdr),
]]
pf = Table(pf_data, colWidths=[DW/5]*5)
pf.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), ACCENT),
    ("GRID",          (0,0),(-1,-1), 0.5, colors.white),
    ("TOPPADDING",    (0,0),(-1,-1), 9),
    ("BOTTOMPADDING", (0,0),(-1,-1), 9),
    ("ALIGN",         (0,0),(-1,-1), "CENTER"),
]))
story.append(pf)
story.append(sp(8))

story.append(Paragraph("Example prompt:", sH3))
story.append(sp(4))

prompt_text = (
    "<b>Context:</b> I am a marketing student applying for a digital marketing internship.<br/><br/>"
    "<b>Task:</b> Write a 200-word cover letter for this job description: [paste JD here].<br/><br/>"
    "<b>Constraints:</b> Tone should be confident but not arrogant. "
    "Do not use the word 'passionate'.<br/><br/>"
    "<b>Format:</b> Return as a single clean paragraph.<br/><br/>"
    "<b>Quality check:</b> Tell me any assumptions you made about my background."
)
prompt_style = S("PS", fontName=BODY_FONT, fontSize=10.5, textColor=BLACK,
                 leading=18, spaceAfter=0, leftIndent=0)

prompt_box = Table([[Paragraph(prompt_text, prompt_style)]], colWidths=[DW])
prompt_box.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#e4eefa")),
    ("TOPPADDING",    (0,0),(-1,-1), 14),
    ("BOTTOMPADDING", (0,0),(-1,-1), 14),
    ("LEFTPADDING",   (0,0),(-1,-1), 16),
    ("RIGHTPADDING",  (0,0),(-1,-1), 16),
    ("LINEBEFORE",    (0,0),(0,-1),  5, ACCENT),
    ("LINEABOVE",     (0,0),(-1,0),  0.6, RULE_CLR),
    ("LINEBELOW",     (0,-1),(-1,-1),0.6, RULE_CLR),
    ("LINEAFTER",     (0,0),(-1,-1), 0.6, RULE_CLR),
]))
story.append(prompt_box)
story.append(sp(8))

story.append(Paragraph("Key Prompting Rules", sH2))
tips = [
    ("Be specific",               "Name the exact output you want. Vague questions produce generic answers."),
    ("Give context",              "Tell Claude who you are, what you are trying to do, and who the audience is."),
    ("Set constraints",           "Specify word count, tone, style, and what to avoid."),
    ("Ask for assumptions",       "End prompts with: 'Tell me what assumptions you made.' This helps catch errors early."),
    ("Plan before output",        "For complex tasks: 'Before writing, describe your approach.' Catch design problems early."),
    ("Ask for criticism",         "Say: 'Be critical. Do not tell me it is good unless it genuinely is.' Claude responds well to this."),
    ("Give examples",             "Paste a sample of the style or format you want. Claude is good at matching examples."),
    ("Break tasks into steps",    "Do not put everything into one massive prompt. Break it into clear stages."),
    ("Push back on weak answers", "If the first response is not useful, say so clearly and ask for a better version."),
]
for tip, desc in tips:
    story.append(bullet(f"<b>{tip}:</b> {desc}"))

# ═══════════════════════════════════════════════════════
# S6 — COMMON MISTAKES
# ═══════════════════════════════════════════════════════
story += section_start("6", "Common User Mistakes")

story.append(Paragraph(
    "These are the most frequent mistakes when working with Claude. "
    "Avoiding them significantly improves the quality and reliability of results.",
    sBody))
story.append(sp(7))

mistakes = [
    ("Asking a vague question and expecting a precise answer",
     "Claude needs specificity. The less detail you give, the more assumptions it makes."),
    ("Trusting specific statistics or figures without verifying",
     "Precise numbers are a high-risk area. Always verify figures against a primary source."),
    ("Copying Claude's output directly without reviewing it",
     "Claude's output is a starting point. Always read, check, and adapt before using."),
    ("Asking for current information without enabling web search",
     "Claude's training has a cutoff date. Enable web search for current information."),
    ("Using generated code without testing it",
     "Claude cannot run its own code. Always test in a safe environment before deploying."),
    ("Expecting Claude to remember a previous conversation",
     "Without a memory feature enabled, each session starts fresh. Re-provide context as needed."),
    ("Using Claude as the sole source for an important decision",
     "Claude is an input to your thinking — not a replacement for research or expert advice."),
    ("Asking Claude to add experience or qualifications that are not real",
     "Keep applications accurate. Misrepresentation is your responsibility, not Claude's."),
    ("Accepting the first response without refining",
     "Claude improves significantly with follow-up. Push back and request revisions."),
    ("Omitting technical context for coding tasks",
     "Always include language version, framework, OS, and library versions for accurate help."),
    ("Sending one enormous prompt for a complex task",
     "Break large tasks into stages. Quality drops when too many requirements are bundled together."),
    ("Pasting a summary instead of the original document",
     "Claude works better with the full text. Summaries lose detail that Claude needs."),
]
for title, desc in mistakes:
    story.append(bullet(f"<b>{title}:</b> {desc}"))

# ═══════════════════════════════════════════════════════
# S7 — USE CASES
# ═══════════════════════════════════════════════════════
story += section_start("7", "Real Use Cases")

story.append(Paragraph(
    "Step-by-step guidance for the six primary use cases covered in this session. "
    "Each section ends with what to always verify yourself.",
    sBody))
story.append(sp(7))

use_cases = [
    ("Job Applications", [
        "Paste the full job description and your CV together in the same prompt.",
        "Ask Claude to identify gaps between what the employer wants and what your profile shows.",
        "Ask for a tailored cover letter with explicit tone, length, and structure instructions.",
        "Add: 'Tell me any assumptions you made about my background.' Then correct any inaccuracies.",
        "Use Claude for mock interview practice — ask it to question you and give honest feedback.",
        "Never ask Claude to invent qualifications or experience you do not have.",
        "<b>Always verify:</b> Every factual claim, date, job title, and achievement before submitting.",
    ]),
    ("Resume Editing", [
        "Paste your full resume along with your target role and industry.",
        "Ask for a cold audit: 'What is weak, generic, or missing from this resume?'",
        "Rewrite bullet points using the XYZ formula: Accomplished X, measured by Y, by doing Z.",
        "Request strong action verbs at the start of each bullet. Avoid: 'Responsible for', 'Helped with'.",
        "Ask Claude to match language to a specific job description for ATS optimisation.",
        "<b>Always verify:</b> Every date, title, company name, metric, and factual detail before sending.",
    ]),
    ("Coding and Debugging", [
        "Paste the exact, complete error message — not a paraphrase.",
        "Paste the relevant code block alongside the error.",
        "State your environment: language version, framework, OS, and library versions.",
        "Ask Claude to explain what the error means before suggesting a fix.",
        "Ask: 'What else could break because of this fix?' before implementing.",
        "Always test Claude's fix yourself in a safe environment first.",
        "<b>Never</b> copy Claude's code into a production environment without independent testing.",
    ]),
    ("Research", [
        "Use Claude to understand a topic conceptually — not to source verified facts.",
        "Ask: 'What are the key debates in this field?' or 'What questions should I be asking?'",
        "Do your own sourcing — find real articles, studies, and reports independently.",
        "Paste those sources into Claude and ask it to compare, contrast, and identify patterns.",
        "Treat any reference Claude provides as a lead to investigate, not a confirmed source.",
        "<b>Always verify:</b> Every source Claude mentions before citing it anywhere.",
    ]),
    ("Automation", [
        "Describe what you want to automate in plain English before asking for any code.",
        "Ask Claude to explain the approach and flag potential risks before writing the script.",
        "Specify your OS, preferred language, and any tools already in use.",
        "Ask for error handling and logging to be included — Claude will not add these unless asked.",
        "Test any script on dummy or sample data before running it on real files.",
        "<b>Always review</b> every line of an automation script before executing it on live data.",
    ]),
    ("Media and Press Research", [
        "Press releases: provide key facts and ask Claude to draft — this is a strong area.",
        "Media pitches: specify the publication type, target audience, and news hook clearly.",
        "Coverage analysis: paste articles in and ask Claude to identify the dominant narrative.",
        "Crisis communications: Claude can draft holding statements and prep you for difficult questions.",
        "Do not ask Claude for current journalist contacts or live news without web search enabled.",
        "<b>Always verify:</b> Any claims about publications, journalists, or current events before acting.",
    ]),
]
for title, points in use_cases:
    story.append(KeepTogether([
        Paragraph(title, sH2),
    ] + [bullet(p) for p in points] + [sp(6)]))

# ═══════════════════════════════════════════════════════
# S8 — DAILY WORKFLOW
# ═══════════════════════════════════════════════════════
story += section_start("8", "Daily Workflow")

story.append(Paragraph(
    "A practical five-step workflow for using Claude effectively as a professional tool every day.",
    sBody))
story.append(sp(7))

steps = [
    ("Morning — Prioritise",
     "Paste your task list into Claude. Ask: 'Which tasks require the most careful thinking? What would you prioritise?' Use this to plan your session."),
    ("Research Phase",
     "Ask Claude for a conceptual overview. Do your own sourcing from authoritative references. Paste those sources back into Claude for synthesis and comparison."),
    ("Drafting",
     "Use Claude for first drafts of emails, proposals, documents, reports, and code comments. Always read and adapt the output before using it."),
    ("Review Pass",
     "Paste your own draft back in. Ask: 'What is weak? What is missing? What would make this fail?' Use Claude as a critical reviewer."),
    ("Before Sending or Shipping",
     "Conduct a human review of anything consequential. Claude's output is a high-quality starting point, not a finished product."),
]
num_s = S("wn", fontName=BOLD_FONT, fontSize=14, textColor=ACCENT,
          alignment=TA_CENTER, leading=17)
wf_rows = [hdr("#", "Step", "What to do")]
for i, (step, desc) in enumerate(steps, 1):
    wf_rows.append([Paragraph(str(i), num_s), bcell(step), cell(desc)])

wft = Table(wf_rows, colWidths=[11*mm, 48*mm, DW-59*mm])
wft.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
    ("GRID",          (0,0),(-1,-1), 0.5, RULE_CLR),
    ("TOPPADDING",    (0,0),(-1,-1), 10),
    ("BOTTOMPADDING", (0,0),(-1,-1), 10),
    ("LEFTPADDING",   (0,0),(-1,-1), 11),
    ("RIGHTPADDING",  (0,0),(-1,-1), 11),
    ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ("ALIGN",         (0,0),(0,-1),  "CENTER"),
]))
story.append(wft)
story.append(sp(11))

story.append(Paragraph("When to Use a Different AI Tool", sH2))
story.append(Paragraph(
    "Claude, ChatGPT, and Gemini each have different strengths. "
    "Using the best tool for each task gives better results than relying on any single platform.",
    sBody))
story.append(sp(6))

switch_data = [
    ("Writing, editing, reasoning, analysis",       "Claude",                           "Generally the strongest option for text, structure, and nuanced reasoning."),
    ("Running and testing code",                     "ChatGPT (Code Interpreter)",       "Executes code natively and shows live output — a key practical advantage."),
    ("Image generation",                             "ChatGPT or Gemini",                "Claude does not natively generate images; other platforms commonly offer this."),
    ("Google Docs, Gmail, Sheets integration",       "Gemini",                           "Native integration with the Google Workspace ecosystem."),
    ("Video and audio processing",                   "Gemini",                           "Generally better suited for Google's media formats."),
    ("Real-time web research",                       "Claude (search on) or Perplexity", "Claude supports web search when the tool is enabled in your environment."),
    ("Long document analysis",                       "Claude",                           "Handles large context windows with strong comprehension and follow-through."),
    ("Privacy considerations",                       "Review each platform's policy",    "Data handling varies by platform, plan, and region. Always check the current privacy policy of whichever tool you use before sharing sensitive information."),
]
sw_rows = [hdr("Task", "Often Best Option", "Notes")]
for task, tool, reason in switch_data:
    sw_rows.append([cell(task), bcell(tool), cell(reason)])

st = Table(sw_rows, colWidths=[56*mm, 42*mm, DW-98*mm])
st.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
    ("BACKGROUND",    (1,1),(1,-1),  colors.HexColor("#d8e8f8")),
    ("GRID",          (0,0),(-1,-1), 0.5, RULE_CLR),
    ("LINEAFTER",     (0,0),(0,-1),  1.2, RULE_CLR),
    ("LINEAFTER",     (1,0),(1,-1),  1.2, RULE_CLR),
    ("TOPPADDING",    (0,0),(-1,-1), 9),
    ("BOTTOMPADDING", (0,0),(-1,-1), 9),
    ("LEFTPADDING",   (0,0),(-1,-1), 11),
    ("RIGHTPADDING",  (0,0),(-1,-1), 11),
    ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ("ALIGN",         (1,1),(1,-1),  "CENTER"),
]))
story.append(st)
story.append(sp(7))
story += callout_box(
    "Use Claude to think and write. Use the best available tool for each specific task. These platforms work well in combination.",
    bg=LIGHT_BG, border=ACCENT)

# ═══════════════════════════════════════════════════════
# S9 — KEY THINGS TO REMEMBER
# ═══════════════════════════════════════════════════════
story += section_start("9", "Key Things to Remember")

story.append(KeepTogether([
    Paragraph("Always Do These", sH2),
    sp(4),
    bullet("Give Claude full context — paste the complete document, full error message, or entire job description."),
    bullet("Specify your constraints — word count, tone, audience, format, and what to avoid."),
    bullet("Ask Claude to state its assumptions at the end of every important output."),
    bullet("Push back if the first answer is not strong enough. Ask for a revised version."),
    bullet("Verify every specific fact, statistic, and reference independently."),
    bullet("Test all code Claude produces before using it in any real environment."),
    bullet("Treat Claude's output as a first draft — always review it before using."),
    sp(9),
]))

story.append(KeepTogether([
    Paragraph("Never Do These", sH2),
    sp(4),
    bullet("Use a citation Claude provides without independently verifying it exists and is accurate."),
    bullet("Copy Claude's code directly into a production system without testing and review."),
    bullet("Submit a document or application based solely on Claude's output without fact-checking."),
    bullet("Make legal, medical, or financial decisions from Claude's output without professional advice."),
    bullet("Ask Claude to add qualifications, experience, or achievements that are not genuinely yours."),
    bullet("Treat Claude's first response as final — it is a draft, not a conclusion."),
    bullet("Assume Claude has access to current information without confirming web search is enabled."),
    bullet("Run automation scripts on live data without testing on dummy data first."),
    sp(9),
]))

story.append(Paragraph("Quick Reference — Essential Facts", sH2))
story.append(sp(4))
facts = [
    ("Created by",          "Anthropic — an AI safety company"),
    ("Model family",        "Claude 4 (Sonnet and Opus tiers — availability depends on platform and plan)"),
    ("Knowledge cutoff",    "Training data has a cutoff date — very recent events may not be known"),
    ("Session memory",      "Not retained by default — some platforms offer memory features"),
    ("Web access",          "Not available by default — can be enabled as a tool in supported environments"),
    ("Code execution",      "Not standard — available in certain platform configurations"),
    ("Image generation",    "Not a native capability — use other tools for this"),
    ("Biggest risk",        "Hallucination — confident-sounding but potentially inaccurate output"),
    ("Biggest strength",    "Writing, reasoning, explaining, structuring, and critical analysis"),
    ("Best prompt formula", "Context + Task + Constraints + Format + Quality Check"),
]
fk_s = S("fk", fontName=BOLD_FONT, fontSize=10, textColor=ACCENT, leading=15)
fact_rows = [[Paragraph(k, fk_s), cell(v)] for k, v in facts]
ft = Table(fact_rows, colWidths=[50*mm, DW-50*mm])
ft.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0,0),(-1,-1), [colors.white, LIGHT_BG]),
    ("GRID",           (0,0),(-1,-1), 0.5, RULE_CLR),
    ("TOPPADDING",     (0,0),(-1,-1), 9),
    ("BOTTOMPADDING",  (0,0),(-1,-1), 9),
    ("LEFTPADDING",    (0,0),(-1,-1), 11),
    ("RIGHTPADDING",   (0,0),(-1,-1), 11),
]))
story.append(ft)

# ═══════════════════════════════════════════════════════
# S10 — DAY 1 SUMMARY
# ═══════════════════════════════════════════════════════
story += section_start("10", "Day 1 Internship Learning Summary")

story.append(Paragraph("What Was Covered in This Session", sH2))
story.append(sp(4))
covered = [
    "What Claude is, how it was designed, and what Anthropic's approach to AI safety means in practice.",
    "Claude's core strengths — writing, editing, explaining, brainstorming, code understanding, and document analysis.",
    "Claude's key limitations — hallucination, session memory, knowledge cutoff, and inconsistency.",
    "A structured framework for deciding when to trust Claude and when to verify its output.",
    "How to write effective prompts using the Context + Task + Constraints + Format + Quality Check formula.",
    "Practical step-by-step workflows for six real use cases: job applications, resume editing, coding, research, automation, and press work.",
    "When to use Claude versus other tools such as ChatGPT and Gemini.",
    "A five-step daily professional workflow for getting the most from Claude.",
]
for c in covered:
    story.append(bullet(c))

story.append(sp(11))
story.append(Paragraph("The Most Important Lessons from Today", sH2))
story.append(sp(4))
lessons = [
    "Prompt quality determines output quality. The more specific and contextual your prompt, the better the result.",
    "Confident phrasing from Claude does not mean the information is accurate. Verify facts independently.",
    "Claude is most valuable as a first-draft engine and thinking partner — not as a definitive source of truth.",
    "The right workflow is: Claude helps draft and structure \u2192 you review and verify \u2192 you make the final decision.",
    "No single AI tool does everything well. Claude, ChatGPT, and Gemini each complement each other.",
]
for l in lessons:
    story.append(bullet(l))

story.append(sp(11))

sum_hdr_t = Table([[Paragraph(
    "The Single Most Important Lesson from Day 1",
    S("sh", fontName=BOLD_FONT, fontSize=11.5, textColor=DARK, alignment=TA_CENTER, leading=16)
)]], colWidths=[DW])
sum_hdr_t.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), ACCENT2),
    ("TOPPADDING",    (0,0),(-1,-1), 12),
    ("BOTTOMPADDING", (0,0),(-1,-1), 12),
]))

sum_body_t = Table([[Paragraph(
    "Claude is a powerful reasoning and writing tool.\n"
    "It is not a source of verified truth.\n"
    "Use it to think, structure, and draft.\n"
    "Then verify, review, and decide for yourself.",
    S("sb", fontName=BODY_FONT, fontSize=11.5, textColor=BLACK, alignment=TA_CENTER, leading=19)
)]], colWidths=[DW])
sum_body_t.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), BG_AMBER),
    ("TOPPADDING",    (0,0),(-1,-1), 16),
    ("BOTTOMPADDING", (0,0),(-1,-1), 16),
    ("LINEBELOW",     (0,-1),(-1,-1), 2.5, ACCENT2),
]))
story.append(sum_hdr_t)
story.append(sum_body_t)

story.append(sp(14))
story.append(hr())
story.append(Paragraph(
    "Claude AI \u2013 Practical Notes, Uses, Limitations, and Workflow  \u00b7  Internship Study Notes  \u00b7  April 2026",
    sFoot))

# ── BUILD ──────────────────────────────────────────────────────
doc.build(story)
print("Done:", OUTPUT)
