# Front-End Style & Design System Guidelines

This document outlines the visual design system, CSS architecture standards, color palette, typography, and component specs for the **Controle de Estoque** core interface. Use these rules to ensure design consistency across all existing and new pages.

---

## 1. Core Visual Philosophy

* **Clean & Minimalist:** Prioritize whitespace, clear hierarchy, and clutter-free layouts.
* **Light Theme Focus:** Soft, light-gray backgrounds (`#F4F6F8`) paired with pure white cards (`#FFFFFF`) to reduce visual noise and eye strain.
* **Modern & Subtle Utility:** Use soft drop-shadows, subtle border transitions, and rounded corners to establish depth without heavy container boundaries.

---

## 2. Global CSS Setup & Reset

All pages must include the baseline CSS reset and typography stack:

```css
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

body {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #F4F6F8;
  color: #1A202C;
}
```

---

## 3. Color Palette Specification

### Functional Colors

| Role | Color Name | Hex Code | Usage |
| :--- | :--- | :--- | :--- |
| **Page Background** | Off-White Slate | `#F4F6F8` | Main canvas background |
| **Card / Surface** | Pure White | `#FFFFFF` | Form containers, modal bodies, table cards |
| **Primary Accent** | Slate Blue | `#3182CE` | Primary buttons, active input borders, interactive focus rings |
| **Primary Hover** | Deep Slate Blue | `#2B6CB0` | Button hover and active states |
| **Disabled State** | Muted Slate | `#A0AEC0` | Disabled inputs, buttons, and inactive controls |

### Text Colors

| Role | Color Name | Hex Code | Usage |
| :--- | :--- | :--- | :--- |
| **Primary Text** | Dark Charcoal | `#1A202C` | H1/H2 titles, key values, primary content |
| **Secondary Text**| Medium Gray | `#4A5568` | Form labels, section headers, table headers |
| **Muted Text** | Light Slate | `#718096` | Subtitles, helper text, icons, placeholders |

### Feedback & Status Colors

| Role | Color Name | Hex Code | Usage |
| :--- | :--- | :--- | :--- |
| **Error Fill** | Soft Red | `#FED7D7` | Alert banner background |
| **Error Text** | Dark Red | `#C53030` | Alert text, error validation messages |
| **Success Fill** | Soft Green | `#C6F6D5` | Success banner background |
| **Success Text** | Dark Green | `#22543D` | Success alert text, active status tags |

---

## 4. Typography & Spacing Scale

### Font Sizes & Weights
* **H1 / Main Title:** `1.5rem` (`24px`), Weight: Bold (`700`), Color: `#1A202C`
* **Subtitles / Lead Text:** `0.875rem` (`14px`), Weight: Normal (`400`), Color: `#718096`
* **Form Labels:** `0.875rem` (`14px`), Weight: Semi-bold (`600`), Color: `#4A5568`
* **Input / Button Text:** `1rem` (`16px`), Weight: Regular/Semi-bold, Color: `#1A202C` / `#FFFFFF`
* **Helper / Alert Text:** `0.875rem` (`14px`), Weight: Regular (`400`)

### Spacing & Margins
* **Card Padding:** `2.5rem` (`40px`) for standalone cards; `1.5rem` (`24px`) for secondary content blocks.
* **Form Group Bottom Margin:** `1.25rem` (`20px`).
* **Element Separation:** `0.5rem` (`8px`) between labels and inputs, title and subtitle.

---

## 5. UI Elements & Components

### 5.1 Container Cards
Cards house all focused workflows (logins, form inputs, data summary boxes).

```css
.card {
  background: #FFFFFF;
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 380px; /* Standardize max-width for modal/form cards */
}
```

### 5.2 Form Inputs & Interactive Controls
Inputs use a clear border, non-intrusive placeholders, and smooth focus states.

```css
.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4A5568;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #CBD5E0;
  border-radius: 6px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  border-color: #3182CE;
}
```

### 5.3 Buttons
Primary action buttons stretch full width within form cards or align right in table toolbars.

```css
.btn-primary {
  width: 100%;
  padding: 0.75rem;
  background-color: #3182CE;
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background-color: #2B6CB0;
}

.btn-primary:disabled {
  background-color: #A0AEC0;
  cursor: not-allowed;
}
```

### 5.4 Positioned Controls (e.g., Password Visibility Toggle)
Inside inputs with embedded action icons (e.g., eye toggle, search clear icon), use a wrapper relative layout with absolute icon positioning:

```css
.input-wrapper {
  position: relative;
}

.input-wrapper input {
  padding-right: 2.5rem; /* Reserve space for icon */
}

.input-icon-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
  padding: 0;
}

.input-icon-btn:hover {
  color: #4A5568;
}
```

### 5.5 Alert & Validation Banners
Inline validation messages must be contained within rounded background blocks:

```css
.alert-error {
  display: none;
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #FED7D7;
  color: #C53030;
  border-radius: 6px;
  font-size: 0.875rem;
  text-align: center;
}
```

---

## 6. CSS Rules & Writing Conventions

1. **Box Sizing:** Always set `box-sizing: border-box` globally.
2. **Explicit Transitions:** Prefer explicit `transition: border-color 0.2s ease, background-color 0.2s ease;` over generic `all 0.2s`.
3. **No External Dependencies:** Keep utility SVGs inline or bundled via clean CSS to preserve minimalist performance.
4. **Interactive States:** Every interactive element must define explicit `:hover`, `:focus`, and `:disabled` states.