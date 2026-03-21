# Dependencies & Platform Compatibility

## Core Python Packages

```bash
pip install hwpx lxml pyhwp olefile defusedxml openpyxl Pillow
```

| Package | Purpose |
|---------|---------|
| `hwpx` (python-hwpx) | HWPX read/modify/create |
| `lxml` | XML parsing (unpack/pack pretty-print) |
| `pyhwp` | HWP 5.0 read/extract (hwp5proc CLI) |
| `olefile` | HWP 5.0 OLE container access |
| `defusedxml` | Safe XML parsing (XXE prevention) |
| `openpyxl` | CJK column width utilities |
| `Pillow` | Contact sheet QA (page grid image) |

## System Dependencies

```bash
# macOS (Homebrew)
brew install libreoffice openjdk poppler   # soffice, java, pdftoppm

# Environment variables (add to ~/.zshrc)
export JAVA_HOME="$(brew --prefix openjdk)/libexec/openjdk.jdk/Contents/Home"
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"

# H2Orestart extension (HWPX support for LibreOffice PDF conversion)
# Download: https://github.com/ebandal/H2Orestart/releases
# Install: unopkg add H2Orestart.oxt

# Linux (apt)
sudo apt install libreoffice default-jre poppler-utils
# H2Orestart: apt install libreoffice-h2orestart (Debian sid+) or .oxt manual install
```

## HWP→HWPX Upgrade Tool

```bash
# Recommended: neolord0/hwp2hwpx (Java, most accurate conversion)
git clone https://github.com/neolord0/hwp2hwpx /tmp/hwp2hwpx
cd /tmp/hwp2hwpx && mvn -DskipTests package dependency:copy-dependencies
java -cp 'target/classes:target/dependency/*' \
  kr.dogfoot.hwp2hwpx.CliMain input.hwp output.hwpx
# Requires: Java 11+ + Maven
```

Avoid `@ssabrojs/hwpxjs convert:hwp` — known to produce dummy HWPX with placeholder text for some files.

## Cross-Platform Compatibility

| Feature | macOS | Linux | Windows |
|---------|-------|-------|---------|
| **HWPX read/edit** | ✅ python-hwpx | ✅ python-hwpx | ✅ python-hwpx |
| **HWPX → PDF** | ✅ soffice+H2Orestart+Java | ✅ same | ✅ same |
| **HWP read** | ✅ pyhwp | ✅ pyhwp | ✅ pyhwp |
| **HWP → HWPX upgrade** | ✅ hwp2hwpx | ✅ same | ✅ same |
| **HWP write (binary)** | ❌ | ❌ | ⚠️ COM only (pyhwpx) |
| **unpack/pack/validate** | ✅ pure Python | ✅ pure Python | ✅ pure Python |

- Core editing pipeline (unpack→edit→pack) is pure Python, fully cross-platform
- PDF conversion needs LibreOffice + H2Orestart + Java on all platforms
- HWP binary write is Windows-only via COM. Use upgrade-first strategy instead

## Library Tiers

| Tier | Library | Format | Capabilities |
|------|---------|--------|-------------|
| **1** | python-hwpx | HWPX | R/W/Create — primary tool |
| **1** | pyhwp | HWP 5.0 | Read-only — most mature binary parser |
| **2** | hwp-hwpx-parser | HWP+HWPX | Read-only parser |
| **2** | olefile | HWP 5.0 | Low-level OLE access |
| **3** | @ssabrojs/hwpxjs | HWPX+HWP conv | Node.js — HWP→HWPX conversion |
| **3** | hwplib (Java) | HWP 5.0 | Only HWP binary R/W library |
