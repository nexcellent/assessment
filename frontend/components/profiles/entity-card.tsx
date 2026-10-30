import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

import { cn } from '@/lib/shadcn/utils';

/** The frame every profile entry is drawn in: a white card with the hairline border. */
export function EntityCard({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('rounded-md border border-border bg-card p-6 sm:p-7', className)}>{children}</div>;
}

interface EntityCardHeaderProps {
  icon: LucideIcon;
  title: ReactNode;
  /** The line under the title: company, field of study, role. */
  subtitle?: ReactNode;
  /** The row of metadata pills. Use `MetaBadge` for the individual ones. */
  badges?: ReactNode;
}

/** Icon tile, title, subtitle and the metadata row, the shape the entry cards share. */
export function EntityCardHeader({ icon: Icon, title, subtitle, badges }: EntityCardHeaderProps) {
  return (
    <div className="flex items-start gap-4">
      <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-sm border border-border bg-muted text-ink-soft">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="text-xl leading-tight text-ink">{title}</h3>
        {subtitle && <p className="mt-1 font-head text-[0.95rem] font-medium text-ink-soft">{subtitle}</p>}
        {badges && <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">{badges}</div>}
      </div>
    </div>
  );
}

/** One pill in the metadata row. */
export function MetaBadge({ icon: Icon, children }: { icon?: LucideIcon; children: ReactNode }) {
  return (
    <div className="flex items-center gap-1.5 rounded-sm border border-border bg-muted px-2.5 py-1">
      {Icon && <Icon className="h-3.5 w-3.5" aria-hidden="true" />}
      <span className="font-medium">{children}</span>
    </div>
  );
}

/** A rule and a small caps heading above whatever a card lists below its header. */
export function CardBlock({ heading, children }: { heading: string; children: ReactNode }) {
  return (
    <div className="mt-5 border-t border-border pt-4">
      <p className="font-head text-[0.72rem] font-semibold uppercase tracking-[0.12em] text-muted-foreground">{heading}</p>
      {children}
    </div>
  );
}

/** The bullet points of an entry under their heading, or nothing while there are none. */
export function BulletList({ heading, items }: { heading: string; items: string[] }) {
  const written = items.filter((item) => item.trim());
  if (written.length === 0) {
    return null;
  }
  return (
    <CardBlock heading={heading}>
      <ul className="mt-2 space-y-2">
        {written.map((bullet) => (
          <li key={bullet} className="flex items-start gap-2 text-[0.95rem] leading-relaxed text-ink-soft">
            <span aria-hidden="true" className="text-muted-foreground">
              •
            </span>
            <span className="flex-1">{bullet}</span>
          </li>
        ))}
      </ul>
    </CardBlock>
  );
}
