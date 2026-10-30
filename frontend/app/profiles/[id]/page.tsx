import type { Metadata } from 'next';
import { notFound } from 'next/navigation';

import ProfileView from '@/components/profiles/profile-view';
import { getProfile } from '@/lib/api/profiles';

// A profile is read from the backend on every request, never at build time.
export const dynamic = 'force-dynamic';

interface ProfilePageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: ProfilePageProps): Promise<Metadata> {
  const { id } = await params;
  const profile = await getProfile(id);
  return { title: profile?.personal_info.full_name || 'Profile not found' };
}

export default async function ProfilePage({ params }: ProfilePageProps) {
  const { id } = await params;
  const profile = await getProfile(id);
  if (!profile) {
    notFound();
  }

  return <ProfileView profile={profile} />;
}
