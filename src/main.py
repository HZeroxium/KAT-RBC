# /src/main.py

import os
from pprint import pprint

# Import our workflows
from workflows import CombinedTestingWorkflow, RBCTestWorkflow, KATWorkflow


def main():
    # Example spec file path
    spec_path = "examples/petstore.yaml"

    # You can load content directly if needed
    spec_content = None
    if not os.path.exists(spec_path):
        spec_content = """
        openapi: 3.1.0
        info:
          title: Mock API
          version: 0.1.0
        paths:
          /pets:
            get:
              summary: List all pets
              responses:
                '200':
                  description: A list of pets
                  content:
                    application/json:
                      schema:
                        type: array
                        items:
                          $ref: '#/components/schemas/Pet'
            post:
              summary: Create a pet
              requestBody:
                content:
                  application/json:
                    schema:
                      $ref: '#/components/schemas/Pet'
              responses:
                '201':
                  description: Created
        components:
          schemas:
            Pet:
              type: object
              properties:
                id:
                  type: integer
                  description: The pet ID (must be positive)
                name:
                  type: string
                  description: The pet name (must not be empty)
                status:
                  type: string
                  enum: [available, pending, sold]
        """

    print("===== Running Combined Testing Workflow =====")
    # Initialize the combined workflow
    combined_workflow = CombinedTestingWorkflow()

    # Run the combined workflow
    result = combined_workflow.run(
        combined_workflow.input_class(
            spec_path=spec_path,
            spec_content=spec_content,
            target_base_url="https://petstore.swagger.io/v2",
            save_reports_to="reports/",
        )
    )

    # Display the results
    print("\nDashboard summary:")
    pprint(result.dashboard.model_dump(), depth=2)

    # You can also run individual workflows if needed
    print("\n===== Running RBCTest Workflow (Constraint-focused) =====")
    rbctest_workflow = RBCTestWorkflow()
    rbctest_result = rbctest_workflow.run(
        rbctest_workflow.input_class(
            spec_path=spec_path,
            spec_content=spec_content,
            target_base_url="https://petstore.swagger.io/v2",
        )
    )

    print("\nIdentified constraints:")
    pprint(rbctest_result.unified_constraints, depth=2)

    print("\n===== Running KAT Workflow (Dependency-focused) =====")
    kat_workflow = KATWorkflow()
    kat_result = kat_workflow.run(
        kat_workflow.input_class(
            spec_path=spec_path,
            spec_content=spec_content,
            target_base_url="https://petstore.swagger.io/v2",
        )
    )

    print("\nOperation Dependency Graph:")
    pprint(kat_result.odg.model_dump(), depth=2)


if __name__ == "__main__":
    main()
