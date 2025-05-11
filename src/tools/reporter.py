# /src/tools/reporter.py
from .base import BaseTool
from schemas.index import (
    ReporterInput,
    ReporterOutput,
    DashboardArtifact,
)

from schemas.test_execution import (
    CoverageReport,
    CoverageStats,
)


class ReporterTool(BaseTool[ReporterInput, ReporterOutput]):
    def _generate_mock_data(self, outcomes) -> ReporterOutput:
        """Generate mock dashboard artifact."""
        cov = CoverageReport(
            operation_id="getFlights",
            stats=CoverageStats(
                documented_codes=[200],
                covered_codes=[200],
                undocumented_codes=[],
            ),
            false_positive_count=0,
        )
        dash = DashboardArtifact(coverage_reports=[cov], mismatches=outcomes)
        return ReporterOutput(dashboard=dash)

    def run(self, payload: ReporterInput) -> ReporterOutput:
        return self._generate_mock_data(payload.results.outcomes)
