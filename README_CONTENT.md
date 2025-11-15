# Content Editing Guide

## For Content Writers (Using Word)

1. Edit files in `content/drafts/`
2. Use these heading styles:
   - **Heading 1**: Main sections (e.g., "Header", "Info Tile")
   - **Heading 2**: Subsections (e.g., "Title", "Description")
   - **Normal**: Content text
3. Save and notify developer to convert

## For Developers (Using JSON)

1. Edit `content/*.json` files directly
2. Test changes: `python -m mvpf_package.dashboard`
3. Content auto-reloads in debug mode

## Git Workflow
```bash
# Create branch
git checkout -b content-updates

# Make changes to content/*.json

# Commit
git commit -am "Update component descriptions"

# Push and create PR
git push origin content-updates
```

## JSON Structure
```json
{
  "section_name": {
    "key": "value",
    "nested": {
      "subkey": "value"
    }
  }
}
```
```

## **Recommended Workflow for Your Team**
```
┌─────────────────┐         ┌──────────────────┐
│  Content Writer │         │    Developer     │
│   (Word docs)   │         │  (Code + JSON)   │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │ 1. Edit .docx            │
         │    in drafts/            │
         │                           │
         │ 2. Notify via Slack      │
         ├──────────────────────────>│
         │                           │
         │                  3. Run converter
         │                     word_to_json.py
         │                           │
         │                  4. Review JSON
         │                     git diff
         │                           │
         │ 5. Review in app         │
         │<──────────────────────────┤
         │    (share preview URL)    │
         │                           │
         │ 6. Approve ✓             │
         ├──────────────────────────>│
         │                           │
         │                  7. Merge to main
         │                     git push
         └                           ┘