# /src/core/reporting/reporter.py

"""Test results reporting and dashboard generation."""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

from schemas.test_execution import (
    TestResults,
    TestOutcome,
    TestStatus,
    CoverageReport,
    CoverageStats,
    DashboardArtifact,
)


class Reporter:
    """
    Core component for generating test result reports and dashboards.

    Processes test outcomes to produce coverage metrics, mismatch reports,
    and aggregated dashboards.
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the reporter.

        Args:
            output_dir: Directory for storing reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self, results: TestResults, api_spec_info: Optional[Dict] = None
    ) -> DashboardArtifact:
        """
        Generate a comprehensive test report.

        Args:
            results: Test execution results
            api_spec_info: Optional API specification info for coverage calculation

        Returns:
            Dashboard artifact with coverage and mismatch reports
        """
        # Extract test outcomes
        outcomes = results.outcomes

        # Generate coverage reports
        coverage_reports = self._generate_coverage_reports(outcomes, api_spec_info)

        # Extract mismatches
        mismatches = [
            outcome for outcome in outcomes if outcome.status == TestStatus.MISMATCHED
        ]

        # Create dashboard
        dashboard = DashboardArtifact(
            coverage_reports=coverage_reports, mismatches=mismatches
        )

        # Write HTML report
        self._generate_html_report(dashboard)

        # Write JSON report
        self._generate_json_report(dashboard)

        return dashboard

    def _generate_coverage_reports(
        self, outcomes: List[TestOutcome], api_spec_info: Optional[Dict] = None
    ) -> List[CoverageReport]:
        """
        Generate coverage reports for each operation.

        Args:
            outcomes: Test execution outcomes
            api_spec_info: API specification info for coverage calculation

        Returns:
            List of coverage reports
        """
        # Group outcomes by operation
        operation_outcomes = defaultdict(list)

        for outcome in outcomes:
            # Try to extract operation ID from test name
            parts = outcome.test_name.split("_")
            if len(parts) >= 2 and parts[0].startswith("test"):
                # Format might be like "test_01_getUser"
                op_id = parts[-1]
                operation_outcomes[op_id].append(outcome)
            else:
                # If no clear pattern, put in "unknown" bucket
                operation_outcomes["unknown"].append(outcome)

        # Generate coverage report for each operation
        coverage_reports = []

        for op_id, op_outcomes in operation_outcomes.items():
            # Extract documented status codes from API spec if available
            documented_codes = set()
            if api_spec_info and "operations" in api_spec_info:
                for op in api_spec_info.get("operations", []):
                    if op.get("operation_id") == op_id:
                        for response in op.get("responses", []):
                            documented_codes.add(response.get("status_code", 0))

            # Extract covered status codes from outcomes
            covered_codes = set()
            undocumented_codes = set()
            for outcome in op_outcomes:
                if outcome.actual and outcome.actual.isdigit():
                    code = int(outcome.actual)
                    covered_codes.add(code)
                    if documented_codes and code not in documented_codes:
                        undocumented_codes.add(code)

            # Count false positives (tests reporting mismatches incorrectly)
            false_positive_count = sum(
                1
                for outcome in op_outcomes
                if outcome.status == TestStatus.MISMATCHED
                and self._is_likely_false_positive(outcome)
            )

            # Create coverage report
            report = CoverageReport(
                operation_id=op_id,
                stats=CoverageStats(
                    documented_codes=(
                        list(documented_codes) if documented_codes else [200, 400, 404]
                    ),
                    covered_codes=list(covered_codes),
                    undocumented_codes=list(undocumented_codes),
                ),
                false_positive_count=false_positive_count,
            )

            coverage_reports.append(report)

        return coverage_reports

    def _is_likely_false_positive(self, outcome: TestOutcome) -> bool:
        """
        Determine if a mismatch is likely a false positive.

        Args:
            outcome: Test outcome

        Returns:
            True if likely a false positive, False otherwise
        """
        # Simple heuristic: look for common signs of false positives
        if outcome.details and "expected schema not found" in outcome.details.lower():
            return True

        if outcome.expected and outcome.actual:
            # Check if expected and actual values are semantically equivalent
            try:
                # Handle numeric comparisons (e.g., "200" == 200)
                if outcome.expected.isdigit() and outcome.actual.isdigit():
                    return int(outcome.expected) == int(outcome.actual)

                # Handle boolean comparisons (e.g., "true" == True)
                if outcome.expected.lower() in [
                    "true",
                    "false",
                ] and outcome.actual.lower() in ["true", "false"]:
                    return outcome.expected.lower() == outcome.actual.lower()

            except (ValueError, AttributeError):
                pass

        return False

    def _generate_html_report(self, dashboard: DashboardArtifact):
        """Generate an HTML report from the dashboard."""
        html_path = self.output_dir / "report.html"

        # Simple HTML template
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; text-align: left; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .unknown {{ color: orange; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>API Test Report</h1>
        <p>Generated: {dashboard.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Coverage Summary</h2>
        <table>
            <tr>
                <th>Operation</th>
                <th>Documented Codes</th>
                <th>Covered Codes</th>
                <th>Undocumented Codes</th>
                <th>False Positives</th>
            </tr>
"""

        for report in dashboard.coverage_reports:
            html += f"""
            <tr>
                <td>{report.operation_id}</td>
                <td>{', '.join(map(str, report.stats.documented_codes))}</td>
                <td>{', '.join(map(str, report.stats.covered_codes))}</td>
                <td>{', '.join(map(str, report.stats.undocumented_codes))}</td>
                <td>{report.false_positive_count}</td>
            </tr>"""

        html += """
        </table>
        
        <h2>Mismatches</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Expected</th>
                <th>Actual</th>
                <th>Details</th>
            </tr>
"""

        for mismatch in dashboard.mismatches:
            html += f"""
            <tr class="failure">
                <td>{mismatch.test_name}</td>
                <td>{mismatch.expected or 'N/A'}</td>
                <td>{mismatch.actual or 'N/A'}</td>
                <td>{mismatch.details or 'N/A'}</td>
            </tr>"""

        html += """
        </table>
    </div>
</body>
</html>
"""

        with open(html_path, "w") as f:
            f.write(html)

    def _generate_json_report(self, dashboard: DashboardArtifact):
        """Generate a JSON report from the dashboard."""
        json_path = self.output_dir / "report.json"

        # Convert dashboard to dictionary
        dashboard_dict = dashboard.dict()

        # Convert datetime to string for JSON serialization
        dashboard_dict["generated_at"] = dashboard.generated_at.isoformat()

        # Write to file
        with open(json_path, "w") as f:
            json.dump(dashboard_dict, f, indent=2)
