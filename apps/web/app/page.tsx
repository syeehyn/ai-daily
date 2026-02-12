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
        <p className="mb-3 text-xs uppercase tracking-[0.16em] text-fgMuted">Today’s AI Brief</p>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight">每天一张卡，先看全局，再按 topic 下钻。</h1>
        <p className="mt-4 max-w-2xl text-base text-fgMuted">
          {latest ? `${latest.date} · ${latest.title}` : "暂无当日数据"}
        </p>

        {latestDigest ? (
          <div className="mt-6 rounded-xl border border-border bg-bg p-5">
            <p className="text-sm uppercase tracking-[0.1em] text-fgMuted">当日综述</p>
            <p className="mt-2 line-clamp-3 leading-7 text-fg">{latestDigest.highlights[0]}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Chip>{latest.papers.length} topics</Chip>
              <Chip>takeaways ready</Chip>
              <Chip>blog-style read</Chip>
            </div>
          </div>
        ) : null}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Button href={latest ? `/issues/${latest.date}` : "/"}>进入今日晨读</Button>
          <Button href="https://huggingface.co/papers" variant="secondary">Browse source feed</Button>
        </div>
      </section>

      <section className="mt-14">
        <h2 className="mb-5 text-2xl font-semibold">历史综述卡片</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {issues.map((issue) => {
            const digest = parseDigest(issue);
            return (
              <article key={issue.date} className="rounded-xl border border-border p-5">
                <p className="text-xs uppercase tracking-[0.12em] text-fgMuted">{issue.date}</p>
                <h3 className="mt-2 text-lg font-semibold">{issue.title}</h3>
                <p className="mt-3 line-clamp-3 text-sm text-fgMuted">{digest.highlights[0]}</p>
                <div className="mt-4">
                  <Button href={`/issues/${issue.date}`} variant="ghost">查看当日综述</Button>
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
