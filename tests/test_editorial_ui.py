"""Static contracts for the NewsLens AI editorial interface."""

from pathlib import Path


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
    components = read("ui/components.py")
    config = read("src/config.py")
    about = read("pages/05_Research_About.py")
    assert "Editorial risk signal" in components
    assert "Independent editorial verification remains necessary" in analysis
    assert "Editorial review required" in config
    assert "calibrated confidence" in components
    assert "cannot do" in about
    assert "Important disclaimer" in about
