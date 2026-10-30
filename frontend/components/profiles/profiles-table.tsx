import Link from 'next/link';

import { Badge } from '@/components/shadcn/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/shadcn/ui/table';
import type { ProfileOverview } from '@/models/domain';

/** The profile overview as a plain table: name, title and whether the profile is complete. */
export default function ProfilesTable({ profiles }: { profiles: ProfileOverview[] }) {
  return (
    <div className="overflow-hidden rounded-md border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead>Name</TableHead>
            <TableHead>Title</TableHead>
            <TableHead className="text-right">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {profiles.length === 0 && (
            <TableRow>
              <TableCell colSpan={3} className="text-center text-muted-foreground">
                No profiles.
              </TableCell>
            </TableRow>
          )}
          {profiles.map((profile) => (
            <TableRow key={profile.id}>
              <TableCell className="font-head font-semibold text-ink">
                <Link href={`/profiles/${profile.id}`} className="hover:text-primary">
                  {[profile.first_name, profile.last_name].filter(Boolean).join(' ') || profile.id}
                </Link>
              </TableCell>
              <TableCell className="text-muted-foreground">{profile.title ?? 'Not given'}</TableCell>
              <TableCell className="text-right">
                {profile.incomplete ? (
                  <Badge variant="secondary">Incomplete</Badge>
                ) : (
                  <span className="text-muted-foreground">Complete</span>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
