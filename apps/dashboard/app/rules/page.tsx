import { Card, CardTitle } from "@/components/ui/card";

export default function RuleBuilderPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Rule Builder</h1>
      <Card>
        <CardTitle>Rules &amp; versions</CardTitle>
        <p className="mt-3 text-sm text-foreground/60">
          Placeholder — will read/write <code>GET/POST /rules</code> and{" "}
          <code>POST /rules/&#123;id&#125;/versions</code>. A visual condition-tree editor for the YAML
          DSL in <code>packages/rules</code> is the inStream Studio product line (later phase).
        </p>
      </Card>
    </div>
  );
}
