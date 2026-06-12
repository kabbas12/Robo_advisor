"""
Risk Assessment Module for Robo-Advisor
Complete 7-question questionnaire with professional scoring
"""

import streamlit as st

class RiskProfiler:
    """Professional risk profiling system used by banks"""
    
    # Pre-defined questions with options and scores
    QUESTIONS = [
        {
            "id": 1,
            "text": "What is your investment time horizon?",
            "options": [
                ("Less than 1 year", 1),
                ("1-3 years", 2),
                ("3-5 years", 3),
                ("5-10 years", 4),
                ("More than 10 years", 5)
            ],
            "help": "Longer horizons allow more time to recover from market downturns"
        },
        {
            "id": 2,
            "text": "How would you describe your investment knowledge?",
            "options": [
                ("None - I'm a beginner", 1),
                ("Limited - I know basics", 2),
                ("Moderate - Some experience", 3),
                ("Good - Regular investor", 4),
                ("Expert - Professional experience", 5)
            ],
            "help": "More knowledge often correlates with higher risk tolerance"
        },
        {
            "id": 3,
            "text": "If your portfolio lost 20% in one month, what would you do?",
            "options": [
                ("Sell everything immediately", 1),
                ("Sell half to limit losses", 2),
                ("Do nothing and wait", 3),
                ("Buy more at lower prices", 4),
                ("Aggressively increase investment", 5)
            ],
            "help": "Reaction to loss is the best indicator of true risk tolerance"
        },
        {
            "id": 4,
            "text": "What is your primary investment goal?",
            "options": [
                ("Preserve capital (no losses)", 1),
                ("Generate regular income", 2),
                ("Balanced growth & safety", 3),
                ("Long-term growth", 4),
                ("Maximum growth (high risk)", 5)
            ],
            "help": "Your goal determines the appropriate strategy"
        },
        {
            "id": 5,
            "text": "What percentage of your total savings are you investing?",
            "options": [
                ("Less than 10%", 1),
                ("10-25%", 2),
                ("25-50%", 3),
                ("50-75%", 4),
                ("More than 75%", 5)
            ],
            "help": "Higher percentage suggests higher risk capacity"
        },
        {
            "id": 6,
            "text": "Expected annual return target:",
            "options": [
                ("3-4% (very safe)", 1),
                ("5-6% (conservative)", 2),
                ("7-8% (balanced)", 3),
                ("9-10% (growth)", 4),
                ("11%+ (aggressive)", 5)
            ],
            "help": "Higher returns require accepting higher risk"
        },
        {
            "id": 7,
            "text": "How would a 30% market decline affect your lifestyle?",
            "options": [
                ("Devastating - I'd struggle", 1),
                ("Very concerning - major impact", 2),
                ("Somewhat concerning - minor impact", 3),
                ("Not much - I'd be fine", 4),
                ("No impact - I'm well diversified", 5)
            ],
            "help": "Tests your actual financial capacity for risk"
        }
    ]
    
    @staticmethod
    def get_risk_profile(answers):
        """
        Calculate risk profile from answers
        Returns: profile name, score, recommendation
        """
        total_score = sum(answers)
        
        if total_score <= 14:
            return {
                "profile": "Conservative",
                "score": total_score,
                "max_score": 35,
                "color": "#2E86AB",
                "description": "You prioritize capital preservation over high returns. Your portfolio will focus on bonds and stable assets.",
                "risk_capacity": "Low",
                "suitable_for": "Retirement funds, emergency savings, short-term goals"
            }
        elif total_score <= 24:
            return {
                "profile": "Moderate",
                "score": total_score,
                "max_score": 35,
                "color": "#F18F01",
                "description": "You seek balanced growth with managed risk. Your portfolio will mix stocks and bonds.",
                "risk_capacity": "Medium",
                "suitable_for": "Retirement (5-10 years), college funds, wealth building"
            }
        else:
            return {
                "profile": "Aggressive",
                "score": total_score,
                "max_score": 35,
                "color": "#C73E1D",
                "description": "You pursue maximum growth and accept volatility. Your portfolio will focus on stocks.",
                "risk_capacity": "High",
                "suitable_for": "Long-term wealth, inheritance, high-income investors"
            }
    
    @staticmethod
    def display_questionnaire():
        """Display interactive questionnaire in Streamlit"""
        st.header("📋 Complete Risk Assessment")
        
        answers = []
        
        # Display each question
        for q in RiskProfiler.QUESTIONS:
            st.markdown(f"### {q['id']}. {q['text']}")
            
            # Create radio buttons for options
            options_text = [opt[0] for opt in q['options']]
            selected = st.radio(
                "",
                options=options_text,
                key=f"q_{q['id']}",
                help=q['help'],
                horizontal=False,
                label_visibility="collapsed"
            )
            
            # Get score for selected option
            selected_score = dict(q['options'])[selected]
            answers.append(selected_score)
            
            st.markdown("---")
        
        return answers

# Example usage in Streamlit
def demo_questionnaire():
    st.title("Risk Profiler Demo")
    
    profiler = RiskProfiler()
    answers = profiler.display_questionnaire()
    
    if st.button("Calculate My Risk Profile"):
        result = profiler.get_risk_profile(answers)
        
        st.success(f"### Your Profile: {result['profile']}")
        st.metric("Risk Score", f"{result['score']}/{result['max_score']}")
        st.info(result['description'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Risk Capacity", result['risk_capacity'])
        with col2:
            st.metric("Best For", result['suitable_for'])

if __name__ == "__main__":
    demo_questionnaire()
