// Eolus — função "eolus-ask" (Supabase Edge Function)
// Recebe a pergunta do app BW AI, pergunta ao Gemini e devolve uma resposta curta, falada.
// A chave do Gemini fica SÓ nos Secrets do Supabase (GEMINI_API_KEY). Nunca no código.
//
// Proteções:
//  - só aceita pedidos vindos do site do app (ALLOWED_ORIGINS)
//  - limite de perguntas por minuto (por aparelho/IP e no total) e por dia
//  - limite de tamanho da pergunta, do histórico e da resposta
//  - identidade fixa do Eolus / Bluewind / CEO no "system prompt"
//  - não recebe nem inventa dados da fábrica (produção fica no próprio app)

const ALLOWED_ORIGINS = [
  "https://bluewind-english.github.io",
];

const MAX_Q_CHARS = 400;          // tamanho máximo da pergunta
const MAX_HIST_TURNS = 6;         // mensagens anteriores enviadas como contexto
const MAX_HIST_CHARS = 300;       // tamanho máximo de cada mensagem anterior
const MAX_ANSWER_CHARS = 600;     // tamanho máximo da resposta falada
const PER_IP_PER_MIN = 8;         // perguntas por minuto por aparelho
const GLOBAL_PER_MIN = 30;        // perguntas por minuto no total
const GLOBAL_PER_DAY = 800;       // perguntas por dia no total

// Modelos tentados em ordem (o primeiro que existir na conta é usado).
// Dá para escolher outro criando o Secret GEMINI_MODEL.
const MODELS = [
  Deno.env.get("GEMINI_MODEL") || "",
  "gemini-flash-latest",
  "gemini-3.6-flash",
  "gemini-3.8-flash",
  "gemini-flash-lite-latest",
].filter(Boolean);

// ---------- limites (memória da função; zera quando a função reinicia) ----------
const ipHits = new Map<string, number[]>();
let globalHits: number[] = [];
let dayKey = "";
let dayCount = 0;

function rateLimited(ip: string): boolean {
  const now = Date.now();
  const today = new Date().toISOString().slice(0, 10);
  if (today !== dayKey) { dayKey = today; dayCount = 0; }
  if (dayCount >= GLOBAL_PER_DAY) return true;

  globalHits = globalHits.filter((t) => now - t < 60_000);
  if (globalHits.length >= GLOBAL_PER_MIN) return true;

  const mine = (ipHits.get(ip) || []).filter((t) => now - t < 60_000);
  if (mine.length >= PER_IP_PER_MIN) { ipHits.set(ip, mine); return true; }

  mine.push(now); ipHits.set(ip, mine);
  globalHits.push(now); dayCount++;
  if (ipHits.size > 5000) ipHits.clear();
  return false;
}

// ---------- respostas HTTP ----------
function cors(origin: string) {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, apikey, authorization, x-client-info",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}
function json(body: unknown, status: number, origin: string) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...cors(origin), "Content-Type": "application/json; charset=utf-8" },
  });
}

// ---------- quem é o Eolus ----------
function systemPrompt(lang: "pt" | "en"): string {
  const now = new Date();
  const when = now.toLocaleString(lang === "en" ? "en-US" : "pt-BR", {
    timeZone: "America/Chicago", weekday: "long", day: "numeric", month: "long",
    year: "numeric", hour: "2-digit", minute: "2-digit",
  });
  const sorry = lang === "en"
    ? "I'm sorry, I don't have access to that information at the moment."
    : "Me perdoe, não tenho acesso a essa informação no momento.";
  return [
    "Você é o EOLUS (nome inspirado em Éolo, o deus dos ventos), o assistente de inteligência artificial da Bluewind Technology. Fale sempre no masculino.",
    "A Bluewind Technology é uma empresa brasileira que fabrica nacelles de turbinas eólicas em compósitos; a fábrica onde você trabalha fica em Pensacola, Flórida.",
    "Você faz parte do sistema BlueWind (app BW AI). Você pertence à Bluewind e trabalha só para a Bluewind e seus funcionários: fale da empresa como \"nossa empresa\" e \"nossa fábrica\".",
    "Se perguntarem quem você é, quem te criou ou de quem você é, diga que é o Eolus, o assistente de IA da Bluewind Technology, feito para a Bluewind. Nunca diga que é o Gemini, nem que foi criado pelo Google ou por outra empresa.",
    "O CEO da Bluewind Technology é Jean Zolet. Piada interna: o Jean Zolet é a única pessoa da empresa de quem o André Schmitt não fala mal.",
    `Agora são ${when} (horário de Pensacola).`,
    "Você NÃO tem acesso aos dados internos da fábrica (produção, cronograma, alertas, mensagens, pessoas, compras, qualidade). Nunca invente esses dados, números, nomes ou status.",
    `Se a pergunta depender desses dados internos, ou de qualquer informação que você não tem com segurança, responda exatamente: "${sorry}"`,
    "Para perguntas gerais (conhecimento, explicações, ideias, contas, traduções, inglês, segurança do trabalho em geral), responda normalmente.",
    "A resposta será LIDA EM VOZ ALTA: no máximo 2 ou 3 frases curtas, sem markdown, sem listas, sem asteriscos, sem emojis, sem links. Escreva números e unidades de forma fácil de falar.",
    "Seja cordial, calmo e gentil, como um assistente de confiança. Se a pessoa cumprimentar, responda o cumprimento com simpatia antes.",
    "Recuse com educação pedidos ofensivos, perigosos ou que exponham dados pessoais de alguém.",
    lang === "en"
      ? "IMPORTANT: the employee chose ENGLISH. Always answer in American English."
      : "IMPORTANTE: responda sempre em português do Brasil.",
  ].join("\n");
}

// ---------- limpeza da resposta para voz ----------
function cleanForVoice(t: string): string {
  let s = (t || "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/\[(.*?)\]\((.*?)\)/g, "$1")
    .replace(/https?:\/\/\S+/g, "")
    .replace(/[*_#`>]+/g, "")
    .replace(/^\s*[-•]\s+/gm, "")
    .replace(/\s+/g, " ")
    .trim();
  if (s.length > MAX_ANSWER_CHARS) {
    const cut = s.slice(0, MAX_ANSWER_CHARS);
    const end = Math.max(cut.lastIndexOf(". "), cut.lastIndexOf("! "), cut.lastIndexOf("? "));
    s = end > 80 ? cut.slice(0, end + 1) : cut.trim() + "…";
  }
  return s;
}

// ---------- chamada ao Gemini ----------
type Turn = { role: "user" | "model"; parts: { text: string }[] };

async function callGemini(key: string, model: string, body: unknown, signal: AbortSignal) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
  return await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": key },
    body: JSON.stringify(body),
    signal,
  });
}

async function askGemini(key: string, lang: "pt" | "en", contents: Turn[]): Promise<string | null> {
  const base = {
    systemInstruction: { parts: [{ text: systemPrompt(lang) }] },
    contents,
    generationConfig: { temperature: 0.6, maxOutputTokens: 1024 },
    safetySettings: [
      { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
      { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
      { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
      { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
    ],
  };
  // Com busca no Google (para notícias e dados do dia) — se a conta não permitir, tenta sem.
  const withSearch = { ...base, tools: [{ google_search: {} }] };

  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 12_000);
  try {
    for (const model of MODELS) {
      for (const body of [withSearch, base]) {
        const r = await callGemini(key, model, body, ctl.signal);
        if (r.status === 404) break;                 // modelo não existe: tenta o próximo
        if (r.status === 400 && body === withSearch) continue; // busca não aceita: tenta sem
        if (!r.ok) {
          console.error("gemini", model, r.status, (await r.text()).slice(0, 300));
          return null;
        }
        const d = await r.json();
        const parts = d?.candidates?.[0]?.content?.parts || [];
        const text = parts.filter((p: { thought?: boolean }) => !p.thought)
          .map((p: { text?: string }) => p.text || "").join(" ");
        const clean = cleanForVoice(text);
        return clean || null;
      }
    }
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// ---------- servidor ----------
Deno.serve(async (req) => {
  const origin = req.headers.get("origin") || "";
  const allowed = ALLOWED_ORIGINS.includes(origin);

  if (req.method === "OPTIONS") {
    return allowed ? new Response("ok", { headers: cors(origin) }) : new Response("forbidden", { status: 403 });
  }
  if (!allowed) return new Response(JSON.stringify({ error: "forbidden" }), { status: 403 });
  if (req.method !== "POST") return json({ error: "method" }, 405, origin);

  const ip = (req.headers.get("x-forwarded-for") || "").split(",")[0].trim() || "?";
  if (rateLimited(ip)) return json({ error: "rate_limited" }, 429, origin);

  const key = Deno.env.get("GEMINI_API_KEY") || Deno.env.get("Gemini_API_key");
  if (!key) return json({ error: "no_key" }, 500, origin);

  let payload: { q?: unknown; lang?: unknown; hist?: unknown };
  try {
    const raw = await req.text();
    if (raw.length > 8000) return json({ error: "too_big" }, 413, origin);
    payload = JSON.parse(raw);
  } catch {
    return json({ error: "bad_json" }, 400, origin);
  }

  const q = String(payload.q ?? "").trim();
  if (!q) return json({ error: "empty" }, 400, origin);
  if (q.length > MAX_Q_CHARS) return json({ error: "too_long" }, 413, origin);
  const lang: "pt" | "en" = payload.lang === "en" ? "en" : "pt";

  const contents: Turn[] = [];
  if (Array.isArray(payload.hist)) {
    for (const h of payload.hist.slice(-MAX_HIST_TURNS)) {
      const role = h?.role === "assistant" ? "model" : h?.role === "user" ? "user" : null;
      const text = String(h?.content ?? "").slice(0, MAX_HIST_CHARS).trim();
      if (!role || !text) continue;
      // o Gemini exige alternância user/model
      if (contents.length && contents[contents.length - 1].role === role) contents.pop();
      contents.push({ role, parts: [{ text }] });
    }
  }
  while (contents.length && contents[0].role !== "user") contents.shift();
  if (contents.length && contents[contents.length - 1].role === "user") contents.pop();
  contents.push({ role: "user", parts: [{ text: q }] });

  try {
    const answer = await askGemini(key, lang, contents);
    if (!answer) return json({ error: "no_answer" }, 502, origin);
    return json({ answer }, 200, origin);
  } catch (e) {
    console.error("eolus-ask", String(e));
    return json({ error: "ai_failed" }, 502, origin);
  }
});
