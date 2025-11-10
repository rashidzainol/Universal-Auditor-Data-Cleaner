# Universal Auditor Data Cleaner - Practical Examples & Scenarios

## 📊 Example 1: SAP Business One Trial Balance Report

### **Original Report Format:**
```
ACCOUNT CODE: 11000-000 CASH AND BANK
DATE        JOURNAL   REFERENCE   DESCRIPTION              DEBIT        CREDIT     BALANCE
01/01/2024  GJ001     BNK-001     Customer Receipt       15,000.00              25,000.00
02/01/2024  GJ002     CHQ-001     Office Rent                       8,500.00    16,500.00
03/01/2024  GJ003     BNK-002     Bank Charges              150.00              16,350.00

ACCOUNT CODE: 21000-000 ACCOUNTS PAYABLE
04/01/2024  GJ004     INV-045     Supplier Invoice                  12,000.00   28,000.00
05/01/2024  GJ005     PMT-022     Payment to Vendor      10,000.00              18,000.00
```

### **Configuration Settings:**
- **Date Column**: A
- **Journal Column**: B  
- **Reference Column**: C
- **Description Column**: D
- **Debit Column**: E
- **Credit Column**: F
- **Balance Column**: G
- **Account Code Column**: Auto-detect from headers

### **Processed Output:**
| Account Code | Account Name | Date | Journal | Reference | Description | Debit | Credit | Balance |
|-------------|-------------|------|---------|-----------|-------------|-------|--------|---------|
| 11000-000 | Cash and Bank | 01/01/2024 | GJ001 | BNK-001 | Customer Receipt | 15,000.00 | | 25,000.00 |
| 11000-000 | Cash and Bank | 02/01/2024 | GJ002 | CHQ-001 | Office Rent | | 8,500.00 | 16,500.00 |
| 11000-000 | Cash and Bank | 03/01/2024 | GJ003 | BNK-002 | Bank Charges | 150.00 | | 16,350.00 |
| 21000-000 | Accounts Payable | 04/01/2024 | GJ004 | INV-045 | Supplier Invoice | | 12,000.00 | 28,000.00 |
| 21000-000 | Accounts Payable | 05/01/2024 | GJ005 | PMT-022 | Payment to Vendor | 10,000.00 | | 18,000.00 |

---

## 📊 Example 2: QuickBooks General Ledger Export

### **Original Report Format:**
```
Account: 5010 - Office Expenses
Type    Date        Num   Name                 Memo                  Split   Amount   Balance
DEBIT   01/15/2024        Office Supplies      Printer Cartridges            85.50     85.50
DEBIT   01/20/2024  C-125 Cleaning Service     Monthly janitorial           250.00    335.50
CREDIT  01/25/2024        Refund               Damaged goods return          45.00    290.50

Account: 4010 - Sales Revenue
CREDIT  01/10/2024  INV-1 Customer A           Product sale               1,500.00  1,500.00
CREDIT  01/18/2024  INV-2 Customer B           Service fee                  750.00  2,250.00
```

### **Configuration Settings:**
- **Date Column**: B
- **Journal Column**: C (Num)
- **Reference Column**: C (Num) 
- **Description Column**: D (Name) + E (Memo)
- **Debit Column**: G (for DEBIT transactions)
- **Credit Column**: G (for CREDIT transactions)
- **Balance Column**: H
- **Account Detection**: From "Account:" headers

### **Processed Output:**
| Account Code | Account Name | Date | Journal | Reference | Description | Debit | Credit | Balance |
|-------------|-------------|------|---------|-----------|-------------|-------|--------|---------|
| 5010 | Office Expenses | 01/15/2024 | | | Office Supplies - Printer Cartridges | 85.50 | | 85.50 |
| 5010 | Office Expenses | 01/20/2024 | C-125 | C-125 | Cleaning Service - Monthly janitorial | 250.00 | | 335.50 |
| 5010 | Office Expenses | 01/25/2024 | | | Refund - Damaged goods return | | 45.00 | 290.50 |
| 4010 | Sales Revenue | 01/10/2024 | INV-1 | INV-1 | Customer A - Product sale | | 1,500.00 | 1,500.00 |
| 4010 | Sales Revenue | 01/18/2024 | INV-2 | INV-2 | Customer B - Service fee | | 750.00 | 2,250.00 |

---

## 📊 Example 3: MYOB Transaction Listing

### **Original Report Format:**
```
*** ACCOUNT: 1-1100 Petty Cash ***
Date        Transaction   Supplier/Customer   Details              Debit       Credit
03/01/2024  PC-001        Office Mart        Stationery           125.00    
05/01/2024  PC-002        Taxi Company       Transport             48.00    
08/01/2024  PC-003        Cash Top-up                          1,000.00    

*** ACCOUNT: 2-2100 Credit Card ***
10/01/2024  CC-001        Hotel ABC          Business Trip                  450.00
12/01/2024  CC-002        Airline XYZ        Flight Tickets                 890.00
15/01/2024  CC-003        Restaurant         Client Meeting                 120.00
```

### **Configuration Settings:**
- **Date Column**: A
- **Journal Column**: B (Transaction)
- **Reference Column**: B (Transaction)
- **Description Column**: C (Supplier/Customer) + D (Details)
- **Debit Column**: E
- **Credit Column**: F  
- **Balance Column**: Auto (not present in original)
- **Account Detection**: From "*** ACCOUNT:" patterns

### **Processed Output:**
| Account Code | Account Name | Date | Journal | Reference | Description | Debit | Credit | Balance |
|-------------|-------------|------|---------|-----------|-------------|-------|--------|---------|
| 1-1100 | Petty Cash | 03/01/2024 | PC-001 | PC-001 | Office Mart - Stationery | 125.00 | | |
| 1-1100 | Petty Cash | 05/01/2024 | PC-002 | PC-002 | Taxi Company - Transport | 48.00 | | |
| 1-1100 | Petty Cash | 08/01/2024 | PC-003 | PC-003 | Cash Top-up | 1,000.00 | | |
| 2-2100 | Credit Card | 10/01/2024 | CC-001 | CC-001 | Hotel ABC - Business Trip | | 450.00 | |
| 2-2100 | Credit Card | 12/01/2024 | CC-002 | CC-002 | Airline XYZ - Flight Tickets | | 890.00 | |
| 2-2100 | Credit Card | 15/01/2024 | CC-003 | CC-003 | Restaurant - Client Meeting | | 120.00 | |

---

## 📊 Example 4: Custom Accounting System with Complex Format

### **Original Report Format:**
```
LEDGER ACCOUNT: 500100 - SALARIES & WAGES (DEPARTMENT A)
TRANSACTION DETAIL:
-------------------------------------------
2024-01-05 | PAYRUN-0124 | Monthly Salary | 45,280.00 Dr | 45,280.00
2024-01-12 | PAYRUN-0124 | Overtime       |  2,150.00 Dr | 47,430.00
2024-01-19 | GJ-8845     | Accrual Reversal|              | 45,500.00 Cr

LEDGER ACCOUNT: 500200 - EMPLOYEE BENEFITS
-------------------------------------------
2024-01-08 | GJ-7721     | Medical Claims |  8,750.00 Dr |  8,750.00
2024-01-15 | GJ-7833     | Insurance Premium|             |  6,200.00 Cr
2024-01-22 | GJ-7912     | Training       |  3,500.00 Dr |  2,700.00 Dr
```

### **Configuration Settings:**
- **Date Column**: A (first part before |)
- **Journal Column**: B (second part after |)
- **Reference Column**: B (second part after |)
- **Description Column**: C (third part after |)
- **Debit Column**: D (extract "Dr" amounts)
- **Credit Column**: D (extract "Cr" amounts) 
- **Balance Column**: E
- **Account Detection**: From "LEDGER ACCOUNT:" lines

### **Processed Output:**
| Account Code | Account Name | Date | Journal | Reference | Description | Debit | Credit | Balance |
|-------------|-------------|------|---------|-----------|-------------|-------|--------|---------|
| 500100 | Salaries & Wages (Department A) | 2024-01-05 | PAYRUN-0124 | PAYRUN-0124 | Monthly Salary | 45,280.00 | | 45,280.00 |
| 500100 | Salaries & Wages (Department A) | 2024-01-12 | PAYRUN-0124 | PAYRUN-0124 | Overtime | 2,150.00 | | 47,430.00 |
| 500100 | Salaries & Wages (Department A) | 2024-01-19 | GJ-8845 | GJ-8845 | Accrual Reversal | | 45,500.00 | 45,500.00 |
| 500200 | Employee Benefits | 2024-01-08 | GJ-7721 | GJ-7721 | Medical Claims | 8,750.00 | | 8,750.00 |
| 500200 | Employee Benefits | 2024-01-15 | GJ-7833 | GJ-7833 | Insurance Premium | | 6,200.00 | 6,200.00 |
| 500200 | Employee Benefits | 2024-01-22 | GJ-7912 | GJ-7912 | Training | 3,500.00 | | 2,700.00 |

---

## 🔧 Advanced Configuration Examples

### **Example 5: Handling Different Amount Formats**

```python
# Various amount formats the tool can handle:
"500.00"           # Standard decimal
"1,500.00"         # With thousands separator
"1500"             # No decimal places
"1.500,00"         # European format (comma as decimal)
"$1,500.00"        # With currency symbol
"1 500.00"         # Space as thousands separator
"(500.00)"         # Parentheses for negatives
"-500.00"          # Minus sign for negatives
"500.00 Dr"        # With Dr/Cr indicator
"500.00 Cr"        # With Cr indicator
```

### **Configuration for Complex Amounts:**
- **Debit Column**: Look for positive amounts with "Dr" or no suffix
- **Credit Column**: Look for positive amounts with "Cr" or parentheses/negative signs
- **Balance Column**: Handle all formats with Dr/Cr indicators

### **Example 6: Multi-Line Descriptions**

**Original:**
```
01/01/2024 | GJ-001 | Office Equipment
            Purchase of new computers
            and printers for accounting
            department
```

**Processed:**
- **Description**: "Office Equipment Purchase of new computers and printers for accounting department"

---

## 💡 Pro Tips for Different Systems

### **For SAP Reports:**
- Account codes typically follow patterns like `XXXXX-XXX`
- Use auto-detect for account headers containing "ACCOUNT CODE"
- Balance columns are usually well-structured

### **For QuickBooks:**
- Transactions may have type indicators (DEBIT/CREDIT)
- Combine "Name" and "Memo" columns for full description
- Account detection from "Account:" lines

### **For MYOB:**
- Look for "*** ACCOUNT:" patterns
- Transaction references are often prefixed (PC-, CC-, etc.)
- Supplier/Customer and Details can be combined

### **For Custom Systems:**
- Use the Processing Log to see what patterns are detected
- Adjust column mappings incrementally
- Test with small files first to verify configuration

---

## 🎯 Key Benefits Demonstrated

1. **Format Flexibility**: Handles various report layouts and structures
2. **Amount Intelligence**: Correctly interprets different numeric formats
3. **Account Linking**: Maintains proper account association for all transactions  
4. **Data Integrity**: Preserves all original information in structured format
5. **Time Savings**: Processes complex reports in seconds vs. manual hours

This tool transforms **unstructured financial data** into **analysis-ready tabular format** regardless of the source system's reporting style!

📝 Technical Details
Supported Systems:

    SAP Business One

    QuickBooks

    MYOB

    Custom accounting systems

    Any Excel-based financial reports

Dependencies:

    Python 3.6+

    pandas (data processing)

    openpyxl (Excel file handling)

    tkinter (GUI interface)

File Handling:

    Processes files without modifying originals

    Creates new output files in user-selected locations

    Handles large files efficiently

🎉 Benefits
For Auditors:

    Time Savings: Reduces manual data cleaning from hours to minutes

    Consistency: Standardized output format across different clients

    Accuracy: Reduces human error in data extraction

For Accountants:

    Analysis Ready: Clean data ready for pivot tables, charts, and reports

    Multi-System Support: Single tool for various accounting systems

    Flexibility: Adaptable to different report formats

Developed by Rashid Zainol | JANN Sarawak
Transforming complex financial data into actionable insights


