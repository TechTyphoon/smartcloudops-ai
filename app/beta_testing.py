"""
Beta Testing Management System for SmartCloudOps AI
Manages beta testers, their access levels, and testing scenarios
"""

import json
import logging
import os
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import boto3

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles for access control"""

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    BETA_TESTER = "beta_tester"


class TestingScenario(Enum):
    """Predefined testing scenarios"""

    BASIC_CHATOPS = "basic_chatops"
    ML_ANOMALY_DETECTION = "ml_anomaly_detection"
    AUTO_REMEDIATION = "auto_remediation"
    ADVANCED_CONTEXT = "advanced_context"
    LOAD_TESTING = "load_testing"
    SECURITY_TESTING = "security_testing"


@dataclass
class BetaTester:
    """Beta tester information"""

    name: str
    email: str
    role: UserRole
    access_level: str
    testing_scenarios: List[TestingScenario]
    created_at: datetime
    last_active: Optional[datetime] = None
    feedback_count: int = 0
    is_active: bool = True
    api_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data["role"] = self.role.value
        data["testing_scenarios"] = [s.value for s in self.testing_scenarios]
        data["created_at"] = self.created_at.isoformat()
        if self.last_active:
            data["last_active"] = self.last_active.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BetaTester":
        """Create from dictionary"""
        data["role"] = UserRole(data["role"])
        data["testing_scenarios"] = [
            TestingScenario(s) for s in data["testing_scenarios"]
        ]
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("last_active"):
            data["last_active"] = datetime.fromisoformat(data["last_active"])
        return cls(**data)


@dataclass
class TestingSession:
    """Testing session information"""

    id: str
    tester_email: str
    scenario: TestingScenario
    started_at: datetime
    ended_at: Optional[datetime] = None
    notes: str = ""
    performance_metrics: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data["scenario"] = self.scenario.value
        data["started_at"] = self.started_at.isoformat()
        if self.ended_at:
            data["ended_at"] = self.ended_at.isoformat()
        return data

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate session duration in minutes"""
        if self.ended_at:
            duration = self.ended_at - self.started_at
            return int(duration.total_seconds() / 60)
        return None


@dataclass
class Feedback:
    """Feedback information"""

    id: str
    session_id: str
    tester_email: str
    rating: int
    comments: str
    category: str
    priority: str
    submitted_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data["submitted_at"] = self.submitted_at.isoformat()
        return data


class BetaTestingManager:
    """Manages beta testing program"""

    def __init__(self):
        self.ssm_client = self._init_ssm_client()
        self.s3_client = self._init_s3_client()
        self.testers: List[BetaTester] = []
        self.sessions: List[TestingSession] = []
        self.feedback: List[Feedback] = []
        self._load_testers()
        self._load_sessions()
        self._load_feedback()

    def _init_ssm_client(self) -> Optional[boto3.client]:
        """Initialize SSM client"""
        try:
            return boto3.client("ssm", region_name="ap-south-1")
        except Exception as e:
            logger.warning(f"Could not initialize SSM client: {e}")
            return None

    def _init_s3_client(self) -> Optional[boto3.client]:
        """Initialize S3 client"""
        try:
            return boto3.client("s3", region_name="ap-south-1")
        except Exception as e:
            logger.warning(f"Could not initialize S3 client: {e}")
            return None

    def _load_testers(self):
        """Load testers from SSM or create defaults"""
        try:
            if self.ssm_client:
                response = self.ssm_client.get_parameter(
                    Name="/smartcloudops/beta/testers", WithDecryption=True
                )
                testers_data = json.loads(response["Parameter"]["Value"])
                self.testers = [BetaTester.from_dict(t) for t in testers_data]
                logger.info(f"Loaded {len(self.testers)} testers from SSM")
            else:
                self._create_default_testers()
        except Exception as e:
            logger.warning(f"Could not load testers from SSM: {e}")
            self._create_default_testers()

    def _create_default_testers(self):
        """Create default testers for development"""
        default_testers = [
            {
                "name": "Admin User",
                "email": "admin@smartcloudops.ai",
                "role": UserRole.ADMIN,
                "access_level": "full",
                "testing_scenarios": list(TestingScenario),
                "created_at": datetime.now(),
            },
            {
                "name": "Beta Tester",
                "email": "tester@smartcloudops.ai",
                "role": UserRole.BETA_TESTER,
                "access_level": "limited",
                "testing_scenarios": [
                    TestingScenario.BASIC_CHATOPS,
                    TestingScenario.ML_ANOMALY_DETECTION,
                ],
                "created_at": datetime.now(),
            },
        ]

        for tester_data in default_testers:
            tester = BetaTester(**tester_data)
            tester.api_key = self._generate_api_key()
            self.testers.append(tester)

        logger.info(f"Created {len(self.testers)} default testers")

    def _load_sessions(self):
        """Load sessions from S3 or start fresh"""
        try:
            if self.s3_client:
                response = self.s3_client.get_object(
                    Bucket="smartcloudops-beta-data", Key="sessions.json"
                )
                sessions_data = json.loads(response["Body"].read())
                self.sessions = [TestingSession(**s) for s in sessions_data]
                logger.info(f"Loaded {len(self.sessions)} sessions from S3")
        except Exception as e:
            logger.warning(f"Could not load sessions from S3: {e}")

    def _load_feedback(self):
        """Load feedback from S3 or start fresh"""
        try:
            if self.s3_client:
                response = self.s3_client.get_object(
                    Bucket="smartcloudops-beta-data", Key="feedback.json"
                )
                feedback_data = json.loads(response["Body"].read())
                self.feedback = [Feedback(**f) for f in feedback_data]
                logger.info(f"Loaded {len(self.feedback)} feedback entries from S3")
        except Exception as e:
            logger.warning(f"Could not load feedback from S3: {e}")

    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)

    def add_tester(
        self, name: str, email: str, role: UserRole = UserRole.BETA_TESTER
    ) -> BetaTester:
        """Add a new beta tester"""
        if self.get_tester(email):
            raise ValueError(f"Tester with email {email} already exists")

        tester = BetaTester(
            name=name,
            email=email,
            role=role,
            access_level="limited",
            testing_scenarios=[TestingScenario.BASIC_CHATOPS],
            created_at=datetime.now(),
        )
        tester.api_key = self._generate_api_key()
        self.testers.append(tester)
        self._save_testers()
        logger.info(f"Added new tester: {email}")
        return tester

    def get_tester(self, email: str) -> Optional[BetaTester]:
        """Get tester by email"""
        return next((t for t in self.testers if t.email == email), None)

    def get_tester_by_api_key(self, api_key: str) -> Optional[BetaTester]:
        """Get tester by API key"""
        return next((t for t in self.testers if t.api_key == api_key), None)

    def get_all_testers(self) -> List[BetaTester]:
        """Get all testers"""
        return self.testers

    def update_tester_scenarios(
        self, email: str, scenarios: List[TestingScenario]
    ) -> bool:
        """Update tester's testing scenarios"""
        tester = self.get_tester(email)
        if not tester:
            return False

        tester.testing_scenarios = scenarios
        self._save_testers()
        logger.info(f"Updated scenarios for tester: {email}")
        return True

    def start_session(
        self, tester: BetaTester, scenario: TestingScenario
    ) -> TestingSession:
        """Start a new testing session"""
        session = TestingSession(
            id=secrets.token_urlsafe(16),
            tester_email=tester.email,
            scenario=scenario,
            started_at=datetime.now(),
        )
        self.sessions.append(session)
        tester.last_active = datetime.now()
        self._save_sessions()
        self._save_testers()
        logger.info(f"Started session {session.id} for {tester.email}")
        return session

    def end_session(
        self, session_id: str, tester: BetaTester, notes: str = ""
    ) -> Optional[TestingSession]:
        """End a testing session"""
        session = next((s for s in self.sessions if s.id == session_id), None)
        if not session or session.tester_email != tester.email:
            return None

        session.ended_at = datetime.now()
        session.notes = notes
        tester.last_active = datetime.now()
        self._save_sessions()
        self._save_testers()
        logger.info(f"Ended session {session_id}")
        return session

    def get_tester_sessions(self, tester: BetaTester) -> List[TestingSession]:
        """Get all sessions for a tester"""
        return [s for s in self.sessions if s.tester_email == tester.email]

    def get_active_sessions(self) -> List[TestingSession]:
        """Get all active sessions"""
        return [s for s in self.sessions if not s.ended_at]

    def submit_feedback(
        self,
        session_id: str,
        tester: BetaTester,
        rating: int,
        comments: str,
        category: str = "general",
        priority: str = "medium",
    ) -> Optional[Feedback]:
        """Submit feedback for a session"""
        session = next((s for s in self.sessions if s.id == session_id), None)
        if not session or session.tester_email != tester.email:
            return None

        feedback = Feedback(
            id=secrets.token_urlsafe(16),
            session_id=session_id,
            tester_email=tester.email,
            rating=rating,
            comments=comments,
            category=category,
            priority=priority,
            submitted_at=datetime.now(),
        )

        self.feedback.append(feedback)
        tester.feedback_count += 1
        tester.last_active = datetime.now()
        self._save_feedback()
        self._save_testers()
        logger.info(f"Submitted feedback for session {session_id}")
        return feedback

    def test_notification(self, tester: BetaTester, message: str) -> bool:
        """Test notification system for a tester"""
        try:
            # Simulate notification test
            logger.info(f"Test notification for {tester.email}: {message}")
            tester.last_active = datetime.now()
            self._save_testers()
            return True
        except Exception as e:
            logger.error(f"Notification test failed: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Get beta testing summary"""
        active_testers = [t for t in self.testers if t.is_active]
        active_sessions = [s for s in self.sessions if not s.ended_at]
        total_feedback = sum(t.feedback_count for t in self.testers)

        return {
            "total_testers": len(self.testers),
            "active_testers": len(active_testers),
            "total_sessions": len(self.sessions),
            "active_sessions": len(active_sessions),
            "total_feedback": total_feedback,
            "scenarios": {
                s.value: len([sess for sess in self.sessions if sess.scenario == s])
                for s in TestingScenario
            },
        }

    def _save_testers(self):
        """Save testers to SSM"""
        try:
            if self.ssm_client:
                testers_data = [t.to_dict() for t in self.testers]
                self.ssm_client.put_parameter(
                    Name="/smartcloudops/beta/testers",
                    Value=json.dumps(testers_data),
                    Type="SecureString",
                    Overwrite=True,
                )
        except Exception as e:
            logger.warning(f"Could not save testers to SSM: {e}")

    def _save_sessions(self):
        """Save sessions to S3"""
        try:
            if self.s3_client:
                sessions_data = [s.to_dict() for s in self.sessions]
                self.s3_client.put_object(
                    Bucket="smartcloudops-beta-data",
                    Key="sessions.json",
                    Body=json.dumps(sessions_data),
                )
        except Exception as e:
            logger.warning(f"Could not save sessions to S3: {e}")

    def _save_feedback(self):
        """Save feedback to S3"""
        try:
            if self.s3_client:
                feedback_data = [f.to_dict() for f in self.feedback]
                self.s3_client.put_object(
                    Bucket="smartcloudops-beta-data",
                    Key="feedback.json",
                    Body=json.dumps(feedback_data),
                )
        except Exception as e:
            logger.warning(f"Could not save feedback to S3: {e}")

    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Clean up old inactive sessions"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        old_sessions = [
            s for s in self.sessions if s.started_at < cutoff_time and not s.ended_at
        ]

        for session in old_sessions:
            session.ended_at = datetime.now()
            session.notes = "Auto-ended due to inactivity"

        if old_sessions:
            self._save_sessions()
            logger.info(f"Cleaned up {len(old_sessions)} inactive sessions")
