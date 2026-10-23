"""Marca o painel como português do Brasil para o navegador não oferecer tradução.

O Streamlit serve um index.html fixo com <html lang="en">; Chrome/Chromium lê
isso e pergunta se quer traduzir do inglês, mesmo com o texto em português.

- patch_index_html(): troca o atributo no index.html do Streamlit instalado
  (rodado pelo scripts/iniciar.sh antes de ligar o painel; idempotente).
- marcar_pagina(): reforço em tempo de execução, para quem liga o painel sem
  o iniciar.sh.
"""

import os
import sys

LANG_ATTRS = 'lang="pt-BR" translate="no"'


def patch_index_html() -> bool:
    import streamlit

    path = os.path.join(os.path.dirname(streamlit.__file__), "static", "index.html")
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    if LANG_ATTRS in html:
        return False
    patched = html.replace('<html lang="en">', f"<html {LANG_ATTRS}>", 1)
    if patched == html:
        return False
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(patched)
    except OSError:
        return False  # sem permissão de escrita: fica só o reforço em JS
    return True


def marcar_pagina() -> None:
    import streamlit.components.v1 as components

    components.html(
        """<script>
        const d = window.parent.document;
        d.documentElement.lang = "pt-BR";
        d.documentElement.setAttribute("translate", "no");
        if (!d.querySelector('meta[name="google"]')) {
          const m = d.createElement("meta");
          m.name = "google"; m.content = "notranslate";
          d.head.appendChild(m);
        }
        // O iframe deste script ocupa uma linha vazia no topo: esconde o contêiner.
        const box = window.frameElement && window.frameElement.closest('[data-testid="stElementContainer"]');
        if (box) box.style.display = "none";
        </script>""",
        height=0,
    )


if __name__ == "__main__":
    print("index.html do Streamlit em pt-BR" if patch_index_html() else "index.html já estava em pt-BR")
    sys.exit(0)
