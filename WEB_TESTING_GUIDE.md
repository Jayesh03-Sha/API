# Web (EB) Testing Guide

This guide covers the testing of the Promise Insurance Service portals and dashboards.

## 📊 Management Dashboard
Verify the operational health and real-time statistics.

### 1. Metric Accuracy
- **Action**: Open the Dashboard (`/ui/dashboard/`).
- **Verification**: 
    - Compare "Total Leads" with the count in the Leads table.
    - Check "Total Revenue" matches the sum of transactions in the DB.
    - Verify "Data Source" tags correctly identify where the numbers come from.

### 2. Lead Visibility
- **Action**: Check "Recently Added Leads".
- **Verification**: New leads added via the API or Admin should appear instantly at the top of the table.

---

## 📄 Professional Quote Proposal
Verify the customer-facing quotation extraction document.

### 1. Side-by-Side Comparison
- **Action**: Open a Proposal URL (`/ui/dashboard/quotes/{id}/proposal/`).
- **Verification**: 
    - Check for "Promise Insurance" branding and legal info.
    - Verify the "Best Choice" badge is on the correctly ranked provider.
    - Ensure premiums, coverage, and benefits are correctly aligned across columns.

### 2. Branding & Legal
- **Action**: Scroll to the footer.
- **Verification**: Verify Broker Registration No. 22 and correct office addresses for Dubai and Abu Dhabi.

---

## 💼 CRM Operations
Verify lead management workflows.

### 1. Lead Details
- **Action**: Navigate to `Dashboard -> Leads -> [Lead Name]`.
- **Verification**: Ensure all deal documents and personal details are visible.

### 2. Transaction Flow
- **Action**: Navigate to `Dashboard -> Transactions`.
- **Verification**: Verify that commission amounts are calculated automatically based on the insurer net premium.
