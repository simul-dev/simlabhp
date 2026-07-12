import json
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for
from jinja2 import StrictUndefined


BASE_DIR = Path(__file__).resolve().parent
SUPPORTED_LANGUAGES = ("ko", "en")
DEFAULT_LANGUAGE = "ko"


def _load_translations():
    translations = {}
    for language in SUPPORTED_LANGUAGES:
        translation_path = BASE_DIR / "translations" / f"{language}.json"
        with translation_path.open(encoding="utf-8") as translation_file:
            translations[language] = json.load(translation_file)
    return translations


TRANSLATIONS = _load_translations()


def _translation_shape(value):
    if isinstance(value, dict):
        return {key: _translation_shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_translation_shape(value[0])] if value else []
    return type(value).__name__


reference_shape = _translation_shape(TRANSLATIONS[DEFAULT_LANGUAGE])
for language, translation in TRANSLATIONS.items():
    if _translation_shape(translation) != reference_shape:
        raise ValueError(f"Translation structure for '{language}' does not match '{DEFAULT_LANGUAGE}'.")

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined


def _render_localized_page(template_name, page_name, language):
    if language not in SUPPORTED_LANGUAGES:
        abort(404)

    translations = TRANSLATIONS[language]
    return render_template(
        template_name,
        lang=language,
        common=translations["common"],
        page=translations[page_name],
        current_page=page_name,
    )


def _localized_redirect(endpoint, language, status_code=308):
    target = url_for(endpoint, lang=language)
    if request.query_string:
        target = f"{target}?{request.query_string.decode('ascii')}"
    return redirect(target, code=status_code)


@app.get("/")
def root():
    return _localized_redirect("home", DEFAULT_LANGUAGE, status_code=302)


@app.get("/<lang>/")
def home(lang):
    return _render_localized_page("index.html", "index", lang)


@app.get("/<lang>/resources")
def resources(lang):
    return _render_localized_page("resource.html", "resource", lang)


@app.get("/index.html")
def legacy_index():
    return _localized_redirect("home", "ko")


@app.get("/index_en.html")
def legacy_index_en():
    return _localized_redirect("home", "en")


@app.get("/resource.html")
def legacy_resource():
    return _localized_redirect("resources", "ko")


@app.get("/resource_en.html")
def legacy_resource_en():
    return _localized_redirect("resources", "en")


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
