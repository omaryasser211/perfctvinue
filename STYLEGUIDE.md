# Visual Style Guide

## Palette
- Primary: `#C65B7C` (rose)
- Secondary: `#7A1F3D` (deep burgundy)
- Accent: `#D4A373` (warm gold)
- Surface: `#F9F3EE` (soft cream)
- Text: `#2E2A25` (rich dark brown)
- Muted: `#6B6B6B`

## Typography
- Base family: Segoe UI, system-ui, sans-serif
- Sizes: 12, 14, 16, 18, 24, 32 px scale
- Weights: 400 regular, 600 semi-bold, 700 bold
- Line-height: 1.5 body, 1.2 headings

## Spacing
- 8px grid: 8, 16, 24, 32
- Corners: 12px inputs, 16px cards, 24px buttons
- Shadows: 0 10px 30px rgba(0,0,0,0.08)

## Components
- Buttons: pill radius, solid primary; secondary for less emphasis
- Cards: surface background, soft shadow
- Inputs: 2px border, focus with primary color
- Badges: small pills using accent color

## Accessibility
- Contrast checked: text vs surface >= 7:1, primary on white ~4.5:1
- Focus indicators: 3px outline, offset 2px
- Semantics: landmarks, aria labels for interactive elements

## Background Treatments
- Blur: apply `bg-blur` on a covering element
- Overlay: `body.bg-overlay` adds 12% dark overlay
- Grading: `body.bg-grade` warm gradient overlay
- Vignette: `body.bg-vignette` soft edge darkening

## Application
- CSS variables defined in `static/style.css`
- Chatbot palette aligned in `static/chatbot.css`

## Responsive Breakpoints
- Mobile: 360–480px – full-width cards and inputs
- Tablet: 768px – increased padding, two-column lists where applicable
- Desktop: 1024–1440px – centered content, constrained width

## Testing Results
- Layout scales at 375, 768, 1280px with consistent spacing
- Buttons remain accessible with focus-visible at all sizes
- Background options do not obstruct readability; overlay enabled by default
- Chatbot modal retains focus trap and readable contrast

## Configuration
- Use `APP_ENV` to select environment in `config/config.json`
- `OPENROUTER_API_KEY` required for chatbot API