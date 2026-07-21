import { Card, CardTitle, CardValue } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function OverviewPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Overview</h1>
        <p className="mt-1 text-foreground/60">
          Phase 1 scaffold — these tiles are placeholders wired to nothing yet. Real data lands once{" "}
          <code>/analytics/summary</code> is called from here.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardTitle>Processed today</CardTitle>
          <CardValue>—</CardValue>
        </Card>
        <Card>
          <CardTitle>Automation rate</CardTitle>
          <CardValue>—</CardValue>
        </Card>
        <Card>
          <CardTitle>Human review queue</CardTitle>
          <CardValue>—</CardValue>
        </Card>
        <Card>
          <CardTitle>SLA breaches</CardTitle>
          <CardValue>—</CardValue>
        </Card>
      </div>

      <Card>
        <div className="flex items-center justify-between">
          <CardTitle>Platform status</CardTitle>
          <Badge>Phase 1 — Core Infrastructure</Badge>
        </div>
        <p className="mt-3 text-sm text-foreground/60">
          No customer pack is installed yet. <code>customer_packs/_template</code> documents the shape a
          real pack (starting with Discovery, in Phase 2) will follow.
        </p>
      </Card>
    </div>
  );
}
