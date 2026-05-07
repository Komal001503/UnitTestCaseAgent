# L&T WFM Onboarding Module - User Stories

**Application Name:** L&T_WFM_Onboarding
**Document Name:** User Stories
**Date:** 2025-12-05

## Module Summary

| Module | User Stories Count |
|---|---|
| Quick Onboarding | 3 |
| Rehire | 3 |
| Onboarding Overview | 5 |
| Bulk Upload | 4 |
| Workforce Information | 11 |
| IR Approver | 5 |
| **Total** | **31** |

---

## US-001: IR Login (Quick Onboarding)

- **Story ID:** US-001
- **Title:** IR Login to Application
- **Module:** Login
- **Sub Module:** Login
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an IR, I want to login into the application, so that I can view all the relevant details in the application.
- **Acceptance Criteria:**
  1. Login screen will be displayed with the following elements:
     - User name textbox
     - Password textbox
     - Log In button
     - Login with SSO button
  2. Entering User name and password and clicking 'Log In' button, the user will be able to login into the WFM application.

---

## US-002: Open Quick Onboarding from Menu

- **Story ID:** US-002
- **Title:** Open Quick Onboarding from Side Navigation Menu
- **Module:** Onboarding
- **Sub Module:** Quick Onboarding
- **User Role:** Industrial Relation (IR)
- **Feature:** Open quick onboarding from menu
- **Priority:** High
- **Description:** As an Industrial Relation, I want to click on the Quick Onboarding sub menu, so that I can fill the attributes to open the Quick Onboarding page.
- **Acceptance Criteria:**
  1. Upon logging in, the user will be navigated to the IR dashboard. From the dashboard, the user can click on the hamburger menu to open the side navigation.
  2. In the side navigation, user needs to view the 'Quick Onboarding', 'Rehiring', 'Onboarding Overview', 'Bulk Upload' sub menus from the 'Onboarding' menu.
  3. From the side navigation, user selects 'Quick Onboarding' sub menu from the 'Onboarding' menu.
  4. Quick Onboarding page will be displayed with the following fields:
     - Employee Type - dropdown with values: Apprentice, Advanced Trainee, AT Staff, Temporary Workmen, Permanent Workmen
  5. Buttons displayed:
     - Continue
     - Cancel
  6. After filling values, clicking the Continue button navigates to the Quick Onboarding page.
  7. Clicking Cancel navigates to the previous page.

---

## US-003: Quick Onboarding Page - Initiate Request

- **Story ID:** US-003
- **Title:** View and Submit Quick Onboarding Page
- **Module:** Onboarding
- **Sub Module:** Quick Onboarding
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to view the Quick Onboarding Page, so that I can initiate the Quick Onboarding Request for the employee.
- **Acceptance Criteria:**
  1. User needs to fill all Mandatory Fields (*).
  2. **Name Information:**
     - Title* (dropdown, fetched from title master)
     - Name as per Aadhaar / Full Name*
     - First Name*
     - Middle Name (optional)
     - Last Name*
  3. **Biographical Information:**
     - Date Of Birth* (Date picker)
     - Place Of Birth* (text field)
  4. **Contact Information:**
     - Email ID (text field)
     - Mobile Number (text field)
  5. **Personal Information:**
     - Gender* (dropdown: Male, Female)
     - Marital Status* (Radio Button: Single, Married)
     - Marital Status Since* (Date picker)
     - No of children (numeric field)
     - Nationality* (dropdown, fetched from Nationality Master)
     - Domicile (State)* (dropdown, fetched from State Master)
     - Religion* (dropdown, fetched from Religion Master)
     - Caste Code* (dropdown)
     - Blood Group* (dropdown, fetched from Blood Group Master)
     - Father Name* (text field)
  6. **National ID Information:**
     - Document Type* (dropdown, fetched from Document dropdown)
     - Document ID* (text field)
     - Is Primary* (Radio Button: Yes, No)
     - Upload document button
     - Add icon (to add more documents)
     - Remove icon (to remove documents)
  7. **Organization Information:**
     - Dept Code* (fetched from Dept code master)
  8. **Job Information:**
     - Unit Name* (dropdown, from Location Master)
     - Function Code (dropdown, from Function Code Master)
     - With Company? (Radio Button: Yes, No)
     - Designation
     - Category Code* (dropdown, from Master)
     - Grade/Training Year (numeric field)
     - Previous PS Number (text field)
     - Shift Code* (dropdown, from Shift Code Master)
     - Direct Workman?* (Radio Button: Yes, No)
     - Employee Type* (dropdown, from Employee Type Master)
     - Ex-Trainee? (dropdown: Yes, No)
     - Area* (dropdown, from Department Code Master)
  9. **Compensation Information:**
     - Cadre at Joining* (dropdown, from Cadre Master)
     - Current Cadre* (dropdown, from Cadre Master)
     - Joining Basic* (text field)
     - Confirmation Basic (text field)
     - Current Basic* (text field)
  10. **Right Side Pane:**
      - Upload Image
  11. After filling values, clicking the Submit button sends the request to the IR Approver for approval and displays: 'Your quick onboarding page has been successfully submitted'.
  12. Clicking 'Okay' button in the popup redirects to the Workforce Information / Onboarding Overview page.
  13. **Validation - Mandatory Fields:** If mandatory fields are not filled and the Submit button is clicked, a pop-up notification displays: 'Mandatory fields missing, please fill all the details to proceed further'.
  14. Clicking Cancel navigates to the previous page.
  15. **Validation - Submit Email:** Clicking submit triggers an email to all IR users.
  16. **Validation - Name:** First Name and Last Name are mandatory. Middle Name is optional.
  17. **Validation - DOB:** Date picker and manual entry in DD-MM-YYYY format; age is auto-calculated and displayed in the age field.
  18. **Validation - Document ID:** Based on the document type, the document ID field will be mandatory (e.g., if Aadhaar, then Aadhaar number is mandatory). The list of mandatory fields is fetched from the document master.
  19. **Validation - Aadhaar Masking:** Masking of first 8 digits; only the last 4 digits are displayed.
  20. **Validation - Aadhaar Encryption:** Aadhaar should be encrypted and data securely stored in the background.
  21. **Validation - Document Upload:** Document upload and preview option provided.
  22. **Validation - Marital Status:** If Single is selected, hide "Marital status since" and "No. of children" fields. If Married is selected, display them.
  23. **Validation - No. of Children:** Expand and collapse field based on No. of children selected. Max No. of children = 5.
  24. **Validation - Document Attachment:** File upload with 5MB size limit (configurable, based on Mendix standard).
  25. **Validation - Multiple Documents:** User can upload multiple documents with document name and upload icon for each.
  26. **Validation - Department Code:** Alphanumerical field; auto-fetches and displays corresponding department name from master data.
  27. **Validation - Supervisor Assignment:** Based on department code, auto-fill: Immediate Supervisor (IS), Next Supervisor (NS), Department Head (DH), Contact Supervisor (CS) (if exists), Extension Number, Working Area.
  28. **Validation - Manual IS Selection:** User can manually select a different Immediate Supervisor with editable text field. Based on IS selection, auto-populate NS and DH.
  29. **Validation - Marital Status Fields:** Displayed only when Marital status is "Married"; hidden otherwise.
  30. **Validation - Aadhaar Verification:** Aadhaar verification is NOT required for onboarding and rehiring.

---

## US-004: IR Login (Rehire)

- **Story ID:** US-004
- **Title:** IR Login to Application (Rehire Module)
- **Module:** Login
- **Sub Module:** Login
- **User Role:** IR
- **Feature:** Login to the application
- **Priority:** High
- **Description:** As a user, I want to login into the application, so that I can view all the relevant details in the application.
- **Acceptance Criteria:**
  1. Login screen displays:
     - User name textbox
     - Password textbox
     - Log In button
     - Login with SSO button
     - Forgot Password hyperlink
  2. Entering User name and password and clicking 'Log In' button, the user will be able to login into the WFM application.

---

## US-005: Open Rehiring from Menu

- **Story ID:** US-005
- **Title:** Open Rehiring Sub Menu from Side Navigation
- **Module:** Onboarding
- **Sub Module:** Rehire
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to click on the Rehiring sub menu so that I can fill the attributes to open the Rehiring Onboarding page.
- **Acceptance Criteria:**
  1. Upon logging in, the user navigates to the IR dashboard, clicks the hamburger menu to open side navigation.
  2. From the side navigation, user selects the 'Rehiring' sub menu from the 'Onboarding' menu.
  3. 'Rehiring' page displays with the following fields:
     - Employee Type (dropdown): Apprentice, Advanced Trainee, AT Staff, Temporary Workmen, Permanent Workmen
     - Old PS No (text field & dropdown)
     - Aadhar Number (text field)
  4. Buttons:
     - Continue
     - Cancel
  5. After filling values, clicking Continue navigates to the Rehiring page.
  6. Clicking Cancel navigates to the previous page.
  7. **Validation - Old PS No:** When user types the old PS no, the name of the employee linked to that PS no should be displayed in the Old PS No text field.
  8. **Validation - Old PS No Dropdown:** When user selects the "Old PS No" dropdown, the system displays the list of all inactive employees.

---

## US-006: Rehire Page - Create Rehire Request

- **Story ID:** US-006
- **Title:** View and Submit Rehire Page
- **Module:** Onboarding
- **Sub Module:** Rehire
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to view the Rehire Page so that I can create the Rehire Request.
- **Acceptance Criteria:**
  1. Based on Old PS No, historical data from previous onboarding is auto-populated from workforce information.
  2. User needs to provide the required editable fields:
     - Cadre (dropdown, from Cadre Master)
     - Department (dropdown, from Department Master)
     - Rejoining date (date picker)
     - Basic (number)
  3. All data is fetched from workforce information based on Old PS No.
  4. All details are displayed with an edit icon per section. Clicking the edit icon makes only the fields in that section editable; other sections remain non-editable.
  5. After filling required values and mandatory fields, clicking Submit sends the request to IR Approver for approval and displays: 'Rehiring process has been successfully submitted'.
  6. Clicking 'Okay' in the popup redirects to the "Onboarding Review Overview" page.
  7. Clicking Cancel navigates to the previous page.

---

## US-007: IR Login (Onboarding Overview)

- **Story ID:** US-007
- **Title:** IR Login to Application (Onboarding Overview)
- **Module:** Login
- **Sub Module:** Login
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to login into the application so that I can access my Dashboard.
- **Acceptance Criteria:**
  1. Login screen displays:
     - User name textbox
     - Password textbox
     - Log In button
     - Login with SSO button
     - Forgot Password hyperlink
  2. Entering User name and password and clicking 'Log In' button, the user will be able to login into the WFM application.

---

## US-008: Onboarding Overview - All Tab

- **Story ID:** US-008
- **Title:** View All Requests in Onboarding Overview
- **Module:** Onboarding
- **Sub Module:** Onboarding Overview
- **User Role:** Industrial Relation (IR)
- **Feature:** All Tab
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view all the requests which are created so that I can view all the details of the respective request.
- **Acceptance Criteria:**
  1. Upon login, the user navigates to the IR dashboard and opens the side navigation.
  2. User selects 'Onboarding Overview' sub menu from the 'Onboarding' menu.
  3. 'Onboarding Overview' page displays with tabs: All, Quick Onboarding, Rehiring, Full Onboarding.
  4. User clicks on the 'All' tab.
  5. Data grid columns:
     - PS No
     - Name
     - Employment Type
     - Dept Code
     - Immediate Supervisor
     - Date of Joining
     - Submitted On
     - Approved On
     - Onboarding Type (Quick Onboarding, Rehiring, Full Onboarding)
     - Status
  6. Clicking PS No/Name (hyperlink) directs the user to the Workforce Information details page.
  7. **Search Bar:** User can search requests using the search bar.
  8. **Page Navigation:** User can navigate to other pages using page navigation.
  9. **Validation - PS No Display by Status:**
     - Pending: PS No is NOT displayed.
     - Approved: PS No IS displayed.
     - Completed: PS No IS displayed.
     - Returned: PS No is NOT displayed.
  10. **Validation - Submitted On (Quick Onboarding/Rehiring):** The date when the IR submitted the request for IR Approver's approval.
  11. **Validation - Submitted On (Full Onboarding):** The date when the IR submitted all required fields for onboarding process.

---

## US-009: Onboarding Overview - Quick Onboarding Tab

- **Story ID:** US-009
- **Title:** View Quick Onboarding Requests in Onboarding Overview
- **Module:** Onboarding
- **Sub Module:** Onboarding Overview
- **User Role:** Industrial Relation (IR)
- **Feature:** Quick Onboarding Tab
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the created quick onboarded request so that I can view all the Quick Onboard request details.
- **Acceptance Criteria:**
  1. 'Onboarding Overview' page displays tabs: All, Quick Onboarding, Rehiring, Full Onboarding.
  2. User clicks 'Quick Onboarding' tab.
  3. Grid Columns:
     - PS No
     - Name
     - Employment Type
     - Dept Code
     - Immediate Supervisor
     - Date of Joining
     - Submitted On
     - Status
  4. 'Name' hyperlink directs the user to the Workforce Information details page.
  5. **Search Bar:** User can search requests using the search bar.
  6. **Page Navigation:** User can navigate to other pages using page navigation.
  7. **Validation - PS No Display by Status:**
     - Pending: PS No NOT displayed.
     - Approved: PS No displayed once IR approves.
     - Returned: PS No NOT displayed.
  8. **Validation - Submitted On:** Date when the IR submitted the hiring request for IR Approver's approval.

---

## US-010: Onboarding Overview - Rehiring Tab

- **Story ID:** US-010
- **Title:** View Rehiring Requests in Onboarding Overview
- **Module:** Onboarding
- **Sub Module:** Onboarding Overview
- **User Role:** Industrial Relation (IR)
- **Feature:** Rehiring Tab
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the created rehiring request so that I can view all the Rehire request details.
- **Acceptance Criteria:**
  1. 'Onboarding Overview' page displays tabs: All, Quick Onboarding, Rehiring, Full Onboarding.
  2. User clicks 'Rehiring' tab.
  3. Grid Columns:
     - PS No
     - Old PS No
     - Name
     - Employment Type
     - Dept Code
     - Immediate Supervisor
     - Date of Joining
     - Submitted On
     - Status
  4. 'Name' hyperlink directs the user to the Workforce Information details page.
  5. **Search Bar:** User can search requests using the search bar.
  6. **Page Navigation:** User can navigate to other pages using page navigation.
  7. **Validation - PS No Display by Status:** Pending, Approved, Returned.
  8. **Validation - Submitted On:** Date when the IR submitted the hiring request for IR Approver's approval.

---

## US-011: Onboarding Overview - Full Onboarding Tab

- **Story ID:** US-011
- **Title:** View Full Onboarding Requests in Onboarding Overview
- **Module:** Onboarding
- **Sub Module:** Onboarding Overview
- **User Role:** Industrial Relation (IR)
- **Feature:** Full Onboarding Tab
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the created Full Onboarding request so that I can view all the Full Onboard request details.
- **Acceptance Criteria:**
  1. 'Onboarding Overview' page displays tabs: All, Quick Onboarding, Rehiring, Full Onboarding.
  2. User clicks 'Full Onboarding' tab.
  3. Grid Columns:
     - PS No
     - Name
     - Employment Type
     - Dept Code
     - Immediate Supervisor
     - Date of Joining
     - Submitted On
     - Due Date
     - Status
  4. 'Name' hyperlink directs the user to the Workforce Information details page.
  5. **Search Bar:** User can search requests using the search bar.
  6. **Page Navigation:** User can navigate to other pages using page navigation.
  7. **Validation - PS No Display by Status:** Pending & Completed.
  8. **Validation - Submitted On:** Date when the IR submitted the hiring request for IR Approver's approval.
  9. **Validation - Due Date:** End date for the IR to complete and submit the full onboarding process.
  10. **Disciplinary Action:** Added in the Workman Information page after onboarding with fields: Action Date, Action Type, Remarks.

---

## US-012: IR Login (Bulk Upload)

- **Story ID:** US-012
- **Title:** IR Login to Application (Bulk Upload)
- **Module:** Login
- **Sub Module:** Login
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to login into the application so that I can access my Dashboard.
- **Acceptance Criteria:**
  1. Login screen displays:
     - User name textbox
     - Password textbox
     - Log In button
     - Login with SSO button
     - Forgot Password hyperlink
  2. Entering User name and password and clicking 'Log In' button, the user will be able to login into the WFM application.

---

## US-013: Bulk Upload Page

- **Story ID:** US-013
- **Title:** View and Upload Bulk Upload Document
- **Module:** Onboarding
- **Sub Module:** Bulk Upload
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to be able to view the Bulk Upload page so that I can upload the bulk upload document.
- **Acceptance Criteria:**
  1. From the IR dashboard, user opens side navigation.
  2. User views 'Quick Onboarding', 'Rehiring', 'Onboarding', 'Bulk Upload' sub menus from the 'Onboarding' menu.
  3. User selects 'Bulk Upload' sub menu.
  4. 'Bulk Upload' page displays with cards:
     - Bulk Onboarding 'Upload File'
     - Bulk Update 'Upload File'
  5. Buttons: Download Template
  6. User can upload document (Excel file) for bulk actions:
     - Quick onboarding of workmen
     - Rehiring of workmen
     - Updating workmen details
     - Separation
  7. Dropdown options:
     - Quick Onboarding
     - Rehiring
  8. Based on dropdown selection, related entities and fields are displayed.
     - If Quick Onboarding is selected, all respective quick onboarding fields are displayed.
     - If Rehiring is selected, all entities related to full onboarding are displayed.
  9. **Validation - Quick Onboarding Selection:** All mandatory fields auto-selected in checkbox; user cannot change them.
  10. **Validation - Rehiring Selection:** Respective mandatory fields auto-selected in checkbox; user cannot change them.
  11. User can upload document (Excel file) by drag & drop or by clicking the upload button.
  12. **Validation - Upload Error:** Error message displayed in popup when field characters exceed max limit, are invalid, or when mandatory fields are missing.
  13. **Validation - PS Number Assignment:** After validation, the system assigns sequential PS numbers in the background (e.g., if previous PS No ended at 125 and 30 employees are uploaded, PS numbers 126–155 are assigned).
  14. **Validation - Download Output:** After upload, the system generates a downloadable Excel file listing each employee's name, assigned PS number, and additional configurable fields.

---

## US-014: Download Template

- **Story ID:** US-014
- **Title:** Download Bulk Upload Template
- **Module:** Onboarding
- **Sub Module:** Bulk Upload
- **User Role:** Industrial Relation (IR)
- **Feature:** Download Template
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to be able to view the Bulk Upload page so that I need to select the fields required to download the template.
- **Acceptance Criteria:**
  1. Clicking 'Download Template' button displays 'Download Bulk Update Template' page.
  2. List of Attributes:
     - Select Entity
  3. All sections of the employee details page will be displayed.
  4. By selecting the entity, all fields associated to that entity will be displayed.
  5. By ticking the checkbox, user can select the required field values.
  6. Buttons: Download Template, Cancel.
  7. Clicking Download Template downloads the template.
  8. User selects required fields, then clicks Download button.
  9. Clicking Cancel navigates to the previous page.

---

## US-015: Bulk Image Upload

- **Story ID:** US-015
- **Title:** Bulk Image Upload
- **Module:** Onboarding
- **Sub Module:** Bulk Upload
- **User Role:** Industrial Relation (IR)
- **Feature:** Bulk Image Update
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to be able to fetch the Bulk Image Upload, so that I can store the images in the file directory.
- **Acceptance Criteria:**
  1. Clicking 'Download Template' button displays 'Download Bulk Update Template' page.
  2. List of Attributes:
     - PS No (dropdown) - list of all employee PS No.
     - Upload button
  3. Clicking upload button allows uploading the URL of all images.
  4. System captures the URL and saves all data in the file directory.
  5. Buttons: Save, Cancel.
  6. Clicking Save saves the data.
  7. Clicking Cancel navigates to the previous page.
  8. **Validation - Bulk Photo Upload:** System searches/fetches photos in specified location. Photos must be named with PS number (e.g., 123456.JPG). System extracts PS number and associates the photo.
  9. **Validation - Bulk Document Upload:** System searches for documents in specified location/drive. Documents must be named PS_number_document_code (e.g., PS_number_ad.pdf for Aadhaar). System extracts PS number and adds the record.
  10. **Validation - Photos Download:** Photos can be downloaded per department, all photos, or via uploaded PS numbers through Excel. Bulk photos download as a zip folder.

---

## US-016: IR Login (Workforce Information)

- **Story ID:** US-016
- **Title:** IR Login to Application (Workforce Information)
- **Module:** Login
- **Sub Module:** Login
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to login into the application so that I can access my Dashboard.
- **Acceptance Criteria:**
  1. Login screen displays:
     - User name textbox
     - Password textbox
     - Log In button
     - Login with SSO button
     - Forgot Password hyperlink
  2. Entering User name and password and clicking 'Log In' button, the user will be able to login into the WFM application.

---

## US-017: Workforce Information Page (IR)

- **Story ID:** US-017
- **Title:** View Workforce Information Page (IR Role)
- **Module:** Workforce Information
- **Sub Module:** Workforce Information
- **User Role:** Industrial Relation (IR)
- **Priority:** High
- **Description:** As an Industrial Relation, I want to view the Workforce Information page so that I can view the employee details.
- **Acceptance Criteria:**
  1. From the IR dashboard, user opens side navigation.
  2. Side navigation shows 'Workforce Information', 'Event History', 'Disciplinary Action' sub menus from 'Workforce Information' menu.
  3. User selects 'Workforce Information' sub menu.
  4. Data grid columns:
     - PS No and Employee Name
     - Dept Name and Code
     - Gender
     - Immediate Supervisor
     - Current Status (Probation, Confirmed)
     - Designation
  5. 'Name' hyperlink directs user to workforce information details page displaying:
  6. **Personal Information - Biographical:**
     - PS#* (number)
     - Date of Birth* (date picker)
     - Age
     - Birth Place*
  7. **Personal Information:**
     - Title* (dropdown, from Title Master)
     - First Name* (text field)
     - Middle Name (text field)
     - Last Name* (text field)
     - Name as per Aadhaar/Full Name* (text field)
     - Initials (text field)
     - Gender* (dropdown: Male, Female)
     - Religion* (dropdown, from Religion Master)
     - Caste* (dropdown, from Caste Master)
     - Domicile (State)* (dropdown, from State Master)
     - Father Name* (text field)
     - Marital Status* (radio button: Yes/No)
     - Date Of Marriage* (date picker)
     - Blood Group* (dropdown, from Blood Group Master)
  8. **Contact Info:**
     - Email Id* (text field)
     - Office Tele No. (number field)
     - Mobile No* (number field)
  9. **Emergency Contact:**
     - Contact Person (text field)
     - Relationship (dropdown, from Relationship Master)
     - Mobile No (number field)
  10. **Dependents:**
      - Relationship (dropdown, from Relationship Master)
      - Dependent Status (dropdown: Yes/No)
      - Title (dropdown, from Title Master)
      - First Name (text field)
      - Last Name (text field)
      - Gender (dropdown: Male, Female)
      - Date of Birth (date picker)
      - Age (auto populated)
      - Qualifications (dropdown, from Qualification Master)
      - Occupation (dropdown, from Occupation Master)
      - Aadhar ID (text field)
      - Mediclaim Yes/No (dropdown)
      - Differently Abled (dropdown: Yes/No)
  11. **Permanent Address:**
      - Country (dropdown, from Country Master)
      - C/O
      - Street & House Number (text field)
      - Second Address Line (text field)
      - City/Village (text field)
      - District (dropdown, from District Master)
      - State (dropdown, from State Master)
      - PIN (number field)
      - Present Post Office (text field)
  12. **Present Address:**
      - Country, C/O, Street & House Number, Second Address Line, City/Village, District, State, PIN, Present Post Office (same field types as Permanent Address)
  13. **National ID & Personal Documents:**
      - Aadhaar Number* (number field)
      - PAN (text field)
      - UAN Number (number)
      - PF Account No (numeric field)
      - EPS No (number field)
      - ESIC No (number field)
      - Apprentice Reg. No (text field)
      - E Shram Card No (text field)
      - Apprentice Contract (text field)
      - Reg. No (text field)
  14. **Health Information:**
      - Health Issue (text field)
      - Disabled? (dropdown: Yes/No)
      - Disability by Birth or While Working (dropdown)
      - Disability Type (text field)
      - Disability% (text field)
  15. **Bank Details:**
      - Bank Name (text field)
      - Bank Account No (text field)
      - IFSC Code (text field)
      - Bank Branch (text field)
  16. **Careers - Qualification:**
      - Academic Start Date (date picker)
      - Academic End Date (date picker)
      - Qualification (dropdown, from Qualification Master)
      - Qualification Stream (text field)
      - Education Certificate (text field)
      - Type of the Course (dropdown, from Types of Course Master)
      - Highest Level Education (dropdown, from Education Type Master)
      - Name of Institution/University (text field)
      - Year of Passing (date picker)
      - Duration of the Course (text field)
      - Percentage (number field)
  17. **Work Experience:**
      - Employee ID (number)
      - From Date (date picker)
      - To Date (date picker)
      - Is this your Last Employer? (dropdown: Yes/No)
      - Within L&T? (dropdown: Yes/No)
      - Employer's Name (text field)
      - Employer's Location (dropdown: City/Dist/State)
      - Country (dropdown, from Country Master)
      - Type of Industry (text field)
      - Nature of Work (dropdown, from Master)
      - Employment Type (dropdown, from Employment Type Master)
      - Others Info (text field)
  18. **Employment Information - Employment Details:**
      - Joining Date* (date picker)
      - Probation Date (date picker)
      - Extended Date of Probation (date picker)
      - Confirmation Date (date picker)
      - Retirement Date (date picker)
      - Last Promotion Date (date picker)
      - Experience (text field)
      - Overall Experience YY/MM (text field)
      - Current L&T Experience YY/MM (text field)
      - Previous L&T Experience YY/MM (text field)
      - Previous Experience Outside L&T YY/MM (text field)
  19. **Termination:**
      - Separation Date (date picker)
      - Reason for Separation (text field)
      - OK to Rehire? (Yes/No)
      - HR Comment for Blacklisting (text field)
      - Attachment (document upload button)
  20. **Organization Information:**
      - Location Group (dropdown, from Location Master)
      - Company Name (dropdown, from Company Name Master)
      - Working Area (dropdown, from Working Area Master)
      - IC (dropdown, from IC Master)
      - Dept Code (dropdown, from Dept Code Master)
  21. **Job Information:**
      - Unit Name* (dropdown)
      - Function Code (dropdown, from Function Code Master)
      - Primary Job (radio button: Yes/No)
      - Employee Status?* (dropdown, from Status Master)
      - Designation (text field)
      - Category Code* (dropdown, from Category Master)
      - Employment Type* (dropdown, from Employment Type Master)
      - Transport User? (dropdown: Yes/No)
      - Bus Route Code (dropdown, from Bus Route Code Master)
      - Grade/Training Year (number field)
      - Previous PS Number (number field)
      - Shift Code* (dropdown, from Shift Code Master)
      - Direct Workman* (radio button: Yes/No)
      - Ex-Trainee? (dropdown: Yes/No)
      - Area* (dropdown, from Location Master)
      - Joining Route (dropdown, from Bus Route Master)
  22. **Job Relationship:**
      - DH - Dept Head (auto populated based on dept code)
      - NS - Next Supervisor (auto populated based on dept code)
      - IS - Immediate Supervisor (auto populated based on dept code)
  23. **Payroll - Compensation Information:**
      - Daily/Monthly Wages* (dropdown: Daily/Monthly)
      - Cadre at Joining* (dropdown, from Cadre Master)
      - Current Cadre* (dropdown, from Cadre Master)
      - Joining Basic* (number)
      - Confirmation Basic (number)
      - Current Basic* (number)
  24. **Cadre History:**
      - Event Date (date picker)
      - Event Reason (text field)
      - Previous Cadre (dropdown, from Cadre Master)
      - Current Cadre (dropdown, from Cadre Master)
  25. **Event History:**
      - Effect Date
      - Event Reason (dropdown, from Reason Master)
      - From Cadre (dropdown, from Cadre Master)
      - To Cadre (dropdown, from Cadre Master)
      - Function Code (dropdown, from Function Code Master)
      - Points (number)
      - Basic (number)
      - Transaction Date (date picker)
      - Transaction ID (text field)
  26. **Additional Information - Others:**
      - Extra Information (text field)
      - Years In Gujarat (Since when) (text field)
      - CSN Code (text field)
      - Locker No. (text field)
      - Sports Group (dropdown, from Sports Group Master)
      - TRT Location (1) (text field)
      - TRT Location (2) (text field)
      - Remark (text field)
      - Achievement (text field)
      - Safety Shoe Size (dropdown, from Safety Shoe Size Master)
      - Boiler Suit Size (dropdown, from Boiler Suit Size Master)
  27. **Committee Information:**
      - Role (dropdown, from Committee Role Master)
      - Starting Date (date picker)
      - Ending Date (date picker)
      - Duration (text field)
      - Remarks (text field)
  28. **Right Side Pane:**
      - Employee profile photo (with edit icon)
      - PS Number
      - Employee Name
  29. **Buttons:** Edit, Save Draft, Cancel
  30. **Search Bar:** User can search workmen.
  31. **Page Navigation:** User can navigate pages.

---

## US-018: Event History Page

- **Story ID:** US-018
- **Title:** View Event History Page
- **Module:** Workforce Information
- **Sub Module:** Event History
- **User Role:** Industrial Relation (IR)
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the Event History page so that I can view the Event History details in the grid view.
- **Acceptance Criteria:**
  1. From the IR dashboard, user opens side navigation.
  2. User views 'Workforce Information', 'Event History', 'Disciplinary Action' sub menus from 'Workforce Information' menu.
  3. User selects 'Event History' sub menu.
  4. Data grid columns:
     - Effective Date (event start date)
     - Event (dropdown, fetched from Events Master)
     - From Cadre (dropdown, fetched from Cadre Master)
     - To Cadre (dropdown, fetched from Cadre Master)
     - Dept Code (dropdown, fetched from Dept Code Master)
     - Function (auto filled based on dept code)
     - Basic (text field)
     - Points (text field)
     - PS No (auto populated from Workforce Information)
  5. **Buttons:** Edit, Add New Event
  6. **Search Bar:** User can search workmen.
  7. **Page Navigation:** User can navigate pages.
  8. **Validation:** User can see the old PS number assigned based on cadre.

---

## US-019: Edit Event History

- **Story ID:** US-019
- **Title:** Edit Event History Details
- **Module:** Activities
- **Sub Module:** Event History
- **User Role:** Industrial Relation (IR)
- **Feature:** Edit
- **Priority:** Medium
- **Description:** As an Industrial Relation, I need to click the edit button in the Event History details page so that I can save changes of respective Event History details.
- **Acceptance Criteria:**
  1. Clicking edit button displays 'Edit Event History' page.
  2. User fills all mandatory fields (*).
  3. List of Attributes:
     - Effective Date (event start date)
     - Event (dropdown, fetched from Events Master)
     - From Cadre (dropdown, fetched from Cadre Master)
     - To Cadre (dropdown, fetched from Cadre Master)
     - Dept Code (dropdown, fetched from Dept Code Master)
     - Function (auto filled based on dept code)
     - Basic (text field)
     - Points (text field)
  4. **Buttons:** Save, Cancel
  5. Clicking Save saves the changes.
  6. Clicking Cancel navigates to the previous page.

---

## US-020: Add Event History

- **Story ID:** US-020
- **Title:** Add New Event History
- **Module:** Activities
- **Sub Module:** Event History
- **User Role:** Industrial Relation (IR)
- **Feature:** Add
- **Priority:** Medium
- **Description:** As an Industrial Relation, I need to click the add button in the Event History details page so that I can add new Event History details.
- **Acceptance Criteria:**
  1. Clicking add button displays 'Add Event History' page.
  2. List of Attributes:
     - Effective Date (event start date)
     - Event (dropdown, fetched from Events Master)
     - From Cadre (dropdown, fetched from Cadre Master)
     - To Cadre (dropdown, fetched from Cadre Master)
     - Dept Code (dropdown, fetched from Dept Code Master)
     - Function (auto filled based on dept code)
     - Basic (text field)
     - Points (text field)
  3. **Buttons:** Save, Cancel
  4. Clicking Save adds the created details to the Event History grid view.
  5. Clicking Cancel navigates to the previous page.
  6. **Validation - First Event:** A new event begins every time an employee is onboarded. By default, the first event is "Joining event" auto-filled based on quick onboarding details.
  7. **Validation - Apprentice/AT/Temp Workman:** Only two events displayed (Joining and Separation). Once they become permanent workmen, a new PS No is generated and a new Joining event is created.

---

## US-021: Disciplinary Action Page

- **Story ID:** US-021
- **Title:** View Disciplinary Action Page
- **Module:** Workforce Information
- **Sub Module:** Disciplinary Action
- **User Role:** Industrial Relation (IR)
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the Disciplinary Action page so that I can view the respective disciplinary action details.
- **Acceptance Criteria:**
  1. From IR dashboard, user opens side navigation.
  2. User views 'Workforce Information', 'Event History', 'Disciplinary Action' sub menus from 'Workforce Information' menu.
  3. User selects 'Disciplinary Action' sub menu.
  4. Data grid columns:
     - PS No and Employee Name
     - Dept Code and Dept Name
     - Details of Misconduct
     - Incident Date
     - Report Received (DD-MM-YYYY)
     - Disciplinary Actions
     - Action Date
     - Issued Date
     - Remarks
     - Actions (edit icon)
  5. **Buttons:** Import, Export, Add
  6. **Export:** Details in the list can be exported to an Excel file.
  7. **Search Bar:** User can search workmen.
  8. **Page Navigation:** User can navigate pages.

---

## US-022: Import Disciplinary Action

- **Story ID:** US-022
- **Title:** Import Disciplinary Action Data
- **Module:** Activities
- **Sub Module:** Disciplinary Action
- **User Role:** Industrial Relation (IR)
- **Feature:** Import
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the Import button so that I can import all the listed activities.
- **Acceptance Criteria:**
  1. Clicking Import button imports the list of disciplinary action details into the system.
  2. Imported columns:
     - PS No and Employee Name
     - Dept Code and Dept Name
     - Details of Misconduct
     - Incident Date
     - Report Received (DD-MM-YYYY)
     - Disciplinary Actions
     - Action Date
     - Issued Date
     - Remarks
     - Actions (edit icon)
  3. User needs to import details with matching column values.

---

## US-023: Export Disciplinary Action

- **Story ID:** US-023
- **Title:** Export Disciplinary Action Data
- **Module:** Activities
- **Sub Module:** Disciplinary Action
- **User Role:** Industrial Relation (IR)
- **Feature:** Export
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the Export button so that I can Export all the listed activities.
- **Acceptance Criteria:**
  1. Clicking Export button exports the list of disciplinary action details to an Excel file.
  2. Exported columns:
     - PS No and Employee Name
     - Dept Code and Dept Name
     - Details of Misconduct
     - Incident Date
     - Report Received (DD-MM-YYYY)
     - Disciplinary Actions
     - Action Date
     - Issued Date
     - Remarks
     - Actions (edit icon)
  3. User can save the export file to a location.

---

## US-024: Add Disciplinary Action

- **Story ID:** US-024
- **Title:** Add Disciplinary Action Details
- **Module:** Activities
- **Sub Module:** Disciplinary Action
- **User Role:** Industrial Relation (IR)
- **Feature:** Add
- **Priority:** Medium
- **Description:** As an Industrial Relation, I want to view the add button so that I can add details of required activities.
- **Acceptance Criteria:**
  1. Clicking add button displays 'Add Disciplinary Action' page.
  2. User fills all mandatory fields (*).
  3. List of Attributes:
     - Employee (text field and dropdown)
     - Dept Code
     - Details of Misconduct
     - Incident Date
     - Report Received (DD-MM-YYYY)
     - Disciplinary Actions
     - Action Date
     - Issued Date
     - Remarks (text box)
  4. **Buttons:** Save, Cancel
  5. Clicking Save adds the details to the Disciplinary Action grid.
  6. Clicking Cancel navigates to the previous page.

---

## US-025: Workforce Information - CTCW Role

- **Story ID:** US-025
- **Title:** View Workforce Information (CTCW Role)
- **Module:** Workforce Information
- **Sub Module:** Workforce Information
- **User Role:** CTCW (Central Training Center Workshop)
- **Priority:** Medium
- **Description:** As a CTCW, I want to view the Workforce Information page so that I can view the contract workmen details.
- **Acceptance Criteria:**
  1. From the CTCW dashboard, user opens side navigation.
  2. User selects 'Workforce Information' sub menu.
  3. System captures contractor workman data from API integration and displays it.
  4. Data grid columns:
     - PS No and Employee Name
     - Dept Name and Code
     - Gender
     - Contractor Supervisor
     - Designation
  5. 'Name' hyperlink directs user to workforce information details page.
  6. Fields displayed for CTCW workmen are as per the linked document.
  7. **Right Side Pane:**
     - Employee profile photo (with edit icon)
     - PS Number
     - Employee Name
  8. **Button:** Close (navigates back to previous page)
  9. **Search Bar:** User can search workmen.
  10. **Page Navigation:** User can navigate pages.

---

## US-026: Workforce Information - Multiple Roles

- **Story ID:** US-026
- **Title:** View Workforce Information (Admin and Supervisor Roles)
- **Module:** Workforce Information
- **Sub Module:** Workforce Information
- **User Role:** System Admin, IR Admin, Shop Admin, IR Approver, Shop In Charge, Shop Supervisor, Shop Coordinate, Dept Head, Shop Head, Company Head, Location Head, BU Head, AT Staff (Supervisor)
- **Priority:** Medium
- **Description:** As a user, I want to view the Workforce Information page so that I can view the employee details.
- **Acceptance Criteria:**
  1. From the user dashboard, user opens side navigation.
  2. User selects 'Workforce Information' sub menu.
  3. Data grid columns:
     - PS No and Employee Name
     - Dept Name and Code
     - Gender
     - Immediate Supervisor
     - Current Status (Probation, Confirmed)
     - Designation
  4. 'Name' hyperlink directs user to workforce information details page.
  5. All fields are displayed as per linked document.
  6. **Right Side Pane:**
     - Employee profile photo (with edit icon)
     - PS Number
     - Employee Name
  7. **Button:** Close (navigates back to previous page)
  8. **Search Bar:** User can search workmen.
  9. **Page Navigation:** User can navigate pages.

---

## US-027: IR Approver Login

- **Story ID:** US-027
- **Title:** IR Approver Login to Application
- **Module:** Login
- **Sub Module:** Login
- **User Role:** Industrial Relation Approver
- **Priority:** High
- **Description:** As an Industrial Relation Approver, I want to login into the application so that I can access my Dashboard.
- **Acceptance Criteria:**
  1. Login screen displays:
     - User name textbox
     - Password textbox
     - Log In button
     - Login with SSO button
     - Forgot Password hyperlink
  2. Entering User name and password and clicking 'Log In' button, the user will be able to login into the WFM application.

---

## US-028: Onboarding Approval Overview - All Tab

- **Story ID:** US-028
- **Title:** View All Requests in Onboarding Approval Overview
- **Module:** Onboarding Approval
- **Sub Module:** Onboarding Approval Overview
- **User Role:** Industrial Relation Approver
- **Feature:** All Tab
- **Priority:** High
- **Description:** As an Industrial Relation Approver, I want to view all the requests so that I can view respective details by clicking on it.
- **Acceptance Criteria:**
  1. From the IR Approver dashboard, user opens side navigation.
  2. User selects 'Onboarding Approval' menu.
  3. 'Onboarding Approval' page displays tabs: All, Pending, Approved.
  4. User clicks 'All' tab.
  5. Data grid columns:
     - All Select (Checkbox)
     - PS No
     - Name
     - Employment Type
     - Dept Code
     - Immediate Supervisor
     - Date of Joining
     - Submitted On
     - Onboarding Type
     - Status
  6. **Buttons:** Approve, Reject, Export
  7. User can select all by clicking "All Select" checkbox.
  8. Clicking Approve displays: 'Data approved successful'.
  9. Clicking Export displays: 'Data Exported Successfully'.
  10. 'PS No/Name' hyperlink directs user to the workmen details approval page.
  11. **Search Bar:** User can search requests.
  12. **Page Navigation:** User can navigate pages.
  13. **Validation - PS Number Generation:** PS number is generated for Quick Onboarding and Rehiring only after IR Approver approval.
  14. **Validation - Bulk Approve:** User can select multiple requests and approve in bulk.
  15. **Validation - PS No by Status:**
      - Pending: Waiting for approval from IR Approver.
      - Approved: IR Approver approved the onboarding process.
      - Returned: IR Approver returned the onboarding or rehiring process.
  16. **Validation - Submitted On:** The date when the IR submitted the Quick Onboarding or Rehiring for IR Approver's approval.

---

## US-029: Onboarding Approval - Overview Page (Request Details)

- **Story ID:** US-029
- **Title:** View Workmen Details Approval Page
- **Module:** Onboarding Approval
- **Sub Module:** Onboarding Approval Overview
- **User Role:** Industrial Relation Approver
- **Feature:** Overview Page
- **Priority:** High
- **Description:** As an Industrial Relation Approver, I want to click on the respective request so that I can view the workmen details approval page and process the request.
- **Acceptance Criteria:**
  1. User navigates to request view page by clicking PS No or Name in the All or Pending tab.
  2. User can view all employee details captured during Quick Onboarding or Rehiring (auto-populated in separate sections).
  3. User can approve the employee onboarding by clicking the Approve button.
  4. A popup displays "Approval successful" on successful approval.
  5. User can reject the employee onboarding by clicking the Reject button.
  6. A popup displays "Do you want to reject employee onboarding?"
  7. Clicking Yes returns the onboarding process and redirects to the Onboarding Approval page.
  8. Clicking No keeps the user on the workmen details approval page (onboarding is NOT returned).

---

## US-030: Onboarding Approval - Pending Tab

- **Story ID:** US-030
- **Title:** View Pending Requests in Onboarding Approval
- **Module:** Onboarding Approval
- **Sub Module:** Onboarding Approval Overview
- **User Role:** Industrial Relation Approver
- **Feature:** Pending Tab
- **Priority:** High
- **Description:** As an Industrial Relation Approver, I want to view all the pending requests so that I can view respective details by clicking on it.
- **Acceptance Criteria:**
  1. 'Onboarding Approval' page displays tabs: All, Pending, Approved.
  2. User clicks 'Pending' tab.
  3. Data grid columns:
     - Name
     - Employment Type
     - Dept Code
     - Immediate Supervisor
     - Date of Joining
     - Submitted On
     - Onboarding Type
  4. **Buttons:** Approve, Reject, Export
  5. User can select all by clicking "All Select" checkbox.
  6. Clicking Approve displays: 'Data approved successful'.
  7. Clicking Export displays: 'Data Exported Successfully'.
  8. 'PS No/Name' hyperlink directs user to workmen details approval page.
  9. **Search Bar:** User can search requests.
  10. **Page Navigation:** User can navigate pages.
  11. **Validation - Submitted On:** The date when the IR submitted the Quick Onboarding or Rehiring for IR Approver's approval.

---

## US-031: Onboarding Approval - Approved Tab

- **Story ID:** US-031
- **Title:** View Approved Requests in Onboarding Approval
- **Module:** Onboarding Approval
- **Sub Module:** Onboarding Approval Overview
- **User Role:** Industrial Relation Approver
- **Feature:** Approved Tab
- **Priority:** Medium
- **Description:** As an Industrial Relation Approver, I want to view all the Approved requests so that I can view respective details by clicking on it.
- **Acceptance Criteria:**
  1. 'Onboarding Approval' page displays tabs: All, Pending, Approved.
  2. User clicks 'Approved' tab.
  3. Grid Columns:
     - All Select (Checkbox)
     - PS No
     - Name
     - Employment Type
     - Dept Code
     - Immediate Supervisor
     - Date of Joining
     - Approved On
     - Onboarding Type
  4. **Button:** Export
  5. User can select all by clicking "All Select" checkbox.
  6. Clicking Export displays: 'Data Exported Successful'.
  7. 'PS No/Name' hyperlink directs user to workmen details approval page.
  8. **Search Bar:** User can search requests.
  9. **Page Navigation:** User can navigate pages.
