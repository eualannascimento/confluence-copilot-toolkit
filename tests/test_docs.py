from pathlib import Path
ROOT = Path(__file__).parents[1]
def test_required_docs_exist():
    assert (ROOT / "README.md").exists()
    assert (ROOT / "examples" / "minimal-request.md").exists()
    assert (ROOT / "docs" / "PERMISSIONS.md").exists()
    assert (ROOT / "LICENSE").exists()
