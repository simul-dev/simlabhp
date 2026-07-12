import unittest

from app import TRANSLATIONS, app


class LocalizedPagesTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_canonical_pages_render_in_both_languages(self):
        expectations = {
            "/ko/": ('<html lang="ko">', "DAS Lab이 해결합니다."),
            "/en/": ('<html lang="en">', "DAS Lab solves them."),
            "/ko/resources": ('<html lang="ko">', "학습 자료"),
            "/en/resources": ('<html lang="en">', "Learning Materials"),
        }

        for path, expected_text in expectations.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.get_data(as_text=True)
                for text in expected_text:
                    self.assertIn(text, html)

    def test_language_switch_stays_on_the_same_page_type(self):
        home = self.client.get("/ko/").get_data(as_text=True)
        resources = self.client.get("/ko/resources").get_data(as_text=True)

        self.assertIn('href="/en/">EN</a>', home)
        self.assertIn('href="/en/resources">EN</a>', resources)

    def test_legacy_urls_redirect_to_canonical_urls(self):
        redirects = {
            "/": (302, "/ko/"),
            "/index.html": (308, "/ko/"),
            "/index_en.html": (308, "/en/"),
            "/resource.html": (308, "/ko/resources"),
            "/resource_en.html": (308, "/en/resources"),
        }

        for path, (status_code, location) in redirects.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, status_code)
                self.assertEqual(response.headers["Location"], location)

    def test_legacy_redirect_preserves_query_string(self):
        response = self.client.get("/index_en.html?utm_source=test")
        self.assertEqual(response.headers["Location"], "/en/?utm_source=test")

    def test_rendered_pages_do_not_link_to_legacy_templates(self):
        legacy_names = (
            "index.html",
            "index_en.html",
            "resource.html",
            "resource_en.html",
        )

        for path in ("/ko/", "/en/", "/ko/resources", "/en/resources"):
            with self.subTest(path=path):
                html = self.client.get(path).get_data(as_text=True)
                for legacy_name in legacy_names:
                    self.assertNotIn(f'href="{legacy_name}', html)

    def test_unknown_language_returns_404(self):
        self.assertEqual(self.client.get("/fr/").status_code, 404)
        self.assertEqual(self.client.get("/fr/resources").status_code, 404)

    def test_translation_files_have_matching_structure(self):
        self.assertEqual(
            set(TRANSLATIONS["ko"]),
            set(TRANSLATIONS["en"]),
        )
        self.assertEqual(
            len(TRANSLATIONS["ko"]["index"]["services"]["items"]),
            len(TRANSLATIONS["en"]["index"]["services"]["items"]),
        )
        self.assertEqual(
            len(TRANSLATIONS["ko"]["index"]["clients"]["items"]),
            len(TRANSLATIONS["en"]["index"]["clients"]["items"]),
        )


if __name__ == "__main__":
    unittest.main()
