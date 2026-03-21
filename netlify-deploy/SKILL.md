---
name: netlify-deploy
description: Deploy web projects to Netlify using the Netlify CLI (`npx netlify`). Use when the user asks to deploy, host, publish, or link a site/repo on Netlify, including preview and production deploys.
---

# Netlify Deployment

Deploy web projects to Netlify using the CLI with automatic project detection.

## Prerequisites

- **Netlify CLI**: via npx (no global install required)
- **Authentication**: active Netlify login session
- **Project**: valid web project in current directory

## Workflow

### 1. Verify Authentication

```bash
npx netlify status
```

If not authenticated:

```bash
npx netlify login          # browser-based OAuth (primary)
# OR
export NETLIFY_AUTH_TOKEN=your_token_here  # API key alternative
# Tokens: https://app.netlify.com/user/applications#personal-access-tokens
```

### 2. Link Site

From `netlify status`, check if a site is already linked.

If not linked:

```bash
# Try Git-based linking first
git remote show origin
npx netlify link --git-remote-url <REMOTE_URL>

# If no site exists on Netlify:
npx netlify init
```

`netlify init` guides through team selection, site naming, build settings, and netlify.toml creation.

### 3. Install Dependencies

```bash
npm install  # or yarn/pnpm as appropriate
```

### 4. Deploy

```bash
# Preview deploy (unique URL for testing)
npx netlify deploy

# Production deploy
npx netlify deploy --prod
```

### 5. Report Results

After deployment, report:
- Deploy URL (preview) or Site URL (production)
- Link to deploy logs in Netlify dashboard
- Suggest `netlify open` to view site

## netlify.toml

If present, the CLI uses it automatically. If absent, the CLI prompts for:
- **Build command**: e.g., `npm run build`, `next build`
- **Publish directory**: e.g., `dist`, `build`, `.next`

Common framework defaults:

| Framework | Build Command | Publish Dir |
|-----------|--------------|-------------|
| Next.js | `npm run build` | `.next` |
| React (Vite) | `npm run build` | `dist` |
| Static HTML | (none) | `.` |

Detect framework from `package.json` and suggest appropriate settings.

## Error Handling

| Error | Solution |
|-------|----------|
| "Not logged in" | `npx netlify login` |
| "No site linked" | `npx netlify link` or `npx netlify init` |
| "Build failed" | Check build command, publish dir, dependencies; review build logs |
| "Publish directory not found" | Verify build ran successfully and path is correct |

## Environment Variables

Set secrets in Netlify dashboard (Site Settings → Environment Variables), not in Git.

## Reference

- [Netlify CLI Docs](https://docs.netlify.com/cli/get-started/)
- [netlify.toml Reference](https://docs.netlify.com/configure-builds/file-based-configuration/)
- [CLI commands](references/cli-commands.md)
- [Deployment patterns](references/deployment-patterns.md)
- [netlify.toml guide](references/netlify-toml.md)
