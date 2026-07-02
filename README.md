# NTM & Kosi Relationship Bot

A private Discord relationship assistant built only for NTM (`1417262684990083142`) and Kosi (`1516247373716787363`). It works in DMs and servers, supports guided buttons/modals, logs server activity to a configured channel, stores relationship data in MongoDB, and uses neutral AI mediation when `OPENAI_API_KEY` is configured.

## First-time setup

1. Copy `.env.example` to `.env`.
2. Fill in `DISCORD_TOKEN`, `MONGODB_URI`, and optionally `OPENAI_API_KEY`.
3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Run the bot:

```bash
python bot.py
```

5. In your Discord server, run:

```text
,setup
```

`,setup` saves the current channel as the bot log channel. Use `,setlog` in another channel any time you want to move logs.

## Main guided commands

- `,relationship` — opens the button hub for daily check-ins, concerns, and memories.
- `,help` — opens a paginated guide with explanations and examples.
- `,setup` — configures the server and log channel.
- `,setlog` — changes the log channel.
- `,backup` — owner-only backup preview.

## Core examples

```text
,checkin 8 6 missed you today
,complain
,memory our first movie night made me feel close to you
,goal 40 plan our first visit
,add promise call before sleeping on Fridays
,stats
,card
```

## 50 extra useful commands

The bot includes 50 extra natural-language commands for real relationship use:

- Daily care: `,gratitude`, `,affirm`, `,reassure`, `,goodmorning`, `,goodnight`, `,missyou`, `,comfort`
- Conflict care: `,apology`, `,repair`, `,clarify`, `,compromise`, `,boundaries`, `,trigger`, `,need`, `,listen`, `,cooldown`, `,forgive`
- Fun: `,dateidea`, `,truth`, `,dare`, `,question`, `,wouldyourather`, `,playlist`, `,song`
- Trackers: `,movie`, `,game`, `,book`, `,anime`, `,wishlist`, `,giftidea`, `,bucket`, `,promise`, `,visit`
- Memories: `,milestone`, `,achievement`, `,insidejoke`, `,favorite`, `,randommemory`
- Future: `,dream`, `,plan`, `,countdown`
- Reflection: `,journal`, `,moodnote`, `,lesson`, `,pattern`
- Stats/review: `,streak`, `,communication`, `,lovelanguage`, `,review`, `,weekly`

Run `,help` in Discord to see what each command does and a copy-paste example.

## AI Safety

The AI is instructed to never take sides, identify misunderstandings, summarize viewpoints, ask clarifying questions, recommend compromises, encourage communication, and never shame either person. If no OpenAI key is set, the bot still works with safe offline guidance.

## Deployment

This repository includes `runtime.txt` and `Procfile` for Railway-style worker deployment.
