"""Headless smoke test of the group-internal Streamlit EDA app on real Canvas data."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
app = AppTest.from_file(str(ROOT / "eda_lab" / "app.py"), default_timeout=120)
app.run()
errors = list(app.exception)
if errors:
    raise AssertionError("Streamlit EDA raised exception(s): " + str(errors))
assert len(app.title) >= 1, "The EDA title did not render."
assert len(app.tabs) == 5, "The EDA should expose five exploration tabs."
print("EDA smoke test passed using the original Canvas PathMNIST data.")
