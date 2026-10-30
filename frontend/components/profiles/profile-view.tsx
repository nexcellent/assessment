import { Briefcase, Calendar, Clock, FolderOpen, GraduationCap, Landmark } from 'lucide-react';

import { BulletList, CardBlock, EntityCard, EntityCardHeader, MetaBadge } from '@/components/profiles/entity-card';
import { Badge } from '@/components/shadcn/ui/badge';
import { formatDuration, formatPeriod, yearsOfExperience } from '@/lib/format';
import type { Profile, Skill, SkillLevel } from '@/models/domain';

/** Expert first, beginner last, the skills nobody has assessed yet at the end. */
const LEVELS: readonly (SkillLevel | null)[] = ['expert', 'advanced', 'intermediate', 'beginner', null];

const LEVEL_LABELS: Record<SkillLevel, string> = {
  expert: 'Expert',
  advanced: 'Advanced',
  intermediate: 'Intermediate',
  beginner: 'Beginner',
};

function SectionHead({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="mb-6">
      <p className="eyebrow">{eyebrow}</p>
      <h2 className="text-2xl text-ink sm:text-3xl">{title}</h2>
    </div>
  );
}

function Figure({ value, label }: { value: number; label: string }) {
  return (
    <p className="text-sm text-muted-foreground">
      <span className="font-head text-xl font-semibold text-ink">{value}</span> {label}
    </p>
  );
}

function TechnologyBadge({ skill }: { skill: Skill }) {
  return (
    <Badge variant="secondary" className="gap-1.5 px-3 py-1 text-xs font-medium">
      {skill.name}
      {skill.level && <span className="font-normal text-muted-foreground">{skill.level}</span>}
    </Badge>
  );
}

function EmptySection() {
  return <p className="text-[0.95rem] text-muted-foreground">No entries.</p>;
}

export default function ProfileView({ profile }: { profile: Profile }) {
  const person = profile.personal_info;
  const missing = profile.missing_fields.length;
  const years = yearsOfExperience(profile.work_experience);
  const skillCount = profile.skill_categories.reduce((count, category) => count + category.skills.length, 0);

  return (
    <article className="space-y-16">
      <header className="rounded-brand bg-card-dark px-7 py-10 sm:px-12 sm:py-14">
        <p className="eyebrow text-accent-bright">Consultant profile</p>
        <h1 className="text-4xl text-white sm:text-5xl">{person.full_name}</h1>
        {person.title && <p className="mt-3 font-head text-lg font-medium text-on-card">{person.title}</p>}
        {missing > 0 && (
          <p className="mt-6 inline-flex rounded-pill border border-line-on-card px-3 py-1 font-head text-[0.72rem] font-semibold uppercase tracking-[0.12em] text-on-card-muted">
            Incomplete · {missing} {missing === 1 ? 'field' : 'fields'} missing
          </p>
        )}
      </header>

      <section>
        <SectionHead eyebrow={person.first_name ? `About ${person.first_name}` : 'About'} title="Executive summary" />
        <EntityCard>
          {person.summary ? (
            <p className="max-w-3xl text-[1.05rem] leading-relaxed text-ink-soft">{person.summary}</p>
          ) : (
            <p className="text-[0.95rem] italic text-muted-foreground">No summary yet.</p>
          )}
          <div className="mt-5 flex flex-wrap gap-x-8 gap-y-2 border-t border-border pt-4">
            <Figure value={years} label={years === 1 ? 'year experience' : 'years experience'} />
            <Figure value={profile.projects.length} label={profile.projects.length === 1 ? 'project' : 'projects'} />
            <Figure value={skillCount} label={skillCount === 1 ? 'skill' : 'skills'} />
          </div>
        </EntityCard>
      </section>

      <section>
        <SectionHead eyebrow="Career" title="Work experience" />
        {profile.work_experience.length === 0 && <EmptySection />}
        <div className="space-y-[18px]">
          {profile.work_experience.map((entry) => (
            <EntityCard key={entry.id}>
              <EntityCardHeader
                icon={Briefcase}
                title={entry.position ?? 'Position not given'}
                subtitle={entry.company}
                badges={<MetaBadge icon={Calendar}>{formatPeriod(entry.start_date, entry.end_date)}</MetaBadge>}
              />
              <BulletList heading="Key responsibilities" items={entry.description} />
            </EntityCard>
          ))}
        </div>
      </section>

      <section>
        <SectionHead eyebrow="Background" title="Education" />
        {profile.education.length === 0 && <EmptySection />}
        <div className="space-y-[18px]">
          {profile.education.map((entry) => (
            <EntityCard key={entry.id}>
              <EntityCardHeader
                icon={GraduationCap}
                title={entry.degree ?? 'Degree not given'}
                subtitle={entry.field_of_study}
                badges={
                  <>
                    {entry.institution && <MetaBadge icon={Landmark}>{entry.institution}</MetaBadge>}
                    <MetaBadge icon={Calendar}>{formatPeriod(entry.start_date, entry.end_date)}</MetaBadge>
                  </>
                }
              />
              <BulletList heading="Additional information" items={entry.description} />
            </EntityCard>
          ))}
        </div>
      </section>

      <section>
        <SectionHead eyebrow="Competence" title="Skills" />
        {profile.skill_categories.length === 0 && <EmptySection />}
        <div className="grid gap-[18px] md:grid-cols-2">
          {profile.skill_categories.map((category) => (
            <EntityCard key={category.id}>
              <h3 className="text-xl text-ink">{category.category_name}</h3>
              <div className="mt-4 space-y-3">
                {LEVELS.map((level) => {
                  const skills = category.skills.filter((skill) => skill.level === level);
                  if (skills.length === 0) {
                    return null;
                  }
                  return (
                    <div key={level ?? 'unassessed'}>
                      <p className="font-head text-[0.72rem] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                        {level ? LEVEL_LABELS[level] : 'Not assessed'}
                      </p>
                      <div className="mt-1.5 flex flex-wrap gap-2">
                        {skills.map((skill) => (
                          <Badge key={skill.name} variant="outline" className="px-3 py-1 text-sm font-medium">
                            {skill.name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </EntityCard>
          ))}
        </div>
      </section>

      <section>
        <SectionHead eyebrow="References" title="Projects" />
        {profile.projects.length === 0 && <EmptySection />}
        <div className="space-y-[18px]">
          {profile.projects.map((project) => {
            const duration = formatDuration(project.duration_months);
            return (
              <EntityCard key={project.id}>
                <EntityCardHeader
                  icon={FolderOpen}
                  title={project.title ?? 'Project without a title'}
                  subtitle={[project.role, project.company].filter(Boolean).join(' · ')}
                  badges={
                    <>
                      <MetaBadge icon={Calendar}>{formatPeriod(project.start_date, project.end_date)}</MetaBadge>
                      {duration && <MetaBadge icon={Clock}>{duration}</MetaBadge>}
                    </>
                  }
                />
                <BulletList heading="Key responsibilities" items={project.description} />
                {project.technologies.length > 0 && (
                  <CardBlock heading="Technologies used">
                    <div className="mt-2 flex flex-wrap gap-2">
                      {project.technologies.map((skill) => (
                        <TechnologyBadge key={skill.name} skill={skill} />
                      ))}
                    </div>
                  </CardBlock>
                )}
              </EntityCard>
            );
          })}
        </div>
      </section>
    </article>
  );
}
