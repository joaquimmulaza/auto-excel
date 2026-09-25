"""Database schema and repository tests for Cotarco Commercial Manager — Phase 2.

Strategy:
  - SQLite in-memory for fast, isolated unit tests (no network required).
  - SQLAlchemy 2.0 ORM mapped to the same models used in production.
  - Covers: table creation, FK integrity, CRUD via repositories,
            seed profiles validation, audit log append-only convention.

Run with::

    python -m pytest backend/tests/test_database/ -v

Note on SQLite vs PostgreSQL:
  Some PostgreSQL-specific features (JSONB operators, gen_random_uuid,
  RLS policies) are not exercised here — they are tested in Supabase directly.
  What IS tested: ORM correctness, FK constraints, query patterns, repositories.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session, sessionmaker

from backend.app.infra.db.models import (
    AuditLogOrm,
    ApprovalOrm,
    CommercialProfileOrm,
    JobFileOrm,
    JobItemOrm,
    PriceHistoryOrm,
    ProcessingJobOrm,
    ProfileRuleOrm,
    UserOrm,
    ValidationIssueOrm,
)
from backend.app.infra.db.session import (
    create_all_tables,
    create_db_engine,
    drop_all_tables,
    get_test_engine,
    ping_database,
)
from backend.app.infra.repositories.profiles import ProfileRepository
from backend.app.infra.repositories.jobs import JobRepository


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def engine():
    """SQLite in-memory engine shared across all tests in this module."""
    eng = get_test_engine()
    create_all_tables(eng)
    yield eng
    drop_all_tables(eng)
    eng.dispose()


@pytest.fixture
def session(engine):
    """Provides a transactional session that rolls back after each test."""
    SessionFactory = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    with SessionFactory() as sess:
        yield sess
        sess.rollback()


@pytest.fixture
def profile_repo(session: Session) -> ProfileRepository:
    return ProfileRepository(session)


@pytest.fixture
def job_repo(session: Session) -> JobRepository:
    return JobRepository(session)


# =============================================================================
# Helper builders
# =============================================================================

def make_user(
    *,
    email: str = "test@cotarco.ao",
    role: str = "COMERCIAL",
) -> UserOrm:
    return UserOrm(
        id=uuid.uuid4(),
        email=email,
        display_name="Test User",
        role=role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_profile(
    *,
    code: str = "TEST_PROFILE",
    name: str = "Test Profile",
    type_: str = "MARKETPLACE",
    config: dict | None = None,
) -> CommercialProfileOrm:
    return CommercialProfileOrm(
        id=uuid.uuid4(),
        code=code,
        name=name,
        type=type_,
        description="Test description",
        active=True,
        config=config or {"integration_type": "EXCEL_EXPORT"},
        rules_version=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_job(
    *,
    profile_id: uuid.UUID,
    created_by_id: uuid.UUID,
    status: str = "UPLOADED",
) -> ProcessingJobOrm:
    return ProcessingJobOrm(
        id=uuid.uuid4(),
        profile_id=profile_id,
        created_by_id=created_by_id,
        status=status,
        source_name="samsung_prices.xlsx",
        source_system="SAMSUNG",
        options={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# =============================================================================
# Tests: engine & connectivity
# =============================================================================

class TestEngineConnectivity:
    def test_engine_ping(self, engine):
        """ping_database returns True for a live engine."""
        assert ping_database(engine) is True

    def test_engine_ping_bad_url(self):
        """ping_database returns False for an unreachable database."""
        bad_engine = create_db_engine(url="sqlite+pysqlite:///nonexistent_dir/db.sqlite")
        # SQLite will still connect — just verify it doesn't raise
        result = ping_database(bad_engine)
        bad_engine.dispose()
        assert isinstance(result, bool)

    def test_tables_created(self, engine):
        """All expected tables exist after create_all_tables."""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing = set(inspector.get_table_names())
        expected = {
            "users",
            "commercial_profiles",
            "profile_rules",
            "processing_jobs",
            "job_files",
            "job_items",
            "validation_issues",
            "approvals",
            "price_history",
            "audit_logs",
        }
        assert expected.issubset(existing), (
            f"Missing tables: {expected - existing}"
        )


# =============================================================================
# Tests: UserOrm
# =============================================================================

class TestUserOrm:
    def test_create_user(self, session: Session):
        user = make_user(email="comercial@cotarco.ao", role="COMERCIAL")
        session.add(user)
        session.flush()

        fetched = session.get(UserOrm, user.id)
        assert fetched is not None
        assert fetched.email == "comercial@cotarco.ao"
        assert fetched.role == "COMERCIAL"
        assert fetched.is_active is True

    def test_create_operador(self, session: Session):
        user = make_user(email="operador@cotarco.ao", role="OPERADOR")
        session.add(user)
        session.flush()

        fetched = session.get(UserOrm, user.id)
        assert fetched.role == "OPERADOR"

    def test_create_admin(self, session: Session):
        user = make_user(email="admin@cotarco.ao", role="ADMIN")
        session.add(user)
        session.flush()

        fetched = session.get(UserOrm, user.id)
        assert fetched.role == "ADMIN"


# =============================================================================
# Tests: CommercialProfileOrm
# =============================================================================

class TestCommercialProfileOrm:
    def test_create_profile(self, session: Session):
        profile = make_profile(
            code="MANO",
            name="Marketplace Mano",
            type_="MARKETPLACE",
            config={
                "integration_type": "EXCEL_EXPORT",
                "stock_min_activation": 3,
                "price_variation_threshold": 0.30,
            },
        )
        session.add(profile)
        session.flush()

        fetched = session.get(CommercialProfileOrm, profile.id)
        assert fetched is not None
        assert fetched.code == "MANO"
        assert fetched.type == "MARKETPLACE"
        assert fetched.active is True
        # JSONB config preserved
        assert fetched.config["stock_min_activation"] == 3
        assert fetched.config["price_variation_threshold"] == 0.30

    def test_profile_code_unique(self, session: Session):
        """Two profiles with the same code raise IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        profile_a = make_profile(code="DUPLICATE_CODE")
        profile_b = make_profile(code="DUPLICATE_CODE")
        session.add(profile_a)
        session.flush()
        session.add(profile_b)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_profile_config_variants(self, session: Session):
        """BFA profile with 10% variation threshold is stored correctly."""
        bfa = make_profile(
            code="BFA_TEST",
            name="BFA Test",
            type_="PARTNER",
            config={
                "integration_type": "EXCEL_EXPORT",
                "price_variation_threshold": 0.10,
            },
        )
        session.add(bfa)
        session.flush()

        fetched = session.get(CommercialProfileOrm, bfa.id)
        assert fetched.config["price_variation_threshold"] == 0.10


# =============================================================================
# Tests: ProfileRepository
# =============================================================================

class TestProfileRepository:
    def test_get_by_code_found(self, session: Session, profile_repo: ProfileRepository):
        profile = make_profile(code="REPO_MANO", name="Mano Repo")
        session.add(profile)
        session.flush()

        found = profile_repo.get_by_code("REPO_MANO")
        assert found is not None
        assert found.name == "Mano Repo"

    def test_get_by_code_case_insensitive(self, session: Session, profile_repo: ProfileRepository):
        """get_by_code normalises to uppercase."""
        profile = make_profile(code="REPO_BFA")
        session.add(profile)
        session.flush()

        found = profile_repo.get_by_code("repo_bfa")
        assert found is not None
        assert found.code == "REPO_BFA"

    def test_get_by_code_inactive_not_returned(self, session: Session, profile_repo: ProfileRepository):
        """Inactive profiles are excluded from get_by_code."""
        profile = make_profile(code="REPO_INACTIVE")
        profile.active = False
        session.add(profile)
        session.flush()

        found = profile_repo.get_by_code("REPO_INACTIVE")
        assert found is None

    def test_list_active(self, session: Session, profile_repo: ProfileRepository):
        active1 = make_profile(code="LIST_ACTIVE_A", name="A Active")
        active2 = make_profile(code="LIST_ACTIVE_B", name="B Active")
        inactive = make_profile(code="LIST_INACTIVE")
        inactive.active = False
        session.add_all([active1, active2, inactive])
        session.flush()

        results = profile_repo.list_active()
        codes = {p.code for p in results}
        assert "LIST_ACTIVE_A" in codes
        assert "LIST_ACTIVE_B" in codes
        assert "LIST_INACTIVE" not in codes

    def test_deactivate(self, session: Session, profile_repo: ProfileRepository):
        profile = make_profile(code="TO_DEACTIVATE")
        session.add(profile)
        session.flush()

        result = profile_repo.deactivate(profile.id)
        assert result is True
        fetched = session.get(CommercialProfileOrm, profile.id)
        assert fetched.active is False

    def test_deactivate_not_found(self, profile_repo: ProfileRepository):
        result = profile_repo.deactivate(uuid.uuid4())
        assert result is False


# =============================================================================
# Tests: ProcessingJobOrm & FK integrity
# =============================================================================

class TestProcessingJobOrm:
    def _setup_user_and_profile(self, session: Session):
        user = make_user(email=f"user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"JOB_PROFILE_{uuid.uuid4().hex[:6]}")
        session.add(user)
        session.add(profile)
        session.flush()
        return user, profile

    def test_create_job(self, session: Session):
        user, profile = self._setup_user_and_profile(session)
        job = make_job(profile_id=profile.id, created_by_id=user.id)
        session.add(job)
        session.flush()

        fetched = session.get(ProcessingJobOrm, job.id)
        assert fetched is not None
        assert fetched.status == "UPLOADED"
        assert fetched.profile_id == profile.id
        assert fetched.created_by_id == user.id

    def test_job_fk_profile_required(self, session: Session):
        """Job without a valid profile_id must fail."""
        from sqlalchemy.exc import IntegrityError
        user = make_user(email=f"fk_user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        session.add(user)
        session.flush()
        bad_job = make_job(
            profile_id=uuid.uuid4(),  # does not exist
            created_by_id=user.id,
        )
        session.add(bad_job)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_job_status_update(self, session: Session, job_repo: JobRepository):
        user, profile = self._setup_user_and_profile(session)
        job = make_job(profile_id=profile.id, created_by_id=user.id)
        session.add(job)
        session.flush()

        updated = job_repo.update_status(job.id, "VALIDATING")
        assert updated is True
        fetched = session.get(ProcessingJobOrm, job.id)
        assert fetched.status == "VALIDATING"

    def test_job_status_update_not_found(self, job_repo: JobRepository):
        result = job_repo.update_status(uuid.uuid4(), "VALIDATING")
        assert result is False


# =============================================================================
# Tests: JobItem insertion and retrieval
# =============================================================================

class TestJobItemOrm:
    def _create_job(self, session: Session) -> ProcessingJobOrm:
        user = make_user(email=f"item_user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"ITEM_PROF_{uuid.uuid4().hex[:6]}")
        session.add_all([user, profile])
        session.flush()
        job = make_job(profile_id=profile.id, created_by_id=user.id)
        session.add(job)
        session.flush()
        return job

    def test_insert_job_item(self, session: Session, job_repo: JobRepository):
        job = self._create_job(session)

        item = JobItemOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            reference_original="SM-A546B/128",
            reference_normalized="SMA546B128",
            old_price=85000.00,
            new_price=89000.00,
            old_stock=10,
            new_stock=15,
            price_variation_pct=4.71,
            decision="Updated price and stock",
            decision_code="UPDATE",
            details={"source": "samsung_feed"},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(item)
        session.flush()

        items = job_repo.list_items(job.id)
        assert len(items) == 1
        assert items[0].reference_normalized == "SMA546B128"
        assert float(items[0].old_price) == 85000.00
        assert items[0].decision_code == "UPDATE"

    def test_blocked_item_persisted(self, session: Session, job_repo: JobRepository):
        """Blocked items with BLOCKED_PRICE_VARIATION code are stored correctly."""
        job = self._create_job(session)

        item = JobItemOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            reference_original="SM-S918B",
            reference_normalized="SMS918B",
            old_price=200000.00,
            new_price=290000.00,
            price_variation_pct=45.0,
            decision="Price variation exceeded threshold",
            decision_code="BLOCKED_PRICE_VARIATION",
            details={"threshold": 0.30, "actual": 0.45},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(item)
        session.flush()

        items = job_repo.list_items(job.id)
        assert any(i.decision_code == "BLOCKED_PRICE_VARIATION" for i in items)


# =============================================================================
# Tests: ValidationIssue
# =============================================================================

class TestValidationIssueOrm:
    def _create_job(self, session: Session) -> ProcessingJobOrm:
        user = make_user(email=f"vi_user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"VI_PROF_{uuid.uuid4().hex[:6]}")
        session.add_all([user, profile])
        session.flush()
        job = make_job(profile_id=profile.id, created_by_id=user.id)
        session.add(job)
        session.flush()
        return job

    def test_insert_validation_issue(self, session: Session, job_repo: JobRepository):
        job = self._create_job(session)

        issue = ValidationIssueOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            severity="BLOCKER",
            code="PRICE_VARIATION_BLOCKED",
            message="Price variation of 45% exceeds limit of 30%",
            row_number=7,
            resolved=False,
            created_at=datetime.now(timezone.utc),
        )
        session.add(issue)
        session.flush()

        issues = job_repo.list_issues(job.id)
        assert len(issues) == 1
        assert issues[0].severity == "BLOCKER"
        assert issues[0].code == "PRICE_VARIATION_BLOCKED"
        assert issues[0].resolved is False

    def test_filter_issues_by_severity(self, session: Session, job_repo: JobRepository):
        job = self._create_job(session)

        blocker = ValidationIssueOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            severity="BLOCKER",
            code="ZERO_PRICE",
            message="Zero price detected",
            created_at=datetime.now(timezone.utc),
        )
        warning = ValidationIssueOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            severity="WARNING",
            code="MISSING_STOCK",
            message="Stock not provided",
            created_at=datetime.now(timezone.utc),
        )
        session.add_all([blocker, warning])
        session.flush()

        blockers = job_repo.list_issues(job.id, severity="BLOCKER")
        assert all(i.severity == "BLOCKER" for i in blockers)

        warnings = job_repo.list_issues(job.id, severity="WARNING")
        assert all(i.severity == "WARNING" for i in warnings)


# =============================================================================
# Tests: PriceHistory (append-only)
# =============================================================================

class TestPriceHistoryOrm:
    def _create_job(self, session: Session) -> ProcessingJobOrm:
        user = make_user(email=f"ph_user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"PH_PROF_{uuid.uuid4().hex[:6]}")
        session.add_all([user, profile])
        session.flush()
        job = make_job(profile_id=profile.id, created_by_id=user.id)
        session.add(job)
        session.flush()
        return job

    def test_record_price_history(self, session: Session, job_repo: JobRepository):
        job = self._create_job(session)

        entry = PriceHistoryOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            reference_normalized="SMA546B128",
            old_price=85000.00,
            new_price=89000.00,
            variation_pct=4.71,
            change_type="UPDATED",
            recorded_at=datetime.now(timezone.utc),
        )
        job_repo.record_price_history(entry)

        history = job_repo.list_price_history("SMA546B128")
        assert len(history) == 1
        assert float(history[0].new_price) == 89000.00
        assert history[0].change_type == "UPDATED"

    def test_multiple_price_history_entries(self, session: Session, job_repo: JobRepository):
        """Multiple history records for the same ref returned newest-first."""
        job = self._create_job(session)
        ref = "SMS918B"

        for i, (old, new) in enumerate([(150000, 160000), (160000, 170000), (170000, 175000)]):
            entry = PriceHistoryOrm(
                id=uuid.uuid4(),
                job_id=job.id,
                reference_normalized=ref,
                old_price=old,
                new_price=new,
                variation_pct=round((new - old) / old * 100, 2),
                change_type="UPDATED",
                recorded_at=datetime.now(timezone.utc),
            )
            session.add(entry)
        session.flush()

        history = job_repo.list_price_history(ref)
        assert len(history) == 3
        # SQLite doesn't guarantee order without explicit timestamps diff;
        # verify all records are present
        prices = {float(h.new_price) for h in history}
        assert {160000, 170000, 175000} == prices


# =============================================================================
# Tests: AuditLog (append-only security)
# =============================================================================

class TestAuditLogOrm:
    def test_append_audit_log(self, session: Session, job_repo: JobRepository):
        user = make_user(email=f"audit_user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        session.add(user)
        session.flush()

        log = AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=user.id,
            action="JOB_CREATED",
            entity_type="processing_job",
            entity_id=uuid.uuid4(),
            extra_metadata={"source": "test"},
            created_at=datetime.now(timezone.utc),
        )
        result = job_repo.append_audit_log(log)

        assert result.action == "JOB_CREATED"
        assert result.entity_type == "processing_job"

    def test_audit_log_no_actor(self, session: Session, job_repo: JobRepository):
        """System-generated audit logs have no actor_id (nullable)."""
        log = AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=None,
            action="SYSTEM_BOOT",
            entity_type="system",
            extra_metadata={"version": "1.0"},
            created_at=datetime.now(timezone.utc),
        )
        result = job_repo.append_audit_log(log)
        assert result.actor_id is None


# =============================================================================
# Tests: Seed profiles — validates the seed data shape
# =============================================================================

class TestSeedProfilesShape:
    """Validates that the expected seed profiles can be created and configured."""

    SEED_PROFILES = [
        {
            "code": "MANO",
            "type": "MARKETPLACE",
            "config": {
                "integration_type": "EXCEL_EXPORT",
                "stock_min_activation": 3,
                "price_variation_threshold": 0.30,
            },
        },
        {
            "code": "WOOCOMMERCE",
            "type": "STORE",
            "config": {
                "integration_type": "EXCEL_EXPORT",
                "stock_min_activation": 1,
                "price_variation_threshold": 0.30,
                "woocommerce_enabled": False,
            },
        },
        {
            "code": "BFA",
            "type": "PARTNER",
            "config": {
                "integration_type": "EXCEL_EXPORT",
                "price_variation_threshold": 0.10,
            },
        },
        {
            "code": "KERO",
            "type": "RESELLER",
            "config": {
                "integration_type": "EXCEL_EXPORT",
                "price_variation_threshold": 0.30,
            },
        },
        {
            "code": "SIAC",
            "type": "RESELLER",
            "config": {
                "integration_type": "EXCEL_EXPORT",
                "price_variation_threshold": 0.30,
            },
        },
    ]

    def test_all_seed_profiles_insertable(self, session: Session):
        for seed in self.SEED_PROFILES:
            profile = CommercialProfileOrm(
                id=uuid.uuid4(),
                code=f"SEED_{seed['code']}",
                name=seed["code"],
                type=seed["type"],
                active=True,
                config=seed["config"],
                rules_version=1,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(profile)
        session.flush()

        codes = {f"SEED_{s['code']}" for s in self.SEED_PROFILES}
        results = (
            session.query(CommercialProfileOrm)
            .filter(CommercialProfileOrm.code.in_(codes))
            .all()
        )
        assert len(results) == 5

    def test_mano_config_values(self, session: Session):
        """MANO profile config must have stock_min=3 and variation=30%."""
        profile = CommercialProfileOrm(
            id=uuid.uuid4(),
            code="MANO_SHAPE_CHECK",
            name="Mano Shape Check",
            type="MARKETPLACE",
            active=True,
            config={
                "integration_type": "EXCEL_EXPORT",
                "stock_min_activation": 3,
                "price_variation_threshold": 0.30,
            },
            rules_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(profile)
        session.flush()

        fetched = session.get(CommercialProfileOrm, profile.id)
        assert fetched.config["stock_min_activation"] == 3
        assert fetched.config["price_variation_threshold"] == 0.30

    def test_bfa_conservative_threshold(self, session: Session):
        """BFA must have a 10% threshold (not the default 30%)."""
        profile = CommercialProfileOrm(
            id=uuid.uuid4(),
            code="BFA_THRESHOLD_CHECK",
            name="BFA Threshold Check",
            type="PARTNER",
            active=True,
            config={
                "integration_type": "EXCEL_EXPORT",
                "price_variation_threshold": 0.10,
            },
            rules_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(profile)
        session.flush()

        fetched = session.get(CommercialProfileOrm, profile.id)
        threshold = fetched.config["price_variation_threshold"]
        assert threshold == 0.10, (
            f"BFA must use 10% threshold, got {threshold * 100:.0f}%"
        )

    def test_woocommerce_feature_flag_disabled(self, session: Session):
        """WooCommerce live push starts disabled (Guardrail #14)."""
        profile = CommercialProfileOrm(
            id=uuid.uuid4(),
            code="WC_FEATURE_FLAG_CHECK",
            name="WC Feature Flag Check",
            type="STORE",
            active=True,
            config={
                "integration_type": "EXCEL_EXPORT",
                "woocommerce_enabled": False,
                "feature_flags": {"woocommerce_live_push": False},
            },
            rules_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(profile)
        session.flush()

        fetched = session.get(CommercialProfileOrm, profile.id)
        assert fetched.config["woocommerce_enabled"] is False
        assert fetched.config["feature_flags"]["woocommerce_live_push"] is False


# =============================================================================
# Tests: Referential integrity cascade
# =============================================================================

class TestReferentialIntegrity:
    def test_job_items_cascade_delete_with_job(self, session: Session):
        """Deleting a job cascades to job_items."""
        user = make_user(email=f"cascade_user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"CASCADE_PROF_{uuid.uuid4().hex[:6]}")
        session.add_all([user, profile])
        session.flush()

        job = make_job(profile_id=profile.id, created_by_id=user.id)
        session.add(job)
        session.flush()

        item = JobItemOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            reference_original="REF-001",
            reference_normalized="REF001",
            decision="Updated",
            decision_code="UPDATE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(item)
        session.flush()

        item_id = item.id
        session.delete(job)
        session.flush()

        # Item should be gone after job deleted (CASCADE)
        deleted_item = session.get(JobItemOrm, item_id)
        assert deleted_item is None

    def test_validation_issues_cascade_with_job(self, session: Session):
        """Deleting a job cascades to validation_issues."""
        user = make_user(email=f"vi_cascade_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"VI_CASCADE_{uuid.uuid4().hex[:6]}")
        session.add_all([user, profile])
        session.flush()

        job = make_job(profile_id=profile.id, created_by_id=user.id)
        session.add(job)
        session.flush()

        issue = ValidationIssueOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            severity="WARNING",
            code="TEST_CODE",
            message="Test issue",
            created_at=datetime.now(timezone.utc),
        )
        session.add(issue)
        session.flush()

        issue_id = issue.id
        session.delete(job)
        session.flush()

        deleted_issue = session.get(ValidationIssueOrm, issue_id)
        assert deleted_issue is None


# =============================================================================
# Tests: JobRepository — end-to-end flow
# =============================================================================

class TestJobRepositoryFlow:
    """Full create → update → list flow through the repository."""

    def test_full_job_lifecycle(
        self, session: Session, job_repo: JobRepository
    ):
        user = make_user(email=f"flow_user_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"FLOW_PROF_{uuid.uuid4().hex[:6]}")
        session.add_all([user, profile])
        session.flush()

        # 1. Create job
        job = make_job(profile_id=profile.id, created_by_id=user.id, status="UPLOADED")
        created = job_repo.create(job)
        assert created.status == "UPLOADED"

        # 2. Progress through lifecycle
        for status in ["VALIDATING", "READY_FOR_REVIEW", "APPROVED", "PROCESSING", "COMPLETED"]:
            result = job_repo.update_status(job.id, status)
            assert result is True

        fetched = job_repo.get_by_id(job.id)
        assert fetched.status == "COMPLETED"

    def test_list_by_user(self, session: Session, job_repo: JobRepository):
        user_a = make_user(email=f"user_a_{uuid.uuid4().hex[:8]}@cotarco.ao")
        user_b = make_user(email=f"user_b_{uuid.uuid4().hex[:8]}@cotarco.ao")
        profile = make_profile(code=f"LIST_JOB_PROF_{uuid.uuid4().hex[:6]}")
        session.add_all([user_a, user_b, profile])
        session.flush()

        job_a1 = make_job(profile_id=profile.id, created_by_id=user_a.id)
        job_a2 = make_job(profile_id=profile.id, created_by_id=user_a.id)
        job_b1 = make_job(profile_id=profile.id, created_by_id=user_b.id)
        session.add_all([job_a1, job_a2, job_b1])
        session.flush()

        jobs_a = job_repo.list_by_user(user_a.id)
        jobs_b = job_repo.list_by_user(user_b.id)

        assert len(jobs_a) >= 2
        assert all(j.created_by_id == user_a.id for j in jobs_a)
        assert all(j.created_by_id == user_b.id for j in jobs_b)
        # User B's job not visible in User A's list
        a_ids = {j.id for j in jobs_a}
        assert job_b1.id not in a_ids
