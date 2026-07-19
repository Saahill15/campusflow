# Pragyarambh '26 Design System

This design system defines the brand, visual language, motion, and interface guidelines for the Pragyarambh '26 event management platform. It is the single source of truth for product design, UX, and frontend implementation.

## 1. Brand Personality

- Premium: polished, curated, and thoughtful.
- Modern: clean lines, confident spacing, and contemporary interaction patterns.
- User-friendly: easy to scan, accessible, and intuitive for all audiences.
- Minimal but memorable: restrained and purposeful, with subtle Retro Fusion character.
- Warmly professional: an inviting campus event platform with a refined tone.

## 2. Design Principles

- Clarity first: every interface should feel effortless to understand and navigate.
- Purposeful minimalism: remove noise, keep only what supports action and meaning.
- Subtle nostalgia: reference retro elements through tone, rhythm, and detail—not literal throwback styling.
- Consistent structure: layouts, spacing, and typography must remain predictable across features.
- Mobile-first: start from small screens and scale responsibly to desktop.
- Inclusive by default: accessible contrast, legible text, and clear interaction feedback.

## 3. Visual Identity

- Tone: quiet confidence, polished campus energy, and modern event elegance.
- Expression: balanced use of muted retro accents paired with clean, contemporary surfaces.
- Texture: soft layering and slight geometric rhythm rather than heavy decoration.
- Accent treatment: use subtle retro-inspired color sparingly to call out actions, highlights, and micro-interactions.
- Visual hierarchy: rely on spacing, typography, and restrained color to organize information.

## 4. Color Palette

- Primary Neutral: `#111827` (Primary text, top navigation, strong dark backgrounds)
- Secondary Neutral: `#F8FAFC` (Primary surface, page background, cards)
- Surface Neutral: `#FFFFFF` (Panels, cards, forms, clean surfaces)
- Shadow Neutral: `#8B95A1` (Soft dark surfaces and subtle text)
- Accent Warm: `#D97706` (Primary call-to-action, active states, highlight accents)
- Accent Cool: `#2563EB` (Secondary actions, links, informational highlights)
- Retro Shade: `#9D4EDD` (Delicate brand accent for subtle retro references)
- Support Success: `#16A34A` (Success states, confirmations)
- Support Warning: `#F59E0B` (Warnings, gentle attention)
- Support Error: `#DC2626` (Errors, destructive states)

### Usage

- Primary Neutral: use for headings, body text, navigation, and the darkest UI emphasis.
- Secondary Neutral: page background and large layout surfaces.
- Surface Neutral: cards, form surfaces, and panels.
- Accent Warm: main CTA buttons, active state borders, important badges.
- Accent Cool: secondary buttons, links, informational chips, and subtle data visualization.
- Retro Shade: subtle decorative lines, icon overlays, tag accents, and hover states.
- Support colors: reserved for feedback states only.

## 5. Typography System

### Primary font

- `Inter` — modern, geometric, and highly legible.
- Use for headings, body text, buttons, labels, and interface copy.

### Secondary font

- `Space Grotesk` — subtle nostalgic edge with clean contemporary proportions.
- Use sparingly for brand marks, banner headlines, and decorative emphasis.

### Typographic roles

- Display / Brand headline: `Space Grotesk`, 48–56px, 600–700, tight letter spacing for hero-level statements.
- Page title: `Inter`, 32px, 700.
- Section title: `Inter`, 24px, 600.
- Subsection title: `Inter`, 18px, 600.
- Body large: `Inter`, 16px, 400.
- Body regular: `Inter`, 14px, 400.
- Button / label: `Inter`, 14px, 600, uppercase letter spacing 0.08em for button labels.
- Detail / caption: `Inter`, 12px, 500.

### Text treatment

- Use a single font family per content block to maintain clarity.
- Preserve generous line height: 1.5 for body text, 1.4 for headings.
- Avoid overly condensed or decorative type for functional content.

## 6. Spacing System

- Base unit: `8px`.
- Spacing scale: 4px (micro), 8px, 16px, 24px, 32px, 40px, 48px, 64px, 80px.
- Use spacing consistently for padding, gap, margin, and layout rhythm.

### Layout guidelines

- Mobile page padding: `16px` horizontal.
- Section vertical padding: `32px` on mobile, `48px` on desktop.
- Card padding: `24px` for main cards, `16px` for compact cards.
- Form field gap: `16px` between stacked fields.
- Button group gap: `12px`.

## 7. Border Radius Rules

- Primary surfaces: `16px` for large panels and cards.
- Secondary surfaces: `12px` for nested cards, large buttons.
- Input fields and controls: `10px`.
- Micro elements: `8px` for badges and small chips.

## 8. Shadow System

- Shadow 1 (subtle surface): `0 10px 30px rgba(17, 24, 39, 0.08)`
- Shadow 2 (lifted card): `0 16px 48px rgba(17, 24, 39, 0.10)`
- Shadow 3 (hover emphasis): `0 22px 64px rgba(17, 24, 39, 0.12)`

### Usage

- Use Shadow 1 for base card layering and dropdown surfaces.
- Use Shadow 2 for featured panels, modals, and raised containers.
- Use Shadow 3 only for interactive hover or focus emphasis on cards and surfaces.

## 9. Button Variants

### Primary button

- Background: `#D97706`
- Text: `#FFFFFF`
- Border radius: `12px`
- Shadow: Shadow 1
- Usage: main CTA, submission, next step.

### Secondary button

- Background: `#FFFFFF`
- Border: `1px solid #E2E8F0`
- Text: `#111827`
- Usage: secondary actions, navigation, non-critical controls.

### Accent button

- Background: `#2563EB`
- Text: `#FFFFFF`
- Usage: supportive actions, links, less dominant CTAs.

### Ghost button

- Background: transparent
- Border: `1px solid #CBD5E1`
- Text: `#111827`
- Usage: subtle actions, tertiary controls, cancel buttons.

### Disabled state

- Background: `#F1F5F9`
- Text: `#94A3B8`
- Border: `1px solid #E2E8F0`
- Cursor: not-allowed.

## 10. Form Components

### Text fields

- Background: `#FFFFFF`
- Border: `1px solid #E2E8F0`
- Border radius: `10px`
- Padding: `16px`
- Text color: `#111827`
- Placeholder color: `#94A3B8`

### Select / dropdown

- Use the same surface, border, and radius as text fields.
- Add a clear caret icon and consistent spacing for label and field.

### Text area

- Use the same styling as text fields with a minimum height of `120px`.
- Keep line height comfortable and preserve internal padding.

### Labels

- Font: `Inter`, 14px, 600
- Color: `#111827`
- Spacing: `8px` below label before field.

### Helper text

- Font: `Inter`, 12px, 500
- Color: `#6B7280`
- Usage: supporting guidance, hints, and accessible instructions.

### Validation messages

- Error text: `#DC2626`
- Success text: `#16A34A`
- Warning text: `#F59E0B`
- Use inline validation below fields.

### Toggle / checkbox / radio

- Form controls should be generous sized for touch: minimum `40px` target.
- Apply accent warm or accent cool for active states.
- Keep labels left-aligned and close to the control.

## 11. Cards

### Card structure

- Background: `#FFFFFF`
- Border radius: `16px`
- Padding: `24px`
- Shadow: Shadow 1
- Spacing between cards: `24px`

### Card variants

- Standard card: clean surface, title, body text, and optional action area.
- Highlight card: add a subtle top accent line in `#D97706` or `#9D4EDD`.
- Compact card: `16px` padding, used for summary panels and dashboards.

### Content hierarchy

- Title: `Inter`, 18px, 600.
- Subtitle: `Inter`, 14px, 500.
- Body: `Inter`, 14px, 400.
- Action text: use accent colors for links and buttons.

## 12. Navigation Style

### Top navigation

- Background: `#FFFFFF` or slight off-white.
- Height: `64px` on desktop, `56px` on mobile.
- Spacing: `24px` horizontal padding on desktop, `16px` on mobile.
- Links: `Inter`, 14px, 600.
- Active link accent: underline or colored indicator in `#D97706`.

### Mobile navigation

- Use a clean bottom or side drawer pattern with a minimal icon row.
- Prioritize the most common tasks: Home, Events, Dashboard, Notifications.
- Keep icon labels concise and legible.

### Sidebar / secondary navigation

- Surface: `#F8FAFC`
- Border radius: `16px` for nav panel.
- Link spacing: `16px` vertical.
- Use subtle accent indicators for active section state.

## 13. Footer Style

- Background: `#111827`
- Text: `#F8FAFC`
- Accent text: `#D97706`
- Padding: `40px` top/bottom, `24px` sides.
- Layout: compact grid of links, brand signature, and legal copy.
- Keep the footer visually light with generous spacing and simple hierarchy.

## 14. Icon Style

- Weight: medium stroke or filled glyphs, balanced for readability.
- Proportions: rounded corners with subtle geometric forms.
- Line thickness: consistent across set.
- Color: `#111827` for standard icons, `#2563EB` or `#D97706` for accent states.
- Use icons as supportive UI signals, not decorative noise.

## 15. Illustration Style

- Style: minimal, flat line work with restrained color accents.
- Palette: use the brand neutrals plus one or two accent tones only.
- Composition: simple geometry and abstract layouts rather than literal illustrations.
- Purpose: reinforce content sections, spotlight features, and support onboarding.
- Avoid heavy gradients or overly playful characters; stay polished and editorial.

## 16. Animation Guidelines

- Motion should be smooth, subtle, and purposeful.
- Duration: 120–220ms for hover and tap transitions.
- Easing: use gentle curves such as `cubic-bezier(0.22, 1, 0.36, 1)` for natural interactions.
- Use motion for:
  - button hover and press states
  - card reveal and entrance transitions
  - navigation indicator movement
  - toast and modal appearance
- Avoid long, attention-grabbing animations; keep transitions discreet.

## 17. Responsive Breakpoints

- `sm`: 0px — 639px (mobile)
- `md`: 640px — 767px (large mobile / small tablet)
- `lg`: 768px — 1023px (tablet)
- `xl`: 1024px — 1279px (desktop)
- `2xl`: 1280px and above (wide desktop)

### Responsive behavior

- Mobile-first layout and interactions.
- Collapse complex navigation into simplified mobile patterns.
- Preserve spacing and readability as screens grow.
- Use card stacking on mobile and multi-column layout on desktop.

## 18. Accessibility Rules

- Maintain contrast ratio of at least 4.5:1 for body text and 3:1 for larger text.
- Ensure interactive targets are at least `44px` by `44px`.
- Support keyboard navigation, focus states, and visible outlines.
- Use aria labels and semantic markup for assistive technologies.
- Avoid relying on color alone to convey meaning.
- Provide clear error messaging and status feedback.

## 19. Tailwind Design Tokens

- `--color-base-900`: `#111827`
- `--color-base-50`: `#F8FAFC`
- `--color-surface`: `#FFFFFF`
- `--color-accent-500`: `#D97706`
- `--color-accent-700`: `#2563EB`
- `--color-accent-600`: `#9D4EDD`
- `--color-success`: `#16A34A`
- `--color-warning`: `#F59E0B`
- `--color-error`: `#DC2626`
- `--color-muted`: `#6B7280`
- `--radius-2xl`: `16px`
- `--radius-xl`: `12px`
- `--radius-lg`: `10px`
- `--radius-md`: `8px`
- `--shadow-sm`: `0 10px 30px rgba(17, 24, 39, 0.08)`
- `--shadow-md`: `0 16px 48px rgba(17, 24, 39, 0.10)`
- `--shadow-lg`: `0 22px 64px rgba(17, 24, 39, 0.12)`
- `--font-sans`: `Inter, system-ui, sans-serif`
- `--font-display`: `Space Grotesk, Inter, system-ui, sans-serif`
- `--space-1`: `4px`
- `--space-2`: `8px`
- `--space-3`: `16px`
- `--space-4`: `24px`
- `--space-5`: `32px`
- `--space-6`: `40px`
- `--space-7`: `48px`
- `--space-8`: `64px`

## 20. Do's and Don'ts

### Do

- Do use whitespace and hierarchy to separate content.
- Do keep labels concise and descriptive.
- Do use the accent palette sparingly for emphasis.
- Do prioritize readability over decoration.
- Do treat mobile as the primary experience.
- Do keep interaction states consistent.
- Do use accessible contrast and text sizing.
- Do keep retro references subtle and contextual.

### Don't

- Don’t add excessive neon, flashy gradients, or overly decorative effects.
- Don’t overcrowd interfaces with too many competing accent colors.
- Don’t rely on literal vintage motifs or overly retro graphics.
- Don’t use multiple type families for functional UI text.
- Don’t create inconsistent button and form styles.
- Don’t use tiny touch targets or dense control groups.
- Don’t hide important status feedback behind color only.

---

This document is the foundation for Pragyarambh '26 design implementation. Refer to it for visual consistency, interaction patterns, and brand expression across the platform.