---
name: render-deploy
description: Deploy applications to Render by analyzing codebases, generating render.yaml Blueprints, and providing Dashboard deeplinks. Use when the user wants to deploy, host, publish, or set up their application on Render's cloud platform.
---

# Deploy to Render

Render supports **Git-backed** and **prebuilt Docker image** services. This skill covers Git-backed flows:

1. **Blueprint** — Generate render.yaml for Infrastructure-as-Code deployments
2. **Direct Creation** — Create services instantly via MCP tools

Blueprints can run prebuilt images via `runtime: image`, but the render.yaml still lives in a Git repo.

If no Git remote exists, ask the user to create/push one or use the Render Dashboard/API for image-backed deploys (MCP cannot create image-backed services).

## Happy Path

Before deep analysis, reduce friction with these questions:
1. Git repo or prebuilt Docker image?
2. Should Render provision everything the app needs, or only the app (user brings own infra)?

Then proceed with the appropriate method.

## Method Selection

Both methods require a Git repo pushed to GitHub, GitLab, or Bitbucket.

| Method | Best For | Pros |
|--------|----------|------|
| **Blueprint** | Multi-service apps, IaC workflows | Version controlled, reproducible, complex setups |
| **Direct Creation** | Single services, quick deploys | Instant, no render.yaml needed |

**Use Direct Creation when all are true:**
- Single service (one web app or static site)
- No separate worker/cron services
- No attached databases or Key Value
- Simple env vars only

If this fits and MCP isn't configured, guide MCP setup first.

**Use Blueprint when any are true:**
- Multiple services (web + worker, API + frontend)
- Databases, Redis/Key Value, or other datastores
- Cron jobs, background workers, or private services
- Reproducible IaC or monorepo setup

Default to Blueprint when unsure.

## Prerequisites

Verify in order:

### 1. Git Remote

```bash
git remote -v
```

If none exists, stop and ask the user to create/push a remote.

### 2. MCP Tools (preferred for single-service)

```
list_services()
```

If MCP works, skip CLI installation for most operations.

### 3. Render CLI (for Blueprint validation)

```bash
render --version
```

Install if missing:
- macOS: `brew install render`
- Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | sh`

### 4. MCP Setup (if not configured)

If `list_services()` fails, ask the user's preferred AI tool and provide matching setup.

#### Cursor

1. Get API key: `https://dashboard.render.com/u/*/settings#api-keys`
2. Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": { "Authorization": "Bearer <YOUR_API_KEY>" }
    }
  }
}
```
3. Restart Cursor, retry `list_services()`.

#### Claude Code

1. Get API key: `https://dashboard.render.com/u/*/settings#api-keys`
2. Run:
```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <YOUR_API_KEY>"
```
3. Restart Claude Code, retry `list_services()`.

#### Codex

1. Get API key: `https://dashboard.render.com/u/*/settings#api-keys`
2. Run:
```bash
export RENDER_API_KEY="<YOUR_API_KEY>"
codex mcp add render --url https://mcp.render.com/mcp --bearer-token-env-var RENDER_API_KEY
```
3. Restart Codex, retry `list_services()`.

#### Other Tools

Direct to Render MCP docs for that tool's setup.

### 5. Workspace

After MCP is configured, set the active workspace:
```
get_selected_workspace()
```

Or via CLI: `render workspace current -o json`

### 6. Authentication (CLI fallback)

If MCP unavailable:
```bash
render whoami -o json
```

If unauthenticated:
- **API Key**: `export RENDER_API_KEY="rnd_xxxxx"` (from Dashboard → Settings → API Keys)
- **Login**: `render login` (browser OAuth)

---

# Method 1: Blueprint Deployment

## Step 1: Analyze Codebase

Determine framework/runtime, build/start commands, env vars, datastores, and port binding. Use [references/codebase-analysis.md](references/codebase-analysis.md).

## Step 2: Generate render.yaml

Create a `render.yaml` following the Blueprint spec.

Full spec: [references/blueprint-spec.md](references/blueprint-spec.md)

Key points:
- Use `plan: free` unless user specifies otherwise
- Include all required environment variables
- Mark secrets with `sync: false` (user fills in Dashboard)
- Use appropriate service type and runtime

```yaml
services:
  - type: web
    name: my-app
    runtime: node
    plan: free
    buildCommand: npm ci
    startCommand: npm start
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: postgres
          property: connectionString
      - key: JWT_SECRET
        sync: false  # User fills in Dashboard

databases:
  - name: postgres
    databaseName: myapp_db
    plan: free
```

**Service types:** `web` (HTTP, public), `worker` (background), `cron` (scheduled), `static` (CDN), `pserv` (internal)

Details: [references/service-types.md](references/service-types.md) · [references/runtimes.md](references/runtimes.md) · [assets/](assets/)

## Step 3: Validate and Push

Validate when CLI is available:
```bash
render whoami -o json
render blueprints validate
```

Common validation issues: missing `name`/`type`/`runtime`, invalid YAML syntax, bad env var references.

Config guide: [references/configuration-guide.md](references/configuration-guide.md)

Commit and push (render.yaml must be in the remote for the deeplink to work):
```bash
git add render.yaml && git commit -m "Add Render deployment configuration" && git push origin main
```

## Step 4: Generate Deeplink

```bash
git remote get-url origin
```

Convert SSH to HTTPS if needed:

| SSH Format | HTTPS Format |
|------------|--------------|
| `git@github.com:user/repo.git` | `https://github.com/user/repo` |
| `git@gitlab.com:user/repo.git` | `https://gitlab.com/user/repo` |
| `git@bitbucket.org:user/repo.git` | `https://bitbucket.org/user/repo` |

Pattern: replace `git@<host>:` → `https://<host>/`, remove `.git` suffix.

```
https://dashboard.render.com/blueprint/new?repo=<HTTPS_REPOSITORY_URL>
```

## Step 5: Guide User

Provide the deeplink with instructions:
1. Verify render.yaml is pushed to the remote
2. Click deeplink → Render Dashboard
3. Complete Git provider OAuth if prompted
4. Fill secret env vars (marked `sync: false`)
5. Review services and databases
6. Click "Apply" to deploy

## Step 6: Verify Deployment

```
list_deploys(serviceId: "<service-id>", limit: 1)       # Look for status: "live"
list_logs(resource: ["<service-id>"], level: ["error"], limit: 20)
get_metrics(resourceId: "<service-id>", metricTypes: ["http_request_count", "cpu_usage", "memory_usage"])
```

If errors found, see post-deploy triage below.

---

# Method 2: Direct Service Creation

For single-service deploys without IaC. Repository must be pushed to GitHub, GitLab, or Bitbucket.

```bash
git remote -v && git push origin main
```

Use these steps with full MCP examples in [references/direct-creation.md](references/direct-creation.md):

1. **Analyze codebase** — [references/codebase-analysis.md](references/codebase-analysis.md)
2. **Create resources via MCP** — web/static service, databases, key-value stores
3. **Configure env vars** — add via MCP; secrets can be set in Dashboard instead
4. **Verify deployment** — check deploy status, logs, metrics

If MCP returns Git credential errors, guide the user to connect their Git provider in Dashboard.

---

For service discovery, configuration, and common issues: [references/deployment-details.md](references/deployment-details.md)

---

# Post-Deploy Triage

1. Confirm latest deploy is `live` and serving traffic
2. Hit health endpoint (or root) — verify 200 response
3. Scan recent error logs for failure signatures
4. Verify required env vars and port binding (`0.0.0.0:$PORT`)

Detailed checklist: [references/post-deploy-checks.md](references/post-deploy-checks.md)
Basic triage: [references/troubleshooting-basics.md](references/troubleshooting-basics.md)

For deeper diagnostics (metrics, DB checks, error catalog), suggest installing the `render-debug` skill.
