import { getBackendUrl } from '@/lib/env';
import type { Profile, ProfileOverview } from '@/models/domain';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${getBackendUrl()}/api/v1${path}`, { cache: 'no-store' });
  if (!response.ok) {
    throw new ApiError(`GET ${path} answered ${response.status}`, response.status);
  }
  return (await response.json()) as T;
}

/** Every profile overview, in the store's order. */
export async function getProfiles(): Promise<ProfileOverview[]> {
  const { profiles } = await request<{ profiles: ProfileOverview[] }>('/profiles?limit=100');
  return profiles;
}

/** One complete profile, or null when the backend knows no profile with this id. */
export async function getProfile(id: string): Promise<Profile | null> {
  try {
    const { profile } = await request<{ profile: Profile }>(`/profiles/${encodeURIComponent(id)}`);
    return profile;
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}
