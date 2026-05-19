# n8n AI Avatar Workflows

Три workflow для создания AI-видео аватара. Импортируйте JSON-файлы в self-hosted n8n.

## Стек

| Инструмент | Роль | Стоимость |
|---|---|---|
| self-hosted n8n | Оркестратор | бесплатно |
| ChatGPT 4o-mini | Анализ сайта + сценарий | ~$0.05/скрипт |
| ElevenLabs | Генерация голоса (MP3) | ~$6/мес |
| HeyGen | Рендер аватара в видео | ~$60/мес |
| Midjourney | Генерация персонажа (разово) | ~$10 |

---

## Workflows

### 01 — Script Generator
`workflows/01-script-generator.json`

Принимает URL сайта → парсит текст → GPT-4o-mini пишет готовый сценарий для аватара.

**Входные данные (форма):**
- URL сайта
- Имя аватара
- Тема / продукт
- Длительность (сек)
- Язык

**Результат:** текст сценария + word_count + estimated_duration_sec

---

### 02 — ElevenLabs TTS
`workflows/02-elevenlabs-tts.json`

Тест голоса. Принимает текст → возвращает MP3 (binary).

**Входные данные (форма):**
- Текст для озвучки
- Voice ID (из ElevenLabs)
- Модель (eleven_multilingual_v2 / eleven_turbo_v2_5)
- Stability / Similarity boost

**Результат:** MP3-файл в поле Binary — скачайте через кнопку Download в n8n.

> Полученный MP3 нужно загрузить на хостинг (Cloudflare R2, S3, любой публичный URL)
> и передать в workflow 03 как **Audio URL**.

---

### 03 — HeyGen Avatar Video
`workflows/03-heygen-avatar-video.json`

Создаёт видео в HeyGen и ждёт готовности (поллинг каждые 30 сек, до 12 мин).

**Входные данные (форма):**
- Сценарий (текст)
- Avatar ID (из HeyGen → Avatars)
- Voice ID HeyGen **ИЛИ** Audio URL (готовый MP3 из workflow 02)
- Формат: 16:9 / 9:16 / 1:1
- Тестовый режим (бесплатно, водяной знак)

**Результат:** `video_url`, `thumbnail_url`, `duration_sec`

---

## Настройка переменных

В n8n: **Settings → Variables** — создайте три переменные:

| Переменная | Где взять |
|---|---|
| `OPENAI_API_KEY` | platform.openai.com → API keys |
| `ELEVENLABS_API_KEY` | elevenlabs.io → Profile → API Key |
| `HEYGEN_API_KEY` | app.heygen.com → Settings → API |

---

## Порядок работы

```
1. Workflow 01 → получить сценарий из сайта
       ↓
2. (опционально) Workflow 02 → протестировать голос, скачать MP3
       ↓
3. Загрузить MP3 на публичный URL (или использовать HeyGen Voice ID)
       ↓
4. Workflow 03 → создать видео аватара
       ↓
5. Получить ссылку на готовое видео
```

---

## Требования к n8n

- n8n >= 1.0 (self-hosted)
- Node.js >= 18 (для `fetch` в Code-нодах)
- Execution timeout: увеличьте до 900s в `.env`:
  ```
  EXECUTIONS_TIMEOUT=900
  EXECUTIONS_TIMEOUT_MAX=900
  ```

---

## Получение ID аватара и голоса в HeyGen

**Avatar ID:**
1. HeyGen → Avatars → выбрать аватар → Info → скопировать ID

**Voice ID:**
1. HeyGen → Voices → выбрать голос → скопировать ID
2. Или использовать ElevenLabs Voice ID напрямую (workflow 02 + Audio URL)

## Midjourney → HeyGen аватар

1. Сгенерируйте персонажа в Midjourney (нейтральный фон, анфас, хорошее освещение)
2. Загрузите фото в HeyGen → Avatars → Create → Photo Avatar
3. Скопируйте полученный Avatar ID для workflow 03
