# 🕸 WebAssembly Experiments Collection

**Status:** 🧪 Experimental Series | **Tech:** Rust → WASM | **Time:** 2-3 weeks

## Overview

Bridge between Rust learning and web development with hands-on WASM mini-experiments.

## Experiments

### 1. Image Processor 🖼️

Real-time image filters in the browser.

```bash
cd image-processor
wasm-pack build --target web
```

**Features:**
- Grayscale, sepia, blur filters
- Edge detection
- Color adjustments
- Performance: ~60 FPS

### 2. Markdown Parser 📝

Fast markdown → HTML converter.

```bash
cd markdown-parser
wasm-pack build --target web
```

**Features:**
- CommonMark compliant
- Syntax highlighting
- Table support
- ~10x faster than pure JS

### 3. Game of Life 🎮

Conway's Game of Life with WASM performance.

```bash
cd game-of-life
wasm-pack build --target web
```

**Features:**
- 256x256 grid @ 60 FPS
- Pattern library
- Save/load states
- Color themes

### 4. Syntax Validator ✅

Fast syntax validation for multiple languages.

```bash
cd syntax-validator
wasm-pack build --target web
```

**Features:**
- JSON, YAML, TOML validation
- Real-time error highlighting
- Auto-fix suggestions
- Zero dependencies

## Shared Structure

```
each-experiment/
├── Cargo.toml
├── src/lib.rs
├── web/index.html
└── README.md
```

## Learning Path

1. Start with Image Processor (visual results)
2. Move to Markdown Parser (practical use)
3. Game of Life (algorithms + optimization)
4. Syntax Validator (complex logic)

Each builds on previous lessons!
