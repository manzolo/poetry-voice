from __future__ import annotations

import re

# Fine frase: punto, esclamativo, interrogativo o puntini, seguiti da spazio.
_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")
_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")


def split_into_sentences(text: str) -> str:
    """Riformatta il testo con una frase per riga (per la prosa).

    Gli a capo interni ai paragrafi vengono uniti, poi si spezza sulla
    punteggiatura di fine frase. Le righe vuote tra paragrafi sono preservate,
    cosi restano separatori di strofa per pause e chunking dell'analisi.
    """
    blocks: list[str] = []
    for paragraph in _PARAGRAPH_BREAK.split(text):
        joined = " ".join(line.strip() for line in paragraph.splitlines() if line.strip())
        if not joined:
            continue
        sentences = [sentence.strip() for sentence in _SENTENCE_END.split(joined)]
        blocks.append("\n".join(sentence for sentence in sentences if sentence))
    return "\n\n".join(blocks)
