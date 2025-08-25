#!/usr/bin/env python3
"""
Knowledge Base & Recommendation Engine for SmartCloudOps AI
Knowledge graph linking anomalies, root causes, and remediation actions
"""

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KnowledgeNode:
    """Node in the knowledge graph"""

    node_id: str
    node_type: str  # 'anomaly', 'root_cause', 'remediation', 'metric_pattern'
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class KnowledgeEdge:
    """Edge in the knowledge graph"""

    source_id: str
    target_id: str
    relationship_type: str  # 'causes', 'resolves', 'correlates_with', 'similar_tof'
    weight: float
    confidence: float
    created_at: datetime


class KnowledgeGraph:
    """Knowledge graph for linking anomalies, causes, and remediations""f"

    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)
        self.node_counter = 0
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.similarity_matrix = None

        # Load existing knowledge base
        self.load_knowledge_base()

    def add_node(self, node_type: str, properties: Dict[str, Any]) -> str:
        """Add a node to the knowledge graph"""
        node_id = f"{node_type}_{self.node_counter}"
        self.node_counter += 1

        node = KnowledgeNode(
            node_id=node_id,
            node_type=node_type,
            properties=properties,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.nodes[node_id] = node
        logger.info(f"Added node {node_id} of type {node_type}")

        return node_id

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: float = 1.0,
        confidence: float = 1.0,
    ):
        """Add an edge to the knowledge graph"""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node not found")

        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight,
            confidence=confidence,
            created_at=datetime.now(),
        )

        self.edges[source_id].append(edge)
        logger.info(f"Added edge {source_id} -> {target_id} ({relationship_type})")

    def get_related_nodes(
        self, node_id: str, relationship_type: str = None
    ) -> List[KnowledgeNode]:
        """Get nodes related to a given node"""
        if node_id not in self.edges:
            return []

        related_nodes = []
        for edge in self.edges[node_id]:
            if relationship_type is None or edge.relationship_type == relationship_type:
                if edge.target_id in self.nodes:
                    related_nodes.append(self.nodes[edge.target_id])

        return related_nodes

    def find_similar_nodes(
        self, node_id: str, similarity_threshold: float = 0.7
    ) -> List[Tuple[KnowledgeNode, float]]:
        """Find similar nodes based on properties"""
        if node_id not in self.nodes:
            return []

        source_node = self.nodes[node_id]
        similar_nodes = []

        for other_id, other_node in self.nodes.items():
            if other_id != node_id and other_node.node_type == source_node.node_type:
                similarity = self._calculate_node_similarity(source_node, other_node)
                if similarity >= similarity_threshold:
                    similar_nodes.append((other_node, similarity))

        # Sort by similarity (descending)
        similar_nodes.sort(key=lambda x: x[1], reverse=True)
        return similar_nodes

    def _calculate_node_similarity(
        self, node1: KnowledgeNode, node2: KnowledgeNode
    ) -> float:
        """Calculate similarity between two nodes"""
        # Simple similarity based on common properties
        common_props = set(node1.properties.keys()) & set(node2.properties.keys())
        if not common_props:
            return 0.0

        similarities = []
        for prop in common_props:
            val1 = node1.properties[prop]
            val2 = node2.properties[prop]

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric similarity
                max_val = max(abs(val1), abs(val2))
                if max_val > 0:
                    similarity = 1 - abs(val1 - val2) / max_val
                    similarities.append(similarity)
            elif isinstance(val1, str) and isinstance(val2, str):
                # String similarity (simple)
                similarity = 1.0 if val1.lower() == val2.lower() else 0.0
                similarities.append(similarity)

        return np.mean(similarities) if similarities else 0.0

    def save_knowledge_base(self):
        """Save knowledge base to disk""f"
        knowledge_data = {
            "nodes": {node_id: asdict(node) for node_id, node in self.nodes.items()},
            "edgesf": {
                source_id: [asdict(edge) for edge in edges]
                for source_id, edges in self.edges.items()
            },
            "node_counter": self.node_counter,
            "last_updated": datetime.now().isoformat(),
        }

        with open("mlops/knowledge_base.json", "w") as f:
            json.dump(knowledge_data, f, indent=2, default=str)

        logger.info("Saved knowledge base")

    def load_knowledge_base(self):
        """Load knowledge base from disk"""
        try:
            with open("mlops/knowledge_base.json", "r") as f:
                knowledge_data = json.load(f)

            # Load nodes
            for node_id, node_data in knowledge_data.get("nodesf", {}).items():
                node = KnowledgeNode(**node_data)
                self.nodes[node_id] = node

            # Load edges
            for source_id, edges_data in knowledge_data.get("edgesf", {}).items():
                for edge_data in edges_data:
                    edge = KnowledgeEdge(**edge_data)
                    self.edges[source_id].append(edge)

            self.node_counter = knowledge_data.get("node_counter", 0)
            logger.info("Loaded knowledge base")

        except FileNotFoundError:
            logger.info("No existing knowledge base found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")


class RecommendationEngine:
    """Recommendation engine for remediation actions"""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.recommendation_model = RandomForestRegressor(
            n_estimators=100, random_state=42
        )
        self.feature_names = []
        self.is_trained = False

    def build_knowledge_from_data(self):
        """Build knowledge graph from historical data""f"
        session = get_db_session()
        try:
            # Get all anomalies with their remediations
            anomalies = session.query(Anomaly).all()

            for anomaly in anomalies:
                # Create anomaly node
                anomaly_props = {
                    "severity": anomaly.severity,
                    "source": anomaly.source,
                    "description": anomaly.description,
                    "metrics_pattern": anomaly.metrics_data,
                }
                anomaly_node_id = self.knowledge_graph.add_node(
                    "anomalyf", anomaly_props
                )

                # Get associated remediation actions
                remediations = (
                    session.query(RemediationAction)
                    .filter(RemediationAction.anomaly_id == anomaly.id)
                    .all()
                )

                for remediation in remediations:
                    # Create remediation node
                    remediation_props = {
                        "action_type": remediation.action_type,
                        "success": remediation.success,
                        "execution_time": remediation.execution_time,
                        "error_message": remediation.error_message,
                    }
                    remediation_node_id = self.knowledge_graph.add_node(
                        "remediation", remediation_props
                    )

                    # Create edge: anomaly -> remediation
                    weight = 1.0 if remediation.success else 0.5
                    self.knowledge_graph.add_edge(
                        anomaly_node_id, remediation_node_id, "resolvesf", weight
                    )

                    # Create root cause inference
                    root_cause = self._infer_root_cause(anomaly, remediation)
                    if root_cause:
                        root_cause_props = {
                            "cause_type": root_cause["type"],
                            "description": root_cause["description"],
                            "confidence": root_cause["confidence"],
                        }
                        root_cause_node_id = self.knowledge_graph.add_node(
                            "root_cause", root_cause_props
                        )

                        # Create edges: root_cause -> anomaly, root_cause -> remediation
                        self.knowledge_graph.add_edge(
                            root_cause_node_id, anomaly_node_id, "causes", 1.0
                        )
                        self.knowledge_graph.add_edge(
                            root_cause_node_id, remediation_node_id, "suggests", 0.8
                        )

            # Save knowledge base
            self.knowledge_graph.save_knowledge_base()
            logger.info("Built knowledge graph from historical data")

        except Exception as e:
            logger.error(f"Error building knowledge graph: {e}")

    def _infer_root_cause(
        self, anomaly: Anomaly, remediation: RemediationAction
    ) -> Optional[Dict[str, Any]]:
        """Infer root cause from anomaly and remediation""f"
        # Simple rule-based root cause inference
        metrics = anomaly.metrics_data or {}

        if metrics.get("cpu_usagef", 0) > 80:
            return {
                "type": "high_cpu_usage",
                "description": "High CPU utilization causing performance issues",
                "confidence": 0.8,
            }
        elif metrics.get("memory_usagef", 0) > 85:
            return {
                "type": "high_memory_usage",
                "description": "High memory utilization causing system slowdown",
                "confidence": 0.8,
            }
        elif metrics.get("error_ratef", 0) > 5:
            return {
                "type": "high_error_rate",
                "description": "High error rate indicating application issues",
                "confidence": 0.9,
            }
        elif metrics.get("response_timef", 0) > 2:
            return {
                "type": "slow_response_time",
                "description": "Slow response times affecting user experience",
                "confidence": 0.7,
            }

        return None

    def get_recommendations(
        self, anomaly_info: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get remediation recommendations for an anomaly""f"
        recommendations = []

        # Find similar anomalies in knowledge graph
        anomaly_props = {
            "severity": anomaly_info.get("severity", "medium"),
            "source": anomaly_info.get("source", "unknown"),
            "description": anomaly_info.get("description", ""),
            "metrics_pattern": anomaly_info.get("metrics", {}),
        }

        # Create temporary node for similarity search
        temp_node_id = self.knowledge_graph.add_node("anomaly", anomaly_props)

        try:
            # Find similar anomalies
            similar_anomalies = self.knowledge_graph.find_similar_nodes(
                temp_node_id, 0.6
            )

            for similar_anomaly, similarity in similar_anomalies:
                # Get successful remediations for this anomaly
                remediations = self.knowledge_graph.get_related_nodes(
                    similar_anomaly.node_id, "resolves"
                )

                for remediation in remediations:
                    if remediation.properties.get("successf", False):
                        recommendation = {
                            "action_type": remediation.properties["action_type"],
                            "confidence": similarity
                            * remediation.properties.get("success", 1.0),
                            "similarity_score": similarity,
                            "execution_time": remediation.properties.get(
                                "execution_time", 0
                            ),
                            "source_anomaly": similar_anomaly.properties,
                            "reasoning": "Similar anomaly resolved with {remediation.properties['action_type']}",

                        }
                        recommendations.append(recommendation)

            # Sort by confidence and remove duplicates
            recommendations.sort(key=lambda x: x["confidence"], reverse=True)

            # Remove duplicates based on action_type
            seen_actions = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec["action_type"] not in seen_actions:
                    seen_actions.add(rec["action_type"])
                    unique_recommendations.append(rec)

            return unique_recommendations[:limit]

        finally:
            # Clean up temporary node
            if temp_node_id in self.knowledge_graph.nodes:
                del self.knowledge_graph.nodes[temp_node_id]

    def train_recommendation_model(self):
        """Train ML model for recommendations"""
        # Prepare training data from knowledge graph
        X = []
        y = []

        for node_id, node in self.knowledge_graph.nodes.items():
            if node.node_type == "anomaly":
                # Extract features from anomaly
                features = self._extract_anomaly_features(node)

                # Get successful remediations
                remediations = self.knowledge_graph.get_related_nodes(
                    node_id, "resolves"
                )
                successful_remediations = [
                    r for r in remediations if r.properties.get("success", False)
                ]

                if successful_remediations:
                    # Use the most successful remediation as target
                    best_remediation = max(
                        successful_remediations,
                        key=lambda r: r.properties.get("success", 1.0),
                    )

                    X.append(features)
                    y.append(best_remediation.properties["action_type"])

        if len(X) < 10:
            logger.warning("Not enough training data for recommendation model")
            return

        # Train model
        self.recommendation_model.fit(X, y)
        self.is_trained = True
        self.feature_names = [f"feature_{i}" for i in range(len(X[0]))]

        logger.info(f"Trained recommendation model with {len(X)} samples")

    def _extract_anomaly_features(self, anomaly_node: KnowledgeNode) -> List[float]:
        """Extract features from anomaly node for ML model""f"
        features = []

        # Severity encoding
        severity_encoding = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        features.append(
            severity_encoding.get(anomaly_node.properties.get("severity", "medium"), 1)
        )

        # Source encoding (simple hash)
        source = anomaly_node.properties.get("source", "unknown")
        features.append(hash(source) % 100)

        # Metrics features
        metrics = anomaly_node.properties.get("metrics_patternf", {})
        features.extend(
            [
                metrics.get("cpu_usage", 0),
                metrics.get("memory_usage", 0),
                metrics.get("disk_usage", 0),
                metrics.get("error_rate", 0),
                metrics.get("response_time", 0),
            ]
        )

        return features

    def predict_remediation(self, anomaly_info: Dict[str, Any]) -> str:
        """Predict remediation action using ML model"""
        if not self.is_trained:
            return "unknown"

        # Create temporary node for feature extraction
        temp_node = KnowledgeNode(
            node_id="temp",
            node_type="anomaly",
            properties=anomaly_info,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        features = self._extract_anomaly_features(temp_node)
        prediction = self.recommendation_model.predict([features])[0]

        return prediction


class KnowledgeBaseManager:
    """Manages knowledge base operations"""

    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.recommendation_engine = RecommendationEngine(self.knowledge_graph)

        # Build knowledge base if empty
        if not self.knowledge_graph.nodes:
            self.knowledge_graph.build_knowledge_from_data()
            self.recommendation_engine.train_recommendation_model()

    def get_recommendations(
        self, anomaly_info: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get remediation recommendations"""
        return self.recommendation_engine.get_recommendations(anomaly_info, limit)

    def predict_remediation(self, anomaly_info: Dict[str, Any]) -> str:
        """Predict remediation action"""
        return self.recommendation_engine.predict_remediation(anomaly_info)

    def add_experience(
        self, anomaly_info: Dict[str, Any], remediation_action: str, success: bool
    ):
        """Add new experience to knowledge base"""
        # Create anomaly node
        anomaly_node_id = self.knowledge_graph.add_node("anomalyf", anomaly_info)

        # Create remediation node
        remediation_props = {
            "action_type": remediation_action,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        remediation_node_id = self.knowledge_graph.add_node(
            "remediation", remediation_props
        )

        # Create edge
        weight = 1.0 if success else 0.3
        self.knowledge_graph.add_edge(
            anomaly_node_id, remediation_node_id, "resolves", weight
        )

        # Save knowledge base
        self.knowledge_graph.save_knowledge_base()

        logger.info(
            f"Added experience: {anomaly_info.get(
                'description', 'Unknown')} -> {remediation_action} (success: {success})"
        )

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        node_types = defaultdict(int)
        edge_types = defaultdict(int)

        for node in self.knowledge_graph.nodes.values():
            node_types[node.node_type] += 1

        for edges in self.knowledge_graph.edges.values():
            for edge in edges:
                edge_types[edge.relationship_type] += 1

        return {
            "total_nodes": len(self.knowledge_graph.nodes),
            "total_edges": sum(
                len(edges) for edges in self.knowledge_graph.edges.values()
            ),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
            "recommendation_model_trained": self.recommendation_engine.is_trained,
        }


# Global knowledge base manager
knowledge_base_manager = KnowledgeBaseManager()
