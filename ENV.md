# Environment Setup

Set the `AIXPLAIN_API_KEY` environment variable before running.

Windows (PowerShell):

```powershell
$Env:AIXPLAIN_API_KEY = "<YOUR_KEY>"
```

To persist across sessions, you can add it to your user environment variables or create a `.env` file (if allowed by your environment) with:

```
AIXPLAIN_API_KEY=<YOUR_KEY>
```

The app uses `python-dotenv` to load `.env` automatically when present.