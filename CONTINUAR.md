# BW AI / Eolus: documento de continuação

Atualizado em 23/11/2026. Leia isto primeiro numa conversa nova.

## Quem e o quê
- Usuário: André Schmitt, Process Specialist da Bluewind Technology (Pensacola, FL). É leigo em tecnologia: precisa de passo a passo detalhado. Escreve em português.
- Regras dele para todos os apps:
  - **Nenhum app pode ter zoom ou seleção de texto.**
  - Sempre mostrar **prévia antes** de mudar algo grande.
  - Não mexer no app do Eolus quando estiver trabalhando em outros apps.
  - Materiais de apresentação sem o nome "Claude" e com nomes genéricos (banco de dados na nuvem, repositório de código).
- CEO: **Jean Zolet** (um L só), pronunciado "Zolê". Piada: "a única pessoa de quem o André Schmitt não fala mal" é o Jean Zolet.

## Onde está cada coisa
- **Repositório de código:** GitHub `Bluewind-english/bluewind-gestao` (branch `main`).
- **Site / app:** https://bluewind-english.github.io/bluewind-gestao/, atalho na tela do iPhone chamado **BW AI**.
- **Teste de voz:** https://bluewind-english.github.io/bluewind-gestao/voz-teste.html
- **Banco de dados na nuvem:** Supabase, projeto `xxasbzfozhgjvugiajvt`.
  - URL: `https://xxasbzfozhgjvugiajvt.supabase.co`
  - Chave **publicável** (pública, já está no código): `sb_publishable_vewOALKDkWzDIzu87tRKMA_U3p4AsW6`
  - O app lê via REST (`/rest/v1/<tabela>`, cabeçalho `apikey`) a cada 60 s. Quando lê, aparece o indicador verde "● DADOS AO VIVO".
  - O André edita os dados pelo **Table Editor** do Supabase. Ele já editou a N-105 com sucesso.

### Tabelas do Supabase (colunas que o app usa)
| Tabela | Colunas |
|---|---|
| `nacelles` | `id` (ex.: N-105), `etapa`, `progresso` (0–100), `status` (`ok` / `warn` / `bad`), `prazo`, `responsavel`, `obs` |
| `cronograma` | `dia` (data), `hora`, `nacelle`, `atividade` |
| `alertas` | `nivel` (`warn` / `bad` / `ok`), `titulo`, `descricao`, `criado_em` |
| `mensagens` | `setor`, `texto`, `criado_em` |

Observações:
- Os alertas **não** são gerados automaticamente a partir das nacelles. Eles vêm só da tabela `alertas`.
- A coluna `obs` está em português e aparece assim também no modo inglês. Uma coluna `obs_en` seria uma melhoria pendente.

## Arquivos no repositório
- `index.html`: o app inteiro, num arquivo único (HTML, CSS e JS). Contém:
  - **Tela inicial:**
    - bandeiras PT/EN
    - logo BlueWind recortado da imagem, sem fundo branco, com a hélice girando por cima do nome
    - HORIZONS e "Connecting processes and people"
    - semana, relógio, painel de produção
    - Eolus no centro, com 8 botões em 2 colunas
  - **Modo voz:**
    - só o Eolus, em tela cheia, sem legendas nem botões
    - tocar no Eolus começa a ouvir; arrastar o dedo para a direita volta ao início
    - envia sozinho depois de 4 s de silêncio
  - **Eolus:** imagem verde em camadas (cabeça, corpo, pontinhos), em base64 dentro do HTML.
    - Movimentos humanos: a cabeça inclina, vira e acena ao falar, e o peito respira.
    - Os pontinhos flutuam em volta dele; partículas coloridas saem das bordas.
    - Aura suave atrás dele. Ao falar, o rosto acende em verde forte.
    - Montagem com partículas: "ASSEMBLING… %".
  - **Respostas** (fora do Claude não há IA de verdade ainda):
    - `identity` (quem é ele, CEO, piada)
    - `cordial` (cumprimentos só no início da frase)
    - `liveAnswer`: dólar (open.er-api.com), tempo em Pensacola (Open-Meteo), feriados dos EUA (date.nager.at), data
    - `quickFactory` / `quickAnswerEN`: produção, atrasos, alertas, cronograma, mensagens, hora. Só respondem quando a intenção é clara.
    - Quando não sabe, usa `sorry()`: "Me perdoe, não tenho acesso a essa informação no momento." Em inglês: "I'm sorry, I don't have access to that information at the moment." Se não entende: "Desculpe, não entendi. Pode repetir?"
  - **Voz:**
    - Fora do Claude usa a voz Piper no próprio celular, pelo arquivo `eolus-voz.js`: **Ryan** (`en_US-ryan-medium`) em inglês e **Faber** (`pt_BR-faber-medium`) em português.
    - O modelo (~70 MB) vem do HuggingFace (repositório diffusionstudio/piper-voices) e fica guardado no celular.
    - Efeito leve: velocidade 0,96, equalização, eco curto e compressor.
    - Enquanto a voz não carrega, usa a voz do aparelho.
    - Dentro do Claude usa a voz do Claude.
    - Atenção: o app da Tela de Início do iPhone tem armazenamento separado do Safari, então baixa a voz de novo.
  - `sayFix`: pronúncia de Zolet, Eolus, BlueWind e nacelles.
- `eolus-voz.js`: biblioteca de voz empacotada (piper-tts-web + onnxruntime-web).
- `voz/`: arquivos que essa biblioteca usa (`piper_phonemize.wasm` / `.data` e `ort/`).
- `voz-teste.html`: página de teste das vozes.
- `manifest.json`, `icon-180/192/512/1024.png`, `favicon.png`: ícone atual = **Eolus verde + "BlueWind technology" + HORIZONS** (opção A). Para trocar de ícone no iPhone é preciso apagar o atalho e adicionar de novo; há um `?v=3` para não usar o ícone antigo guardado.
- `video-projeto/`: fontes do **vídeo demonstrativo** (versão final em 4K, 2:54, voz Ryan, legendas em inglês).
  - `v2/page4k.html` + `v2/film4k.py`: renderização das cenas em 4K com Playwright e ffmpeg.
  - `v2/audio.py`: trilha sonora.
  - `v2/lines.py`: falas.
  - `img/`: imagens do Eolus, logo e camadas.
  - Cenas na ordem:
    1. abertura
    2. montagem do Eolus
    3. dia a dia: tempo, furacão, pôr do sol
    4. produção (N-105 atrasada)
    5. funcionalidades
    6. fábrica conectada
    7. câmeras: infusão desorganizada, nacele WT20 fora do trilho, carro na vaga do CEO
    8. ligação para o Tyler (manutenção, bomba de vácuo nº 3)
    9. trabalhador na nacele sem cinto e ligação para o Mike (gerente de segurança)
    10. anúncio da Safety Meeting (segunda, 10:30, Main Hall)
    11. empilhadeira × pedestre
    12. calor de 96°F e pausa para água
    13. encerramento
- `README.md`: descrição curta.

## Como publicar (para o Claude)
- Editar `index.html`, testar com Playwright (Chrome em `/usr/bin/google-chrome`).
- Commit e `git -c push.negotiate=true push`. O GitHub Pages atualiza em 1–2 minutos.
- Copiar também para o arquivo de trabalho, se houver.

## Pendências e próximos passos
1. **Ligar uma IA de verdade (combinado para "amanhã" em 23/11):** começar pelo **Gemini grátis**.
   - O André cria a chave no Google AI Studio e guarda nos **Secrets** do Supabase. **Ele não deve mandar a chave na conversa.**
   - O Claude escreve uma **Edge Function** (`eolus-ask`) com estas proteções:
     - só aceita pedidos do site `bluewind-english.github.io`
     - limita as perguntas por minuto
     - limita o tamanho das perguntas e das respostas
     - mantém a identidade do Eolus, da Bluewind e do CEO
   - O app chama essa função quando `quickAnswer` / `liveAnswer` não sabem. Se a IA falhar, usa `sorry()`.
   - Aviso dado ao André: no plano grátis, o Google pode usar os dados, então nada confidencial. Depois, plano pago (Claude ou Gemini).
   - **23/11: código pronto e publicado.** Função em `supabase/functions/eolus-ask/index.ts`; no `index.html` a função `cloudAsk()` é chamada dentro de `ask()` quando `quickFactory`/`quickAnswerEN` não respondem.
     - A função **não recebe dados da fábrica** (só pergunta, idioma e as últimas 6 falas). Produção/cronograma continuam respondidos pelo próprio app.
     - Modelos tentados em ordem: Secret `GEMINI_MODEL` (opcional), `gemini-flash-latest`, `gemini-3.6-flash`, `gemini-3.8-flash`, `gemini-flash-lite-latest`. Tenta com busca no Google e, se não puder, sem.
     - Limites: 8 perguntas/min por aparelho, 30/min no total, 800/dia; pergunta até 400 caracteres; resposta até 600.
     - Precisa no Supabase: Secret `GEMINI_API_KEY`, função criada pelo editor com o nome `eolus-ask` e **"Verify JWT" desligado** (a chave publicável não é JWT; a proteção é a origem + limites).
     - Falta confirmar: o André fazer esses passos e testar no celular.
1b. **Modo conversa (combinado em 23/11 para fazer junto com a IA):** tocar no Eolus uma vez e ir conversando, igual ao Gemini por voz.
   - Depois que ele termina de falar (`talkDone`), reabrir o microfone sozinho (`dict.start()`).
   - Terminar ao arrastar para a direita ou depois de ~10 s de silêncio.
   - Se o iPhone bloquear o microfone sem toque, mostrar "toque para continuar".
   - Interromper o Eolus no meio da fala fica para uma segunda etapa.
   - **Mostrar prévia ao André antes de publicar.**
2. Reforçar a segurança do Supabase (login) antes de colocar dados sensíveis.
3. Coluna `obs_en` para o modo inglês.
4. Skill Station (outro repositório, `skill-station`): integrar a apresentação de segurança como uma aba "Apresentação" (prévia já aprovada antes) e talvez renomear Turbine para Eolus lá. Ainda não feito.
5. Ideias futuras:
   - câmeras reais
   - alto-falantes da fábrica
   - ligações automáticas
   - alertas gerados automaticamente a partir das nacelles atrasadas
