"""Generate integration architecture and capability overview PNGs for the TFC deck."""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

OUT_DIR = Path(__file__).parent.parent / "reports" / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# WK / NTT DATA visual palette (approximated from the Unicredit deck)
C_AZURE_BG = "#E8F1FB"
C_AZURE_BORDER = "#1F5FA8"
C_WK_BG = "#EAF7EE"
C_WK_BORDER = "#0F8A3A"
C_ORCH = "#0D3B66"
C_ORCH_TEXT = "#FFFFFF"
C_COMPONENT = "#FFFFFF"
C_COMPONENT_BORDER = "#4C4C4C"
C_ACCENT = "#1F5FA8"
C_TEXT = "#1A1A1A"
C_MUTED = "#5A6672"


def _rounded_box(ax, x, y, w, h, *, fc, ec, lw=1.2, radius=0.03, zorder=2):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=zorder,
    )
    ax.add_patch(box)
    return box


def _text(ax, x, y, s, *, size=10, weight="normal", color=C_TEXT, ha="center", va="center", zorder=5):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va, zorder=zorder)


def _arrow(ax, x1, y1, x2, y2, *, color=C_ACCENT, lw=1.6, style="-|>", ls="-", zorder=4):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, mutation_scale=14,
        color=color, linewidth=lw, linestyle=ls, zorder=zorder,
    )
    ax.add_patch(arr)


def build_architecture_diagram(out_path: Path) -> None:
    """Slide 4 diagram: TCF on Azure <-> FAB Workspace in WK Legal Environment."""
    fig, ax = plt.subplots(figsize=(11.5, 7.8), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.set_axis_off()

    # === Left cloud: Azure (TCF customer environment) ===
    _rounded_box(ax, 2, 4, 44, 60, fc=C_AZURE_BG, ec=C_AZURE_BORDER, lw=1.6, radius=1.2, zorder=1)
    _text(ax, 24, 61, "Azure Cloud – Cliente TCF", size=13, weight="bold", color=C_AZURE_BORDER)
    _text(ax, 24, 58.4, "Ambiente privato e segregato", size=9, color=C_MUTED)

    # User (browser) at top-left of the customer env
    _rounded_box(ax, 5, 47, 15, 8, fc=C_COMPONENT, ec=C_COMPONENT_BORDER, radius=0.6)
    _text(ax, 12.5, 52.5, "Utente TCF", size=10, weight="bold")
    _text(ax, 12.5, 50, "Wizard / UI", size=8, color=C_MUTED)

    # TCF Application
    _rounded_box(ax, 24, 46, 18, 10, fc=C_COMPONENT, ec=C_COMPONENT_BORDER, radius=0.6)
    _text(ax, 33, 53.5, "TCF Application", size=10, weight="bold")
    _text(ax, 33, 51.2, "Tax Control Framework", size=8, color=C_MUTED)
    _text(ax, 33, 49.2, "• RCM  • Fattispecie  • Driver", size=8, color=C_MUTED)
    _text(ax, 33, 47.4, "• Documenti cliente (privati)", size=8, color=C_MUTED)

    # Arrow user -> tcf
    _arrow(ax, 20.2, 51, 23.8, 51, color=C_COMPONENT_BORDER, lw=1.3)

    # DB TCF
    _rounded_box(ax, 5, 33, 15, 8, fc=C_COMPONENT, ec=C_COMPONENT_BORDER, radius=0.6)
    _text(ax, 12.5, 38.5, "DB TCF", size=10, weight="bold")
    _text(ax, 12.5, 36, "Dati cliente cifrati", size=8, color=C_MUTED)

    # Storage documenti
    _rounded_box(ax, 24, 33, 18, 8, fc=C_COMPONENT, ec=C_COMPONENT_BORDER, radius=0.6)
    _text(ax, 33, 38.5, "Storage Documentale", size=10, weight="bold")
    _text(ax, 33, 36, "Strategie, pareri, big four", size=8, color=C_MUTED)

    # tcf app <-> DB, storage
    _arrow(ax, 21.2, 46, 15.5, 41, color=C_COMPONENT_BORDER, lw=1.1, style="<|-|>")
    _arrow(ax, 33, 46, 33, 41, color=C_COMPONENT_BORDER, lw=1.1, style="<|-|>")

    # TCF Integration Connector (bottom of Azure)
    _rounded_box(ax, 6, 15, 36, 12, fc="#DDEBFA", ec=C_AZURE_BORDER, lw=1.4, radius=0.6)
    _text(ax, 24, 24, "Integration Connector", size=11, weight="bold", color=C_AZURE_BORDER)
    _text(ax, 24, 21.2, "REST client + Auth (One ID Legal)", size=9, color=C_MUTED)
    _text(ax, 24, 18.8, "Standard I/O JSON per ogni caso d’uso", size=9, color=C_MUTED)
    _text(ax, 24, 16.5, "Data residency EU · GDPR / AI Act", size=8, color=C_MUTED)

    _arrow(ax, 33, 33, 33, 27.2, color=C_COMPONENT_BORDER, lw=1.2, style="<|-|>")

    # === Right cloud: WK Legal Environment (FAB) ===
    _rounded_box(ax, 54, 4, 44, 60, fc=C_WK_BG, ec=C_WK_BORDER, lw=1.6, radius=1.2, zorder=1)
    _text(ax, 76, 61, "WK Legal Environment – FAB", size=13, weight="bold", color=C_WK_BORDER)
    _text(ax, 76, 58.4, "Workspace dedicata One Fiscale", size=9, color=C_MUTED)

    # Orchestrator Agent
    _rounded_box(ax, 60, 46, 32, 11, fc=C_ORCH, ec=C_ORCH, radius=0.6)
    _text(ax, 76, 53.6, "Orchestrator Agent", size=11, weight="bold", color=C_ORCH_TEXT)
    _text(ax, 76, 50.8, "Routing per caso d’uso", size=8, color="#DCE7F5")
    _text(ax, 76, 48.6, "System prompt & fallback algoritmico", size=8, color="#DCE7F5")

    # Sub-agents row
    subs = [
        ("Gap\nAnalysis", 58.6),
        ("Driver\nAssistant", 65.6),
        ("Impact\nAnalysis", 72.6),
        ("Drafting\nAssistant", 79.6),
        ("Q&A\nContestuale", 88.4),
    ]
    widths = [5.6, 5.6, 5.6, 5.6, 8.6]
    for (label, cx), bw in zip(subs, widths):
        _rounded_box(ax, cx - bw / 2, 34, bw, 8.4, fc=C_COMPONENT, ec=C_WK_BORDER, radius=0.5)
        _text(ax, cx, 38.2, label, size=8, weight="bold", color=C_WK_BORDER)
        # link to orchestrator
        _arrow(ax, cx, 42.4, cx, 46, color=C_WK_BORDER, lw=1.0, style="-|>")

    # Periodic Briefing (separate lane)
    _rounded_box(ax, 60, 24, 32, 6.5, fc="#F5FBF7", ec=C_WK_BORDER, radius=0.5)
    _text(ax, 76, 27.2, "Periodic Briefing Job (mensile)", size=9, weight="bold", color=C_WK_BORDER)

    # FAB Indexes
    _rounded_box(ax, 60, 12, 15, 9, fc=C_COMPONENT, ec=C_WK_BORDER, radius=0.5)
    _text(ax, 67.5, 17.5, "Indice", size=9, weight="bold", color=C_WK_BORDER)
    _text(ax, 67.5, 15.5, "One Fiscale", size=9, color=C_TEXT)
    _text(ax, 67.5, 13.7, "(banca dati WK)", size=7, color=C_MUTED)

    _rounded_box(ax, 77, 12, 15, 9, fc=C_COMPONENT, ec=C_WK_BORDER, radius=0.5)
    _text(ax, 84.5, 17.5, "Indice", size=9, weight="bold", color=C_WK_BORDER)
    _text(ax, 84.5, 15.5, "TCF Cliente", size=9, color=C_TEXT)
    _text(ax, 84.5, 13.7, "(documenti privati)", size=7, color=C_MUTED)

    for cx in [67.5, 84.5]:
        _arrow(ax, cx, 21, cx, 24, color=C_WK_BORDER, lw=1.0, style="<|-|>")

    # === Cross-cloud secure link ===
    _arrow(ax, 42, 21, 54, 21, color=C_ACCENT, lw=2.2, style="<|-|>")
    _text(ax, 48, 23.4, "HTTPS · mTLS", size=9, weight="bold", color=C_ACCENT)
    _text(ax, 48, 18.6, "Private\nEndpoint", size=8, color=C_MUTED)

    # Legend footer
    _text(ax, 50, 1.5, "Dati cliente restano nell’Azure TCF · Nessuna condivisione con altri tenant WK", size=8, color=C_MUTED)

    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.15, facecolor="white")
    plt.close(fig)


def build_capability_matrix(out_path: Path) -> None:
    """Slide 3 supporting image: functional overview of the 6 AI use cases."""
    fig, ax = plt.subplots(figsize=(9.5, 6.4), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 62)
    ax.set_axis_off()

    cards = [
        ("Gap Analysis",
         "Confronta linee guida Ag. Entrate\ncon dati wizard cliente e segnala\ni rischi non mappati."),
        ("Driver Assistant",
         "Suggerisce probabilità, impatto\ne pesi dei driver in base al Tax\nCompliance Model del cliente."),
        ("Impact Analysis",
         "Individua i rischi della RCM\nimpattati da nuove norme,\ncircolari e prassi."),
        ("Drafting Assistant",
         "Aiuta a redigere fattispecie\ninterpretative (es. fusioni\ncross-border) con soglie e driver."),
        ("Q&A Contestuale",
         "Chatbot su corpus normativo\ne contesto cliente basato\nsulla banca dati One Fiscale."),
        ("Periodic Briefing",
         "Report mensile intelligente\ncon novità fiscali filtrate\nsu processi e rischi del cliente."),
    ]

    positions = [(x, y) for y in [36, 8] for x in [4, 36, 68]]
    for (label, desc), (x, y) in zip(cards, positions):
        _rounded_box(ax, x, y, 28, 22, fc="#F4F8FD", ec=C_AZURE_BORDER, lw=1.3, radius=0.7)
        _rounded_box(ax, x, y + 16.5, 28, 5.5, fc=C_AZURE_BORDER, ec=C_AZURE_BORDER, radius=0.7)
        _text(ax, x + 14, y + 19.1, label, size=11, weight="bold", color="#FFFFFF")
        _text(ax, x + 14, y + 8, desc, size=8.5, color=C_TEXT)

    _text(ax, 50, 2, "6 assistenti AI dedicati, orchestrati da un unico agente su FAB", size=9, color=C_MUTED)

    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.15, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    arch = OUT_DIR / "tfc_architecture.png"
    caps = OUT_DIR / "tfc_capabilities.png"
    build_architecture_diagram(arch)
    build_capability_matrix(caps)
    print(f"Wrote: {arch}")
    print(f"Wrote: {caps}")
