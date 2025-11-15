use wasm_bindgen::prelude::*;
use syntect::easy::HighlightLines;
use syntect::highlighting::{ThemeSet, Style};
use syntect::parsing::SyntaxSet;
use syntect::html::{styled_line_to_highlighted_html, IncludeBackground};
use syntect::util::LinesWithEndings;

#[wasm_bindgen]
pub struct SyntaxHighlighter {
    syntax_set: SyntaxSet,
    theme_set: ThemeSet,
}

#[wasm_bindgen]
impl SyntaxHighlighter {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        // Set panic hook for better error messages in the browser console
        #[cfg(feature = "console_error_panic_hook")]
        console_error_panic_hook::set_once();

        Self {
            syntax_set: SyntaxSet::load_defaults_newlines(),
            theme_set: ThemeSet::load_defaults(),
        }
    }

    /// Highlight code and return HTML
    ///
    /// # Arguments
    /// * `code` - The code to highlight
    /// * `language` - Language identifier (e.g., "rust", "python", "javascript")
    /// * `theme_name` - Theme name (e.g., "base16-ocean.dark", "InspiredGitHub")
    #[wasm_bindgen]
    pub fn highlight(&self, code: &str, language: &str, theme_name: &str) -> Result<String, JsValue> {
        let syntax = self.syntax_set
            .find_syntax_by_token(language)
            .ok_or_else(|| JsValue::from_str(&format!("Language '{}' not found", language)))?;

        let theme = &self.theme_set.themes.get(theme_name)
            .ok_or_else(|| JsValue::from_str(&format!("Theme '{}' not found", theme_name)))?;

        let mut highlighter = HighlightLines::new(syntax, theme);
        let mut html = String::new();

        for line in LinesWithEndings::from(code) {
            let ranges: Vec<(Style, &str)> = highlighter
                .highlight_line(line, &self.syntax_set)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            let line_html = styled_line_to_highlighted_html(&ranges[..], IncludeBackground::Yes)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            html.push_str(&line_html);
        }

        Ok(html)
    }

    /// Get list of available languages
    #[wasm_bindgen]
    pub fn get_languages(&self) -> Vec<String> {
        self.syntax_set
            .syntaxes()
            .iter()
            .map(|s| s.name.clone())
            .collect()
    }

    /// Get list of available themes
    #[wasm_bindgen]
    pub fn get_themes(&self) -> Vec<String> {
        self.theme_set
            .themes
            .keys()
            .cloned()
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_highlight_rust() {
        let highlighter = SyntaxHighlighter::new();
        let code = "fn main() {\n    println!(\"Hello, world!\");\n}";
        let result = highlighter.highlight(code, "rust", "base16-ocean.dark");
        assert!(result.is_ok());
        assert!(result.unwrap().contains("fn"));
    }

    #[test]
    fn test_get_languages() {
        let highlighter = SyntaxHighlighter::new();
        let languages = highlighter.get_languages();
        assert!(!languages.is_empty());
        assert!(languages.iter().any(|l| l == "Rust"));
    }

    #[test]
    fn test_get_themes() {
        let highlighter = SyntaxHighlighter::new();
        let themes = highlighter.get_themes();
        assert!(!themes.is_empty());
    }
}
