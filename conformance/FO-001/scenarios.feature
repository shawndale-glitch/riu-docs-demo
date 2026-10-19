# Generated from workflows/front-office/FO-001/workflow.yaml by tooling/workflow_render.py. Do not edit.
# Happy path = the shortest start-to-end path (governance/workflow-rules.yaml, conformance C2).
@FO-001 @v0.1.0
Feature: FO-001 Solicitud de check-in anticipado

  @happy @path-1
  Scenario: Path 1 (Yes)
    Given the process "FO-001" starts with "Early check-in requested" [38:511]
    When "Front desk" performs "Check room status" [38:514]
    And "Front desk" decides "Room clean and inspected?" [38:516]
    And the decision resolves to "Yes"
    And "Front desk" performs "Assign room" [38:519]
    And "Front desk" performs "Check in guest" [38:521]
    Then the process ends with "Guest checked in" [38:523]

  @path-2
  Scenario: Path 2 (No)
    Given the process "FO-001" starts with "Early check-in requested" [38:511]
    When "Front desk" performs "Check room status" [38:514]
    And "Front desk" decides "Room clean and inspected?" [38:516]
    And the decision resolves to "No"
    And "Housekeeping" performs "Prioritise room cleaning" [38:526]
    And "Housekeeping" performs "Inspect room" [38:528]
    And "Front desk" performs "Assign room" [38:519]
    And "Front desk" performs "Check in guest" [38:521]
    Then the process ends with "Guest checked in" [38:523]
