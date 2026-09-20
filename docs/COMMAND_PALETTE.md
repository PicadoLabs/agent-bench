# Command Palette

AgentBench's React dashboard provides a global keyboard-driven command palette for navigation and common platform actions.

## Controls

| Input | Behavior |
| --- | --- |
| `Ctrl+K` / `Cmd+K` | Open the palette from anywhere in the dashboard |
| Typing | Filter commands using substring or fuzzy matching |
| `ArrowDown` / `ArrowUp` | Move the active command |
| `Enter` | Execute the active command |
| `Escape` | Close the palette |

## Design

The palette is dependency-free and uses the existing React Router and Lucide dependencies. Commands are represented by a typed registry containing an id, label, description, route, and search keywords.

The filtering layer first rewards direct substring matches, then falls back to ordered character matching. This keeps common navigation queries predictable while still allowing short fuzzy queries to find commands.

The dialog uses labelled dialog/listbox semantics, selected options, keyboard navigation, a focusable search input, and outside-click dismissal.

## Extending the Registry

Add a new `CommandItem` to `COMMANDS` in `frontend/src/components/CommandPalette.tsx`:

```ts
{
  id: 'my-command',
  label: 'My Command',
  description: 'What this command does',
  path: '/my-route',
  keywords: ['alias', 'search', 'terms'],
}
```

No router or sidebar changes are required when the command targets an existing route.

## Verification

```bash
cd frontend
npm run build
```

This runs TypeScript compilation followed by the Vite production build.
