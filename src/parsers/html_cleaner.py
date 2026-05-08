from bs4 import BeautifulSoup

class HTMLCleaner:
    @staticmethod
    def clean(html: str) -> str:
        if not html:
            return ""

        soup = BeautifulSoup(html, "lxml")

        # elimina tags basura si hubiera
        text = soup.get_text(separator="\n")

        # limpieza básica
        lines = [line.strip() for line in text.split("\n")]
        lines = [l for l in lines if l]

        return "\n".join(lines)