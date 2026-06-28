# AWS S3 File Management System ☁️

A professional, production-quality, and modern AWS S3 File Management dashboard built using Python, Streamlit, and `boto3`. This project provides a clean user interface to manage S3 bucket operations, suitable for college projects or simple production bucket explorer systems.

## Features

- **📊 Dashboard Statistics**: Displays real-time metrics showing total file count and storage space consumed (formatted in B/KB/MB/GB).
- **📤 Upload Portal**: Drag and drop file uploader. Prevents accidental file overwriting with automatic duplicate checks.
- **🗂️ Search & Sorting**: Real-time search filter and sorting options (Sort by Name, Size, or Last Modified).
- **📝 Native File Type Emojis**: Automatically assigns relevant emojis based on file extensions.
- **📥 Download Mechanism**: Fetches files in-memory from AWS S3 only on demand, saving bandwidth.
- **🗑️ Safe Deletion**: Prompts with confirmation prompts before deleting S3 objects.
- **🔒 Credentials Separation**: Strict isolation of credentials through environment configurations (`.env`).
- **🛡️ Error Handling**: Safe validation for missing environment variables, AWS permission limits (403), missing buckets (404), and connectivity loss.

---

## Project Structure

```text
Testing-S3/
│
├── app.py                  # Main Streamlit Frontend Dashboard
├── s3_utils.py             # S3 backend interaction functions (boto3)
├── requirements.txt        # Project package dependencies
├── .env                    # Credentials configuration template (ignored in Git)
├── README.md               # Extensive guide and documentation
└── assets/
      └── logo.png          # Sidebar branding logo
```

---

## Installation & Setup

Follow these steps to configure the project on your local machine:

### 1. Clone or Copy the Workspace
Place the files into a single directory on your machine (e.g., `Testing-S3`).

### 2. Create a Virtual Environment
It is highly recommended to isolate your project using a virtual environment:

**On Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

---

## AWS Configuration

To interact with AWS, you need to create an S3 bucket and acquire API credentials.

### Step 1: Create an S3 Bucket
1. Log in to the [AWS Management Console](https://aws.amazon.com/console/).
2. Search for and select **S3** under services.
3. Click **Create bucket**.
4. Give it a globally unique name (e.g., `college-assignment-s3-bucket`).
5. Choose your target **AWS Region** (e.g., `us-east-1` or `ap-south-1`).
6. Leave other configurations as default and click **Create bucket**.

### Step 2: Create IAM User & Permissions Policy
1. Search for and select **IAM** (Identity and Access Management) in the AWS Console.
2. Click **Users** in the sidebar, then click **Create user**.
3. Choose a username (e.g., `s3-manager-app`).
4. On the permissions setup screen, choose **Attach policies directly**.
5. You can attach the standard AWS-managed policy `AmazonS3FullAccess`.
   
   *(Alternative) For better security practice, click **Create policy**, paste the following JSON configuration restricting access to only your bucket, and attach it to the user:*
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:ListBucket",
                   "s3:GetBucketLocation"
               ],
               "Resource": "arn:aws:s3:::your-bucket-name"
           },
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:DeleteObject"
               ],
               "Resource": "arn:aws:s3:::your-bucket-name/*"
           }
       ]
   }
   ```
6. Complete user creation.

### Step 3: Generate Access Keys
1. Go back to the **IAM Users** list and select your newly created user.
2. Navigate to the **Security credentials** tab.
3. Scroll down to the **Access keys** section and click **Create access key**.
4. Choose **Application running outside AWS** and proceed.
5. Copy your **Access Key ID** and **Secret Access Key** immediately. *Note: Secret key is only visible once.*

---

## Configure `.env` File

Open the `.env` file in the root folder of the project. Replace the empty placeholders with your AWS details:

```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
BUCKET_NAME=college-assignment-s3-bucket
```

> [!WARNING]
> Keep your Access Keys confidential. Never commit your `.env` file to a public repository (GitHub/GitLab).

---

## Running the Application

After updating the `.env` file, launch the dashboard:

```bash
streamlit run app.py
```

The app will compile and automatically launch in your default web browser (typically at `http://localhost:8501`).

---

## Screenshots Placeholders

Once running, the application will display:
1. **Disconnected State**: Instructions detailing how to verify credentials.
2. **Dashboard Main View**: High-level metrics row, upload container, object list table with file extensions logos, download selections, and deletion modules.
