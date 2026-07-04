# Page Lifecycle

## Storage

원본은 dashboard store에 저장:

```text
~/.cli-jaw-dashboard/design/
  projects/
    <project-key>/
      project.json
      pages/
        <page-id>/
          page.json       # source of truth, revision 필드 포함
          artifact.html   # generated artifact
          prompt.md       # last prompt
          assets/
          snapshots/
            <run-id>-before/
            <run-id>-after/
```

`project-key`는 `projectDir`의 canonical path hash.
projectDir에는 `Export to project` 전까지 쓰지 않는다.

## Instance Isolation

각 인스턴스는 자기 `projectDir`에 매핑된 design pages만 본다.
같은 `projectDir`을 가리키는 인스턴스들은 같은 pages를 공유.

## CLI

```bash
jaw design create --title "..." --kind html [--template wireframe]
jaw design list [--project <dir>] [--json]
jaw design show <page-id> [--json]
jaw design path <page-id> [--json]   # pageDir, artifactPath, exportTarget
jaw design edit <page-id> [--editor cursor|code|finder|terminal]
```
