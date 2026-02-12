export type Block =
  | { kind: "h2" | "h3" | "p" | "quote" | "callout" | "code" | "figcaption"; text: string }
  | { kind: "list"; items: string[] };

export function parseBlocks(markdown: string): Block[] {
  const lines = markdown.split("\n");
  const blocks: Block[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i].trim();
    if (!line) {
      i += 1;
      continue;
    }

    if (line.startsWith("### ")) {
      blocks.push({ kind: "h3", text: line.slice(4) });
      i += 1;
      continue;
    }
    if (line.startsWith("## ")) {
      blocks.push({ kind: "h2", text: line.slice(3) });
      i += 1;
      continue;
    }
    if (line.startsWith("> [!NOTE]")) {
      blocks.push({ kind: "callout", text: line.replace("> [!NOTE]", "").trim() });
      i += 1;
      continue;
    }
    if (line.startsWith("> ")) {
      blocks.push({ kind: "quote", text: line.slice(2) });
      i += 1;
      continue;
    }
    if (line.startsWith("```")) {
      const code: string[] = [];
      i += 1;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        code.push(lines[i]);
        i += 1;
      }
      blocks.push({ kind: "code", text: code.join("\n") });
      i += 1;
      continue;
    }
    if (line.startsWith("*Figure:")) {
      blocks.push({ kind: "figcaption", text: line.replace("*Figure:", "").trim() });
      i += 1;
      continue;
    }
    if (line.startsWith("- ")) {
      const items: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("- ")) {
        items.push(lines[i].trim().slice(2));
        i += 1;
      }
      blocks.push({ kind: "list", items });
      continue;
    }

    blocks.push({ kind: "p", text: line.replace(/\*\*/g, "") });
    i += 1;
  }

  return blocks;
}
