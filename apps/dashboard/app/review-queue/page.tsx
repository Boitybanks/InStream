import { Card, CardTitle } from "@/components/ui/card";

export default function ReviewQueuePage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Review Queue</h1>
      <Card>
        <CardTitle>ROUTED_REVIEW workflow runs</CardTitle>
        <p className="mt-3 text-sm text-foreground/60">
          Placeholder — will list <code>GET /workflow-runs?state=ROUTED_REVIEW</code> once the API client
          is wired up in Phase 3.
        </p>
      </Card>
    </div>
  );
}
