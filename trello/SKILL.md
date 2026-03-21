---
name: trello
description: Manage Trello boards, lists, and cards via the Trello REST API.
homepage: https://developer.atlassian.com/cloud/trello/rest/
metadata:
  {
    "openclaw":
      { "emoji": "📋", "requires": { "bins": ["jq"], "env": ["TRELLO_API_KEY", "TRELLO_TOKEN"] } },
  }
---

# Trello Skill

Manage Trello boards, lists, and cards directly from OpenClaw.

## Setup

1. Get your API key: https://trello.com/app-key
2. Generate a token (click "Token" link on that page)
3. Set environment variables:
   ```bash
   export TRELLO_API_KEY="your-api-key"
   export TRELLO_TOKEN="your-token"
   ```

## Usage

All commands use curl to hit the Trello REST API.

### List boards

```bash
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

### List lists in a board

```bash
curl -s "https://api.trello.com/1/boards/{boardId}/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

### List cards in a list

```bash
curl -s "https://api.trello.com/1/lists/{listId}/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id, desc}'
```

### Create a card

```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={listId}" \
  -d "name=Card Title" \
  -d "desc=Card description"
```

### Move a card to another list

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={newListId}"
```

### Add a comment to a card

```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "text=Your comment here"
```

### Archive a card

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "closed=true"
```

## Notes

- Find Board/List/Card IDs in the Trello URL or via the list commands above
- Keep API key and token secret — they grant full account access
- Rate limits: 300 req/10s per API key; 100 req/10s per token; `/1/members`: 100 req/900s
