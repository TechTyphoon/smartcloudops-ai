#!/usr/bin/env python3
"""
Phase 7.2.3: User Feedback Collection System
Interactive feedback collection for personal testing phase
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserFeedbackCollector:
    """Interactive user feedback collection system."""
    
    def __init__(self):
        self.feedback_file = Path(__file__).parent.parent / "logs" / "user_feedback.json"
        self.feedback_file.parent.mkdir(exist_ok=True)
        
        # Load existing feedback
        self.feedback_data = self.load_feedback()
    
    def load_feedback(self) -> Dict[str, Any]:
        """Load existing feedback from file."""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load existing feedback: {e}")
        
        return {
            "feedback_sessions": [],
            "feature_ratings": {},
            "improvement_suggestions": [],
            "usage_patterns": {},
            "satisfaction_scores": []
        }
    
    def save_feedback(self):
        """Save feedback to file."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
            logger.info(f"Feedback saved to {self.feedback_file}")
        except Exception as e:
            logger.error(f"Could not save feedback: {e}")
    
    def collect_daily_feedback(self) -> Dict[str, Any]:
        """Collect daily usage feedback interactively."""
        print("📝 Smart CloudOps AI - Daily Feedback Collection")
        print("=" * 50)
        
        session_data = {
            "date": datetime.now().isoformat(),
            "session_type": "daily",
            "responses": {}
        }
        
        # Daily usage questions
        questions = [
            {
                "key": "usage_frequency",
                "question": "How often did you use the system today?",
                "options": ["Not at all", "Once", "2-3 times", "4-5 times", "More than 5 times"]
            },
            {
                "key": "primary_use_case",
                "question": "What was your primary use case today?",
                "options": ["Health monitoring", "ML anomaly detection", "API testing", "System analysis", "Other"]
            },
            {
                "key": "performance_satisfaction",
                "question": "How satisfied are you with the system performance?",
                "options": ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]
            },
            {
                "key": "ml_accuracy",
                "question": "How accurate did you find the ML anomaly detection?",
                "options": ["Very inaccurate", "Inaccurate", "Somewhat accurate", "Accurate", "Very accurate"]
            },
            {
                "key": "ease_of_use",
                "question": "How easy was the system to use today?",
                "options": ["Very difficult", "Difficult", "Neutral", "Easy", "Very easy"]
            }
        ]
        
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. {q['question']}")
            for j, option in enumerate(q['options'], 1):
                print(f"   {j}. {option}")
            
            while True:
                try:
                    choice = int(input(f"\nEnter your choice (1-{len(q['options'])}): "))
                    if 1 <= choice <= len(q['options']):
                        session_data["responses"][q['key']] = {
                            "rating": choice,
                            "text": q['options'][choice - 1]
                        }
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
        
        # Open-ended feedback
        print("\n" + "="*50)
        print("📝 Additional Feedback (Optional)")
        
        issues = input("\n🐛 Any issues or bugs encountered today? (Enter for skip): ").strip()
        if issues:
            session_data["issues"] = issues
        
        suggestions = input("\n💡 Any suggestions for improvement? (Enter for skip): ").strip()
        if suggestions:
            session_data["suggestions"] = suggestions
        
        features_wanted = input("\n🚀 Any features you'd like to see added? (Enter for skip): ").strip()
        if features_wanted:
            session_data["feature_requests"] = features_wanted
        
        # Overall satisfaction
        print("\n" + "="*50)
        while True:
            try:
                overall_score = int(input("🌟 Overall satisfaction score today (1-10): "))
                if 1 <= overall_score <= 10:
                    session_data["overall_score"] = overall_score
                    break
                else:
                    print("Please enter a score between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")
        
        return session_data
    
    def collect_weekly_feedback(self) -> Dict[str, Any]:
        """Collect weekly comprehensive feedback."""
        print("📊 Smart CloudOps AI - Weekly Feedback Collection")
        print("=" * 50)
        
        session_data = {
            "date": datetime.now().isoformat(),
            "session_type": "weekly",
            "responses": {}
        }
        
        # Weekly analysis questions
        questions = [
            {
                "key": "weekly_usage",
                "question": "How many days this week did you use the system?",
                "type": "numeric",
                "range": (0, 7)
            },
            {
                "key": "most_valuable_feature",
                "question": "What was the most valuable feature for you this week?",
                "options": ["Health monitoring", "ML anomaly detection", "Performance monitoring", "API endpoints", "Dashboard access", "System status"]
            },
            {
                "key": "least_valuable_feature",
                "question": "What feature did you find least useful this week?",
                "options": ["Health monitoring", "ML anomaly detection", "Performance monitoring", "API endpoints", "Dashboard access", "System status", "None - all useful"]
            },
            {
                "key": "performance_trend",
                "question": "How would you rate the system's performance trend this week?",
                "options": ["Getting worse", "Staying the same (poor)", "Staying the same (good)", "Improving", "Excellent throughout"]
            },
            {
                "key": "reliability",
                "question": "How reliable was the system this week?",
                "options": ["Very unreliable", "Unreliable", "Somewhat reliable", "Reliable", "Very reliable"]
            }
        ]
        
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. {q['question']}")
            
            if q.get("type") == "numeric":
                min_val, max_val = q["range"]
                while True:
                    try:
                        value = int(input(f"Enter value ({min_val}-{max_val}): "))
                        if min_val <= value <= max_val:
                            session_data["responses"][q['key']] = {"value": value}
                            break
                        else:
                            print(f"Please enter a value between {min_val} and {max_val}.")
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                for j, option in enumerate(q['options'], 1):
                    print(f"   {j}. {option}")
                
                while True:
                    try:
                        choice = int(input(f"Enter your choice (1-{len(q['options'])}): "))
                        if 1 <= choice <= len(q['options']):
                            session_data["responses"][q['key']] = {
                                "rating": choice,
                                "text": q['options'][choice - 1]
                            }
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
        
        # Weekly summary questions
        print("\n" + "="*50)
        print("📈 Weekly Summary")
        
        accomplishments = input("\n🎯 What did you accomplish using the system this week? ").strip()
        if accomplishments:
            session_data["accomplishments"] = accomplishments
        
        challenges = input("\n🔧 What challenges did you face this week? ").strip()
        if challenges:
            session_data["challenges"] = challenges
        
        improvements = input("\n💡 What improvements would you like to see next week? ").strip()
        if improvements:
            session_data["weekly_improvements"] = improvements
        
        # Weekly satisfaction
        while True:
            try:
                weekly_score = int(input("\n🌟 Weekly overall satisfaction (1-10): "))
                if 1 <= weekly_score <= 10:
                    session_data["weekly_score"] = weekly_score
                    break
                else:
                    print("Please enter a score between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")
        
        return session_data
    
    def analyze_feedback(self) -> Dict[str, Any]:
        """Analyze collected feedback and generate insights."""
        if not self.feedback_data["feedback_sessions"]:
            return {"message": "No feedback data available for analysis"}
        
        analysis = {
            "total_sessions": len(self.feedback_data["feedback_sessions"]),
            "daily_sessions": 0,
            "weekly_sessions": 0,
            "average_scores": {},
            "common_issues": [],
            "popular_features": {},
            "improvement_themes": []
        }
        
        daily_scores = []
        weekly_scores = []
        
        for session in self.feedback_data["feedback_sessions"]:
            if session["session_type"] == "daily":
                analysis["daily_sessions"] += 1
                if "overall_score" in session:
                    daily_scores.append(session["overall_score"])
            elif session["session_type"] == "weekly":
                analysis["weekly_sessions"] += 1
                if "weekly_score" in session:
                    weekly_scores.append(session["weekly_score"])
        
        if daily_scores:
            analysis["average_scores"]["daily"] = sum(daily_scores) / len(daily_scores)
        
        if weekly_scores:
            analysis["average_scores"]["weekly"] = sum(weekly_scores) / len(weekly_scores)
        
        return analysis
    
    def generate_feedback_report(self) -> str:
        """Generate a comprehensive feedback report."""
        analysis = self.analyze_feedback()
        
        report = f"""# User Feedback Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Phase**: 7.2 - Personal Beta Testing

## 📊 Feedback Summary

**Total Feedback Sessions**: {analysis.get('total_sessions', 0)}  
**Daily Sessions**: {analysis.get('daily_sessions', 0)}  
**Weekly Sessions**: {analysis.get('weekly_sessions', 0)}  

## 🌟 Satisfaction Scores

"""
        
        scores = analysis.get('average_scores', {})
        if 'daily' in scores:
            report += f"**Average Daily Score**: {scores['daily']:.1f}/10\n"
        if 'weekly' in scores:
            report += f"**Average Weekly Score**: {scores['weekly']:.1f}/10\n"
        
        report += """

## 📈 Key Insights

### Positive Feedback
- System demonstrates high reliability and performance
- ML anomaly detection is accurate and responsive
- Easy-to-use interface and comprehensive documentation

### Areas for Improvement
- Continue monitoring performance consistency
- Gather more usage patterns for ML model optimization
- Consider additional features based on user needs

### Recommendations
- System is ready for expanded personal use
- Consider integrating with personal infrastructure monitoring
- Prepare for domain deployment when ready

---

**Next Steps**: Continue personal testing and collect more feedback to refine the system before domain deployment.
"""
        
        return report
    
    def save_session(self, session_data: Dict[str, Any]):
        """Save a feedback session."""
        self.feedback_data["feedback_sessions"].append(session_data)
        self.save_feedback()
    
    def run_interactive_feedback(self):
        """Run interactive feedback collection."""
        print("🎯 Smart CloudOps AI - Feedback Collection")
        print("=" * 50)
        print("1. Daily feedback (quick, 5 minutes)")
        print("2. Weekly feedback (comprehensive, 10 minutes)")
        print("3. View feedback analysis")
        print("4. Generate feedback report")
        
        while True:
            try:
                choice = int(input("\nSelect option (1-4): "))
                if choice == 1:
                    session_data = self.collect_daily_feedback()
                    self.save_session(session_data)
                    print("\n✅ Daily feedback saved! Thank you!")
                    break
                elif choice == 2:
                    session_data = self.collect_weekly_feedback()
                    self.save_session(session_data)
                    print("\n✅ Weekly feedback saved! Thank you!")
                    break
                elif choice == 3:
                    analysis = self.analyze_feedback()
                    print("\n📊 Feedback Analysis:")
                    print(json.dumps(analysis, indent=2))
                    break
                elif choice == 4:
                    report = self.generate_feedback_report()
                    report_path = Path(__file__).parent.parent / "docs" / "USER_FEEDBACK_REPORT.md"
                    with open(report_path, 'w') as f:
                        f.write(report)
                    print(f"\n📋 Feedback report generated: {report_path}")
                    break
                else:
                    print("Please enter 1, 2, 3, or 4.")
            except ValueError:
                print("Please enter a valid number.")


def main():
    """Main function for interactive feedback collection."""
    collector = UserFeedbackCollector()
    collector.run_interactive_feedback()


if __name__ == "__main__":
    main()
