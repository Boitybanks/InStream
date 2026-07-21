import { Card, CardTitle } from "@/components/ui/card";

export default function AnalyticsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Analytics</h1>
      <Card>
        <CardTitle>SLA, automation rate &amp; exceptions</CardTitle>
        <p className="mt-3 text-sm text-foreground/60">
          Placeholder — will chart <code>GET /analytics/summary</code>.
        </p>
      </Card>
    </div>
  );
}
