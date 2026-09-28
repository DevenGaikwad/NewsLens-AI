"""Build compact GitHub SVGs from current source palette and recorded evidence."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/github"
P = {"paper": "#F3F0E8", "ivory": "#FAF8F2", "beige": "#EAE4D8", "warm": "#D8CCBA",
     "taupe": "#A89984", "coffee": "#6D5947", "deep": "#40352C", "charcoal": "#1A1917",
     "border": "#D4CEC2", "green": "#496454", "green_paper": "#E7ECE6",
     "amber": "#8A693D", "amber_paper": "#F1E9DA", "red": "#813F39", "red_paper": "#F1E2DF"}


def rect(x: int, y: int, w: int, h: int, fill: str = "ivory", stroke: str = "border", rx: int = 14) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{P.get(fill, fill)}" stroke="{P.get(stroke, stroke)}" stroke-width="2"/>'


def text(x: int, y: int, value: str, size: int = 20, *, color: str = "charcoal", serif: bool = False, weight: int = 400, anchor: str = "start") -> str:
    font = "Georgia, Times New Roman, serif" if serif else "Arial, Helvetica, sans-serif"
    return f'<text x="{x}" y="{y}" fill="{P.get(color, color)}" font-family="{font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'


def line(points: str, *, color: str = "coffee", arrow: bool = True) -> str:
    end = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<polyline points="{points}" fill="none" stroke="{P[color]}" stroke-width="3" stroke-linejoin="round"{end}/>'


def document(name: str, width: int, height: int, title: str, desc: str, parts: list[str]) -> None:
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="{P['coffee']}"/></marker></defs>
{rect(1, 1, width-2, height-2, 'paper', 'border', 20)}
{''.join(parts)}
</svg>'''
    (OUT / name).write_text(content + "\n", encoding="utf-8")


def hero() -> None:
    parts = [rect(1, 1, 1198, 12, "deep", "deep", 0),
             rect(45, 64, 104, 104, "ivory", "deep", 7),
             '<path d="M68 89h56 M68 105h56 M68 121h38" stroke="#6D5947" stroke-width="5"/>',
             '<circle cx="123" cy="135" r="19" fill="#EAE4D8" stroke="#40352C" stroke-width="5"/>',
             '<path d="M137 148l18 18" stroke="#40352C" stroke-width="6"/>',
             text(185, 109, "NEWSLENS AI", 48, serif=True, weight=700),
             text(185, 153, "Synthetic reference comparison · local article summarisation", 23, color="deep"),
             line("185,178 1120,178", arrow=False),
             text(185, 219, "Original fiction", 19, color="coffee", weight=700),
             text(420, 219, "Calibrated scope", 19, color="coffee", weight=700),
             text(665, 219, "Human review", 19, color="coffee", weight=700),
             text(895, 219, "Private session", 19, color="coffee", weight=700),
             text(45, 272, "ACADEMIC DEMONSTRATION  /  NOT GENERAL NEWS VERIFICATION", 16, color="deep", weight=700)]
    document("readme-hero.svg", 1200, 300, "NewsLens AI repository banner",
             "NewsLens AI: independently authored synthetic reference comparison and local article summarisation, with calibrated scope and human editorial review. No general news verification claim.", parts)


def runtime() -> None:
    parts = [text(52, 62, "Runtime processing and editorial accountability", 36, serif=True, weight=700),
             text(52, 94, "Two independent paths from one validated article", 18, color="coffee"),
             rect(52, 125, 510, 85), text(78, 160, "Input and safe extraction", 25, serif=True, weight=700),
             text(78, 188, "Paste · public URL · TXT · text PDF; clean and validate", 17),
             rect(640, 125, 510, 85), text(666, 160, "Supported input boundary", 25, serif=True, weight=700),
             text(666, 188, "Complete, unambiguous fictional field pair", 17),
             line("562,167 640,167"),
             rect(52, 260, 510, 185, "ivory", "coffee"),
             text(78, 303, "A · Independent summary", 25, serif=True, weight=700),
             text(78, 341, "TF-IDF centroid ranks original sentences", 18),
             text(78, 377, "Selected-length reading view", 18),
             rect(640, 260, 510, 185, "ivory", "coffee"),
             text(666, 303, "B · Reference comparison", 25, serif=True, weight=700),
             text(666, 341, "Visible field signals → synthetic linear model", 18),
             text(666, 377, "Bound Platt calibration → review policy", 18),
             text(666, 413, "Local explanation only when supported", 18),
             line("307,210 307,260"), line("895,210 895,260"),
             rect(52, 485, 735, 92, "beige", "coffee"),
             text(78, 517, "Editorial result and session-isolated archive", 23, serif=True, weight=700),
             text(78, 544, "Fields agree/conflict or review · JSON/PDF/CSV", 17),
             text(78, 569, "Privacy-safe aggregate analytics", 17),
             line("307,445 307,485"), line("895,445 895,466 705,466 705,485"),
             rect(826, 485, 324, 92, "amber_paper", "amber"),
             text(849, 518, "Offline only", 24, serif=True, weight=700),
             text(849, 547, "Training and evaluation", 18)]
    document("runtime-flow-landscape.svg", 1200, 620, "NewsLens AI runtime architecture",
             "Validated input branches into independent extractive summarisation and synthetic Reference comparison. The latter uses visible fields, a TF-IDF Logistic Regression model, bound Platt calibration, scope review and local explanation. Results support human review, exports, a session-isolated archive and privacy-safe aggregates. Training and evaluation are offline only.", parts)


def decisions() -> None:
    parts = [text(52, 62, "Application decision workflow", 36, serif=True, weight=700),
             text(52, 94, "A score is shown only within the supported comparison format", 18, color="coffee")]
    nodes = [
        (52, 134, 330, "1 · Validate input", "Safe extract and clean article"),
        (435, 134, 330, "2 · Summarise", "Independent reading view"),
        (818, 134, 330, "3 · Check scope", "Both complete field blocks?"),
        (52, 306, 330, "4 · Compare fields", "Synthetic linear classifier"),
        (435, 306, 330, "5 · Calibrate", "Bound Platt score and guard"),
        (818, 306, 330, "6 · Editorial outcome", "Agree / conflict / review"),
    ]
    for x,y,w,title,subtitle in nodes:
        parts.extend((rect(x,y,w,105), text(x+23,y+43,title,23,serif=True,weight=700), text(x+23,y+76,subtitle,17)))
    parts += [line("382,185 435,185"), line("765,185 818,185"),
              line("983,239 983,266 217,266 217,306"),
              line("382,357 435,357"), line("765,357 818,357"),
              rect(52, 463, 1096, 90, "beige", "coffee"),
              text(82, 501, "Review and result delivery", 23, serif=True, weight=700),
              text(82, 532, "Unsupported or ambiguous → score withheld; human review, exports, session-local archive.", 17),
              line("983,411 983,463"), line("1148,185 1170,185 1170,447 1090,447 1090,463")]
    document("decision-workflow.svg", 1200, 590, "NewsLens AI bounded decision workflow",
             "Validate and safely extract article input. Produce an independent summary. Check for two complete unambiguous fictional field blocks. Compare the visible fields with a synthetic linear model and bound Platt calibration. A supported outcome can say fields agree or conflict; missing, ambiguous, or discordant input is withheld for editorial review. Results are exportable and session-local.", parts)


def evidence() -> None:
    locked = json.loads((ROOT / "reports/results/model_metrics.json").read_text())
    challenge = json.loads((ROOT / "reports/results/phase5w_challenge.json").read_text())
    assert locked["confusion_matrix"] == [[600,0],[0,600]]
    assert challenge["confusion_matrix"] == [[22,0],[22,0]]
    parts = [text(50, 61, "Synthetic evidence: locked split and hard challenge", 32, serif=True, weight=700),
             text(50, 94, "Class order: fields agree, fields conflict · rows actual, columns predicted", 18, color="coffee")]
    cards = ((50, "Locked final test", "1,200 authored split rows", locked["confusion_matrix"]),
             (620, "Phase 5W unfamiliar challenge", "44 structured cases · 8 fictional events", challenge["confusion_matrix"]))
    for x,title,subtitle,matrix in cards:
        parts.extend((rect(x,125,530,360), text(x+26,166,title,26,serif=True,weight=700),
                      text(x+26,196,subtitle,17),
                      text(x+189,230,"PREDICTED",14,color="coffee",weight=700),
                      text(x+227,257,"Agree",15,anchor="middle"),text(x+388,257,"Conflict",15,anchor="middle"),
                      text(x+24,335,"ACTUAL",14,color="coffee",weight=700),
                      text(x+132,318,"Agree",15,anchor="middle"),text(x+132,408,"Conflict",15,anchor="middle")))
        for i in range(2):
            for j in range(2):
                fill = ("green_paper" if i==j else "red_paper") if x == 50 else ("green_paper" if i==j and matrix[i][j] else "red_paper" if i!=j and matrix[i][j] else "ivory")
                xx,yy=x+167+j*160, 273+i*90
                parts.extend((rect(xx,yy,140,78,fill,"border",8),text(xx+70,yy+49,str(matrix[i][j]),31,serif=True,weight=700,anchor="middle")))
    parts += [rect(50,510,1100,80,"amber_paper","amber"),
              text(75,543,"Phase 5W public automatic coverage: 14 / 44 structured cases (31.8%)",20,weight=700),
              text(75,573,"The guard reviews conflicting/ambiguous cases; perfect locked-test results do not imply wider reliability.",17)]
    document("readme-model-evidence.svg",1200,620,"NewsLens AI locked-test and challenge confusion matrices",
             "Side-by-side synthetic matrices with actual rows and predicted columns, class order agree then conflict. Locked final test on 1,200 in-distribution rows: 600 agreements and 600 conflicts correct. Unfamiliar Phase 5W challenge on 44 structured cases: 22 agreements correct, 22 conflicts incorrectly predicted as agreements. Public automatic decisions cover only 14 of those 44; remaining cases are sent to review. This is not real-world news validation.",parts)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    hero(); runtime(); decisions(); evidence()
    print("Created four compact, evidence-backed README SVGs.")
