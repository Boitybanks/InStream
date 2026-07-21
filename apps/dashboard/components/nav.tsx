import Link from "next/link";

const LINKS = [
  { href: "/", label: "Overview" },
  { href: "/review-queue", label: "Review Queue" },
  { href: "/rules", label: "Rule Builder" },
  { href: "/analytics", label: "Analytics" },
];

export function Nav() {
  return (
    <nav className="flex items-center gap-6 border-b border-border px-8 py-4">
      <span className="font-semibold">inStream</span>
      <div className="flex gap-4 text-sm text-foreground/60">
        {LINKS.map((link) => (
          <Link key={link.href} href={link.href} className="hover:text-foreground">
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
