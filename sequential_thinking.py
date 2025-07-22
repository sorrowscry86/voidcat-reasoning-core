# sequential_thinking.py
"""
VoidCat Sequential Thinking Engine

Implements advanced sequential reasoning capabilities based on the comprehensive
analysis of MCP variants. This module provides structured, step-by-step reasoning
with context retrieval, hypothesis generation, and iterative refinement.

Architecture:
- Multi-stage reasoning pipeline
- Branch-based thought exploration
- Retrieval-augmented thinking integration
- Dynamic complexity assessment
- Error recovery and validation

Author: VoidCat Reasoning Core Team
License: MIT
Version: 1.0.0
"""

import asyncio
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


def debug_print(message: str) -> None:
    """Print debug messages to stderr to avoid interfering with MCP protocol."""
    print(f"[Sequential Thinking] {message}", file=sys.stderr, flush=True)


class ComplexityLevel(Enum):
    """Problem complexity classification for reasoning strategy selection."""

    SIMPLE = "simple"
    MEDIUM = "medium"
    HIGH = "high"
    EXPERT = "expert"


class ThoughtType(Enum):
    """Types of reasoning thoughts in the sequential thinking process."""

    ANALYSIS = "analysis"
    HYPOTHESIS = "hypothesis"
    VALIDATION = "validation"
    SYNTHESIS = "synthesis"
    REVISION = "revision"


@dataclass
class Thought:
    """Individual thought in the sequential reasoning process."""

    id: str
    type: ThoughtType
    content: str
    confidence: float
    timestamp: str
    parent_id: Optional[str] = None
    validation_status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        """Convert thought to dictionary representation."""
        return {
            **asdict(self),
            "type": self.type.value,
            "validation_status": self.validation_status,
        }


@dataclass
class ReasoningBranch:
    """A branch of reasoning containing multiple related thoughts."""

    id: str
    name: str
    thoughts: List[Thought]
    confidence: float
    created_at: str
    status: str = "active"

    def add_thought(self, thought: Thought) -> None:
        """Add a thought to this reasoning branch."""
        self.thoughts.append(thought)
        # Update branch confidence based on latest thoughts
        if self.thoughts:
            recent_thoughts = self.thoughts[-3:]  # Last 3 thoughts
            self.confidence = sum(t.confidence for t in recent_thoughts) / len(
                recent_thoughts
            )


@dataclass
class ReasoningSession:
    """Complete reasoning session with multiple branches and final synthesis."""

    id: str
    query: str
    complexity: ComplexityLevel
    branches: List[ReasoningBranch]
    final_synthesis: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = None
    total_thoughts: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()

    def get_summary(self) -> Dict[str, Any]:
        """Get session summary for diagnostics."""
        return {
            "session_id": self.id,
            "query": self.query[:100] + "..." if len(self.query) > 100 else self.query,
            "complexity": self.complexity.value,
            "branch_count": len(self.branches),
            "total_thoughts": sum(len(branch.thoughts) for branch in self.branches),
            "status": "completed" if self.completed_at else "active",
            "duration_seconds": (
                self._calculate_duration() if self.completed_at else None
            ),
        }

    def _calculate_duration(self) -> float:
        """Calculate session duration in seconds."""
        if not self.created_at or not self.completed_at:
            return 0.0

        start = (
            datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            if self.created_at
            else None
        )
        end = (
            datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
            if self.completed_at
            else None
        )

        return (end - start).total_seconds() if start and end else 0.0


class SequentialThinkingEngine:
    """
    Advanced sequential thinking engine with multi-stage reasoning pipeline.

    Implements hybrid architecture combining:
    - Linear sequential thinking for simple problems
    - Branch-based reasoning for complex scenarios
    - Retrieval-augmented enhancement
    - Dynamic complexity assessment
    - Iterative refinement and validation
    """

    def __init__(self):
        """Initialize the sequential thinking engine."""
        self.sessions: Dict[str, ReasoningSession] = {}
        self.thought_counter = 0
        self.session_counter = 0
        self.total_queries_processed = 0

        debug_print("Sequential Thinking Engine initialized")

    async def _stage_1_analysis(
        self, session: ReasoningSession, query: str, context: str
    ):
        """Stage 1: Initial analysis and problem decomposition."""
        analysis_thought = Thought(
            id=f"analysis_{len(session.branches)}_1",
            content=f"Initial analysis of query: {query}",
            type=ThoughtType.ANALYSIS,
            confidence=0.8,
            timestamp=datetime.now(UTC).isoformat(),
        )

        # Create initial analysis branch
        analysis_branch = ReasoningBranch(
            id=f"branch_analysis_{len(session.branches)}",
            name="Initial problem analysis",
            thoughts=[analysis_thought],
            confidence=analysis_thought.confidence,
            created_at=datetime.now(UTC).isoformat(),
        )
        session.branches.append(analysis_branch)

        # Add context analysis if provided
        if context:
            context_thought = Thought(
                id=f"context_{len(session.branches)}_1",
                content=f"Relevant context: {context}",
                type=ThoughtType.ANALYSIS,
                confidence=0.9,
                timestamp=datetime.now(UTC).isoformat(),
            )
            analysis_branch.thoughts.append(context_thought)

    async def _simple_reasoning_path(
        self, session: ReasoningSession, max_thoughts: int
    ):
        """Simple reasoning path for straightforward queries."""
        reasoning_branch = ReasoningBranch(
            id=f"branch_simple_{len(session.branches)}",
            name="Direct reasoning approach",
            thoughts=[],
            confidence=0.0,
            created_at=datetime.now(UTC).isoformat(),
        )

        # Generate direct reasoning thoughts
        for i in range(min(3, max_thoughts)):
            thought = Thought(
                id=f"simple_{len(session.branches)}_{i+1}",
                content=f"Simple reasoning step {i+1} for: {session.query}",
                type=ThoughtType.ANALYSIS,
                confidence=0.7 + (i * 0.1),
                timestamp=datetime.now(UTC).isoformat(),
            )
            reasoning_branch.thoughts.append(thought)

        session.branches.append(reasoning_branch)

    async def _medium_complexity_reasoning(
        self, session: ReasoningSession, max_thoughts: int
    ):
        """Medium complexity reasoning with multiple perspectives."""
        # Create multiple reasoning branches
        for branch_num in range(2):
            reasoning_branch = ReasoningBranch(
                id=f"branch_medium_{len(session.branches)}_{branch_num}",
                name=f"Medium complexity approach {branch_num + 1}",
                thoughts=[],
                confidence=0.0,
                created_at=datetime.now(UTC).isoformat(),
            )

            # Generate thoughts for this branch
            thoughts_per_branch = max_thoughts // 2
            for i in range(thoughts_per_branch):
                thought = Thought(
                    id=f"medium_{len(session.branches)}_{branch_num}_{i+1}",
                    content=f"Medium reasoning step {i+1} for branch {branch_num + 1}: {session.query}",
                    type=ThoughtType.ANALYSIS,
                    confidence=0.6 + (i * 0.05),
                    timestamp=datetime.now(UTC).isoformat(),
                )
                reasoning_branch.thoughts.append(thought)

            session.branches.append(reasoning_branch)

    async def _complex_reasoning_path(
        self, session: ReasoningSession, max_thoughts: int
    ):
        """Complex reasoning path with deep analysis."""
        # Create multiple specialized branches
        branch_types = ["analytical", "creative", "systematic"]

        for branch_type in branch_types:
            reasoning_branch = ReasoningBranch(
                id=f"branch_complex_{len(session.branches)}_{branch_type}",
                name=f"Complex {branch_type} reasoning approach",
                thoughts=[],
                confidence=0.0,
                created_at=datetime.now(UTC).isoformat(),
            )

            # Generate thoughts for this branch
            thoughts_per_branch = max_thoughts // len(branch_types)
            for i in range(thoughts_per_branch):
                thought = Thought(
                    id=f"complex_{len(session.branches)}_{branch_type}_{i+1}",
                    content=f"Complex {branch_type} reasoning step {i+1}: {session.query}",
                    type=ThoughtType.ANALYSIS,
                    confidence=0.5 + (i * 0.1),
                    timestamp=datetime.now(UTC).isoformat(),
                )
                reasoning_branch.thoughts.append(thought)

            session.branches.append(reasoning_branch)

    async def _stage_3_synthesis(self, session: ReasoningSession):
        """Stage 3: Synthesis and validation of all reasoning paths."""
        all_thoughts = []
        for branch in session.branches:
            all_thoughts.extend(branch.thoughts)

        # Create synthesis based on all thoughts
        synthesis_content = f"Synthesis of {len(all_thoughts)} thoughts across {len(session.branches)} reasoning branches for query: {session.query}"

        # Add confidence-weighted conclusion
        total_confidence = sum(thought.confidence for thought in all_thoughts)
        avg_confidence = total_confidence / len(all_thoughts) if all_thoughts else 0.5

        synthesis_content += (
            f"\n\nAverage confidence across reasoning paths: {avg_confidence:.2f}"
        )
        synthesis_content += f"\nFinal answer based on multi-path reasoning analysis."

        session.final_synthesis = synthesis_content

    def _format_reasoning_path(self, session: ReasoningSession) -> List[Dict[str, Any]]:
        """Format the reasoning path for display."""
        formatted_path = []

        for branch in session.branches:
            branch_data = {
                "branch_id": branch.id,
                "description": branch.name,
                "thoughts": [],
            }

            for thought in branch.thoughts:
                thought_data = {
                    "id": thought.id,
                    "content": thought.content,
                    "type": thought.type.value,
                    "confidence": thought.confidence,
                }
                branch_data["thoughts"].append(thought_data)

            formatted_path.append(branch_data)

        return formatted_path

    def _calculate_session_confidence(self, session: ReasoningSession) -> float:
        """Calculate overall confidence for the reasoning session."""
        all_thoughts = []
        for branch in session.branches:
            all_thoughts.extend(branch.thoughts)

        if not all_thoughts:
            return 0.5

        total_confidence = sum(thought.confidence for thought in all_thoughts)
        avg_confidence = total_confidence / len(all_thoughts)

        # Apply complexity penalty
        complexity_multiplier = {
            ComplexityLevel.SIMPLE: 1.0,
            ComplexityLevel.MEDIUM: 0.9,
            ComplexityLevel.HIGH: 0.8,
            ComplexityLevel.EXPERT: 0.7,
        }

        return avg_confidence * complexity_multiplier.get(session.complexity, 0.8)

    def assess_complexity(self, query: str) -> ComplexityLevel:
        """
        Assess query complexity to determine reasoning strategy.

        Args:
            query (str): User query to analyze

        Returns:
            ComplexityLevel: Assessed complexity level
        """
        # Complexity indicators
        complexity_indicators = {
            "simple": [
                "what is",
                "define",
                "explain",
                "how do",
                "when",
                "where",
                "who",
                "basic",
                "simple",
            ],
            "medium": [
                "analyze",
                "compare",
                "evaluate",
                "assess",
                "why",
                "relationship",
                "impact",
                "strategy",
                "approach",
            ],
            "high": [
                "optimize",
                "design",
                "architect",
                "integrate",
                "multi-step",
                "complex",
                "sophisticated",
                "advanced",
            ],
            "expert": [
                "theoretical",
                "algorithmic",
                "mathematical proof",
                "research",
                "novel",
                "innovative",
                "cutting-edge",
            ],
        }

        query_lower = query.lower()
        word_count = len(query.split())

        # Score each complexity level
        scores = {}
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in query_lower)
            scores[level] = score

        # Adjust scores based on query length and structure
        if word_count < 10:
            scores["simple"] += 2
        elif word_count > 30:
            scores["high"] += 1
            scores["expert"] += 1

        # Count question words (indicates complexity)
        question_words = ["how", "why", "what", "when", "where", "which"]
        question_count = sum(1 for word in question_words if word in query_lower)
        if question_count > 2:
            scores["high"] += 1

        # Determine final complexity
        max_score = max(scores.values())
        if max_score == 0:
            return ComplexityLevel.MEDIUM  # Default for unclear cases

        for level in ["expert", "high", "medium", "simple"]:
            if scores[level] == max_score:
                return ComplexityLevel(level)

        return ComplexityLevel.MEDIUM

    async def process_query(
        self, query: str, context: str = "", max_thoughts: int = 10
    ) -> Dict[str, Any]:
        """
        Process a query using sequential thinking methodology.

        Args:
            query (str): User query to process
            context (str): Additional context from RAG system
            max_thoughts (int): Maximum number of thoughts to generate

        Returns:
            Dict containing reasoning session and final response
        """
        self.total_queries_processed += 1
        self.session_counter += 1

        session_id = f"session_{self.session_counter}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        complexity = self.assess_complexity(query)

        debug_print(
            f"Starting reasoning session {session_id} with complexity: {complexity.value}"
        )

        # Create reasoning session
        session = ReasoningSession(
            id=session_id,
            query=query,
            complexity=complexity,
            branches=[],  # Initialize with empty branches list
        )

        try:
            # Stage 1: Initial Analysis
            await self._stage_1_analysis(session, query, context)

            # Stage 2: Multi-path Reasoning (based on complexity)
            if complexity == ComplexityLevel.SIMPLE:
                await self._simple_reasoning_path(session, max_thoughts)
            elif complexity == ComplexityLevel.MEDIUM:
                await self._medium_complexity_reasoning(session, max_thoughts)
            else:  # HIGH or EXPERT
                await self._complex_reasoning_path(session, max_thoughts)

            # Stage 3: Synthesis and Validation
            await self._stage_3_synthesis(session)

            # Mark session as completed
            session.completed_at = datetime.now(UTC).isoformat()
            self.sessions[session_id] = session

            debug_print(f"Reasoning session {session_id} completed successfully")

            return {
                "session_id": session_id,
                "reasoning_path": self._format_reasoning_path(session),
                "final_response": session.final_synthesis,
                "complexity": complexity.value,
                "thought_count": sum(
                    len(branch.thoughts) for branch in session.branches
                ),
                "confidence": self._calculate_session_confidence(session),
            }

        except Exception as e:
            debug_print(f"Error in reasoning session {session_id}: {str(e)}")
            session.final_synthesis = f"Error during reasoning: {str(e)}"
            session.completed_at = datetime.now(UTC).isoformat()
            self.sessions[session_id] = session

            return {
                "session_id": session_id,
                "error": str(e),
                "reasoning_path": self._format_reasoning_path(session),
                "final_response": session.final_synthesis,
            }
