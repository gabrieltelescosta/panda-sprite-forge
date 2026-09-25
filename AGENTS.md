# AGENTS.md — instruções pro Codex (e outros agentes de CLI)

Este repo é o **Panda Sprite Forge**: uma CLI Python que gera sprites pixel-art com o
GPT Image (`gpt-image-1`) da OpenAI e normaliza pra paleta/atlas do projeto
**panda-idle**. Não tem servidor, front-end nem testes — é só a CLI.

## O que você (agente) faz aqui

O usuário pede um sprite em linguagem natural ("gera um idle do panda respirando",
"repinta esse atlas mantendo as poses"). Você traduz isso num comando do `forge` e roda.
Não invente API nova nem outra biblioteca: só orquestre os comandos abaixo.

## Setup (uma vez)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # cole a OPENAI_API_KEY (peça ao usuário; nunca invente a chave)
```

A chave vem do `.env` (ou da env var `OPENAI_API_KEY`). `generate`/`edit` precisam dela e
batem na rede — rode com acesso à rede liberado e confirme o comando com o usuário, porque
**cada chamada custa** na conta da OpenAI. `pixelate` é offline (só Pillow), pode rodar à vontade.

## Comandos

- `python -m forge.cli generate -c <char> -a "<ação/pose>" --name <arquivo>`
  texto → sprite novo. Sai em `output/<arquivo>.png`.
- `python -m forge.cli edit --ref <img...> -c <char> -a "<ação>" --name <arquivo>`
  referência + texto → repinta mantendo grade/poses (`--input-fidelity high` é o padrão).
- `python -m forge.cli pixelate -i output/<arquivo>.png --downscale 64 --preview 8`
  offline: downscale + alpha binário + trava na paleta de 6 cores.

Flags: `--size` (1024x1024 / 1024x1536 / 1536x1024 / auto), `--quality`
(low / medium / high / auto), `-n` (variações), `--opaque`, `--dry-run`.

## Regras de operação

1. **Sempre ofereça `--dry-run` antes de gastar.** Ele imprime o prompt final sem chamar a
   API. Itere no prompt com `--dry-run` e só então rode de verdade.
2. **Itere em `--quality low`**; suba pra `high` só no take final (custo).
3. **Personagem = arquivo.** `-c panda` lê `prompts/characters/panda.md`. Personagem novo
   (inimigo/boss) = criar `prompts/characters/<nome>.md` primeiro; ele herda `prompts/style.md`.
4. **Fluxo completo:** `generate`/`edit` → `pixelate` → levar o PNG pro **panda-idle** e rodar
   `scripts/gen_frames.py` lá (fatia o atlas em `src/assets/<nome>Frames.ts`). Este repo cuida
   só da geração e da normalização de estilo.
5. **Nunca commite** `.env` nem `output/` (já no `.gitignore`). A arte canônica vive no
   panda-idle, não aqui.
6. **Estilo e paleta (6 cores) são fixos** em `forge/config.py` + `prompts/style.md` — não mude
   sem o usuário pedir.

## Estrutura

`forge/cli.py` (comandos) · `config.py` (modelo / tamanhos / paleta / spec do atlas) ·
`prompt.py` (compõe style + character + task) · `openai_client.py` (Images API) ·
`postprocess.py` (pixelate). Prompts em `prompts/style.md` + `prompts/characters/*.md`.
