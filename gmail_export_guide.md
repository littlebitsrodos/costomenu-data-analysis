# 📥 CEO Guide: How to Export Invoices (Method 2: Google Takeout)

**Goal:** Export all "Pro-Forma Receipts" and Invoices to a single file using Google's official tool.

---

### Step 1: Create the "CostoInvoices" Label
*We need to group all these emails under one label so Google Takeout knows what to grab.*

1.  **Open Gmail** on your computer.
2.  **Paste this Search** into the search bar (matches the document you shared):
    ```text
    "Λεπτομέρειες Προ-Φόρμας Απόδειξης" OR "CostoMenu" has:attachment
    ```
3.  **Select All:**
    *   Click the **checkbox** at the very top left (above the first email) to select the emails on the current page.
    *   **Crucial:** A blue message will appear saying *"All 50 conversations on this page are selected. Select all XXX conversations in Search Results"*. **Click that link.**
4.  **Apply Label:**
    *   Click the **Label Icon** (🏷️) in the toolbar.
    *   Type **CostoInvoices** and click "(Create new)".
    *   Click **OK**.

*(Now all present and future invoices have this tag)*

---

### Step 2: Google Takeout (The Export)
1.  Go to **[takeout.google.com](https://takeout.google.com)**.
2.  **Deselect All** (Click the link at the top of the list).
3.  Scroll down to **Mail** and check the box [x].
4.  Click on the button that says **"All Mail data included"**.
    *   Uncheck "Include all messages in Mail".
    *   Scroll down and **Check ONLY "CostoInvoices"**.
    *   Click **OK**.
5.  Scroll to the very bottom and click **Next step**.
6.  **Destination:** "Send download link via email".
7.  **Frequency:** "Export once".
8.  **File type:** ".zip".
9.  Click **Create export**.

---

### Step 3: Dropbox
1.  Google will email you when the ZIP is ready (usually takes 5-10 minutes).
2.  Download the ZIP.
3.  **Drag and drop** that ZIP file into the `invoices_dropzone` folder we created.
4.  We will handle the rest!
