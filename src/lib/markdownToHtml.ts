import { remark } from "remark";
import remarkGfm from "remark-gfm";
import html from "remark-html";

export default async function markdownToHtml(markdown: string) {
  // remark-gfm turns "|---|---|" pipe tables into real <table> elements.
  // Without it, tables render as raw pipe-delimited text.
  const result = await remark()
    .use(remarkGfm)
    .use(html, { sanitize: false })
    .process(markdown);
  return result.toString();
}
