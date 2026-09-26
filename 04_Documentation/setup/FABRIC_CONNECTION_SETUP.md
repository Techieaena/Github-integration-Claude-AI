# Fabric & Kagglehub Connection Setup Guide

## 🔐 Step 1: Login to Fabric & Get Credentials

### **A. Go to Fabric Portal**
```
URL: https://fabric.microsoft.com
```

### **B. Login with Microsoft Account**
1. Click **"Sign in"**
2. Enter your **Microsoft Email** (corporate or personal)
3. Enter **Password**
4. Complete Multi-Factor Authentication if prompted
5. You're now in Fabric!

---

## 📍 Step 2: Collect Fabric Workspace Details

### **Get Workspace Information:**

1. In Fabric, look for **Workspace Name** (top-left corner)
2. Click on **Settings** (gear icon)
3. Go to **Workspace Settings**
4. Copy these values:
   ```
   Workspace Name: _________________ (e.g., fabricaena)
   Workspace ID: _________________ (shown in URL or settings)
   ```

### **Get Lakehouse Details:**

1. In Workspace, click on your **Lakehouse** (e.g., githubclaude)
2. Look at the URL: `https://fabric.microsoft.com/workspaces/[WORKSPACE_ID]/lakehouses/[LAKEHOUSE_ID]`
3. Copy:
   ```
   Lakehouse Name: _________________ (e.g., githubclaude)
   Lakehouse ID: _________________ (from URL)
   ```

---

## 🔑 Step 3: Get Azure Tenant & Subscription IDs

### **Go to Azure Portal**
```
URL: https://portal.azure.com
```

### **Get Tenant ID:**
1. Click on **Azure Active Directory** (from menu)
2. Click on **Properties**
3. Copy:
   ```
   Tenant ID (Directory ID): _________________ 
   (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
   ```

### **Get Subscription ID:**
1. Go to **Subscriptions** (search at top)
2. Select your subscription
3. Copy:
   ```
   Subscription ID: _________________
   (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
   ```

---

## 📊 Step 4: Get Kagglehub API Credentials

### **Go to Kaggle**
```
URL: https://kaggle.com/settings/account
```

### **Login to Kaggle**
1. Click **Sign in** (top-right)
2. Enter **Email/Username**
3. Enter **Password**
4. Complete verification if needed

### **Get API Key:**
1. On account page, scroll to **API** section
2. Click **"Create New API Token"**
   - This downloads a file: `kaggle.json`
3. Open the file with notepad
4. Copy these values:
   ```
   Username: _________________ (username field)
   API Key: _________________ (key field, looks like random string)
   ```

### **Setup Kaggle Credentials:**
1. Save the `kaggle.json` file to:
   ```
   C:\Users\admin\.kaggle\kaggle.json
   ```
2. Or on Mac/Linux:
   ```
   ~/.kaggle/kaggle.json
   ```

---

## 📋 Credentials Summary Form

**Fill this in once you've collected everything:**

```
═══════════════════════════════════════════════════════════════
                    FABRIC CREDENTIALS
═══════════════════════════════════════════════════════════════

Tenant ID:              _________________________________
Subscription ID:        _________________________________
Workspace Name:         _________________________________
Workspace ID:           _________________________________
Lakehouse Name:         _________________________________
Lakehouse ID:           _________________________________

═══════════════════════════════════════════════════════════════
                   KAGGLEHUB CREDENTIALS
═══════════════════════════════════════════════════════════════

Kaggle Username:        _________________________________
Kaggle API Key:         _________________________________

═══════════════════════════════════════════════════════════════
```

---

## ✅ Step 5: Configure MCP Servers

Once you have credentials, I'll:

1. **Update medallion_pipeline.py:**
   ```python
   TENANT_ID = "[Your Tenant ID]"
   WORKSPACE_ID = "[Your Workspace ID]"
   LAKEHOUSE_ID = "[Your Lakehouse ID]"
   LAKEHOUSE_NAME = "[Your Lakehouse Name]"
   ```

2. **Setup Kaggle credentials** in:
   ```
   C:\Users\admin\.kaggle\kaggle.json
   ```
   Content:
   ```json
   {
     "username": "[Your Username]",
     "key": "[Your API Key]"
   }
   ```

3. **Restart Claude Code** to reconnect MCP servers

---

## 🚀 Ready?

**Reply with:**
1. ✅ Tenant ID
2. ✅ Subscription ID  
3. ✅ Workspace Name
4. ✅ Workspace ID
5. ✅ Lakehouse Name
6. ✅ Lakehouse ID
7. ✅ Kaggle Username
8. ✅ Kaggle API Key

I'll then configure everything automatically!

---

## ⚠️ Security Notes

- **Never share your API Keys publicly**
- Keep `kaggle.json` private (already in .gitignore)
- Use service principal for production (I can help set that up)
- Credentials are for YOUR Fabric workspace only

---

## 🆘 Troubleshooting

**Can't find Workspace ID?**
- URL: `https://fabric.microsoft.com/workspaces/[THIS_IS_WORKSPACE_ID]/...`

**Can't create Kaggle token?**
- Ensure you're logged in to Kaggle
- Check email verification is complete
- Try creating token again

**Permission denied errors?**
- Ensure you have contributor/admin access to Fabric workspace
- Ensure Kaggle API is enabled
- Check Azure subscription permissions

---

**Status:** 🔴 Waiting for credentials  
**Next Step:** Provide the 8 credential values above
