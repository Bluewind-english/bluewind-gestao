# Vídeo demonstrativo BlueWind HORIZONS / Eolus

- page.html: cenas animadas (1920x1080), render(t) controlado pelo film.py
- film.py: `python3 film.py stills 15 37` (quadros de teste) | `python3 film.py N` (renderiza a cena N, 0–6)
- audio.py: trilha + bipes + vozes (aud/*.wav) -> track.wav
- lines.py / timeline.json: falas e tempos (Eolus = 'e', operador = 'o')
- img/: Eolus (fundo transparente), hélice, logo, HORIZONS, CONNECTING
- Caminhos no film.py apontam para /tmp e /home/claude/cover: ajustar para img/ ao reutilizar.

Pendências: trocar a voz por uma voz grátis lisa/natural (estilo assistente britânico, mais alta);
adicionar perguntas gerais (tempo hoje, dólar hoje) e função futura de câmeras (estacionamento congestionado, limpeza da fábrica).
