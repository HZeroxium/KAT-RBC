# KAT-RBC: Knowledge-Augmented Test Generation for REST APIs Based on Constraints

## Overview

KAT-RBC is a framework for automated testing of REST APIs using constraint-based methods. It integrates static analysis of OpenAPI specifications with dynamic analysis of API execution logs to generate effective test cases.

## Architecture

The system follows a pipeline architecture with these main components:

1. **Specification Processing**: Loads and parses OpenAPI/Swagger specifications
2. **Constraint Mining**: Extracts constraints from both static specs and dynamic execution
3. **Operation Dependency Analysis**: Constructs operation dependency graphs (ODG)
4. **Test Generation**: Creates test data and test scripts based on discovered constraints
5. **Test Execution & Reporting**: Runs tests against target APIs and generates reports

## Installation

```bash
# Clone the repository
git clone https://github.com/HZeroxium/KAT-RBC.git
cd KAT-RBC

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
# Basic usage
python src/main.py
```

## Project Structure

```plaintext
KAT-RBC/
├── src/
│   ├── main.py              # Main pipeline entry point
│   ├── tools/               # Testing tool implementations
│   └── schemas/             # Pydantic data models
│       ├── index.py         # Schema exports
│       ├── system_io.py     # System I/O related schemas
│       └── ...
├── tests/                   # Test suite for the framework
└── docs/                    # Documentation
```

## Tools

The framework includes various tools for different stages of the testing pipeline:

- **SpecLoaderTool**: Loads and parses OpenAPI specifications
- **ODGConstructorTool**: Builds operation dependency graphs
- **StaticConstraintMinerTool**: Extracts constraints from specifications
- **DynamicConstraintMinerTool**: Discovers invariants from execution logs
- **ConstraintCombinerTool**: Unifies constraints from different sources
- **OperationSequencerTool**: Determines API call sequences
- **TestDataGeneratorTool**: Generates test data based on constraints
- **TestScriptGeneratorTool**: Creates executable test scripts
- **SemanticVerifierTool**: Validates generated tests
- **TestExecutorTool**: Runs tests against target APIs
- **ExperienceReinforcementTool**: Improves testing based on results
- **ReporterTool**: Generates test reports and dashboards

## License
