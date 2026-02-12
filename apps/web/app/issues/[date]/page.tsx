import { notFound } from "next/navigation";
import { T } from "@/components/language";
import { Button, Chip, FooterColumns } from "@/components/ui";
import { getIssue, getIssues } from "@/lib/content";
import { parseDigest } from "@/lib/digest";

export function generateStaticParams() {
  return getIssues().map((issue) => ({ date: issue.date }));
}

export const dynamicParams = false;

export default async function IssuePage({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  const issue = getIssue(date);
  if (!issue) return notFound();

  const digest = parseDigest(issue);

  return (
    <main className="mx-auto w-full max-w-5xl px-6 pb-16 pt-10">
      <article className="mx-auto max-w-3xl">
        <p className="mb-3 text-xs uppercase tracking-[0.14em] text-fgMuted"><T zh="每日晨报" en="Daily Brief" /> · {issue.date}</p>
        <h1 className="text-4xl font-semibold tracking-tight">{issue.title}</h1>
        <p className="mt-4 text-base text-fgMuted"><T zh="给碎片时间的 AI 晨读：先看全局，再按 topic 深入。" en="Morning AI scan: macro first, then topic-by-topic details." /></p>

        <div className="mt-6">
          <Button href="/" variant="ghost"><T zh="返回首页" en="Back to landing" /></Button>
        </div>

        <section className="mt-10 rounded-xl border border-border bg-bgMuted/40 p-6">
          <h2 className="text-xl font-semibold"><T zh="今日亮点" en="Top highlights" /></h2>
          <div className="mt-4 space-y-3 text-fg">
            {digest.highlights.map((item, idx) => (
              <p key={idx} className="leading-7">{item}</p>
            ))}
          </div>
        </section>

        <section className="mt-10">
          <h2 className="text-xl font-semibold">Topic 速读与 Takeaways</h2>
          <div className="mt-5 space-y-5">
            {issue.papers.map((paper) => (
              <article key={paper.id} className="rounded-xl border border-border p-5">
                <div className="mb-2 flex flex-wrap gap-2">
                  {paper.tags.slice(0, 3).map((tag) => <Chip key={tag}>{tag}</Chip>)}
                </div>
                <h3 className="text-lg font-semibold leading-tight">{paper.title}</h3>
                <p className="mt-2 text-sm text-fgMuted">{paper.authors}</p>
                <p className="mt-3 leading-7 text-fg">{paper.summary}</p>
                <div className="mt-4">
                  <Button href={`/issues/${issue.date}/${paper.id}`}>阅读全文</Button>
                </div>
              </article>
            ))}
          </div>
        </section>

        {digest.trends.length ? (
          <section className="mt-10 rounded-xl border border-border bg-bgMuted/30 p-6">
            <h2 className="text-xl font-semibold">趋势观察</h2>
            <ul className="mt-4 list-disc space-y-2 pl-6 text-fg">
              {digest.trends.map((item, idx) => <li key={idx}>{item}</li>)}
            </ul>
          </section>
        ) : null}
      </article>

      <FooterColumns />
    </main>
  );
}
