# Mem.AI to Obsidian

JSON Notes conversion tool from Mem.AI JSON format to Obsidian-friendly .md files. 

Features:

- creates .md files for each entry in the JSON
- extracts `tags` from the second line of each entry into frontmatter
- adds `created` and `updated` attributes to frontmatter
- uses the note title as filename
- strips the heading (h1) title from the note so it doesn't show up as duplicated
- skips empty notes or notes that only have the title and no content
- downloads any embedded images into a local folder and updates the Markdown links
- fixes image extensions (they have a hash added)

# License

See the [LICENSE](./LICENSE) file.
