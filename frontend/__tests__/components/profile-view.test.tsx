import { render, screen } from '@testing-library/react';

import ProfileView from '@/components/profiles/profile-view';
import type { Profile } from '@/models/domain';

const profile: Profile = {
  id: 'jane-doe',
  personal_info: {
    first_name: 'Jane',
    last_name: 'Doe',
    title: 'Software Engineer',
    summary: 'Builds data platforms.',
    full_name: 'Jane Doe',
  },
  work_experience: [
    {
      id: 'w1',
      company: 'Tech Solutions Inc',
      position: 'Senior Software Engineer',
      start_date: '2021-01-01',
      end_date: '2024-12-31',
      description: ['Designed scalable microservices'],
      is_current_position: false,
    },
  ],
  education: [
    {
      id: 'e1',
      institution: 'Tech University',
      degree: 'Master of Science',
      field_of_study: 'Computer Science',
      start_date: '2018-09-01',
      end_date: '2020-05-31',
      description: ['Specialisation in distributed systems'],
    },
  ],
  skill_categories: [
    {
      id: 'c1',
      category_name: 'Programming Languages',
      skills: [
        { name: 'Python', level: 'expert' },
        { name: 'Go', level: null },
      ],
    },
  ],
  projects: [
    {
      id: 'p1',
      title: 'Data Processing Platform',
      company: 'Tech Solutions Inc',
      role: 'Lead Developer',
      start_date: '2023-01-01',
      end_date: '2023-06-30',
      description: ['Built a platform for automated data processing'],
      technologies: [{ name: 'Python', level: 'expert' }],
      duration_months: 6,
    },
    {
      id: 'p2',
      title: 'Undated Project',
      company: null,
      role: 'Developer',
      start_date: null,
      end_date: '2024-04-30',
      description: [],
      technologies: [],
      duration_months: null,
    },
  ],
  missing_fields: [{ section: 'projects', item_id: 'p2', field: 'start_date' }],
};

describe('ProfileView', () => {
  it('opens with the person and the executive summary with its figures', () => {
    render(<ProfileView profile={profile} />);

    expect(screen.getByRole('heading', { level: 1, name: 'Jane Doe' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: 'Executive summary' })).toBeInTheDocument();
    expect(screen.getByText('Builds data platforms.')).toBeInTheDocument();
    expect(screen.getByText('years experience')).toHaveTextContent('3 years experience');
    expect(screen.getByText('projects')).toHaveTextContent('2 projects');
    expect(screen.getByText(/1 field missing/)).toBeInTheDocument();
  });

  it('shows the stations, the education and the projects with their bullet points', () => {
    render(<ProfileView profile={profile} />);

    expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('Jan 2021 – Dec 2024')).toBeInTheDocument();
    expect(screen.getByText('Designed scalable microservices')).toBeInTheDocument();
    expect(screen.getByText('Additional information')).toBeInTheDocument();
    expect(screen.getByText('Specialisation in distributed systems')).toBeInTheDocument();
    expect(screen.getByText('6 months')).toBeInTheDocument();
    expect(screen.getByText('until Apr 2024')).toBeInTheDocument();
  });

  it('groups skills by level and lists the unassessed ones last', () => {
    render(<ProfileView profile={profile} />);

    expect(screen.getByText('Expert')).toBeInTheDocument();
    expect(screen.getByText('Not assessed')).toBeInTheDocument();
    expect(screen.getByText('Go')).toBeInTheDocument();
  });

  it('says so when a section has no entries', () => {
    render(<ProfileView profile={{ ...profile, projects: [] }} />);

    expect(screen.getByText('No entries.')).toBeInTheDocument();
  });
});
