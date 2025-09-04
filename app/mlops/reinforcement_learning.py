#!/usr/bin/env python3
"""
Reinforcement Learning & Active Learning for SmartCloudOps AI
Continuous learning from remediation outcomes and user feedback
"""

import json
import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class State:
    """System state representation for RL"""

    timestamp: datetime
    metrics: Dict[str, float]
    anomaly_present: bool
    anomaly_severity: str
    previous_actions: List[str]
    system_health_score: float


@dataclass
class Action:
    """Remediation action for RL"""

    action_type: str
    parameters: Dict[str, Any]
    confidence: float
    expected_impact: float


@dataclass
class Reward:
    """Reward signal for RL"""

    immediate_reward: float
    long_term_reward: float
    user_satisfaction: float
    system_improvement: float


class ReinforcementLearningAgent:
    """Reinforcement learning agent for automated remediation"""

    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.9):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.state_history = []
        self.action_history = []
        self.reward_history = []

        # Load existing Q-table if available
        self.load_q_table()

    def get_state_representation(
        self, metrics: Dict[str, float], anomaly_info: Dict[str, Any]
    ) -> str:
        """Convert system state to string representation for Q-table"""
        # Discretize continuous metrics
        cpu_level = self._discretize_value(
            metrics.get("cpu_usage", 0), [0, 50, 80, 100]
        )
        memory_level = self._discretize_value(
            metrics.get("memory_usage", 0), [0, 50, 80, 100]
        )
        error_level = self._discretize_value(
            metrics.get("error_rate", 0), [0, 5, 10, 100]
        )

        # Anomaly severity level
        severity_level = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(
            anomaly_info.get("severity", "low"), 0
        )

        return f"{cpu_level}_{memory_level}_{error_level}_{severity_level}"

    def _discretize_value(self, value: float, thresholds: List[float]) -> int:
        """Discretize continuous value into discrete levels"""
        for i, threshold in enumerate(thresholds):
            if value <= threshold:
                return i
        return len(thresholds)

    def select_action(
        self, state: str, available_actions: List[str], exploration_rate: float = 0.1
    ) -> str:
        """Select action using epsilon-greedy policy"""
        if np.random.random() < exploration_rate:
            # Exploration: random action
            return np.random.choice(available_actions)
        else:
            # Exploitation: best action based on Q-values
            q_values = [self.q_table[state][action] for action in available_actions]
            best_action_idx = np.argmax(q_values)
            return available_actions[best_action_idx]

    def update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-value using Q-learning algorithm"""
        current_q = self.q_table[state][action]

        # Get maximum Q-value for next state
        next_q_values = [
            self.q_table[next_state][a] for a in self.q_table[next_state].keys()
        ]
        max_next_q = max(next_q_values) if next_q_values else 0

        # Q-learning update rule
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.q_table[state][action] = new_q

    def calculate_reward(self, action: str, outcome: Dict[str, Any]) -> float:
        """Calculate reward based on action outcome"""
        reward = 0.0

        # Base reward for successful remediation
        if outcome.get("success", False):
            reward += 10.0

        # Penalty for failed remediation
        else:
            reward -= 5.0

        # Reward based on system improvement
        system_improvement = outcome.get("system_improvement", 0)
        reward += system_improvement * 2.0

        # Reward based on user satisfaction
        user_satisfaction = outcome.get("user_satisfaction", 0)
        reward += user_satisfaction * 1.5

        # Penalty for action cost (time, resources)
        action_cost = outcome.get("action_cost", 0)
        reward -= action_cost * 0.5

        return reward

    def learn_from_experience(
        self, state: str, action: str, reward: float, next_state: str
    ):
        """Learn from a single experience"""
        self.update_q_value(state, action, reward, next_state)

        # Store experience for batch learning
        self.state_history.append(state)
        self.action_history.append(action)
        self.reward_history.append(reward)

        # Save Q-table periodically
        if len(self.state_history) % 100 == 0:
            self.save_q_table()

    def get_action_recommendations(
        self, current_state: str, available_actions: List[str]
    ) -> List[Tuple[str, float]]:
        """Get action recommendations with confidence scores"""
        recommendations = []

        for action in available_actions:
            self.q_table[current_state][action]
            confidence = self._calculate_confidence(current_state, action)
            recommendations.append((action, confidence))

        # Sort by confidence (descending)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations

    def _calculate_confidence(self, state: str, action: str) -> float:
        """Calculate confidence score for an action"""
        q_value = self.q_table[state][action]

        # Normalize Q-value to confidence score (0-1)
        all_q_values = [self.q_table[state][a] for a in self.q_table[state].keys()]
        if not all_q_values:
            return 0.5

        max_q = max(all_q_values)
        min_q = min(all_q_values)

        if max_q == min_q:
            return 0.5

        confidence = (q_value - min_q) / (max_q - min_q)
        return max(0.0, min(1.0, confidence))

    def save_q_table(self):
        """Save Q-table to disk"""
        q_table_file = "mlops/q_table.json"

        # Convert defaultdict to regular dict for JSON serialization
        q_table_dict = {}
        for state in self.q_table:
            q_table_dict[state] = dict(self.q_table[state])

        with open(q_table_file, "w") as f:
            json.dump(q_table_dict, f, indent=2)

        logger.info("Saved Q-table")

    def load_q_table(self):
        """Load Q-table from disk"""
        q_table_file = "mlops/q_table.json"

        if os.path.exists(q_table_file):
            try:
                with open(q_table_file, "r") as f:
                    q_table_dict = json.load(f)

                # Convert back to defaultdict
                for state, actions in q_table_dict.items():
                    for action, q_value in actions.items():
                        self.q_table[state][action] = q_value

                logger.info("Loaded Q-table")
            except Exception as e:
                logger.error(f"Error loading Q-table: {e}")


class ActiveLearningSystem:
    """Active learning system for uncertain anomaly detection"""

    def __init__(self, uncertainty_threshold: float = 0.3):
        self.uncertainty_threshold = uncertainty_threshold
        self.uncertain_samples = []
        self.user_feedback = {}
        self.learning_queue = []

    def calculate_uncertainty(self, prediction_proba: np.ndarray) -> float:
        """Calculate prediction uncertainty using entropy"""
        if len(prediction_proba) == 0:
            return 1.0

        # Calculate entropy as uncertainty measure
        entropy = -np.sum(prediction_proba * np.log(prediction_proba + 1e-10))
        return entropy

    def should_request_feedback(self, prediction_proba: np.ndarray) -> bool:
        """Determine if user feedback should be requested"""
        uncertainty = self.calculate_uncertainty(prediction_proba)
        return uncertainty > self.uncertainty_threshold

    def add_uncertain_sample(
        self,
        sample_id: str,
        features: Dict[str, float],
        prediction_proba: np.ndarray,
        timestamp: datetime,
    ):
        """Add uncertain sample to learning queue"""
        uncertainty = self.calculate_uncertainty(prediction_proba)

        sample = {
            "sample_id": sample_id,
            "features": features,
            "prediction_proba": prediction_proba.tolist(),
            "uncertainty": uncertainty,
            "timestamp": timestamp,
            "feedback_received": False,
        }

        self.uncertain_samples.append(sample)
        self.learning_queue.append(sample_id)

        logger.info(
            f"Added uncertain sample {sample_id} with uncertainty {uncertainty:.3f}"
        )

    def record_user_feedback(
        self,
        sample_id: str,
        user_label: bool,
        confidence: float,
        feedback_text: str = "",
    ):
        """Record user feedback for uncertain sample"""
        feedback = {
            "user_label": user_label,
            "confidence": confidence,
            "feedback_text": feedback_text,
            "timestamp": datetime.now(),
        }

        self.user_feedback[sample_id] = feedback

        # Mark sample as feedback received
        for sample in self.uncertain_samples:
            if sample["sample_id"] == sample_id:
                sample["feedback_received"] = True
                sample["user_feedback"] = feedback
                break

        logger.info(f"Recorded user feedback for sample {sample_id}")

    def get_learning_samples(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get samples that need user feedback"""
        uncertain_samples = [
            s for s in self.uncertain_samples if not s.get("feedback_received", False)
        ]

        # Sort by uncertainty (highest first)
        uncertain_samples.sort(key=lambda x: x["uncertainty"], reverse=True)

        return uncertain_samples[:limit]

    def retrain_with_feedback(self, model_type: str = "anomaly_detection"):
        """Retrain model with user feedback"""
        # Get samples with user feedback
        labeled_samples = []
        for sample in self.uncertain_samples:
            if (
                sample.get("feedback_received", False)
                and sample["sample_id"] in self.user_feedback
            ):
                labeled_samples.append(sample)

        if len(labeled_samples) < 5:
            logger.info("Not enough labeled samples for retraining")
            return

        # Prepare training data
        X = []
        y = []

        for sample in labeled_samples:
            features = list(sample["features"].values())
            X.append(features)
            y.append(self.user_feedback[sample["sample_id"]]["user_label"])

        X = np.array(X)
        y = np.array(y)

        # Retrain model
        try:
            # Create new model with additional data
            new_model = RandomForestClassifier(n_estimators=100, random_state=42)
            new_scaler = StandardScaler()

            # Scale features
            X_scaled = new_scaler.fit_transform(X)

            # Train new model
            new_model.fit(X_scaled, y)

            # Evaluate new model
            y_pred = new_model.predict(X_scaled)
            accuracy = np.mean(y_pred == y)

            # Register new model version
            # metrics = {
            #     "accuracy": accuracy,
            #     "training_samples": len(X),
            #     "feedback_samples": len(labeled_samples),
            # }  # TODO: Use metrics in model registration

            # hyperparameters = {"n_estimators": 100, "random_state": 42}  # TODO: Use hyperparameters in model registration

            list(labeled_samples[0]["features"].keys())

            logger.info(f"Retrained model with user feedback. Accuracy: {accuracy:.3f}")

            # Clear processed samples
            self.uncertain_samples = [
                s
                for s in self.uncertain_samples
                if not s.get("feedback_received", False)
            ]

        except Exception as e:
            logger.error(f"Error retraining model with feedback: {e}")


class ContinuousLearningOrchestrator:
    """Orchestrates continuous learning processes"""

    def __init__(self):
        self.rl_agent = ReinforcementLearningAgent()
        self.active_learning = ActiveLearningSystem()
        self.learning_stats = {
            "total_experiences": 0,
            "user_feedback_requests": 0,
            "model_retrainings": 0,
            "last_learning_cycle": None,
        }

    async def run_learning_cycle(self):
        """Run a complete learning cycle"""
        logger.info("Starting continuous learning cycle")

        # 1. Collect recent experiences for RL
        await self._collect_rl_experiences()

        # 2. Process uncertain samples for active learning
        await self._process_uncertain_samples()

        # 3. Retrain models if needed
        await self._retrain_models()

        # 4. Update learning statistics
        self.learning_stats["last_learning_cycle"] = datetime.now().isoformat()

        logger.info("Completed continuous learning cycle")

    async def _collect_rl_experiences(self):
        """Collect recent experiences for reinforcement learning"""
        try:
            # Simplified implementation - in practice would query database
            logger.info("Collecting RL experiences")

            # Mock experience collection
            mock_experiences = [
                {
                    "state": "high_cpu_high_memory",
                    "action": "scale_up",
                    "reward": 5.0,
                    "next_state": "medium_cpu_medium_memory",
                }
            ]

            for exp in mock_experiences:
                self.rl_agent.learn_from_experience(
                    exp["state"], exp["action"], exp["reward"], exp["next_state"]
                )
                self.learning_stats["total_experiences"] += 1

        except Exception as e:
            logger.error(f"Error collecting RL experiences: {e}")

    async def _process_uncertain_samples(self):
        """Process uncertain samples for active learning"""
        # Get samples that need user feedback
        learning_samples = self.active_learning.get_learning_samples(limit=5)

        for sample in learning_samples:
            # In a real system, this would trigger a user notification
            # For now, we'll simulate some feedback
            if np.random.random() < 0.3:  # 30% chance of getting feedback
                user_label = np.random.choice([True, False])
                confidence = np.random.uniform(0.7, 1.0)

                self.active_learning.record_user_feedback(
                    sample["sample_id"], user_label, confidence
                )

                self.learning_stats["user_feedback_requests"] += 1

    async def _retrain_models(self):
        """Retrain models with new data"""
        # Retrain with user feedback
        self.active_learning.retrain_with_feedback()

        # Save RL agent state
        self.rl_agent.save_q_table()

        self.learning_stats["model_retrainings"] += 1

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return self.learning_stats.copy()

    def get_action_recommendations(
        self, current_metrics: Dict[str, float], anomaly_info: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """Get action recommendations using RL agent"""
        state = self.rl_agent.get_state_representation(current_metrics, anomaly_info)

        # Available actions (in practice, this would be dynamic)
        available_actions = [
            "restart_service",
            "scale_up",
            "scale_down",
            "clear_cache",
            "restart_database",
            "increase_memory",
            "decrease_load",
        ]

        return self.rl_agent.get_action_recommendations(state, available_actions)


# Global continuous learning orchestrator
continuous_learning = ContinuousLearningOrchestrator()
