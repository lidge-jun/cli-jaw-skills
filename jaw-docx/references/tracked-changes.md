# Tracked Changes & Comments XML Reference

## Insertion

```xml
<w:ins w:id="1" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:t>inserted text</w:t></w:r>
</w:ins>
```

## Deletion

```xml
<w:del w:id="2" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
```

Inside `<w:del>`, use `<w:delText>` instead of `<w:t>`, and `<w:delInstrText>` instead of `<w:instrText>`.

## Minimal Edits — only mark what changes

```xml
<!-- Change "30 days" to "60 days" -->
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Agent" w:date="2026-03-08T00:00:00Z">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

## Paragraph Deletion

Prevent orphan empty paragraphs by marking the paragraph properties:

```xml
<w:p>
  <w:pPr><w:rPr>
    <w:del w:id="3" w:author="Agent" w:date="2026-03-08T00:00:00Z"/>
  </w:rPr></w:pPr>
  <w:del w:id="4" w:author="Agent" w:date="2026-03-08T00:00:00Z">
    <w:r><w:delText>paragraph content</w:delText></w:r>
  </w:del>
</w:p>
```

Without `<w:del/>` inside `<w:pPr><w:rPr>`, an empty paragraph remains after accepting.

## Rejecting Another Author's Insertion

Nest deletion inside their insertion:

```xml
<w:ins w:author="Jane" w:id="5">
  <w:del w:author="Agent" w:id="10">
    <w:r><w:delText>their inserted text</w:delText></w:r>
  </w:del>
</w:ins>
```

## Restoring Another Author's Deletion

Add insertion after — preserve their deletion unchanged:

```xml
<w:del w:author="Jane" w:id="5">
  <w:r><w:delText>deleted text</w:delText></w:r>
</w:del>
<w:ins w:author="Agent" w:id="10">
  <w:r><w:t>deleted text</w:t></w:r>
</w:ins>
```

## Adding Comments

```bash
# Add a comment
python scripts/comment.py unpacked/ 0 "Comment text"

# Add a reply to comment 0
python scripts/comment.py unpacked/ 1 "Reply text" --parent 0
```

After running, add markers to document.xml:

```xml
<w:commentRangeStart w:id="0"/>
  ... commented content ...
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
```

## Post-processing

```bash
# Merge adjacent runs with identical formatting
python scripts/ooxml/merge_runs.py unpacked/

# Simplify adjacent tracked changes from same author
python scripts/ooxml/simplify_tracked.py unpacked/

# Verify tracked changes correctness against original
python scripts/ooxml/redline_diff.py unpacked/ original.docx --author Agent
```
