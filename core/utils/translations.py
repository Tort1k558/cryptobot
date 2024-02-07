import json


def load_translations(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


translations_files = {
    "russian": "translations/translations_rus.json",
    "english": "translations/translations_eng.json",
    "polish": "translations/translations_pls.json",
    "ukrainian": "translations/translations_urk.json"
}

translations = {lang: load_translations(file) for lang, file in translations_files.items()}


def get_translate(phrase, language):
    return translations[language].get(phrase, "Translation not available")
