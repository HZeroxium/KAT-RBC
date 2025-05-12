# /src/core/reinforcement/experience_reinforcement.py

"""Experience reinforcement for improving test generation."""

import json
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import sqlite3

from schemas.test_execution import TestResults, TestOutcome, TestStatus
from schemas.experience_reinforcement import ReinforcementUpdate, PromptTemplate
from schemas.dependency import ODGEdge


class ExperienceReinforcement:
    """
    Core component for reinforcement learning from test execution results.

    Stores test outcomes and uses them to refine prompts and dependency weights.
    """

    def __init__(self, db_path: str = "experience.db"):
        """
        Initialize the experience reinforcement.

        Args:
            db_path: Path to the SQLite database for storing experience
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the SQLite database for storing experience."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS test_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT,
            status TEXT,
            expected TEXT,
            actual TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            template_text TEXT,
            version TEXT,
            success_rate REAL,
            usage_count INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS odg_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_operation TEXT,
            dst_operation TEXT,
            weight REAL DEFAULT 1.0,
            successful_uses INTEGER DEFAULT 0,
            failed_uses INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        conn.commit()
        conn.close()

    def process_results(self, test_results: TestResults) -> ReinforcementUpdate:
        """
        Process test execution results for reinforcement learning.

        Args:
            test_results: Results from test execution

        Returns:
            Reinforcement update with refined prompts and adjusted weights
        """
        # Store results in database
        self._store_results(test_results)

        # Update prompt templates based on results
        refined_prompts = self._update_prompts(test_results)

        # Update ODG edge weights based on results
        updated_weights = self._update_weights(test_results)

        return ReinforcementUpdate(
            refined_prompts=refined_prompts, updated_odg_weights=updated_weights
        )

    def _store_results(self, test_results: TestResults):
        """Store test results in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for outcome in test_results.outcomes:
            cursor.execute(
                """
                INSERT INTO test_outcomes 
                (test_name, status, expected, actual, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    outcome.test_name,
                    outcome.status.value,
                    outcome.expected or "",
                    outcome.actual or "",
                    outcome.details or "",
                ),
            )

        conn.commit()
        conn.close()

    def _update_prompts(self, test_results: TestResults) -> List[PromptTemplate]:
        """
        Update prompt templates based on test results.

        Args:
            test_results: Results from test execution

        Returns:
            List of refined prompt templates
        """
        # In a full implementation, this would:
        # 1. Analyze which prompts led to successful vs. failed tests
        # 2. Use LLM to refine prompt templates based on success/failure patterns
        # 3. Update the database with new templates

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current templates
        cursor.execute("SELECT name, template_text, version FROM prompt_templates")
        templates = cursor.fetchall()

        # Close connection before returning
        conn.close()

        # Create PromptTemplate objects for each template
        refined_templates = [
            PromptTemplate(name=name, template_text=template, version=version)
            for name, template, version in templates
        ]

        # If no templates exist, create a default one
        if not refined_templates:
            default_template = PromptTemplate(
                name="default_constraint_template",
                template_text=(
                    "You are an API testing assistant. "
                    "Given the following API specification, extract constraints "
                    "that should be verified in tests:\n\n"
                    "{{specification}}\n\n"
                    "Please output constraints in the following format:\n"
                    "- Constraint: [description]\n"
                    "- Expression: [testable expression]\n"
                ),
                version="1.0.0",
            )
            refined_templates.append(default_template)

        return refined_templates

    def _update_weights(self, test_results: TestResults) -> Dict[str, float]:
        """
        Update ODG edge weights based on test results.

        Args:
            test_results: Results from test execution

        Returns:
            Dictionary of updated ODG edge weights
        """
        updated_weights = {}

        # In a full implementation, this would:
        # 1. Parse test names to identify operations in each test
        # 2. Analyze sequence correctness based on test outcomes
        # 3. Update weights for edges in the ODG

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current weights
        cursor.execute("SELECT src_operation, dst_operation, weight FROM odg_weights")
        weights = cursor.fetchall()

        for src, dst, weight in weights:
            edge_key = f"{src}->{dst}"
            updated_weights[edge_key] = weight

            # In a real implementation, we would update weights based on test outcomes
            # For example, increase weight if tests for this edge were successful

        # Close connection
        conn.close()

        return updated_weights

    def get_prompt_templates(self) -> List[PromptTemplate]:
        """Get all prompt templates from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name, template_text, version FROM prompt_templates")
        templates = cursor.fetchall()

        conn.close()

        return [
            PromptTemplate(name=name, template_text=template, version=version)
            for name, template, version in templates
        ]

    def get_odg_weights(self) -> Dict[str, float]:
        """Get all ODG edge weights from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT src_operation, dst_operation, weight FROM odg_weights")
        weights = cursor.fetchall()

        conn.close()

        return {f"{src}->{dst}": weight for src, dst, weight in weights}

    def add_prompt_template(self, template: PromptTemplate) -> bool:
        """
        Add a new prompt template to the database.

        Args:
            template: Prompt template to add

        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO prompt_templates
                (name, template_text, version, success_rate, usage_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (template.name, template.template_text, template.version, 0.0, 0),
            )
            conn.commit()
            success = True
        except sqlite3.Error:
            conn.rollback()
            success = False
        finally:
            conn.close()

        return success

    def update_odg_edge(
        self, src_operation: str, dst_operation: str, weight: float
    ) -> bool:
        """
        Update an ODG edge weight in the database.

        Args:
            src_operation: Source operation ID
            dst_operation: Destination operation ID
            weight: New edge weight

        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if edge exists
            cursor.execute(
                """
                SELECT COUNT(*) FROM odg_weights
                WHERE src_operation = ? AND dst_operation = ?
                """,
                (src_operation, dst_operation),
            )
            count = cursor.fetchone()[0]

            if count > 0:
                # Update existing edge
                cursor.execute(
                    """
                    UPDATE odg_weights
                    SET weight = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE src_operation = ? AND dst_operation = ?
                    """,
                    (weight, src_operation, dst_operation),
                )
            else:
                # Insert new edge
                cursor.execute(
                    """
                    INSERT INTO odg_weights
                    (src_operation, dst_operation, weight)
                    VALUES (?, ?, ?)
                    """,
                    (src_operation, dst_operation, weight),
                )

            conn.commit()
            success = True
        except sqlite3.Error:
            conn.rollback()
            success = False
        finally:
            conn.close()

        return success
