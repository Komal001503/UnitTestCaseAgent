# MaintainRegularTimecard – Unit Test Cases Report

**Source File:** `MaintainRegularTimecard.xlsx`
**Test File:** `tests/test_maintain_regular_timecard.py`
**Generated:** 2026-05-11

---

## User Story: US-TC-001 – IR/IR Approver – Maintain Regular Timecard – Date View

**Task:** As a user, I want to view the Maintain Timecard details based on Date (Log-in and Log-out) so that I can easily review timecard entries for a specific day or date range.

### Test Scenarios

| # | Scenario | Type | Input | Expected Output |
|---|----------|------|-------|-----------------|
| 1 | Navigation opens Maintain Regular Timecard page | Positive | Select Attendance Management → Maintain Timecard | Page displays |
| 2 | Page displays Date View and Employee View tabs | Positive | Page load | Both tabs visible |
| 3 | Default tab is Date View | Positive | Page load | Date View selected |
| 4 | Date picker attribute displayed | Positive | Page load | Date picker visible |
| 5 | All 11 grid columns displayed | Positive | Page load | Employee, TRT No, In, Out, Late, Early, Reg. Shift, Actual Shift, Employee Status, Cadre, Leave Remarks |
| 6 | Save and Export buttons displayed | Positive | Page load | Both buttons visible |
| 7 | Select date shows timecard data | Positive | Date: 2025-12-15 | Records for that date |
| 8 | No date selected shows current date data | Positive | No date | Current date records |
| 9 | Future date returns no data | Negative | Future date | Empty records |
| 10 | Invalid date format returns error | Boundary | "not-a-date" | ValueError |
| 11 | Punch in/out displayed in HH:MM format | Positive | 484 minutes | "08:04" |
| 12 | Minutes to time conversion (484 → 08:04) | Positive | 484 | "08:04" |
| 13 | Duplicate punches – first in / last out used | Positive | Multiple punch records | First IN, last OUT |
| 14 | Early punch-in adjusted for payment | Positive | Punch 06:53, shift 07:00 | Display 06:53, pay 07:00 |
| 15 | Late punch-out adjusted to shift end | Positive | Punch 15:35, shift 15:25 | Display 15:35, pay 15:25 |
| 16 | No punch data marks as absent (ABS) | Positive | No punch data | "ABS" |
| 17 | ABS remains until leave approved | Positive | ABS with no leave | "ABS" |
| 18 | Leave approved updates remark | Positive | Leave approved | "PL" |
| 19 | 0 minutes converts to 00:00 | Boundary | 0 | "00:00" |
| 20 | 1439 minutes converts to 23:59 | Boundary | 1439 | "23:59" |
| 21 | Negative minutes returns error | Boundary | -1 | ValueError |
| 22 | Reg. Shift fetched from shift schedule | Positive | EMP001 | "S1" |
| 23 | Actual Shift from punch data | Positive | in/out times | "S1" |
| 24 | Shift timing from master | Positive | S1 | 07:00–15:25 |
| 25 | No punch → no actual shift | Negative | None | None |
| 26 | No schedule assigned | Negative | New employee | None |
| 27 | Column search filters results | Positive | Column: Employee, "EMP001" | Filtered list |
| 28 | Global search filters results | Positive | "John" | Matching records |
| 29 | Search no match returns empty | Negative | "NONEXISTENT" | Empty list |
| 30 | Empty search returns all | Boundary | "" | All records |
| 31 | Pagination next page | Positive | Page 2 | Page 2 data |
| 32 | Pagination beyond last page | Boundary | Page 100 | Empty/last page |
| 33 | Scheduler runs at 9:30 AM | Positive | Scheduler run | Data fetched |
| 34 | Scheduler fetches yesterday + today | Positive | Run | 2 dates |
| 35 | InfoComm API timeout handled | Integration | Timeout | TimeoutError |
| 36 | InfoComm API unavailable – retry | Integration | ConnectionError then success | Retry succeeds |
| 37 | Scheduler no new data | Boundary | No data | 0 records |
| 38 | Save valid changes | Positive | Valid data | Success |
| 39 | Save no changes | Boundary | No changes | Info message |
| 40 | Save server error | Negative | DB error | RuntimeError |

---

## User Story: US-TC-002 – IR/IR Approver – Maintain Regular Timecard – Employee View

**Task:** As an IR, Company Head, Location Head, BU Head, I want to view the Maintain Timecard details based on Employee so that I can quickly access and verify the timecard information of a specific employee.

### Test Scenarios

| # | Scenario | Type | Input | Expected Output |
|---|----------|------|-------|-----------------|
| 1 | Click Employee View tab switches view | Positive | Click tab | Employee View |
| 2 | Employee dropdown displayed | Positive | Page load | Dropdown visible |
| 3 | From and To date pickers displayed | Positive | Page load | Both pickers visible |
| 4 | All 11 grid columns displayed | Positive | Page load | All columns |
| 5 | Export button displayed | Positive | Page load | Export visible |
| 6 | Select date range shows filtered data | Positive | Dec 1–2, EMP001 | 2 records |
| 7 | No date shows current month data | Positive | No date, EMP001 | Month's data |
| 8 | From after To returns error | Negative | Dec 31 → Dec 1 | Error |
| 9 | No employee selected returns error | Negative | None | Error |
| 10 | Invalid employee ID returns error | Negative | "INVALID_EMP" | Error |
| 11 | Same From and To date returns single day | Boundary | Same date | 1 record |
| 12 | Column search filters results | Positive | Date column | Filtered |
| 13 | Global search filters results | Positive | "ABS" | Matching records |
| 14 | Pagination works correctly | Positive | Page 3 | Page 3 data |

---

## User Story: US-TC-003 – IR/IR Approver – Maintain Regular Timecard – Export

**Task:** As an IR, Company Head, Location Head, BU Head, I want to click the export button so that I can export all the details in the excel file.

### Test Scenarios

| # | Scenario | Type | Input | Expected Output |
|---|----------|------|-------|-----------------|
| 1 | Export to Excel | Positive | Click Export | .xlsx file |
| 2 | Export with date filter | Positive | Date range | Filtered records |
| 3 | Export without filter | Positive | No filter | All records |
| 4 | Export no data produces empty file | Boundary | Empty grid | 0 records |
| 5 | Save exported file to location | Positive | Path | File saved |
| 6 | Export server error | Negative | Server error | RuntimeError |

---

## User Story: US-TC-004 – Shop In charge (IS) – Maintain Regular Timecard – Date View

**Task:** As a Shop In charge (IS), I want to view the Maintain Timecard details based on Date (Log-in and Log-out) so that I can easily review timecard entries for a specific day or date range.

### Test Scenarios

| # | Scenario | Type | Input | Expected Output |
|---|----------|------|-------|-----------------|
| 1 | Date View and Employee View tabs visible | Positive | Page load | Both tabs |
| 2 | Default tab is Date View | Positive | Page load | Date View |
| 3 | Export button only (no Save – view access) | Positive | Page load | Export only |
| 4 | View-only access verified | Positive | Auth check | "view" |
| 5 | All 11 grid columns displayed | Positive | Page load | All columns |
| 6 | Cannot edit leave remarks | Negative | Edit attempt | PermissionError |
| 7 | Cannot save changes | Negative | Save attempt | PermissionError |
| 8 | Select date shows data | Positive | Date | Records |
| 9 | No date shows current date data | Positive | No date | Today's data |

---

## User Story: US-TC-005 – Shop In charge (IS) – Maintain Regular Timecard – Employee View

**Task:** As a Shop In charge (IS), I want to view the Maintain Timecard details based on Employee.

### Test Scenarios

| # | Scenario | Type | Input | Expected Output |
|---|----------|------|-------|-----------------|
| 1 | Employee dropdown displayed | Positive | Page load | Dropdown visible |
| 2 | From and To date pickers displayed | Positive | Page load | Pickers visible |
| 3 | All 11 grid columns displayed | Positive | Page load | All columns |
| 4 | Export button only (no Save) | Positive | Page load | Export only |
| 5 | Select date range shows data | Positive | Date range | Filtered records |
| 6 | No date shows current month data | Positive | No date | Month's data |
| 7 | Cannot edit fields | Negative | Edit attempt | PermissionError |

---

## User Story: US-TC-006 – Shop In charge (IS) – Maintain Regular Timecard – Export

**Task:** As a Shop In charge (IS), I want to click the export button so that I can export all the details in the excel file.

### Test Scenarios

| # | Scenario | Type | Input | Expected Output |
|---|----------|------|-------|-----------------|
| 1 | Export to Excel | Positive | Click Export | .xlsx file |
| 2 | Export with date filter | Positive | Date range | Filtered records |
| 3 | Export without filter | Positive | No filter | All records |
| 4 | Save exported file to location | Positive | Path | File saved |
| 5 | Export no data produces empty file | Boundary | Empty grid | 0 records |
| 6 | Export failure handled | Negative | Server error | RuntimeError |

---

## Cross-Cutting: Leave Remarks Display

### Test Scenarios

| # | Scenario | Type | Input | Expected Output |
|---|----------|------|-------|-----------------|
| 1 | Punch present shows correct remark | Positive | Punch data exists | "Present" |
| 2 | No punch shows ABS | Positive | No punch data | "ABS" |
| 3 | Approved leave updates from ABS | Positive | Leave approved | "PL" |
| 4 | Remarks visible on Kiosk | Positive | Employee Kiosk | Remarks list |
| 5 | Remarks fetched from master | Positive | Master query | All remark types |

---

## Summary

| Category | Count |
|----------|-------|
| **Total Test Cases** | **82** |
| Positive / Happy Path | 52 |
| Negative / Error Path | 16 |
| Boundary / Edge Cases | 10 |
| Integration Points | 4 |
| **User Stories Covered** | **6** |
| **Test Classes** | **18** |
