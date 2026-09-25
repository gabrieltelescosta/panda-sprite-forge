"""CLI do Panda Sprite Forge.

    python -m forge.cli generate --character panda --action "pose de idle" --name panda_idle
    python -m forge.cli edit --ref ref/soldier_atlas.png --character panda --name panda_atlas
    python -m forge.cli pixelate --input output/panda_idle-1.png --downscale 64 --preview 8

Precisa de OPENAI_API_KEY (via .env ou variável de ambiente) para generate/edit.
O comando pixelate roda offline, só com Pillow.
"""

from __future__ import annotations

import argparse
import os
import sys

from . import config, openai_client, postprocess
from .config import GenSettings
from .prompt import compose


def _load_dotenv() -> None:
    """Carrega .env se python-dotenv estiver disponível (opcional)."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass


def _save_all(images: list[bytes], out_dir: str, name: str, ext: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, data in enumerate(images, start=1):
        suffix = "" if len(images) == 1 else f"-{i}"
        path = os.path.join(out_dir, f"{name}{suffix}.{ext}")
        with open(path, "wb") as fh:
            fh.write(data)
        paths.append(path)
    return paths


def _settings_from_args(args) -> GenSettings:
    return GenSettings(
        size=args.size,
        quality=args.quality,
        output_format=args.format,
        n=args.n,
        background="opaque" if args.opaque else "transparent",
        input_fidelity=getattr(args, "input_fidelity", config.DEFAULT_INPUT_FIDELITY),
    )


def cmd_generate(args) -> int:
    _load_dotenv()
    prompt = compose(task=args.action or "", character=args.character)
    if args.dry_run:
        print(prompt)
        return 0
    s = _settings_from_args(args)
    images = openai_client.generate(prompt, s)
    paths = _save_all(images, args.out, args.name, args.format)
    for p in paths:
        print(f"salvo: {p}")
    return 0


def cmd_edit(args) -> int:
    _load_dotenv()
    for ref in args.ref:
        if not os.path.exists(ref):
            print(f"referência não encontrada: {ref}", file=sys.stderr)
            return 2
    prompt = compose(task=args.action or "", character=args.character)
    if args.dry_run:
        print(prompt)
        return 0
    s = _settings_from_args(args)
    images = openai_client.edit(prompt, args.ref, s)
    paths = _save_all(images, args.out, args.name, args.format)
    for p in paths:
        print(f"salvo: {p}")
    return 0


def cmd_pixelate(args) -> int:
    out = args.output or (args.input.rsplit(".", 1)[0] + ".pixel.png")
    saved = postprocess.pixelate(
        input_path=args.input,
        out_path=out,
        downscale=args.downscale,
        preview_scale=args.preview,
    )
    print(f"salvo: {saved}")
    if args.preview and args.preview > 1:
        print(f"preview: {saved.rsplit('.', 1)[0]}.x{args.preview}.png")
    return 0


def _add_gen_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--character", "-c", help="nome em prompts/characters/<nome>.md")
    p.add_argument("--action", "-a", default="", help="descrição/pose desta geração")
    p.add_argument("--name", default="sprite", help="nome-base do arquivo de saída")
    p.add_argument("--out", default=config.OUTPUT_DIR, help="pasta de saída")
    p.add_argument("--size", default=config.DEFAULT_SIZE, choices=config.SIZES)
    p.add_argument("--quality", default=config.DEFAULT_QUALITY, choices=config.QUALITIES)
    p.add_argument("--format", default=config.DEFAULT_OUTPUT_FORMAT, choices=("png", "webp"))
    p.add_argument("-n", type=int, default=1, help="quantas variações gerar")
    p.add_argument("--opaque", action="store_true", help="fundo opaco (padrão: transparente)")
    p.add_argument("--dry-run", action="store_true", help="só imprime o prompt final")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="forge", description="Gerador de sprites com GPT Image (OpenAI).")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="texto -> sprite (personagem do zero)")
    _add_gen_flags(g)
    g.set_defaults(func=cmd_generate)

    e = sub.add_parser("edit", help="referência(s) + texto -> sprite (repinta uma folha)")
    _add_gen_flags(e)
    e.add_argument("--ref", nargs="+", required=True, help="imagem(ns) de referência")
    e.add_argument(
        "--input-fidelity",
        default=config.DEFAULT_INPUT_FIDELITY,
        choices=config.INPUT_FIDELITIES,
        help="high mantém grade/poses da referência",
    )
    e.set_defaults(func=cmd_edit)

    x = sub.add_parser("pixelate", help="normaliza p/ pixel-art nativo + paleta fixa (offline)")
    x.add_argument("--input", "-i", required=True, help="imagem gerada pelo GPT")
    x.add_argument("--output", "-o", help="saída (padrão: <input>.pixel.png)")
    x.add_argument("--downscale", type=int, default=config.DEFAULT_ATLAS.native_downscale)
    x.add_argument("--preview", type=int, default=0, help="fator de reamplia nearest p/ inspeção")
    x.set_defaults(func=cmd_pixelate)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
