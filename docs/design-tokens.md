# Design Tokens (v2)

## Color scale
- `--color-bg`: base surface
- `--color-bg-muted`: elevated muted blocks
- `--color-fg`: primary text
- `--color-fg-muted`: secondary text
- `--color-border`: default separators
- `--color-border-strong`: emphasized borders/focus support
- `--color-accent`: interactive strong action
- `--color-accent-soft`: subtle interactive background
- `--color-inverse`: text on dark accent

Both light and dark values are defined in `apps/web/app/globals.css`.

## Spacing
- Uses Tailwind spacing scale (`p-2 ... p-10`, `gap-2 ... gap-8`)
- Main container width: `max-w-6xl`
- Article reading width: `max-w-3xl`

## Typography
- System stack only: `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`
- Editorial hierarchy:
  - Hero/title: `text-4xl` semibold
  - Section: `text-2xl`
  - Body: `text-base` / `leading-7`
  - Meta labels: `text-xs` uppercase + letter spacing

## Radii and borders
- `--radius-sm`: `0.35rem`
- `--radius-md`: `0.65rem`
- `--radius-lg`: `1rem`
- Border usage:
  - default: `1px var(--color-border)`
  - emphasized: `1px var(--color-border-strong)`

## Motion and transitions
- `--duration-fast`: `130ms`
- `--duration-base`: `200ms`
- Motion is purposefully restrained (hover/focus emphasis only)
- Reduced-motion is respected globally in `globals.css`

## Accessibility notes
- Semantic HTML by default (`header/nav/main/article/section/footer`)
- Keyboard-visible outlines on links/buttons/toggle
- Color contrast tuned for grayscale readability in both schemes
- Dark mode supports both `prefers-color-scheme` and explicit user toggle
