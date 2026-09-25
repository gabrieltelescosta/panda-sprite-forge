"""Wrapper fino sobre a Images API do OpenAI (GPT Image).

Duas operações:
  - generate(): texto -> imagem (personagem novo, do zero).
  - edit(): referência(s) + texto -> imagem (repinta uma folha existente,
    mantendo grade/poses). É o fluxo que o panda-idle já usa: pega o atlas do
    soldado e repinta como panda.

Devolve sempre uma lista de bytes PNG já decodificados.
"""

from __future__ import annotations

import base64
import os

from . import config
from .config import GenSettings


def _client():
    # Import tardio para o --help funcionar sem o pacote/chave instalados.
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não definida. Copie .env.example para .env e "
            "preencha a chave, ou exporte a variável no shell."
        )
    return OpenAI(api_key=api_key)


def _decode(resp) -> list[bytes]:
    out: list[bytes] = []
    for item in resp.data:
        if not item.b64_json:
            raise RuntimeError("Resposta sem b64_json — modelo inesperado?")
        out.append(base64.b64decode(item.b64_json))
    return out


def generate(prompt: str, s: GenSettings) -> list[bytes]:
    """Texto -> imagem."""
    client = _client()
    kwargs = dict(
        model=config.MODEL,
        prompt=prompt,
        size=s.size,
        n=s.n,
        quality=s.quality,
        background=s.background,
        output_format=s.output_format,
    )
    kwargs.update(s.extra)
    resp = client.images.generate(**kwargs)
    return _decode(resp)


def edit(prompt: str, ref_paths: list[str], s: GenSettings) -> list[bytes]:
    """Referência(s) + texto -> imagem.

    `input_fidelity="high"` mantém a estrutura da folha de referência (grade,
    quantidade de frames, posicionamento) enquanto repinta o conteúdo.
    """
    client = _client()
    files = [open(p, "rb") for p in ref_paths]
    try:
        kwargs = dict(
            model=config.MODEL,
            image=files if len(files) > 1 else files[0],
            prompt=prompt,
            size=s.size,
            n=s.n,
            quality=s.quality,
            background=s.background,
            output_format=s.output_format,
            input_fidelity=s.input_fidelity,
        )
        kwargs.update(s.extra)
        try:
            resp = client.images.edit(**kwargs)
        except TypeError:
            # SDK antigo pode não conhecer input_fidelity: tenta sem.
            kwargs.pop("input_fidelity", None)
            for f in files:
                f.seek(0)
            resp = client.images.edit(**kwargs)
    finally:
        for f in files:
            f.close()
    return _decode(resp)
