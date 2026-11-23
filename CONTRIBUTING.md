# Contributing to Koipun

Thanks for helping. Koipun is a small Japanese-learning blog, and pull requests are welcome.

## Good first contributions

- **Broken links.** Many posts are from 2015 to 2019, and some of the sites they link to are gone. A PR that swaps a dead link for its Wayback Machine copy (or the page's new address) is the most useful thing you can send.
- **Accessibility.** Contrast, keyboard use, screen-reader text, alt text that doesn't describe the photo.
- **Japanese.** A wrong furigana reading, a kanji typo, a missing `lang="ja"`. Readings use the `{{< ruby "漢字" "かん|じ" >}}` shortcode.
- **Bugs.** Layout problems on a browser or screen size, a broken redirect from an old URL, a build warning.
- **The design system.** Fixes to templates, `assets/css/main.css` or the `/styleguide/` page. Read `BRAND.md` first.

## Please don't

- **Reword old posts.** They're archival: typos and opinions from 2017 stay as they were. Fix links, readings and markup, not the writing.
- **Edit the interviews.** They are other people's words, published with their permission.
- **Add JavaScript, trackers or third-party embeds.** The site ships no JavaScript, and its security policy blocks scripts.
- **Use `dark:` variants or raw hex colors** in templates. Use the semantic tokens (`text-fg`, `bg-raised`, `border-line`…), as `BRAND.md` explains.

## How to send a PR

1. Fork the repo and create a branch.
2. Install and run it:
   ```sh
   npm ci
   npm run dev      # http://localhost:1313
   ```
3. Before you push, run the same checks the deploy runs:
   ```sh
   npm run check    # class order, clean build, every legacy URL, SEO audit
   ```
   If the class order check fails, `npm run format:classes` fixes it.
4. Open the PR with a short description of what changed and why. For anything visual, include a before and after screenshot, in light and dark mode if colors changed.

For bigger changes (a new page, a new component, a redesign of something), open an issue first so we can agree on the approach before you spend time on it.

## License

By contributing, you agree that your code is released under the MIT License and that content changes (fixes to posts and pages) become part of the site's content under the same terms as the rest of it. See `LICENSE`.
