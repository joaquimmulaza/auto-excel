"""Repository for CommercialProfile data access.

Follows the Repository pattern: isolates all DB queries behind a clean
interface so that domain and service layers never import ORM models directly.

GUARDRAIL: No FastAPI, no HTTP, no domain engine imports here.
           Pure DB I/O via SQLAlchemy sessions.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.infra.db.models import CommercialProfileOrm, ProfileRuleOrm


class ProfileRepository:
    """Data access layer for ``commercial_profiles`` and ``profile_rules``."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # commercial_profiles
    # ------------------------------------------------------------------

    def get_by_id(self, profile_id: uuid.UUID) -> Optional[CommercialProfileOrm]:
        """Fetch a profile by its UUID primary key."""
        return self._session.get(CommercialProfileOrm, profile_id)

    def get_by_code(self, code: str) -> Optional[CommercialProfileOrm]:
        """Fetch an active profile by its unique machine code (e.g. 'MANO')."""
        return (
            self._session.query(CommercialProfileOrm)
            .filter(
                CommercialProfileOrm.code == code.upper(),
                CommercialProfileOrm.active.is_(True),
            )
            .first()
        )

    def list_active(self) -> list[CommercialProfileOrm]:
        """Return all active commercial profiles ordered by name."""
        return (
            self._session.query(CommercialProfileOrm)
            .filter(CommercialProfileOrm.active.is_(True))
            .order_by(CommercialProfileOrm.name)
            .all()
        )

    def list_all(self) -> list[CommercialProfileOrm]:
        """Return all profiles (active and inactive) — Admin use only."""
        return (
            self._session.query(CommercialProfileOrm)
            .order_by(CommercialProfileOrm.name)
            .all()
        )

    def create(self, profile: CommercialProfileOrm) -> CommercialProfileOrm:
        """Persist a new profile and return the attached instance."""
        self._session.add(profile)
        self._session.flush()  # assign server-generated UUID without committing
        return profile

    def update(self, profile: CommercialProfileOrm) -> CommercialProfileOrm:
        """Merge and persist changes to an existing profile."""
        merged = self._session.merge(profile)
        self._session.flush()
        return merged

    def deactivate(self, profile_id: uuid.UUID) -> bool:
        """Soft-delete: mark a profile inactive. Returns True if found."""
        profile = self.get_by_id(profile_id)
        if not profile:
            return False
        profile.active = False
        self._session.flush()
        return True

    # ------------------------------------------------------------------
    # profile_rules
    # ------------------------------------------------------------------

    def get_active_rules(
        self, profile_id: uuid.UUID, version: int
    ) -> list[ProfileRuleOrm]:
        """Return all active rules for a profile at a specific version."""
        return (
            self._session.query(ProfileRuleOrm)
            .filter(
                ProfileRuleOrm.profile_id == profile_id,
                ProfileRuleOrm.version == version,
                ProfileRuleOrm.active.is_(True),
            )
            .order_by(ProfileRuleOrm.rule_code)
            .all()
        )

    def add_rule(self, rule: ProfileRuleOrm) -> ProfileRuleOrm:
        """Persist a new profile rule."""
        self._session.add(rule)
        self._session.flush()
        return rule
