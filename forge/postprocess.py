"""Pós-processamento: transforma a imagem "lisa" do GPT em pixel-art de verdade.

O gpt-image-1 tende a devolver uma ilustração em alta resolução com cara de
pixel-art, não pixels nativos. Aqui a gente:
  1. dá downscale (média) para a resolução nativa desejada;
  2. joga o alpha para binário (sprite não tem meia-transparência);
  3. "snapa" cada cor para a paleta fixa (6 cores do panda), matando gradientes
     e antialiasing;
  4. opcionalmente reamplia com nearest-neighbor só para inspeção.

Não depende de numpy — as imagens já estão minúsculas depois do downscale.
"""

from __future__ import annotations

import os

from PIL import Image

from .config import DEFAULT_ATLAS


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _nearest(rgb, palette_rgb):
    r, g, b = rgb
    best = palette_rgb[0]
    best_d = 1 << 30
    for pr, pg, pb in palette_rgb:
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if d < best_d:
            best_d = d
            best = (pr, pg, pb)
    return best


def pixelate(
    input_path: str,
    out_path: str,
    downscale: int | None = None,
    palette: tuple[str, ...] | None = None,
    alpha_threshold: int = 128,
    preview_scale: int = 0,
) -> str:
    """Aplica o tratamento e salva em `out_path`. Retorna o caminho salvo."""
    downscale = downscale or DEFAULT_ATLAS.native_downscale
    palette = palette or DEFAULT_ATLAS.palette
    palette_rgb = [_hex_to_rgb(c) for c in palette]

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    img = Image.open(input_path).convert("RGBA")

    # Downscale mantendo proporção (lado maior = downscale).
    w, h = img.size
    if max(w, h) > downscale:
        if w >= h:
            nw, nh = downscale, max(1, round(h * downscale / w))
        else:
            nw, nh = max(1, round(w * downscale / h)), downscale
        img = img.resize((nw, nh), Image.LANCZOS)

    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a < alpha_threshold:
                px[x, y] = (0, 0, 0, 0)
            else:
                nr, ng, nb = _nearest((r, g, b), palette_rgb)
                px[x, y] = (nr, ng, nb, 255)

    img.save(out_path)

    if preview_scale and preview_scale > 1:
        big = img.resize(
            (img.width * preview_scale, img.height * preview_scale), Image.NEAREST
        )
        preview_path = out_path.rsplit(".", 1)[0] + f".x{preview_scale}.png"
        big.save(preview_path)

    return out_path
