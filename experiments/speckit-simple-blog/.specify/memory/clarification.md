# Clarifications - Simple Blog Service

## Purpose
This document records design decisions, resolved ambiguities, and trade-offs made during the specification and planning phases. It bridges the gap between "what we want" (specification) and "how we'll build it" (plan).

## Design Decisions

### 1. Static Site Generator Choice

**Question**: Which static site generator should we use?

**Options Considered**:
- **Next.js**: Popular, great TypeScript support, image optimization built-in
- **Astro**: Excellent performance, supports multiple frameworks, island architecture
- **Eleventy**: Simple, flexible, pure JavaScript, minimal overhead
- **Gatsby**: Mature, rich plugin ecosystem, GraphQL data layer

**Decision**: **Astro**

**Rationale**:
- Best performance out of the box (ships zero JS by default)
- Excellent developer experience with TypeScript
- Built-in image optimization
- Markdown support is first-class
- Component-based but framework-agnostic
- Growing ecosystem with good documentation

**Trade-offs**:
- Smaller community than Next.js
- Fewer third-party integrations than Gatsby
- Newer framework (less battle-tested)

**Documented By**: Initial specification
**Date**: 2025-11-05

---

### 2. Image Storage Strategy

**Question**: How should images be stored and served?

**Options Considered**:
- **Git Repository**: Store images directly in repo
- **Git LFS**: Use Git Large File Storage for images
- **External CDN**: Store images on Cloudinary/Imgix
- **Hybrid**: Small images in repo, large ones on CDN

**Decision**: **Git Repository with Astro Image Optimization**

**Rationale**:
- Simpler workflow: images are versioned with content
- Astro's image optimization handles resizing and formats automatically
- No external dependencies or API keys needed
- Works offline during development
- Blog images are typically not huge (under 1MB each)
- Deployment to CDN happens automatically with static assets

**Trade-offs**:
- Repository size will grow with image count
- May need to migrate to LFS if repo exceeds 1GB
- Manual image optimization before adding to repo is recommended

**Constraints**:
- Maximum image size: 2MB per image
- Recommended dimensions: 1200x800 for cover images
- Accept formats: JPG, PNG, WebP

**Documented By**: Technical planning
**Date**: 2025-11-05

---

### 3. Search Implementation

**Question**: What search implementation should we use?

**Options Considered**:
- **Client-side index (Pagefind)**: Build search index at build time, search in browser
- **Algolia**: Third-party search service, excellent UX
- **Simple grep**: Server-side search (requires backend)
- **No search**: Just use tags and archive for discovery

**Decision**: **Pagefind (client-side search index)**

**Rationale**:
- Zero-cost solution (no API fees)
- Works with static hosting
- Excellent performance for small-to-medium blogs (under 1000 posts)
- Privacy-friendly (no data sent to third parties)
- Easy integration with Astro
- Supports highlighting and snippets

**Trade-offs**:
- Search index adds to bundle size (~10KB per 100 posts)
- Less sophisticated than Algolia (no typo tolerance)
- Doesn't work without JavaScript

**Implementation Notes**:
- Pagefind runs as post-build step
- Index includes title, description, content, and tags
- Results limited to 20 per query
- Fallback: If JS disabled, show tag-based navigation

**Documented By**: Feature analysis
**Date**: 2025-11-05

---

### 4. Dark Mode Support

**Question**: Should the blog support dark mode?

**Options Considered**:
- **System preference only**: Respect OS dark mode setting
- **Manual toggle**: Let user choose independent of system
- **Both**: Toggle with system preference as default
- **No dark mode**: Light mode only

**Decision**: **Both (manual toggle with system preference default)**

**Rationale**:
- User preference is important for reading experience
- Many developers (target audience) prefer dark mode
- Modern browsers support prefers-color-scheme
- Low implementation cost with CSS variables
- Improves accessibility for light-sensitive users

**Implementation Details**:
- CSS custom properties for color scheme
- Toggle button in header
- Preference saved to localStorage
- Default to system preference on first visit
- Smooth transition between modes (200ms)

**Colors**:
```css
/* Light mode */
--bg: #ffffff;
--text: #1a1a1a;
--accent: #0066cc;

/* Dark mode */
--bg: #1a1a1a;
--text: #e5e5e5;
--accent: #4da6ff;
```

**Documented By**: UX planning
**Date**: 2025-11-05

---

### 5. Homepage Layout

**Question**: Should there be a homepage hero section or just a post list?

**Options Considered**:
- **Hero + recent posts**: Large header with about/bio, then posts
- **Just recent posts**: Simple list of recent posts, no hero
- **Featured post + list**: One large featured post, then smaller list
- **Grid layout**: Card-based grid of recent posts

**Decision**: **Simple header + recent posts list**

**Rationale**:
- Aligns with "simplicity first" principle
- Faster to load (less content above fold)
- Better for ADHD-friendly design (less visual distraction)
- Content is king: get to posts quickly
- About page exists separately if readers want bio

**Layout Details**:
- Small header with blog title and tagline
- Navigation menu (Home, Archive, Tags, About, Search)
- Recent posts as cards (title, date, excerpt, tags, reading time)
- 10 posts per page with pagination
- Sidebar is optional (can be added later)

**Responsive Behavior**:
- Mobile: Single column, full-width cards
- Tablet: Single column, max-width 700px centered
- Desktop: Single column, max-width 800px centered

**Documented By**: Design specification
**Date**: 2025-11-05

---

### 6. Code Syntax Highlighting

**Question**: Which code syntax highlighting library should we use?

**Options Considered**:
- **Prism.js**: Popular, many themes, plugins available
- **Highlight.js**: Auto language detection, zero config
- **Shiki**: Uses VS Code themes, excellent syntax accuracy
- **None**: Basic `<pre><code>` without highlighting

**Decision**: **Shiki**

**Rationale**:
- Uses actual VS Code grammar definitions (most accurate)
- Static generation: highlighting happens at build time (zero runtime JS)
- Beautiful themes out of the box
- TypeScript support is excellent
- Works perfectly with Astro's markdown pipeline

**Configuration**:
- Theme: "github-dark" for dark mode, "github-light" for light mode
- Line numbers: Optional (enabled via code fence metadata)
- Line highlighting: Support for highlighting specific lines
- Language support: Auto-detect or specify in code fence

**Example Usage**:
````markdown
```typescript {2,5-7}
function greet(name: string): string {
  return `Hello, ${name}!`; // This line will be highlighted
}

// These lines will be highlighted
const greeting = greet("World");
console.log(greeting);
```
````

**Documented By**: Technical specification
**Date**: 2025-11-05

---

### 7. RSS Feed Format

**Question**: Should we generate RSS, Atom, or both?

**Options Considered**:
- **RSS 2.0**: Most popular, widely supported
- **Atom**: More modern, better specification
- **JSON Feed**: Modern alternative, simpler parsing
- **All three**: Maximum compatibility

**Decision**: **RSS 2.0 + JSON Feed**

**Rationale**:
- RSS 2.0: Universal support in feed readers
- JSON Feed: Easy for developers to parse, modern apps support it
- Atom: Less popular, RSS 2.0 covers most use cases
- Generating both adds minimal build time

**Feed Content**:
- Include full post content (not just excerpt)
- Images use absolute URLs
- Include publication date, author, categories (tags)
- Update feed on any post change
- Maximum 50 most recent posts in feed

**Feed URLs**:
- RSS: `/rss.xml`
- JSON Feed: `/feed.json`

**Documented By**: Content delivery planning
**Date**: 2025-11-05

---

### 8. Performance Budget

**Question**: What specific performance targets should we enforce?

**Decision**: **Hard performance budgets in CI/CD**

**Budgets**:
| Metric | Target | Maximum | Failure Threshold |
|--------|--------|---------|-------------------|
| HTML per page | 30KB | 50KB | 75KB |
| CSS bundle | 20KB | 30KB | 50KB |
| JS bundle (if any) | 50KB | 100KB | 150KB |
| Images (optimized) | 100KB | 200KB | 500KB |
| Total page weight | 200KB | 400KB | 600KB |
| Time to Interactive | 2.5s | 3.5s | 5s |
| Lighthouse Performance | 95 | 90 | 85 |

**Enforcement**:
- Lighthouse CI runs on every pull request
- Build fails if budgets exceeded
- Budget report posted as PR comment
- Exception process: Document reason in PR description

**Documented By**: Performance planning
**Date**: 2025-11-05

---

### 9. Deployment Strategy

**Question**: Which hosting platform should be the primary target?

**Options Considered**:
- **Netlify**: Excellent DX, generous free tier, preview deployments
- **Vercel**: Similar to Netlify, great Next.js support (though we're using Astro)
- **GitHub Pages**: Free, integrated with GitHub, simple
- **Cloudflare Pages**: Fast global CDN, generous limits

**Decision**: **Netlify (primary) + GitHub Pages (fallback)**

**Rationale**:
- Netlify has best developer experience for static sites
- Automatic preview deployments for PRs
- Form handling and serverless functions available if needed later
- GitHub Pages as fallback ensures vendor independence
- Both support custom domains and HTTPS

**Deployment Workflow**:
1. Push to main branch
2. Netlify detects push
3. Runs build command: `npm run build`
4. Deploys to production if build succeeds
5. GitHub Actions also builds and deploys to GitHub Pages as backup

**Environment Variables** (if needed):
- `NODE_ENV=production`
- `SITE_URL=https://yourblog.com`

**Documented By**: Infrastructure planning
**Date**: 2025-11-05

---

## Assumptions

### Content Volume
- Assumed blog will have 1-100 posts initially
- Growth rate: 1-4 posts per month
- Search performance tuned for under 500 posts
- Can scale to 1000+ posts with minor optimizations

### Technical Environment
- Readers use modern browsers (last 2 versions)
- Writer has access to text editor and git
- Writer comfortable with basic command line
- Development machine has Node.js 18+ installed

### Content Types
- Primarily text-based blog posts
- Occasional images (1-3 per post)
- Code snippets in posts are common
- No video hosting (external embeds only)
- No podcast/audio hosting (external embeds only)

## Constraints Accepted

### Technical Debt
- **Acknowledged**: Using git for content means non-technical collaborators need git training
- **Mitigation**: Create clear documentation and git aliases for common operations

### Scalability Limits
- **Acknowledged**: Client-side search won't scale beyond ~1000 posts
- **Mitigation**: Re-evaluate search solution if blog reaches 500+ posts

### Browser Support
- **Acknowledged**: Dark mode toggle requires JavaScript, won't work in no-JS browsers
- **Mitigation**: System preference still works via CSS media query

## Questions for Future Clarification

### Deferred Decisions
1. **Analytics**: Which privacy-friendly analytics? (Plausible, Fathom, Simple Analytics, or none?)
2. **Comments**: Add comments later? If yes, which service? (Utterances, Giscus, Webmentions?)
3. **Newsletter**: Integrate newsletter signup? Which service? (ConvertKit, Buttondown, Substack?)
4. **Related Posts Algorithm**: Simple tag-based or more sophisticated content similarity?
5. **Multi-author Support**: Currently single author, but structure should allow multiple authors in future

### Future Enhancements
- Series/collections (multi-part posts grouped together)
- Code block copy button
- Reading progress indicator
- Estimated reading time accuracy improvements
- Table of contents sticky positioning on desktop

---

**Last Updated**: 2025-11-05
**Version**: 1.0.0
**Status**: 🧪 Experimental
**Next Review**: Before implementation phase
