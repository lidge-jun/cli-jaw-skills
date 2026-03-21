---
name: vercel-deploy
description: Deploy applications and websites to Vercel using the bundled `scripts/deploy.sh` claimable-preview flow. Use when the user asks to deploy to Vercel, wants a preview URL, or says to push a project live on Vercel.
---

# Vercel Deploy

Deploy any project to Vercel instantly. No authentication required.

## How It Works

1. Packages your project into a `.tar.gz` (excludes `node_modules` and `.git`)
2. Auto-detects framework from `package.json`
3. Uploads to deployment service
4. Returns **Preview URL** (live site) and **Claim URL** (transfer to your Vercel account)

## Usage

```bash
bash scripts/deploy.sh [path]
```

**Arguments:**
- `path` - Directory to deploy, or a `.tgz` file (defaults to current directory)

If you pass a directory, the script will create a `.tar.gz` before upload.

**Examples:**

```bash
# Deploy current directory
bash scripts/deploy.sh

# Deploy specific project
bash scripts/deploy.sh /path/to/project

# Deploy existing tarball
bash scripts/deploy.sh /path/to/project.tgz
```

## Packaging Rules

- Exclude `node_modules`, `.git`, and `.env*`
- If no `package.json`, keep `framework` as `null`
- For static HTML with a single `.html` file, rename it to `index.html` before packaging

## Output

```
Preparing deployment...
Creating deployment package...
Deploying...
✓ Deployment successful!

Preview URL: https://skill-deploy-abc123.vercel.app
Claim URL:   https://vercel.com/claim-deployment?code=...
```

The script also outputs JSON to stdout for programmatic use.

```json
{
  "previewUrl": "https://skill-deploy-abc123.vercel.app",
  "claimUrl": "https://vercel.com/claim-deployment?code=...",
  "deploymentId": "dpl_...",
  "projectId": "prj_..."
}
```

## Framework Detection

The script auto-detects frameworks from `package.json` (Next.js, Vite, Remix, Nuxt, SvelteKit, Astro, Express, Hono, and many more). For static HTML projects (no `package.json`), framework is set to `null` and a lone `.html` file is renamed to `index.html` automatically.

## Troubleshooting

### Network Egress Error

If deployment fails due to network restrictions, tell the user:

```
Deployment failed due to network restrictions. To fix this:

1. Allow outbound access to *.vercel.com
2. Try deploying again
```
