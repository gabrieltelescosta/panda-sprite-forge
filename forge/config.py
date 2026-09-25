"""Configuração central do Panda Sprite Forge.

Tudo que é "tunável" (modelo, tamanho, paleta, spec do atlas) vive aqui, para
o resto do código só ler. Os defaults refletem o pipeline atual do panda-idle:
atlas 900x800, células 100x100, paleta de 6 cores, RGBA transparente.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- Modelo OpenAI (GPT Image) -------------------------------------------------

# gpt-image-1 é o modelo de imagem do GPT. Sempre devolve base64 (sem URL).
MODEL = "gpt-image-1"

# Tamanhos aceitos pelo gpt-image-1. O modelo NÃO gera 900x800 nativo; a gente
# gera num tamanho suportado e normaliza depois (comando `pixelate` + gen_frames).
SIZES = ("1024x1024", "1024x1536", "1536x1024", "auto")
DEFAULT_SIZE = "1024x1024"

# low | medium | high | auto — custo/qualidade.
QUALITIES = ("low", "medium", "high", "auto")
DEFAULT_QUALITY = "high"

# png preserva transparência; webp também. Sprite = png.
DEFAULT_OUTPUT_FORMAT = "png"

# Só vale em edit: quão fiel ao(s) reference(s). "high" mantém grade/poses.
INPUT_FIDELITIES = ("low", "high")
DEFAULT_INPUT_FIDELITY = "high"


# --- Spec do atlas / arte (herdado do panda-idle) ------------------------------


@dataclass(frozen=True)
class AtlasSpec:
    """Formato do sprite sheet que o engine do panda-idle consome."""

    width: int = 900
    height: int = 800
    columns: int = 9
    rows: int = 8
    cell: int = 100
    # Paleta de 6 cores do panda (do output/panda-v3/animations.json).
    palette: tuple[str, ...] = (
        "#181b24",
        "#323845",
        "#606775",
        "#a5a6a4",
        "#deddd4",
        "#fff3db",
    )
    # Resolução "nativa" aproximada do sprite dentro da célula, usada pelo
    # comando `pixelate` para dar o downscale antes de quantizar a paleta.
    native_downscale: int = 64


DEFAULT_ATLAS = AtlasSpec()


# --- Caminhos ------------------------------------------------------------------

PROMPTS_DIR = "prompts"
CHARACTERS_DIR = "prompts/characters"
STYLE_FILE = "prompts/style.md"
OUTPUT_DIR = "output"


@dataclass
class GenSettings:
    """Parâmetros de uma geração, resolvidos a partir da CLI."""

    size: str = DEFAULT_SIZE
    quality: str = DEFAULT_QUALITY
    output_format: str = DEFAULT_OUTPUT_FORMAT
    n: int = 1
    background: str = "transparent"
    input_fidelity: str = DEFAULT_INPUT_FIDELITY
    extra: dict = field(default_factory=dict)
