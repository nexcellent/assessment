import ProfilesTable from '@/components/profiles/profiles-table';
import { getProfiles } from '@/lib/api/profiles';

// The list is read from the backend on every request, never at build time.
export const dynamic = 'force-dynamic';

export default async function ProfilesPage() {
  const profiles = await getProfiles();

  return (
    <div>
      <div className="mb-8">
        <p className="eyebrow">Overview</p>
        <h1 className="text-4xl text-ink sm:text-5xl">Consultant profiles</h1>
        <p className="mt-3 text-muted-foreground">
          {profiles.length} {profiles.length === 1 ? 'profile' : 'profiles'}
        </p>
      </div>
      <ProfilesTable profiles={profiles} />
    </div>
  );
}
