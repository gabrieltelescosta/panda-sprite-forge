# Panda Sprite Forge

Gerador de sprites pixel-art usando **GPT Image (OpenAI `gpt-image-1`)** com a
**nossa própria chave**. Repo separado, só pra isso: você descreve o personagem/ação,
ele gera, e o `pixelate` normaliza pra pixel-art de verdade (paleta fixa + alpha binário)
pronta pra entrar no pipeline do **panda-idle**.

Não é um serviço, não tem login/pagamento/infra — é uma CLI enxuta que bate direto
na API da OpenAI.

## Por que assim (e não um builder pronto)

Os builders prontos ou não usam o GPT direto (PerfectPixel/blendi passam por
fal.ai/OpenRouter) ou vêm com tema fixo. Aqui a arte-direção do **panda** e a
**paleta de 6 cores** já estão embutidas, batendo com o atlas 900×800 que o
engine do panda-idle já consome (`scripts/gen_frames.py`).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # e cole a OPENAI_API_KEY
```

## Uso

```bash
# Personagem novo do zero (texto -> sprite)
python -m forge.cli generate --character panda --action "pose de idle respirando" --name panda_idle

# Repintar uma folha existente mantendo grade/poses (referência + texto -> sprite)
python -m forge.cli edit --ref ref/soldier_atlas.png --character panda --name panda_atlas

# Ver o prompt final sem gastar chamada
python -m forge.cli generate --character panda --action "andando" --dry-run

# Normalizar pra pixel-art nativa (offline, só Pillow): downscale + snap na paleta
python -m forge.cli pixelate --input output/panda_idle.png --downscale 64 --preview 8
```

### Comandos

| Comando    | O que faz                                                        | Precisa de chave |
|------------|------------------------------------------------------------------|:----------------:|
| `generate` | Texto → sprite (personagem novo).                                | sim              |
| `edit`     | Referência(s) + texto → sprite (repinta folha, mantém poses).    | sim              |
| `pixelate` | Downscale + alpha binário + snap na paleta de 6 cores.           | não              |

Flags úteis: `--size` (1024x1024 / 1024x1536 / 1536x1024), `--quality`
(low/medium/high), `-n` (variações), `--opaque` (fundo opaco), `--dry-run`.

## Usando pelo Codex (CLI)

A gente usa este repo direto pelo **Codex** no terminal: abre o Codex na pasta e pede o
sprite em português ("gera um idle do panda respirando", "repinta esse atlas mantendo as
poses"). O Codex lê o [`AGENTS.md`](AGENTS.md) — as instruções de operação do repo — e
traduz o pedido num comando do `forge`.

```bash
cd panda-sprite-forge
codex            # abre o agente na pasta; ele já conhece os comandos pelo AGENTS.md
```

Dá pra rodar tudo na mão também (seção **Uso** acima); o Codex só automatiza isso. Pontos de
atenção ao dirigir pelo agente:

- **Chave:** garanta a `OPENAI_API_KEY` no `.env` antes — o agente não inventa a chave.
- **Rede + custo:** `generate`/`edit` batem na API e custam por imagem. Deixe o Codex rodar
  com acesso à rede liberado e confirme o comando antes de gastar. Use `--dry-run` pra revisar
  o prompt sem chamar a API.

## Como encaixa no panda-idle

O `gpt-image-1` **não** gera 900×800 nativo — ele devolve uma imagem grande.
O fluxo é:

1. `generate`/`edit` → imagem base em `output/`.
2. `pixelate` → reduz pra resolução nativa + trava na paleta.
3. leva o resultado pro **panda-idle** e roda `scripts/gen_frames.py` (que fatia
   o atlas em `src/assets/<nome>Frames.ts`).

O alinhamento fino no grid de 100×100 do atlas ainda é feito no panda-idle; este
repo cuida da **geração** e da **normalização de estilo**.

## Estrutura

```
panda-sprite-forge/
├── forge/
│   ├── cli.py            # CLI (generate / edit / pixelate)
│   ├── config.py         # modelo, tamanhos, spec do atlas, paleta
│   ├── prompt.py         # compõe estilo + personagem + tarefa
│   ├── openai_client.py  # wrapper da Images API (generate/edit)
│   └── postprocess.py    # pixelate: downscale + quantização de paleta
├── prompts/
│   ├── style.md          # guardrails de estilo (todo sprite herda)
│   └── characters/
│       └── panda.md      # arte-direção do herói panda
├── requirements.txt
├── .env.example
├── AGENTS.md             # instruções de operação pro Codex / agentes de CLI
└── output/               # gerado (gitignored)
```

Novos personagens (inimigos, bosses): crie `prompts/characters/<nome>.md` e use
`--character <nome>`.

## Custo

Pago por imagem via OpenAI (`gpt-image-1`), na nossa própria conta. `--quality low`
sai bem mais barato pra iterar; suba pra `high` no take final.
