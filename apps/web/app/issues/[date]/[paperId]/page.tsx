import Image from "next/image";
import { notFound } from "next/navigation";
import {
  ArticleCallout,
  ArticleCode,
  ArticleHeading,
  ArticleList,
  ArticleParagraph,
  ArticleQuote,
  FigureCaption
} from "@/components/article-primitives";
import { Button, Chip, FooterColumns, RecommendationCard, TextLink } from "@/components/ui";
import { getIssues, getPaper } from "@/lib/content";
import { parseBlocks } from "@/lib/markdown";

export default async function ArticlePage({
  params
}: {
  params: Promise<{ date: string; paperId: string }>;
}) {
  const { date, paperId } = await params;
  const result = getPaper(date, paperId);
  if (!result) return notFound();

  const { issue, paper } = result;
  const blocks = parseBlocks(paper.markdown);
  const recommendations = getIssues()
    .flatMap((item) => item.papers.map((p) => ({ ...p, date: item.date })))
    .filter((item) => !(item.date === date && item.id === paperId))
    .slice(0, 6);

  return (
    <main className="mx-auto w-full max-w-6xl px-6 pb-16 pt-8">
      <article className="mx-auto max-w-3xl">
        <p className="mb-3 text-xs uppercase tracking-[0.14em] text-fgMuted">Issue {issue.date}</p>
        <h1 className="text-4xl font-semibold tracking-tight">{paper.title}</h1>
        <p className="mt-3 text-sm text-fgMuted">{paper.authors}</p>

        <div className="mt-5 flex flex-wrap gap-2">
          {paper.tags.map((tag) => (
            <Chip key={tag}>{tag}</Chip>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Button href="/" variant="ghost">Back to archive</Button>
          {paper.url ? <TextLink href={paper.url}>Open source page</TextLink> : null}
        </div>

        {paper.image ? (
          <figure className="mt-8 overflow-hidden rounded-lg border border-border">
            <Image src={paper.image} alt={`Preview for ${paper.title}`} width={1200} height={630} className="h-auto w-full" />
            <FigureCaption>Paper image resolved by OpenClaw metadata fallback pipeline.</FigureCaption>
          </figure>
        ) : null}

        <section className="mt-8">
          {blocks.map((block, idx) => {
            const key = `${block.kind}-${idx}`;
            if (block.kind === "h2") return <ArticleHeading key={key}>{block.text}</ArticleHeading>;
            if (block.kind === "h3") return <ArticleHeading key={key} level={3}>{block.text}</ArticleHeading>;
            if (block.kind === "p") return <ArticleParagraph key={key}>{block.text}</ArticleParagraph>;
            if (block.kind === "quote") return <ArticleQuote key={key}>{block.text}</ArticleQuote>;
            if (block.kind === "callout") return <ArticleCallout key={key}>{block.text}</ArticleCallout>;
            if (block.kind === "code") return <ArticleCode key={key}>{block.text}</ArticleCode>;
            if (block.kind === "figcaption") return <FigureCaption key={key}>{block.text}</FigureCaption>;
            if (block.kind === "list") return <ArticleList key={key} items={block.items} />;
            return null;
          })}
        </section>
      </article>

      <section className="mt-16">
        <h2 className="mb-5 text-2xl font-semibold">Recommended next reads</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {recommendations.map((item) => (
            <RecommendationCard
              key={`${item.date}-${item.id}`}
              title={item.title}
              summary={item.summary}
              href={`/issues/${item.date}/${item.id}`}
              date={item.date}
            />
          ))}
        </div>
      </section>

      <FooterColumns />
    </main>
  );
}
