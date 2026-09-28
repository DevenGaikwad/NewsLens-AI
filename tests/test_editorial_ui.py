"""Static contracts for the NewsLens AI editorial interface."""

from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_local_editorial_assets_exist_and_are_attributed() -> None:
    for relative in [
        "assets/logo.svg",
        "assets/editorial_masthead.svg",
        "assets/ATTRIBUTIONS.md",
    ]:
        path = ROOT / relative
        assert path.exists()
        assert path.stat().st_size > 100


def test_masthead_title_stays_inside_its_black_banner() -> None:
    root = ET.parse(ROOT / "assets/editorial_masthead.svg").getroot()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    title = next(
        node
        for node in root.findall(".//svg:text", namespace)
        if "".join(node.itertext()) == "THE NEWS INTELLIGENCE DESK"
    )
    banner = next(
        node
        for node in root.findall(".//svg:rect", namespace)
        if node.attrib.get("x") == "35" and node.attrib.get("y") == "38"
    )
    title_left = float(title.attrib["x"])
    title_right = title_left + float(title.attrib["textLength"])
    banner_left = float(banner.attrib["x"])
    banner_right = banner_left + float(banner.attrib["width"])
    assert title_left - banner_left >= 20
    assert banner_right - title_right >= 20
    assert title.attrib["lengthAdjust"] == "spacingAndGlyphs"


def test_theme_contains_required_warm_design_tokens() -> None:
    theme = read("ui/theme.py")
    for token in [
        "--paper-primary: #F3F0E8",
        "--paper-secondary: #EAE4D8",
        "--editorial-brown: #6D5947",
        "--charcoal: #1A1917",
        "--success-muted: #496454",
        "--warning-muted: #8A693D",
        "--danger-muted: #813F39",
    ]:
        assert token in theme


def test_theme_uses_only_approved_editorial_palette() -> None:
    theme = read("ui/theme.py").lower()
    for excluded in ["#00d4ff", "#7c5cfc", "glassmorphism", "space grotesk"]:
        assert excluded not in theme


def test_navigation_exposes_every_working_page() -> None:
    router = read("app.py")
    navigation = read("ui/navigation.py")
    components = read("ui/components.py")
    for page in [
        "pages\" / \"00_News_Desk.py",
        "pages\" / \"01_Analyse_Article.py",
        "pages\" / \"02_Model_Performance.py",
        "pages\" / \"03_Dataset_EDA.py",
        "pages\" / \"04_Analysis_History.py",
        "pages\" / \"05_Research_About.py",
    ]:
        assert page in router
    assert "st.navigation(PAGES, position=\"top\")" in router
    assert "st.page_link(" in components
    runtime_navigation = "\n".join([router, navigation, components])
    assert "target=\"_blank\"" not in runtime_navigation
    assert "window.open" not in runtime_navigation
    assert "href=\"./" not in runtime_navigation


def test_every_page_uses_the_shared_editorial_shell() -> None:
    expected = {
        "pages/00_News_Desk.py": 'active="home"',
        "pages/01_Analyse_Article.py": 'active="analyse"',
        "pages/02_Model_Performance.py": 'active="performance"',
        "pages/03_Dataset_EDA.py": 'active="eda"',
        "pages/04_Analysis_History.py": 'active="history"',
        "pages/05_Research_About.py": 'active="about"',
    }
    for relative, active in expected.items():
        source = read(relative)
        assert "configure_page(" in source
        assert active in source
    analysis = read("pages/01_Analyse_Article.py")
    archive = read("pages/04_Analysis_History.py")
    assert "session_history_path()" in analysis
    assert "path=history_database" in archive


def test_interface_keeps_responsible_prediction_language() -> None:
    analysis = read("pages/01_Analyse_Article.py")
    archive = read("pages/04_Analysis_History.py")
    components = read("ui/components.py")
    config = read("src/config.py")
    about = read("pages/05_Research_About.py")
    assert "Reference comparison ·" in components
    assert "REFERENCE_AGREEMENT_OUTCOME" in components
    assert "REFERENCE_CONFLICT_OUTCOME" in components
    assert "Independent editorial verification remains necessary" in analysis
    assert "Editorial review required" in config
    assert "reference-comparison confidence" in components
    assert "Fields agree - calibrated probability" in config
    assert "Fields conflict - calibrated probability" in config
    assert "It is not factual certainty" in config
    assert "What do these scores mean?" in analysis
    assert "What do these scores mean?" in archive
    assert "cannot do" in about
    assert "Important disclaimer" in about


def test_public_ui_uses_punctuation_free_tagline_and_concise_authorship() -> None:
    home = read("pages/00_News_Desk.py")
    components = read("ui/components.py")
    theme = read("ui/theme.py")
    web_layout = read("web/app/layout.tsx")
    assert '"News intelligence\\nWith scope intact"' in home
    assert "News intelligence," not in home
    assert "scope intact." not in home
    assert "hero-title-line" in components
    assert "hero-title-line" in theme
    assert "Designed and developed by" in components
    assert "PUBLIC_AUTHOR" in components
    assert "PROJECT_AUTHOR" not in components
    assert "Designed and developed by Deven Gaikwad" in web_layout
    assert "© 2026 · All rights reserved" in web_layout


def test_tablet_hero_stacks_only_outer_columns_and_wraps_title() -> None:
    components = read("ui/components.py")
    theme = read("ui/theme.py")
    tablet = theme.split("@media (max-width: 900px) {", 1)[1].split(
        "@media (max-width: 560px) {", 1
    )[0]
    mobile = theme.split("@media (max-width: 560px) {", 1)[1]
    outer = (
        '.st-key-nl_hero > [data-testid="stLayoutWrapper"] > '
        '[data-testid="stHorizontalBlock"]'
    )
    assert 'with st.container(key="nl_hero"):' in components
    assert 'st.columns([1.18, 0.82]' in components
    assert 'key="nl_hero_actions",' in components
    assert f"{outer} {{\n    flex-direction: column;" in tablet
    assert (
        f'{outer} > [data-testid="stColumn"] {{\n'
        "    flex: 1 1 auto;\n    width: 100%;\n    min-width: 0;"
    ) in tablet
    assert ".hero-title-line {\n    white-space: normal;" in tablet
    assert '.st-key-nl_hero_actions [data-testid="stPageLink-NavLink"]' in mobile


def test_public_ui_removes_publication_banner_and_named_private_dataset() -> None:
    public_sources = "\n".join(
        read(relative)
        for relative in [
            "pages/00_News_Desk.py",
            "pages/01_Analyse_Article.py",
            "pages/02_Model_Performance.py",
            "pages/03_Dataset_EDA.py",
            "pages/04_Analysis_History.py",
            "pages/05_Research_About.py",
            "ui/components.py",
            "ui/theme.py",
            "web/app/page.tsx",
            "web/app/layout.tsx",
        ]
    )
    assert "Publication status" not in public_sources
    assert "ISOT" not in public_sources
    assert "Outside supported comparison scope" in public_sources
    assert "Not reported" in public_sources
