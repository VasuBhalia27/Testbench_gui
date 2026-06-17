# ISTQB Certified Tester Foundation Level (CTFL) v4.0
# Practice Exam — 40 Questions

**Instructions:** Each question has four options (A–D). Select the ONE best answer.  
Time allowed: 60 minutes | Pass mark: 65% (26/40 correct)

---

## CHAPTER 1 — Fundamentals of Testing (Questions 1–7)

---

**Q1.** Which of the following is NOT a typical test objective?

- A) Evaluating work products such as requirements, user stories, and designs
- B) Triggering failures and finding defects
- C) Writing the code to fix identified defects
- D) Reducing the level of risk of inadequate software quality
**Q1 — Answer: C**  
Writing code to fix defects is **debugging**, which is a non-testing activity. Test objectives include finding defects, evaluating quality, reducing risk, verifying requirements, and building confidence — not fixing the code. *(Syllabus §1.1.1)*
---

**Q2.** Which statement BEST describes the relationship between testing and Quality Assurance (QA)?

- A) Testing and QA are the same activity
- B) Testing is a form of Quality Control (QC), while QA is a process-oriented, preventive approach
- C) QA focuses on executing tests and fixing defects found during testing
- D) Testing is a direct subset of QA and cannot exist independently
**Q2 — Answer: B**  
Testing is a form of **Quality Control (QC)** — product-oriented and corrective. **QA** is process-oriented and preventive, focused on implementing and improving processes. They are not the same. *(Syllabus §1.2.2)*
---

**Q3.** A developer makes a mistake in the code logic. When the software is executed, the system produces incorrect output. Which sequence CORRECTLY represents this chain of events?

- A) Failure → Error → Defect
- B) Error → Failure → Defect
- C) Error → Defect → Failure
- D) Defect → Error → Failure
**Q3 — Answer: C**  
The chain is: a human makes an **error** (mistake) → that error produces a **defect** (fault/bug) in the code → when executed, the defect may cause a **failure** (observable wrong behaviour). *(Syllabus §1.2.3)*
---

**Q4.** Which of the seven testing principles states: "If the same tests are repeated many times, they become increasingly ineffective in detecting new defects"?

- A) Absence-of-defects fallacy
- B) Tests wear out
- C) Exhaustive testing is impossible
- D) Defects cluster together
**Q4 — Answer: B**  
Principle 5 is **"Tests wear out"** — repeating the same tests reduces their effectiveness at finding new defects (pesticide paradox). *(Syllabus §1.3)*
---

**Q5.** According to the testing principles, which of the following is TRUE about exhaustive testing?

- A) It is always achievable with sufficient time and budget
- B) It is only possible for simple, low-complexity applications
- C) It is not feasible except in trivial cases
- D) It can be achieved using automated testing tools
**Q5 — Answer: C**  
Principle 2 states exhaustive testing is **not feasible except in trivial cases**. Use risk-based approaches and test techniques instead. *(Syllabus §1.3)*
---

**Q6.** Which statement CORRECTLY describes the responsibilities of the two principal roles in testing?

- A) The test management role is only performed by senior testers with 10+ years of experience
- B) The test management role focuses on test planning, monitoring, and completion; the testing role focuses on test analysis, design, implementation, and execution
- C) The testing role includes test planning, while the test management role only covers test reporting
- D) The test management role only exists in Agile projects, not in sequential models
**Q6 — Answer: B**  
The **test management role** covers test planning, monitoring, control, and completion. The **testing role** covers test analysis, design, implementation, and execution. *(Syllabus §1.4.5)*
---

**Q7.** Which of the following BEST describes the "Whole Team Approach"?

- A) Only dedicated testers are responsible for quality within the team
- B) Any team member with the necessary knowledge and skills can perform any task, and everyone is responsible for quality
- C) Testing is performed entirely by an independent external test team
- D) The test manager delegates all testing tasks to the development team
**Q7 — Answer: B**  
The **whole team approach** (from Extreme Programming) means any team member can perform any task, and quality is everyone's responsibility. *(Syllabus §1.5.2)*
---

## CHAPTER 2 — Testing Throughout the SDLC (Questions 8–13)

---

**Q8.** Which of the following is an example of a "test-first" development approach?

- A) Regression testing
- B) Confirmation testing
- C) Test-Driven Development (TDD)
- D) Exploratory testing
**Q8 — Answer: C**  
**TDD** is a test-first approach: tests are written before the code. ATDD and BDD are also test-first. Regression and confirmation testing are not test-first approaches. *(Syllabus §2.1.3)*
---

**Q9.** The "shift-left" approach in testing PRIMARILY means:

- A) Moving testers from the test team to the development team permanently
- B) Starting testing earlier in the Software Development Lifecycle
- C) Automating all tests so they run faster on the left side of the CI pipeline
- D) Shifting testing responsibility from testers to developers
**Q9 — Answer: B**  
**Shift-left** means performing testing **earlier in the SDLC** — not waiting for code to be complete or components to be integrated. It does not mean neglecting later testing. *(Syllabus §2.1.5)*
---

**Q10.** What is the PRIMARY purpose of confirmation testing?

- A) To verify that the entire system has no remaining defects after a release
- B) To verify that changes made to one component have not caused failures in other parts
- C) To confirm that an original defect has been successfully fixed
- D) To ensure all planned test cases have been executed
**Q10 — Answer: C**  
**Confirmation testing** (re-testing) verifies that a specific, previously found defect has been successfully fixed. **Regression testing** (B) checks for unintended side-effects in other areas. *(Syllabus §2.2.3)*
---

**Q11.** Which of the following CORRECTLY describes Component Integration Testing?

- A) It focuses on testing the overall behavior and end-to-end capabilities of an entire system
- B) It focuses on testing the interfaces and interactions between components
- C) It requires the participation of end users and business representatives
- D) It is performed to validate business requirements using UAT
**Q11 — Answer: B**  
**Component integration testing** focuses on the interfaces and interactions between components. System testing (A) covers overall system behaviour. UAT (D) is acceptance testing. *(Syllabus §2.2.1)*
---

**Q12.** Which statement about regression testing is CORRECT?

- A) Regression testing is only performed after the initial production release of a system
- B) Regression testing confirms that no adverse consequences have been caused by a change
- C) Regression testing replaces the need for confirmation testing when time is limited
- D) Regression testing is not a strong candidate for automation due to frequent changes
**Q12 — Answer: B**  
**Regression testing** confirms that a change (fix, enhancement) has not introduced adverse consequences in the system. It is also a strong candidate for automation. *(Syllabus §2.2.3)*
---

**Q13.** Which of the following can trigger maintenance testing?

- A) Only new feature requests from business stakeholders
- B) Modifications, upgrades/migrations of the operational environment, and retirement of systems
- C) Only corrective (bug-fix) changes to the production system
- D) Only planned enhancements in scheduled release cycles
**Q13 — Answer: B**  
Maintenance testing is triggered by: **modifications** (enhancements, hot fixes), **upgrades/migrations** of the environment, and **retirement** of a system (e.g., data archiving). *(Syllabus §2.3)*
---

## CHAPTER 3 — Static Testing (Questions 14–16)

---

**Q14.** Which of the following is a key difference between static testing and dynamic testing?

- A) Static testing requires the software to be executed to identify defects
- B) Static testing finds defects directly, while dynamic testing causes failures from which defects are then determined through analysis
- C) Static testing can only be applied to source code, not to requirements or designs
- D) Dynamic testing can be applied to non-executable work products such as requirements specifications
**Q14 — Answer: B**  
Static testing finds defects directly (no execution needed). Dynamic testing executes the software, causing failures; defects are then found by analysing those failures. *(Syllabus §3.1.3)*
---

**Q15.** In a formal review (Inspection), who is NOT permitted to act as the review leader or scribe?

- A) A subject matter expert from another team
- B) The author of the work product under review
- C) An external reviewer from outside the organisation
- D) A quality manager who is not part of the development team
**Q15 — Answer: B**  
In an **Inspection** (most formal review type), **the author cannot act as the review leader or scribe** to ensure objectivity. *(Syllabus §3.2.4)*
---

**Q16.** Which review type is LED BY THE AUTHOR and can serve objectives such as educating reviewers, gaining consensus, and generating new ideas?

- A) Inspection
- B) Technical Review
- C) Walkthrough
- D) Informal Review
**Q16 — Answer: C**  
A **Walkthrough** is led by the author and serves objectives such as educating reviewers, gaining consensus, generating new ideas, and detecting anomalies. *(Syllabus §3.2.4)*
---

## CHAPTER 4 — Test Analysis and Design (Questions 17–30)

---

**Q17.** Which of the following BEST describes black-box test techniques?

- A) They are based on an analysis of the test object's internal structure and code
- B) They are based on an analysis of the specified behavior of the test object without reference to its internal structure
- C) They require direct access to the source code to derive test cases
- D) They can only be used at the component (unit) test level
**Q17 — Answer: B**  
**Black-box techniques** (specification-based) test the observable behaviour without knowledge of internal structure. They do not require access to source code. *(Syllabus §4.1)*
---

**Q18.** In Equivalence Partitioning (EP), what is required to achieve 100% coverage?

- A) Test cases must test every possible individual value in each partition
- B) Test cases must exercise each identified partition (including invalid partitions) at least once
- C) Test cases must only cover valid partitions; invalid partitions are out of scope
- D) Test cases must cover only the boundary values at the edge of each partition
**Q18 — Answer: B**  
EP requires test cases to **exercise each partition at least once**, including invalid partitions. Coverage = partitions exercised ÷ total partitions × 100%. *(Syllabus §4.2.1)*
---

**Q19.** A system accepts age values from 1 to 120. Using **2-value** Boundary Value Analysis, which set of test values CORRECTLY covers the lower boundary?

- A) 0, 1
- B) 0, 1, 2
- C) 1, 2
- D) 1, 120
**Q19 — Answer: A**  
For **2-value BVA**, at the lower boundary of 1: the boundary value is **1** and its closest neighbour in the adjacent (invalid) partition is **0**. So: {0, 1}. *(Syllabus §4.2.2)*
---

**Q20.** Which of the following describes the key STRENGTH of decision table testing?

- A) It is the simplest and quickest test technique to apply in all situations
- B) It provides a systematic approach to identify all combinations of conditions, helping to find gaps or contradictions in requirements
- C) It works best when there is a very large number of conditions (more than 10)
- D) It does not require business rules or conditions to be clearly defined upfront
**Q20 — Answer: B**  
Decision table testing's key strength is providing a **systematic approach to identify all combinations of conditions**, ensuring no combination is overlooked and revealing gaps or contradictions in requirements. *(Syllabus §4.2.3)*
---

**Q21.** In state transition testing, which coverage criterion is considered the MOST WIDELY USED?

- A) All states coverage
- B) Valid transitions coverage (also called 0-switch coverage)
- C) All transitions coverage
- D) Decision coverage
**Q21 — Answer: B**  
**Valid transitions coverage (0-switch coverage)** is the most widely used criterion. All states coverage is weaker; all transitions coverage is stronger and required for safety-critical systems. *(Syllabus §4.2.4)*
---

**Q22.** In branch testing (a white-box technique), achieving 100% branch coverage means:

- A) All executable statements in the code have been executed at least once
- B) All unconditional and conditional branches in the code have been exercised by test cases
- C) Every possible path through the code has been executed
- D) All functions and methods in the code have been called at least once
**Q22 — Answer: B**  
100% branch coverage means all **unconditional and conditional branches** have been exercised. A conditional branch covers both the true and false outcomes of an if-then decision. *(Syllabus §4.3.2)*
---

**Q23.** Which statement about the relationship between branch coverage and statement coverage is CORRECT?

- A) Achieving 100% statement coverage guarantees 100% branch coverage
- B) Achieving 100% branch coverage guarantees 100% statement coverage (but not vice versa)
- C) Branch coverage and statement coverage are completely independent measures
- D) Neither branch coverage nor statement coverage subsumes the other
**Q23 — Answer: B**  
**Branch coverage subsumes statement coverage**: any set of tests achieving 100% branch coverage also achieves 100% statement coverage. The reverse is NOT true. *(Syllabus §4.3.2)*
---

**Q24.** Which of the following BEST describes exploratory testing?

- A) Tests are designed in advance strictly based on the system requirements specification
- B) Tests are simultaneously designed, executed, and evaluated while the tester learns about the test object
- C) Tests are fully automated and run without any human involvement during execution
- D) Tests follow a predefined, scripted procedure that cannot be changed during execution
**Q24 — Answer: B**  
**Exploratory testing** is simultaneous design, execution, and evaluation — the tester learns about the system as they test it. Often conducted in time-boxed sessions with a test charter. *(Syllabus §4.4.2)*
---

**Q25.** Error guessing is an experience-based test technique. Which of the following is a METHODICAL approach to implementing error guessing?

- A) Equivalence Partitioning
- B) Boundary Value Analysis
- C) Fault Attacks
- D) Checklist-based testing
**Q25 — Answer: C**  
**Fault attacks** are the methodical implementation of error guessing — the tester creates/acquires a list of possible errors and designs tests to expose them. *(Syllabus §4.4.1)*
---

**Q26.** What does the acronym **INVEST** represent in the context of good user stories?

- A) Independent, Negotiable, Valuable, Estimable, Small, Testable
- B) Integrated, Necessary, Verified, Executable, Structured, Traceable
- C) Independent, Normalized, Validated, Effective, Specific, Tested
- D) Iterative, Negotiable, Valuable, Efficient, Simple, Testable
**Q26 — Answer: A**  
**INVEST** = **I**ndependent, **N**egotiable, **V**aluable, **E**stimable, **S**mall, **T**estable. These are the criteria for a good user story. *(Syllabus §4.5.1)*
---

**Q27.** What is the PRIMARY characteristic of Acceptance Test-Driven Development (ATDD)?

- A) All acceptance tests must be automated before development begins
- B) Test cases are created from acceptance criteria PRIOR to implementing the user story
- C) The system is tested only after full deployment to the production environment
- D) It replaces all forms of user acceptance testing in Agile projects

---

**Q28.** Which of the following is the CORRECT format for the most common user story?

- A) "When [event occurs], I need [feature] so that [business benefit]"
- B) "As a [role], I want [goal to be accomplished], so that I can [resulting business value for the role]"
- C) "Given [precondition], When [action is taken], Then [expected outcome]"
- D) "For [user type], the system shall [perform action] in order to [achieve goal]"

---

**Q29.** In **3-value** Boundary Value Analysis (BVA), for each boundary value, how many coverage items must be exercised?

- A) One — the boundary value itself
- B) Two — the boundary value and one neighbor in the adjacent partition
- C) Three — the boundary value and both its neighbors (one on each side)
- D) Four — two values on each side of the boundary

---

**Q30.** A fundamental weakness of white-box testing compared to black-box testing is:

- A) White-box testing cannot achieve measurable code coverage
- B) If the software does not implement one or more requirements, white-box testing may not detect defects of omission
- C) White-box tests become invalid whenever the requirements change
- D) White-box techniques cannot be used alongside static testing

---

## CHAPTER 5 — Managing the Test Activities (Questions 31–39)

---

**Q31.** According to the test pyramid model, which layer should typically contain the GREATEST NUMBER of tests?

- A) End-to-end tests (top layer) — complex, high-level tests
- B) Service/Integration tests (middle layer)
- C) Unit/Component tests (bottom layer) — small, isolated, fast tests
- D) The number of tests should be equal across all layers

---

**Q32.** Risk level is determined by which TWO factors?

- A) Severity of the defect and the number of defects found
- B) Risk likelihood and risk impact
- C) Project schedule pressure and available budget
- D) Test coverage achieved and the number of test cases executed

---

**Q33.** Which of the following is an example of a **PROJECT** risk (not a product risk)?

- A) Security vulnerabilities in the software product
- B) Poor user experience due to a confusing interface
- C) Shortage of staff with the right testing skills
- D) Incorrect calculations in the application's business logic

---

**Q34.** In the Testing Quadrants model, which quadrant contains **smoke tests** and **non-functional tests** (excluding usability)?

- A) Q1 — Technology facing, support the team
- B) Q2 — Business facing, support the team
- C) Q3 — Business facing, critique the product
- D) Q4 — Technology facing, critique the product

---

**Q35.** A team uses three-point estimation. The most optimistic estimate is 6 person-hours, the most likely is 9, and the most pessimistic is 18. What is the final estimate (E)?

- A) 9 person-hours
- B) 10 person-hours
- C) 11 person-hours
- D) 12 person-hours

*(Formula: E = (a + 4m + b) / 6)*

---

**Q36.** In Agile software development, what term is commonly used for **exit criteria** (what must be achieved before declaring an activity complete)?

- A) Definition of Ready
- B) Acceptance Criteria
- C) Definition of Done
- D) Test Completion Report

---

**Q37.** Which of the following is a **defect metric** used in test monitoring?

- A) Task completion percentage
- B) Resource usage (person-hours consumed)
- C) Defect density
- D) Test environment preparation progress

---

**Q38.** What is the PRIMARY purpose of Configuration Management (CM) in testing?

- A) To automate test execution and remove the need for manual testing
- B) To identify, control, and track work products such as test plans, test cases, test scripts, and test results as configuration items
- C) To manage the overall project schedule, budget, and resource allocation
- D) To report defects directly to the development team for immediate fixing

---

**Q39.** A tester has just found a failure during test execution. Which of the following items should be included in the defect report?

- A) The developer's personal coding preferences and style guide violations
- B) Steps to reproduce the defect, expected results, actual results, and severity
- C) Future feature development plans and the product roadmap
- D) The team's overall project risk assessment and mitigation strategy

---

## CHAPTER 6 — Test Tools (Question 40)

---

**Q40.** Which of the following is a potential **RISK** of test automation (not a benefit)?

- A) Faster test execution leading to shorter feedback cycles
- B) More objective assessment of coverage
- C) Test automation requires additional resources and may be difficult to establish and maintain
- D) Prevention of simple human errors through greater consistency

---

---

# ANSWER KEY

| Q | Answer | Q | Answer |
|---|--------|---|--------|
| 1 | C | 21 | B |
| 2 | B | 22 | B |
| 3 | C | 23 | B |
| 4 | B | 24 | B |
| 5 | C | 25 | C |
| 6 | B | 26 | A |
| 7 | B | 27 | B |
| 8 | C | 28 | B |
| 9 | B | 29 | C |
| 10 | C | 30 | B |
| 11 | B | 31 | C |
| 12 | B | 32 | B |
| 13 | B | 33 | C |
| 14 | B | 34 | D |
| 15 | B | 35 | B |
| 16 | C | 36 | C |
| 17 | B | 37 | C |
| 18 | B | 38 | B |
| 19 | A | 39 | B |
| 20 | B | 40 | C |

---

# DETAILED EXPLANATIONS

**Q1 — Answer: C**  
Writing code to fix defects is **debugging**, which is a non-testing activity. Test objectives include finding defects, evaluating quality, reducing risk, verifying requirements, and building confidence — not fixing the code. *(Syllabus §1.1.1)*

**Q2 — Answer: B**  
Testing is a form of **Quality Control (QC)** — product-oriented and corrective. **QA** is process-oriented and preventive, focused on implementing and improving processes. They are not the same. *(Syllabus §1.2.2)*

**Q3 — Answer: C**  
The chain is: a human makes an **error** (mistake) → that error produces a **defect** (fault/bug) in the code → when executed, the defect may cause a **failure** (observable wrong behaviour). *(Syllabus §1.2.3)*

**Q4 — Answer: B**  
Principle 5 is **"Tests wear out"** — repeating the same tests reduces their effectiveness at finding new defects (pesticide paradox). *(Syllabus §1.3)*

**Q5 — Answer: C**  
Principle 2 states exhaustive testing is **not feasible except in trivial cases**. Use risk-based approaches and test techniques instead. *(Syllabus §1.3)*

**Q6 — Answer: B**  
The **test management role** covers test planning, monitoring, control, and completion. The **testing role** covers test analysis, design, implementation, and execution. *(Syllabus §1.4.5)*

**Q7 — Answer: B**  
The **whole team approach** (from Extreme Programming) means any team member can perform any task, and quality is everyone's responsibility. *(Syllabus §1.5.2)*

**Q8 — Answer: C**  
**TDD** is a test-first approach: tests are written before the code. ATDD and BDD are also test-first. Regression and confirmation testing are not test-first approaches. *(Syllabus §2.1.3)*

**Q9 — Answer: B**  
**Shift-left** means performing testing **earlier in the SDLC** — not waiting for code to be complete or components to be integrated. It does not mean neglecting later testing. *(Syllabus §2.1.5)*

**Q10 — Answer: C**  
**Confirmation testing** (re-testing) verifies that a specific, previously found defect has been successfully fixed. **Regression testing** (B) checks for unintended side-effects in other areas. *(Syllabus §2.2.3)*

**Q11 — Answer: B**  
**Component integration testing** focuses on the interfaces and interactions between components. System testing (A) covers overall system behaviour. UAT (D) is acceptance testing. *(Syllabus §2.2.1)*

**Q12 — Answer: B**  
**Regression testing** confirms that a change (fix, enhancement) has not introduced adverse consequences in the system. It is also a strong candidate for automation. *(Syllabus §2.2.3)*

**Q13 — Answer: B**  
Maintenance testing is triggered by: **modifications** (enhancements, hot fixes), **upgrades/migrations** of the environment, and **retirement** of a system (e.g., data archiving). *(Syllabus §2.3)*

**Q14 — Answer: B**  
Static testing finds defects directly (no execution needed). Dynamic testing executes the software, causing failures; defects are then found by analysing those failures. *(Syllabus §3.1.3)*

**Q15 — Answer: B**  
In an **Inspection** (most formal review type), **the author cannot act as the review leader or scribe** to ensure objectivity. *(Syllabus §3.2.4)*

**Q16 — Answer: C**  
A **Walkthrough** is led by the author and serves objectives such as educating reviewers, gaining consensus, generating new ideas, and detecting anomalies. *(Syllabus §3.2.4)*

**Q17 — Answer: B**  
**Black-box techniques** (specification-based) test the observable behaviour without knowledge of internal structure. They do not require access to source code. *(Syllabus §4.1)*

**Q18 — Answer: B**  
EP requires test cases to **exercise each partition at least once**, including invalid partitions. Coverage = partitions exercised ÷ total partitions × 100%. *(Syllabus §4.2.1)*

**Q19 — Answer: A**  
For **2-value BVA**, at the lower boundary of 1: the boundary value is **1** and its closest neighbour in the adjacent (invalid) partition is **0**. So: {0, 1}. *(Syllabus §4.2.2)*

**Q20 — Answer: B**  
Decision table testing's key strength is providing a **systematic approach to identify all combinations of conditions**, ensuring no combination is overlooked and revealing gaps or contradictions in requirements. *(Syllabus §4.2.3)*

**Q21 — Answer: B**  
**Valid transitions coverage (0-switch coverage)** is the most widely used criterion. All states coverage is weaker; all transitions coverage is stronger and required for safety-critical systems. *(Syllabus §4.2.4)*

**Q22 — Answer: B**  
100% branch coverage means all **unconditional and conditional branches** have been exercised. A conditional branch covers both the true and false outcomes of an if-then decision. *(Syllabus §4.3.2)*

**Q23 — Answer: B**  
**Branch coverage subsumes statement coverage**: any set of tests achieving 100% branch coverage also achieves 100% statement coverage. The reverse is NOT true. *(Syllabus §4.3.2)*

**Q24 — Answer: B**  
**Exploratory testing** is simultaneous design, execution, and evaluation — the tester learns about the system as they test it. Often conducted in time-boxed sessions with a test charter. *(Syllabus §4.4.2)*

**Q25 — Answer: C**  
**Fault attacks** are the methodical implementation of error guessing — the tester creates/acquires a list of possible errors and designs tests to expose them. *(Syllabus §4.4.1)*

**Q26 — Answer: A**  
**INVEST** = **I**ndependent, **N**egotiable, **V**aluable, **E**stimable, **S**mall, **T**estable. These are the criteria for a good user story. *(Syllabus §4.5.1)*

**Q27 — Answer: B**  
**ATDD** is a test-first approach where test cases are created from acceptance criteria **before** the user story is implemented. It involves customers, developers, and testers. *(Syllabus §4.5.3)*

**Q28 — Answer: B**  
The standard user story format is: **"As a [role], I want [goal], so that I can [business value]"**, followed by acceptance criteria. *(Syllabus §4.5.1)*

**Q29 — Answer: C**  
In **3-value BVA**, for each boundary value there are **three coverage items**: the boundary value itself and both its neighbours (one on each side). *(Syllabus §4.2.2)*

**Q30 — Answer: B**  
White-box testing derives tests from the implementation. If a requirement is simply **not implemented**, there is no code path to test — so **defects of omission** may be missed. *(Syllabus §4.3.3)*

**Q31 — Answer: C**  
The **test pyramid** model has the most tests at the **bottom layer** (unit/component tests — small, fast, isolated). Higher layers have fewer but more complex tests. *(Syllabus §5.1.6)*

**Q32 — Answer: B**  
**Risk level = Risk likelihood × Risk impact**. A higher risk level means the risk is more important to treat and mitigate. *(Syllabus §5.2.1)*

**Q33 — Answer: C**  
**Shortage of staff** is a people issue and a **project risk**. Security vulnerabilities (A), poor UX (B), and incorrect calculations (D) are all **product risks** related to quality characteristics. *(Syllabus §5.2.2)*

**Q34 — Answer: D**  
**Q4 (technology facing, critique the product)** contains smoke tests and non-functional tests (excluding usability). Q3 contains usability testing. *(Syllabus §5.1.7)*

**Q35 — Answer: B**  
Using E = (a + 4m + b) / 6:  
E = (6 + 4×9 + 18) / 6 = (6 + 36 + 18) / 6 = 60 / 6 = **10 person-hours** *(Syllabus §5.1.4)*

**Q36 — Answer: C**  
In Agile, exit criteria are called **Definition of Done** (DoD). Entry criteria (what must be met to START) are called **Definition of Ready** (DoR). *(Syllabus §5.1.3)*

**Q37 — Answer: C**  
**Defect density** is a defect metric (defects per size unit). Task completion and resource usage are project progress metrics; environment preparation is a test progress metric. *(Syllabus §5.3.1)*

**Q38 — Answer: B**  
Configuration Management in testing **identifies, controls, and tracks** all work products (test plans, test cases, test scripts, test results, etc.) as versioned configuration items to maintain traceability. *(Syllabus §5.4)*

**Q39 — Answer: B**  
A defect report must include: unique identifier, title, steps to reproduce, expected results, **actual results**, severity, priority, status, and context. *(Syllabus §5.5)*

**Q40 — Answer: C**  
A key **risk** of test automation is that it **requires additional resources and may be difficult to establish and maintain** (tools, skills, infrastructure, maintenance effort). Options A, B, and D are benefits. *(Syllabus §6.2)*

---

## Score Interpretation

| Score | Result | Notes |
|-------|--------|-------|
| 34–40 (85–100%) | Excellent | Well prepared — review any incorrect questions |
| 26–33 (65–82%) | Pass | Meets ISTQB pass threshold — review weak areas |
| 20–25 (50–62%) | Near pass | Additional study needed in weak chapters |
| < 20 (< 50%) | Fail | Significant study needed across all chapters |

**ISTQB exam tip:** The real exam is 60 minutes, 40 questions, K1/K2/K3 cognitive levels. Focus extra study time on Chapter 4 (Test Techniques — largest weight) and Chapter 5 (Test Management).
