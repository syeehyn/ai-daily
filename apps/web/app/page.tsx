import { T } from "@/components/language";
import { Button, Chip, FooterColumns } from "@/components/ui";
import { getIssues } from "@/lib/content";
import { parseDigest } from "@/lib/digest";

export default function HomePage() {
  const issues = getIssues();
  const latest = issues[0];
  const latestDigest = latest ? parseDigest(latest) : null;

  return (
    <main className="mx-auto w-full max-w-6xl px-6 pb-16 pt-10">
      <section className="rounded-2xl border border-border bg-bgMuted/50 p-8">
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight">
          <T zh="每天一张卡，先看全局，再按 topic 下钻。" en="One card each day: macro first, then topic deep dives." />
        </h1>
        <p className="mt-4 max-w-2xl text-base text-fgMuted">{latest ? `${latest.date} · ${latest.title}` : "暂无当日数据"}</p>

        {latestDigest ? (
          <div className="mt-6 rounded-xl border border-border bg-bg p-5">
            <p className="text-sm uppercase tracking-[0.1em] text-fgMuted"><T zh="当日综述" en="Today summary" /></p>
            <p className="mt-2 leading-7 text-fg">{latestDigest.highlights[0]}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Chip>{latest.papers.length} <T zh="个主题" en="topics" /></Chip>
              <Chip><T zh="含 takeaways" en="takeaways included" /></Chip>
              <Chip><T zh="晨读友好" en="morning-read friendly" /></Chip>
            </div>
          </div>
        ) : null}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Button href={latest ? `/issues/${latest.date}` : "/"}><T zh="进入今日晨读" en="Open today's brief" /></Button>
        </div>
      </section>

      {latestDigest ? (
        <section className="mt-10 rounded-xl border border-border bg-bgMuted/30 p-6">
          <h2 className="text-2xl font-semibold"><T zh="趋势观察（详细）" en="Trend watch (detailed)" /></h2>
          <div className="mt-4 space-y-3">
            {latestDigest.trends.map((item, idx) => (
              <p key={idx} className="leading-7 text-fg">• {item}</p>
            ))}
            {latestDigest.highlights.slice(1, 3).map((item, idx) => (
              <p key={`h-${idx}`} className="leading-7 text-fgMuted">{item}</p>
            ))}
          </div>
        </section>
      ) : null}

      {latest ? (
        <section className="mt-14">
          <h2 className="mb-5 text-2xl font-semibold"><T zh="今日 topic 速读" en="Today's topic quick reads" /></h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {latest.papers.map((paper) => (
              <article key={paper.id} className="rounded-xl border border-border p-5">
                <div className="mb-2 flex flex-wrap gap-2">
                  {paper.tags.slice(0, 4).map((tag) => <Chip key={tag}>{tag}</Chip>)}
                </div>
                <h3 className="text-lg font-semibold leading-tight">{paper.title}</h3>
                <p className="mt-2 text-sm text-fgMuted">{paper.authors}</p>
                <p className="mt-3 line-clamp-4 leading-7 text-fg">{paper.summary}</p>
                <div className="mt-4">
                  <Button href={`/issues/${latest.date}/${paper.id}`} variant="ghost"><T zh="阅读全文" en="Read full note" /></Button>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="mt-14">
        <h2 className="mb-5 text-2xl font-semibold"><T zh="历史综述卡片" en="Archive summary cards" /></h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {issues.map((issue) => {
            const digest = parseDigest(issue);
            return (
              <article key={issue.date} className="rounded-xl border border-border p-5">
                <p className="text-xs uppercase tracking-[0.12em] text-fgMuted">{issue.date}</p>
                <h3 className="mt-2 text-lg font-semibold">{issue.title}</h3>
                <p className="mt-3 line-clamp-3 text-sm text-fgMuted">{digest.highlights[0]}</p>
                <div className="mt-4">
                  <Button href={`/issues/${issue.date}`} variant="ghost"><T zh="查看当日综述" en="Open day digest" /></Button>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <FooterColumns />
    </main>
  );
}
