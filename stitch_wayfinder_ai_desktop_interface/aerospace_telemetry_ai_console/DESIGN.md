---
name: Aerospace Telemetry AI Console
colors:
  surface: '#f4fafd'
  surface-dim: '#d4dbdd'
  surface-bright: '#f4fafd'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eef5f7'
  surface-container: '#e8eff1'
  surface-container-high: '#e3e9eb'
  surface-container-highest: '#dde4e6'
  on-surface: '#161d1e'
  on-surface-variant: '#3c494b'
  inverse-surface: '#2b3233'
  inverse-on-surface: '#ebf2f4'
  outline: '#6c797c'
  outline-variant: '#bbc9cc'
  surface-tint: '#006874'
  primary: '#006874'
  on-primary: '#ffffff'
  primary-container: '#03c8dd'
  on-primary-container: '#004f58'
  inverse-primary: '#36d9ee'
  secondary: '#34666d'
  on-secondary: '#ffffff'
  secondary-container: '#b8ebf4'
  on-secondary-container: '#3a6c73'
  tertiary: '#855400'
  on-tertiary: '#ffffff'
  tertiary-container: '#f3a63a'
  on-tertiary-container: '#653f00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#98f0ff'
  primary-fixed-dim: '#36d9ee'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#004f58'
  secondary-fixed: '#b8ebf4'
  secondary-fixed-dim: '#9dcfd8'
  on-secondary-fixed: '#001f24'
  on-secondary-fixed-variant: '#184e55'
  tertiary-fixed: '#ffddb7'
  tertiary-fixed-dim: '#ffb95e'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f4fafd'
  on-background: '#161d1e'
  surface-variant: '#dde4e6'
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 24px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 15px
    fontWeight: '500'
    lineHeight: 20px
  body-lg:
    fontFamily: Geist
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 12px
    letterSpacing: 0.06em
  code-stream:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 0.75rem
  margin: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style
The design system establishes a mission-critical, high-density computing environment engineered for precision autonomy, complex orchestration, and cognitive leverage. Designed for technical operators, power users, and engineers, the interface eliminates decorative froth in favor of structural authority, high-contrast legibility, and telemetry-grade responsiveness.

The aesthetic fuses Brutalist technical precision with Aerospace HUD instrumentation:
- **Instrumentation Density:** High visual bandwidth utilizing deliberate grid alignment, structural hairlines, and information-rich micro-typography.
- **Instrument Reality:** Zero organic, soft-pill curves or nebulous multi-stop gradients. Mechanical discipline rules every boundary, tick mark, and status node.
- **Cognitive Clarity:** Strict semantic color usage ensures operators immediately differentiate active focus states, autonomous execution pipelines, and critical safety interrupts.

## Colors
The color architecture relies on a clean, high-contrast light canvas illuminated by precise electrical accents. 

### Surface Tiers
- **Canvas Base (`#FFFFFF`):** System background and application root window.
- **Sidebar Rail (`#F4F6F9`):** Persistent structural navigation and workspace tree.
- **Working Panel (`#FFFFFF`):** Canvas containers, split view panes, and stream docks.
- **Raised Panel / Interactive Surface (`#E9EDF2`):** Cards, dropdown menus, focused input surfaces, and module containers.

### Functional Accents
- **Sharp Cyan (`#03C8DD`):** Primary interactive elements, active rail selectors, focused telemetry nodes, cursor vectors, and primary caret indicators.
- **Muted Teal (`#4E7F87`):** Execution directives, pipeline runs, commit triggers, and secondary operational actions.
- **Amber (`#FFB043`):** Nominal telemetry states, system warnings, human-in-the-loop approval gates, and rate-limit thresholds.
- **Coral (`#FF687A`):** Critical halts, model exceptions, telemetry failure, and destructive commands.

### Boundary & Telemetry Accents
- **Structural Border (`#CBD5E1`):** Crisp 1px container delineation.
- **Telemetry Grid Line (`rgba(3, 200, 221, 0.15)`):** Coordinate grids, axis dividers, and technical alignment markers.
- **Text Primary (`#71787A`):** Primary UI labels, dynamic chat streams, and console outputs.
- **Text Secondary (`#64748B`):** System metadata, keyboard shortcuts, field titles, and hardware telemetry.

## Typography
The typographic hierarchy balances structural geometric headings with a neutral, highly readable body typeface and an uncompromising monospaced engine for telemetry, metadata, and agent tokens.

- **Headlines (`Space Grotesk`):** Delivers an architectural, aerospace command feel. Used strictly for window modules, primary cockpit status titles, and panel headers.
- **Body (`Geist`):** Delivers clean, unhindered comprehension for complex natural-language agent reasoning, synthesized documents, and conversation streams.
- **Labels & System Code (`JetBrains Mono`):** Applied to all technical micro-labels, system metrics (latency, token speed, context window allocation), status chips, and command line inputs. Micro-labels (`label-sm` and `label-md`) must always render in uppercase for telemetry authenticity.

## Layout & Spacing
Designed natively as a modular desktop command station, the layout operates on a compact 4px structural baseline grid with high-density content packing.

### Layout Model
- **Desktop Window Architecture:** Fixed application shell featuring a 32px height custom system titlebar, an 8px utility boundary, and responsive multi-pane docked splitters.
- **Grid Philosophy:** Fluid multi-column modular pane system with vertical and horizontal splitter gutters fixed at `0.75rem` (`12px`) to preserve structural containment without wasted screen space.
- **Panel Insets:** Internal panel paddings follow strict scale boundaries: micro controls use `space-xs` (4px) to `space-sm` (8px), whereas active canvas panels and stream windows use `space-lg` (16px).
- **Reflow & Breakpoints:** 
  - Standard workstation screen (`>= 1440px`): Triple-pane layout active (Navigation Rail, Workspace Terminal, Telemetry/Inspector Dock).
  - Compact display (`1024px - 1439px`): Right inspector collapses to an icon flyout dock; gutters condense to 8px.
  - Sub-compact view (`< 1024px`): Single-focus active pane with bottom slide-up command rail.

## Elevation & Depth
This design system rejects blurred, diffused drop shadows and float aesthetics in favor of high-contrast light mode tonal layering, crisp structural hairlines, and edge light insets.

- **Z-Index Tiers:**
  - `Base Floor (z-0)`: `#FFFFFF` — The canvas floor.
  - `Structural Walls (z-10)`: `#F4F6F9` & `#FFFFFF` — Inset sidebar rails, terminal backgrounds, divided by 1px borders of `#CBD5E1`.
  - `Raised Instrumentation (z-20)`: `#E9EDF2` — Module cards, tool palettes, node blocks. Borders use `#CBD5E1`. Active or hover states gain a 1px inner border highlight.
  - `Overlays & Popovers (z-30)`: `#FFFFFF` surface bound by a sharp outer border `1px solid #03C8DD` with no drop shadow, creating a HUD viewport lock.
- **Corner Tick Markers & Telemetry Lines:** Panels feature subtle pseudo-element corner ticks (`4px x 4px` sharp marks in `#03C8DD` at top-left and bottom-right corners) to emphasize precision instrumentation.

## Shapes
Geometry is strict, mechanical, and angular. Curves are restrained to functional ergonomic smoothing rather than decorative softness.

- **Corner Radii:** Set strictly to `0.25rem` (4px maximum, with 2px for micro elements) to sustain a machined-aluminum feel.
- **Chamfers & Angles:** Specialized action triggers, titlebar badges, and node anchors may utilize 45-degree chamfered corners (`clip-path: polygon(...)`) across 4px cutoffs to reinforce the aerospace HUD language.
- **Dividers:** Absolute 1px hair-lines (`#CBD5E1`) with zero edge blurring.

## Components

### Titlebar & Window Controls
- **Shell Header:** Height 32px, background `#F4F6F9`, bottom border `1px solid #CBD5E1`.
- **System Metrics:** Displays active agent node status (`SYSTEM: NOMINAL` in `label-sm`, `#FFB043`) and session ping in `JetBrains Mono`.
- **Controls:** Square 24px x 24px minimize, maximize, and close triggers. Close action switches hover state to `#FF687A` text on `#CBD5E1` background.

### Buttons & Interactive Triggers
- **Primary Operational (`#03C8DD`):** Rectangular with 3px border radius. Bold monospace or Space Grotesk text in `#71787A`. Hover triggers a crisp cyan edge-glow (`box-shadow: 0 0 0 1px #03C8DD`).
- **Secondary Execution (`#4E7F87`):** Border `1px solid #4E7F87`, background `rgba(78, 127, 135, 0.08)`, text `#71787A`. Hover fills surface to `rgba(78, 127, 135, 0.15)`.
- **Ghost Utility:** Background transparent, border `1px solid #CBD5E1`, text `#64748B`. Active focus switches border to `#03C8DD` and text to `#71787A`.

### Chips & Telemetry Status Badges
- **Form:** 18px height, 2px border radius, uppercase `label-sm` font.
- **Execution States:**
  - *Nominal:* Background `rgba(255, 176, 67, 0.1)`, text `#FFB043`, border `1px solid rgba(255, 176, 67, 0.4)`. Includes 4px static indicator square.
  - *Requires Approval:* Background `rgba(255, 176, 67, 0.1)`, text `#FFB043`, border `1px solid rgba(255, 176, 67, 0.5)`. Flashing 1Hz pulse on the square indicator.
  - *Alert:* Background `rgba(255, 104, 122, 0.1)`, text `#FF687A`, border `1px solid #FF687A`.

### Input Fields & Command Prompts
- **Surface:** `#F4F6F9` background, `1px solid #CBD5E1`, text `#71787A` in `JetBrains Mono`.
- **Focus:** Sharp `1px solid #03C8DD` with an inset `0 0 0 1px #03C8DD`. Prompt caret is an authoritative solid cyan block (`width: 7px`).
- **Telemetry Readout:** Character and context token counts positioned in bottom-right corner in `#64748B` `label-sm`.

### Cards & Module Containers
- **Construction:** Background `#FFFFFF` with `#E9EDF2` headers. Container stroke `1px solid #CBD5E1`.
- **Corner Accents:** Selected cards render micro 4px corner tick lines at top-right and bottom-left in `#03C8DD`.
- **Headers:** Inset border divider, uppercase title in `label-md` accompanied by contextual action icons.

### Navigation Rails & Node Motif
- **Compass Node Navigation:** Active workspace indicator displays a geometric radial reticle with coordinate crosshairs in `#03C8DD`.
- **Rail Items:** Height 36px, left border strip (2px) active indicator in `#03C8DD`. Inactive items render `#64748B` on transparent backgrounds; active items render `#71787A` on `#FFFFFF`.

### Telemetry Grid & Data Visualizers
- **Background Grids:** Thin technical hairlines `rgba(3, 200, 221, 0.15)` spaced at 24px intervals for canvas mapping.
- **Node Connectors:** 1px orthogonal paths in `#CBD5E1` with active data packet pulses rendered in `#03C8DD`.