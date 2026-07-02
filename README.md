# NTM & Kosi Relationship Bot

A private Discord relationship assistant built only for NTM (`1417262684990083142`) and Kosi (`1516247373716787363`). It works in DMs and servers, supports guided buttons/modals, logs server activity to a configured channel, stores relationship data in SQLite by default, can still use MongoDB when explicitly configured, and uses neutral AI mediation when `OPENAI_API_KEY` is configured.

## First-time setup

1. Copy `.env.example` to `.env`.
2. Fill in `DISCORD_TOKEN` and optionally `OPENAI_API_KEY`. Leave `DATABASE_BACKEND=sqlite` for Railway free-tier deployments. Use `DATABASE_BACKEND=mongodb` only when your MongoDB volume has enough free space.
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

This repository includes `runtime.txt`, `Procfile`, and `railway.json` for Railway worker deployment. The default SQLite backend writes to `data/relationship_bot.sqlite3`, avoiding MongoDB free-tier disk/index failures.

## Railway MongoDB disk-space behavior

On small/free MongoDB deployments, startup index creation can fail with `OutOfDiskSpace`. The bot now defaults to SQLite so a full MongoDB volume is no longer required. If you choose `DATABASE_BACKEND=mongodb`, startup index builds are treated as nonessential maintenance: if MongoDB reports `OutOfDiskSpace`, startup continues and logs a warning, but normal database writes can still fail until the MongoDB volume has enough free space. Free space by deleting old data, compacting the database, recreating the database, or moving to a larger MongoDB tier if writes are rejected.
