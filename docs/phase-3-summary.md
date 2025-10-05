# Phase 3: Enhanced Detection Engine — Plan Summary

## Objectives
- Integrate AI insights with AST-based static analysis
- Enhance detection rules and implement a blended risk scoring model

## Key Tasks
- Merge AST findings with AI labels and confidence
- Rules: SSTI, SQLi, hardcoded secrets, missing error handling
- Multi-agent routing for specialized vulnerability classes
- Natural-language vulnerability descriptions for reports

## Quality & Security
- Integration tests over end-to-end sample PRs
- Clear, explainable scoring; guard against empty/invalid inputs

## Risks/Notes
- Balancing false positives/negatives; tune thresholds with small dataset

## Exit Criteria
- Reproducible risk scores and human-readable findings for test PRs
