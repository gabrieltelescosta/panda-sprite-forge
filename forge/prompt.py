"""Composição de prompt.

A ideia: todo sprite compartilha um bloco de *guardrails* de estilo
(`prompts/style.md`) para a arte sair coerente. Em cima disso vem a direção de
arte do personagem (`prompts/characters/<nome>.md`, opcional) e por fim a
tarefa específica daquela geração (ação/pose/descrição livre).

    [ ESTILO GLOBAL ]  +  [ PERSONAGEM ]  +  [ TAREFA ]
"""

from __future__ import annotations

import os

from . import config


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def load_style() -> str:
    """Guardrails de estilo compartilhados por todo sprite."""
    if os.path.exists(config.STYLE_FILE):
        return _read(config.STYLE_FILE)
    return ""


def load_character(name: str | None) -> str:
    """Direção de arte de um personagem (prompts/characters/<name>.md)."""
    if not name:
        return ""
    path = os.path.join(config.CHARACTERS_DIR, f"{name}.md")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Personagem '{name}' não encontrado em {path}. "
            f"Crie o arquivo ou rode sem --character."
        )
    return _read(path)


def compose(task: str, character: str | None = None) -> str:
    """Junta estilo + personagem + tarefa num único prompt.

    `task` é a descrição livre da geração (ex.: "folha completa de 8 linhas" ou
    "pose de idle respirando"). Pode vir vazio quando o personagem já descreve
    tudo.
    """
    parts: list[str] = []

    style = load_style()
    if style:
        parts.append(f"# ESTILO (obrigatório em toda a arte)\n{style}")

    char = load_character(character)
    if char:
        parts.append(f"# PERSONAGEM\n{char}")

    if task and task.strip():
        parts.append(f"# TAREFA\n{task.strip()}")

    if not parts:
        raise ValueError("Prompt vazio: passe --prompt/--action ou --character.")

    return "\n\n".join(parts)
