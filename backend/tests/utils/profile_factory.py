"""Centralized factory for creating consistent test profile data."""

from pathlib import Path
from typing import Any

from app.models.profile import Profile

# The profile documents the application loads at start-up (``fixtures/profiles`` at the repository root).
FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "profiles"


class ProfileTestDataFactory:
    """Test profiles with consistent content, as stored documents or as validated models."""

    @staticmethod
    def create_document(profile_id: str = "test-profile", **overrides: Any) -> dict[str, Any]:
        """A complete profile document with one entry per section; ``overrides`` replace whole sections."""
        document: dict[str, Any] = {
            "id": profile_id,
            "personal_info": {
                "first_name": "Jane",
                "last_name": "Doe",
                "title": "Software Engineer",
                "summary": "Experienced software engineer specialising in cloud platforms.",
            },
            "work_experience": [
                {
                    "id": "work-1",
                    "company": "Tech Solutions Inc",
                    "position": "Senior Software Engineer",
                    "start_date": "2022-01-01",
                    "end_date": None,
                    "description": ["Designed scalable microservices"],
                }
            ],
            "education": [
                {
                    "id": "edu-1",
                    "institution": "Tech University",
                    "degree": "Master of Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2018-09-01",
                    "end_date": "2020-05-31",
                    "description": ["Specialisation in distributed systems"],
                }
            ],
            "skill_categories": [
                {
                    "id": "skill-cat-1",
                    "category_name": "Programming Languages",
                    "skills": [{"name": "Python", "level": "expert"}, {"name": "TypeScript", "level": "advanced"}],
                }
            ],
            "projects": [
                {
                    "id": "proj-1",
                    "title": "Data Processing Platform",
                    "company": "Tech Solutions Inc",
                    "role": "Lead Developer",
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-30",
                    "description": ["Built a platform for automated data processing"],
                    "technologies": [{"name": "Python", "level": "expert"}],
                }
            ],
        }
        document.update(overrides)
        return document

    @staticmethod
    def create_profile(profile_id: str = "test-profile", **overrides: Any) -> Profile:
        """The same profile as a validated model."""
        return Profile.model_validate(ProfileTestDataFactory.create_document(profile_id, **overrides))
