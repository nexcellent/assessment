"""Core domain models for the profile system."""

from datetime import UTC
from datetime import date
from datetime import datetime
from typing import Any
from typing import Protocol
from typing import TypeVar

from pydantic import ConfigDict
from pydantic import Field
from pydantic import ValidationInfo
from pydantic import computed_field
from pydantic import field_serializer
from pydantic import field_validator
from pydantic import model_validator

from app.models.base import BaseEntity
from app.models.base import IdentifiedEntity
from app.models.enums import SkillLevel

DATE_FORMAT = "%Y-%m-%d"


def months_between(start: date, end: date | None) -> int:
    """Inclusive month count of a period, counting to today while it is still open.

    Both end months count: a project that ran through April alone lasted one month,
    not none. The document prints this figure and the model reports it, so it is
    defined here once rather than in each of them.
    """
    last = end or datetime.now(tz=UTC).date()
    return (last.year - start.year) * 12 + (last.month - start.month) + 1


def parse_date(value: str | date) -> date:
    """Read a ``YYYY-MM-DD`` string as a date; pass an existing date through."""
    if not isinstance(value, str):
        return value
    try:
        return datetime.strptime(value, DATE_FORMAT).replace(tzinfo=UTC).date()
    except ValueError:
        msg = "Invalid date format. Expected YYYY-MM-DD"
        raise ValueError(msg) from None


def parse_optional_date(value: str | date | None) -> date | None:
    """Same as :func:`parse_date`, but a blank field means there is no date.

    A cleared HTML date input arrives as an empty string. Reading that as "no
    date" is what lets someone remove an end date again.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return parse_date(value)


class PersonalInfoBase(BaseEntity):
    """PersonalInfo model for write operations (without computed fields)."""

    MANDATORY = ("first_name", "last_name", "title")

    first_name: str | None = Field(None, min_length=1, max_length=100, description="First name")
    last_name: str | None = Field(None, min_length=1, max_length=100, description="Last name")
    title: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Professional title, e.g. 'Senior Consultant'",
    )
    summary: str | None = Field(None, description="Professional summary, the paragraph that opens the profile")


class PersonalInfo(PersonalInfoBase):
    """Basic personal information with computed full name."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        """Generate full name."""
        return " ".join(part for part in (self.first_name, self.last_name) if part)

    @model_validator(mode="before")
    @classmethod
    def reject_computed_fields(cls, personal_info_obj: dict[str, Any]) -> dict[str, Any]:
        """Reject input data containing computed fields."""
        for name in cls.model_computed_fields:
            if name in personal_info_obj:
                msg = f"Computed field '{name}' should not be provided in input data"
                raise ValueError(msg)
        return personal_info_obj


class Skill(BaseEntity):
    """Individual skill with proficiency level."""

    name: str = Field(..., min_length=1, max_length=200, description="Skill name")
    level: SkillLevel | None = Field(None, description="Proficiency level; empty until it has been assessed")


class SkillCategory(IdentifiedEntity):
    """Group of related skills."""

    category_name: str = Field(..., min_length=1, max_length=100, description="Category name")
    skills: list[Skill] = Field(default_factory=list, description="Skills in this category")

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, skills: list[Skill]) -> list[Skill]:
        # Check for duplicate skill names
        names = [skill.name.lower() for skill in skills]
        if len(names) != len(set(names)):
            msg = "Duplicate skill names not allowed in same category"
            raise ValueError(msg)

        return skills


class WorkExperienceBase(IdentifiedEntity):
    """WorkExperience model for write operations (without computed fields)."""

    MANDATORY = ("company", "position", "start_date")

    company: str | None = Field(None, min_length=1, max_length=200, description="Company name")
    position: str | None = Field(None, min_length=1, max_length=200, description="Job position/title")
    start_date: date | None = Field(None, description="Employment start date")
    end_date: date | None = Field(None, description="Employment end date (None if current)")
    description: list[str] = Field(default_factory=list, description="Job responsibilities and achievements")

    @field_validator("start_date", mode="before")
    @classmethod
    def validate_start_date(cls, start_date: str | date | None) -> date | None:
        return parse_optional_date(start_date)

    @field_validator("end_date", mode="before")
    @classmethod
    def validate_end_date_format(cls, end_date: str | date | None) -> date | None:
        return parse_optional_date(end_date)

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, end_date: date | None, info: ValidationInfo) -> date | None:
        start_date = info.data.get("start_date")
        if end_date and start_date and end_date < parse_date(start_date):
            msg = "End date cannot be before start date"
            raise ValueError(msg)
        return end_date

    @field_serializer("start_date")
    def serialize_start_date(self, start_date: date | None) -> str | None:
        return start_date.strftime(DATE_FORMAT) if start_date else None

    @field_serializer("end_date")
    def serialize_end_date(self, end_date: date | None) -> str | None:
        return end_date.strftime(DATE_FORMAT) if end_date else None


class WorkExperience(WorkExperienceBase):
    """Professional work experience entry with computed current position status."""

    @computed_field
    def is_current_position(self) -> bool:
        """Check if this is a current position."""
        return self.end_date is None

    @model_validator(mode="before")
    @classmethod
    def reject_computed_fields(cls, work_experience_obj: dict[str, Any]) -> dict[str, Any]:
        """Reject input data containing computed fields."""
        if "is_current_position" in work_experience_obj:
            msg = "Computed field 'is_current_position' should not be provided in input data"
            raise ValueError(msg)
        return work_experience_obj


class Education(IdentifiedEntity):
    """Educational background entry."""

    MANDATORY = ("institution", "degree", "field_of_study", "start_date")

    institution: str | None = Field(None, min_length=1, max_length=200, description="Educational institution")
    degree: str | None = Field(None, min_length=1, max_length=200, description="Degree or qualification")
    field_of_study: str | None = Field(None, min_length=1, max_length=200, description="Field of study/major")
    start_date: date | None = Field(None, description="Education start date")
    end_date: date | None = Field(None, description="Education end date (None if ongoing)")
    description: list[str] = Field(default_factory=list, description="Additional details")

    @field_validator("start_date", mode="before")
    @classmethod
    def validate_start_date(cls, start_date_str: str | date | None) -> date | None:
        return parse_optional_date(start_date_str)

    @field_validator("end_date", mode="before")
    @classmethod
    def validate_end_date_format(cls, end_date_str: str | date | None) -> date | None:
        return parse_optional_date(end_date_str)

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, end_date: date | None, info: ValidationInfo) -> date | None:
        start_date = info.data.get("start_date")
        if end_date and start_date and end_date < parse_date(start_date):
            msg = "End date cannot be before start date"
            raise ValueError(msg)
        return end_date

    @field_serializer("start_date")
    def serialize_start_date(self, start_date: date | None) -> str | None:
        return start_date.strftime(DATE_FORMAT) if start_date else None

    @field_serializer("end_date")
    def serialize_end_date(self, end_date: date | None) -> str | None:
        return end_date.strftime(DATE_FORMAT) if end_date else None


class ProjectBase(IdentifiedEntity):
    """Project model for write operations (without computed fields)."""

    MANDATORY = ("title", "role", "start_date")

    title: str | None = Field(None, min_length=1, max_length=200, description="Project title")
    company: str | None = Field(None, max_length=200, description="Company/organization")
    role: str | None = Field(None, min_length=1, max_length=200, description="Role in the project")
    start_date: date | None = Field(None, description="Project start date")
    end_date: date | None = Field(None, description="Project end date (None if ongoing)")
    description: list[str] = Field(default_factory=list, description="Project details and achievements")
    technologies: list[Skill] = Field(default_factory=list, description="Technologies and skills used")

    @field_validator("start_date", mode="before")
    @classmethod
    def validate_start_date(cls, start_date: str | date | None) -> date | None:
        return parse_optional_date(start_date)

    @field_validator("end_date", mode="before")
    @classmethod
    def validate_end_date_format(cls, end_date: str | date | None) -> date | None:
        return parse_optional_date(end_date)

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, end_date: date | None, info: ValidationInfo) -> date | None:
        start_date = info.data.get("start_date")
        if end_date and start_date and end_date < parse_date(start_date):
            msg = "End date cannot be before start date"
            raise ValueError(msg)
        return end_date

    @field_serializer("start_date")
    def serialize_start_date(self, start_date: date | None) -> str | None:
        return start_date.strftime(DATE_FORMAT) if start_date else None

    @field_serializer("end_date")
    def serialize_end_date(self, end_date: date | None) -> str | None:
        return end_date.strftime(DATE_FORMAT) if end_date else None


class Project(ProjectBase):
    """Project experience entry with computed duration."""

    @model_validator(mode="before")
    @classmethod
    def reject_computed_fields(cls, project_obj: dict[str, Any]) -> dict[str, Any]:
        """Reject input data containing computed fields."""
        if "duration_months" in project_obj:
            msg = "Computed field 'duration_months' should not be provided in input data"
            raise ValueError(msg)
        return project_obj

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration_months(self) -> int | None:
        """Project duration in months, inclusive of both end months; None without a start."""
        return months_between(self.start_date, self.end_date) if self.start_date else None


class ProfileOverview(IdentifiedEntity):
    """Lightweight profile summary for list views.

    It carries what the profile list shows; everything else takes a fetch of the full profile.
    """

    first_name: str | None = Field(None, description="First name; empty until filled in after a CV import")
    last_name: str | None = Field(None, description="Last name; empty until filled in after a CV import")
    title: str | None = Field(None, description="Professional title; empty until filled in after a CV import")
    incomplete: bool = Field(
        default=False,
        description="Whether mandatory fields are still empty after a CV import; see Profile.missing_fields",
    )


class _Dated(Protocol):
    @property
    def start_date(self) -> date | None: ...


_DatedT = TypeVar("_DatedT", bound=_Dated)


def newest_first(entries: list[_DatedT]) -> list[_DatedT]:
    """The entries by start date, most recent first; those without a start date last."""
    return sorted(entries, key=lambda entry: (entry.start_date is not None, entry.start_date or date.min), reverse=True)


class MissingField(BaseEntity):
    """A mandatory field a CV import left empty, for the editor to point at."""

    section: str = Field(..., description="The profile section: personal_info, work_experience, education, ...")
    item_id: str | None = Field(None, description="The entry of a list section; None for personal_info")
    field: str = Field(..., description="The empty field")


# The sections whose entries have mandatory fields (``BaseEntity.MANDATORY``).
MANDATORY_LIST_SECTIONS: dict[str, tuple[str, ...]] = {
    "work_experience": WorkExperienceBase.MANDATORY,
    "education": Education.MANDATORY,
    "projects": ProjectBase.MANDATORY,
}


def missing_mandatory_fields(profile: "Profile") -> list[MissingField]:
    """Every mandatory field of the profile that is still empty, section by section."""
    missing = [MissingField(section="personal_info", field=name) for name in profile.personal_info.missing_mandatory()]
    for section in MANDATORY_LIST_SECTIONS:
        for entry in getattr(profile, section):
            missing += [
                MissingField(section=section, item_id=entry.id, field=name) for name in entry.missing_mandatory()
            ]
    return missing


class Profile(IdentifiedEntity):
    """Complete professional profile for API responses (without the store's metadata)."""

    personal_info: PersonalInfo = Field(..., description="Basic personal information")
    work_experience: list[WorkExperience] = Field(default_factory=list, description="Work history")
    education: list[Education] = Field(default_factory=list, description="Educational background")
    skill_categories: list[SkillCategory] = Field(default_factory=list, description="Skill categories")
    projects: list[Project] = Field(default_factory=list, description="Project portfolio")

    model_config = ConfigDict(
        extra="ignore",
    )  # Ignore the document store's metadata when parsing from the store

    @computed_field  # type: ignore[prop-decorator]
    @property
    def missing_fields(self) -> list[MissingField]:
        """Mandatory fields still empty after a CV import; the export waits for them."""
        return missing_mandatory_fields(self)

    @field_validator("work_experience")
    @classmethod
    def validate_work_experience(cls, work_experiences: list[WorkExperience]) -> list[WorkExperience]:
        return newest_first(work_experiences)

    @field_validator("education")
    @classmethod
    def validate_education(cls, education: list[Education]) -> list[Education]:
        return newest_first(education)

    @field_validator("projects")
    @classmethod
    def validate_projects(cls, projects: list[Project]) -> list[Project]:
        return newest_first(projects)
