---
name: run-acceptance-tests
description: Guide for running acceptance tests for a Terraform provider. Use this when asked to run an acceptance test or to run a test with the prefix `TestAcc`.
license: MPL-2.0
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
---

An acceptance test is a Go test function with the prefix `TestAcc`.

To run a focused acceptance test named `TestAccFeatureHappyPath`:

1. Run `go test -run=TestAccFeatureHappyPath` with `TF_ACC=1`.
   Default to non-verbose output.
1. Some providers require additional environment variables. If the test output
   reports missing variables, suggest secure setup steps.

To diagnose a failing test, apply these options cumulatively (each includes the previous):

1. Re-run with `-count=1` to bypass the Go test cache.
1. Add `-v` for verbose output.
1. Set `TF_LOG=debug` for debug-level logging.
1. Set `TF_ACC_WORKING_DIR_PERSIST=1` to preserve the Terraform workspace for
   inspection.

A passing test may be a false negative. To "flip" a passing test:

1. Edit a TestCheckFunc value in a TestStep of the TestCase.
1. Run the test — expect failure.
1. If it fails, undo the edit and report a successful flip.
   If it passes, keep the edit and report an unsuccessful flip.
