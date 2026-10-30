/**
 * Domain models, as the backend serves them (`backend/app/models/profile.py`).
 *
 * Dates are ISO strings (`YYYY-MM-DD`). `full_name`, `is_current_position`,
 * `duration_months` and `missing_fields` are computed by the backend on read.
 */

export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export interface Skill {
  name: string;
  /** Empty until the level has been assessed. */
  level: SkillLevel | null;
}

export interface SkillCategory {
  id: string;
  category_name: string;
  skills: Skill[];
}

export interface WorkExperience {
  id: string;
  company: string | null;
  position: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string[];
  is_current_position: boolean;
}

export interface Education {
  id: string;
  institution: string | null;
  degree: string | null;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string[];
}

export interface Project {
  id: string;
  title: string | null;
  company: string | null;
  role: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string[];
  technologies: Skill[];
  /** Inclusive of both end months; null while the start date is missing. */
  duration_months: number | null;
}

export interface PersonalInfo {
  first_name: string | null;
  last_name: string | null;
  title: string | null;
  summary: string | null;
  full_name: string;
}

/** A mandatory field a CV import left empty, as the backend reports it on the profile. */
export interface MissingField {
  section: string;
  item_id: string | null;
  field: string;
}

export interface Profile {
  id: string;
  personal_info: PersonalInfo;
  work_experience: WorkExperience[];
  education: Education[];
  skill_categories: SkillCategory[];
  projects: Project[];
  missing_fields: MissingField[];
}

export interface ProfileOverview {
  id: string;
  first_name: string | null;
  last_name: string | null;
  title: string | null;
  incomplete: boolean;
}
