import shutil
from pathlib import Path
from app import app

DEST = Path("docs")

PAGES = [
    ("/ko/",          "ko/index.html"),
    ("/en/",          "en/index.html"),
    ("/ko/resources", "ko/resources/index.html"),
    ("/en/resources", "en/resources/index.html"),
]

ROOT_REDIRECT = (
    '<!DOCTYPE html><html lang="ko"><head>'
    '<meta charset="utf-8">'
    '<meta http-equiv="refresh" content="0; url=/ko/">'
    '<link rel="canonical" href="/ko/">'
    '</head><body></body></html>'
)


def render(url: str) -> str:
    with app.test_client() as c:
        r = c.get(url)
        if r.status_code != 200:
            raise RuntimeError(f"{url} → HTTP {r.status_code}")
        return r.data.decode("utf-8")


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir()

    shutil.copytree("static", DEST / "static")

    for url, path in PAGES:
        out = DEST / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(url), encoding="utf-8")
        print(f"  {url}  →  docs/{path}")

    (DEST / "index.html").write_text(ROOT_REDIRECT, encoding="utf-8")
    print("  /  →  docs/index.html  (redirect)")

    (DEST / ".nojekyll").touch()

    print("\nBuild complete → docs/")


if __name__ == "__main__":
    main()
