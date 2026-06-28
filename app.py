import streamlit as st
import pandas as pd
import os
from typing import Any
from s3_utils import (
    create_s3_client,
    verify_bucket_existence,
    upload_file,
    list_files,
    download_file,
    delete_file,
    get_bucket_size,
    format_size,
    get_file_icon
)

# Page configuration
st.set_page_config(
    page_title="AWS S3 Bucket Manager",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS styling compatible with light and dark modes
st.markdown("""
<style>
    /* Styling adjustments */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
    }
    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    .metric-container {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        background: rgba(128, 128, 128, 0.12);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2b78e4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #888888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 15px;
        text-align: center;
        width: 100%;
    }
    .status-online {
        background-color: rgba(40, 167, 69, 0.15);
        color: #28a745;
        border: 1px solid #28a745;
    }
    .status-offline {
        background-color: rgba(220, 53, 69, 0.15);
        color: #dc3545;
        border: 1px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State values for reactive updates
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0

# Load environment configuration variables
bucket_name = os.getenv("BUCKET_NAME", "").strip()
region_name = os.getenv("AWS_REGION", "").strip()

# Sidebar Configuration
with st.sidebar:
    # Display S3 branding logo if available
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.title("☁️ S3 Cloud Manager")
        
    st.markdown("---")
    
    st.subheader("Configuration Status")
    
    # State tracking variables
    s3_client = None
    connected = False
    connection_error = None
    
    # Validate environment credentials presence
    aws_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    
    has_creds = True
    if not aws_key or not aws_secret or not region_name or not bucket_name:
        has_creds = False
        connection_error = "Missing AWS Configuration. Please configure your `.env` file."
        
    if has_creds:
        try:
            s3_client = create_s3_client()
            verify_bucket_existence(s3_client, bucket_name)
            connected = True
        except Exception as e:
            connected = False
            connection_error = str(e)
            
    if connected:
        st.markdown('<div class="status-badge status-online">🟢 CONNECTED TO AWS</div>', unsafe_allow_html=True)
        st.markdown(f"**Bucket:** `{bucket_name}`")
        st.markdown(f"**Region:** `{region_name}`")
    else:
        st.markdown('<div class="status-badge status-offline">🔴 DISCONNECTED</div>', unsafe_allow_html=True)
        if connection_error:
            st.error(connection_error)
            
    st.markdown("---")
    
    # Refresh Button in Sidebar
    if st.button("🔄 Refresh Bucket Data", use_container_width=True, disabled=not connected):
        st.session_state.refresh_trigger += 1
        st.rerun()

# Main Header Container
st.markdown("""
<div class="main-header">
    <h1>AWS S3 Bucket Manager</h1>
    <p>Securely upload, list, download, and manage S3 resources via a streamlined console</p>
</div>
""", unsafe_allow_html=True)

# Helper function to get bucket list (cached or re-loaded based on trigger)
@st.cache_data(show_spinner=False)
def load_bucket_data(trigger_val: int, _client: Any, bucket: str):
    if not _client or not bucket:
        return [], 0, 0
    try:
        files = list_files(_client, bucket)
        total_files, total_size = get_bucket_size(_client, bucket)
        return files, total_files, total_size
    except Exception as e:
        st.error(f"Failed to fetch S3 data: {str(e)}")
        return [], 0, 0

# If disconnected, display credential help guide
if not connected:
    st.info("💡 **Welcome to the AWS S3 Bucket Manager!** To get started, follow these instructions to link your S3 bucket.")
    
    st.markdown("""
    ### Quick Setup Guide
    
    1. **Create S3 Bucket**: Log in to AWS S3 Console, create a new bucket, and take note of its name and AWS region.
    2. **Generate Access Keys**:
        - Go to the **IAM Console** in AWS.
        - Select/create an IAM user with `AmazonS3FullAccess` or restricted S3 policies.
        - Create an Access Key to obtain an **Access Key ID** and **Secret Access Key**.
    3. **Configure the Environment**:
        - Locate the `.env` file in the project's root folder.
        - Enter your AWS configurations exactly like this:
          ```env
          AWS_ACCESS_KEY_ID=your_access_key_id
          AWS_SECRET_ACCESS_KEY=your_secret_access_key
          AWS_REGION=your_aws_region
          BUCKET_NAME=your_bucket_name
          ```
    4. **Reload**: Save the file changes and click **Refresh Bucket Data** in the sidebar.
    """)
    st.warning("⚠️ Credentials are currently empty. Fill in the `.env` configurations to unlock AWS integration.")
    st.stop()

# Fetch active bucket contents
with st.spinner("Loading bucket statistics and objects..."):
    all_files, total_files_count, total_size_bytes = load_bucket_data(
        st.session_state.refresh_trigger, s3_client, bucket_name
    )

# Top Metrics Row
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{total_files_count}</div>
        <div class="metric-label">📁 Total Files</div>
    </div>
    """, unsafe_allow_html=True)
with col_m2:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{format_size(total_size_bytes)}</div>
        <div class="metric-label">💾 Storage Used</div>
    </div>
    """, unsafe_allow_html=True)
with col_m3:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{bucket_name}</div>
        <div class="metric-label">🪣 Active Bucket</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------
# SECTION 1: Upload File
# --------------------------------------------------
st.header("📤 Upload File")
uploaded_file = st.file_uploader("Choose a file to upload directly to S3", key="file_upload_input")

if uploaded_file is not None:
    filename = uploaded_file.name
    # Check if a file with the same name exists
    file_exists = filename in [f['Key'] for f in all_files]
    
    can_upload = True
    if file_exists:
        st.warning(f"⚠️ A file named `{filename}` already exists in this S3 bucket.")
        overwrite = st.checkbox("Do you want to overwrite this existing file?", value=False, key="overwrite_status")
        if not overwrite:
            can_upload = False
            st.info("ℹ️ Overwrite option must be checked to replace files with duplicate names.")
            
    if can_upload:
        if st.button("🚀 Upload to S3", use_container_width=True):
            try:
                with st.spinner(f"Uploading {filename} to AWS S3..."):
                    upload_file(s3_client, uploaded_file, filename, bucket_name)
                st.success(f"🎉 Success! `{filename}` uploaded successfully to `{bucket_name}`.")
                st.session_state.refresh_trigger += 1
                st.rerun()
            except Exception as e:
                st.error(f"❌ Upload failed: {str(e)}")

st.markdown("---")

# --------------------------------------------------
# SECTION 2: Bucket Objects
# --------------------------------------------------
st.header("🗂️ Bucket Objects")

if not all_files:
    st.info("📭 Your S3 bucket is empty. Upload a file above to display content.")
else:
    # Filtration, search, and sorting controls
    search_col, sort_col, order_col = st.columns([2, 1, 1])
    with search_col:
        search_query = st.text_input("🔍 Search files by name", "", placeholder="Type name to filter...")
    with sort_col:
        sort_by = st.selectbox("Sort list by", ["Name", "Size", "Date"])
    with order_col:
        sort_order = st.selectbox("Ordering style", ["Ascending", "Descending"])

    # Filter objects matching search query
    filtered_files = [f for f in all_files if search_query.lower() in f['Key'].lower()]

    # Sort objects according to selectbox settings
    reverse_sort = (sort_order == "Descending")
    if sort_by == "Name":
        filtered_files.sort(key=lambda x: x['Key'].lower(), reverse=reverse_sort)
    elif sort_by == "Size":
        filtered_files.sort(key=lambda x: x['Size'], reverse=reverse_sort)
    elif sort_by == "Date":
        filtered_files.sort(key=lambda x: x['LastModified'], reverse=reverse_sort)

    if not filtered_files:
        st.warning("🔍 No files match your query parameters.")
    else:
        # Create display dataframe
        table_data = []
        for file in filtered_files:
            table_data.append({
                "Icon": get_file_icon(file['Key']),
                "File Name": file['Key'],
                "Size": format_size(file['Size']),
                "Last Modified (UTC)": file['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
            })
            
        df = pd.DataFrame(table_data)
        
        # Display custom styled table
        st.dataframe(
            df,
            column_config={
                "Icon": st.column_config.TextColumn("Type", width="small"),
                "File Name": st.column_config.TextColumn("File Name"),
                "Size": st.column_config.TextColumn("Size"),
                "Last Modified (UTC)": st.column_config.TextColumn("Last Modified (UTC)")
            },
            hide_index=True,
            use_container_width=True
        )

st.markdown("---")

# --------------------------------------------------
# SECTION 3: Download Object
# --------------------------------------------------
st.header("📥 Download Object")

if not all_files:
    st.info("📭 No S3 objects available to download.")
else:
    file_names = [f['Key'] for f in all_files]
    selected_download = st.selectbox("Choose a file to download:", options=file_names, key="download_selector")
    
    if selected_download:
        dl_btn_col, dl_status_col = st.columns([1, 3])
        with dl_btn_col:
            if st.button("📥 Retrieve from S3", use_container_width=True):
                try:
                    with st.spinner(f"Retrieving '{selected_download}' from S3..."):
                        file_bytes = download_file(s3_client, bucket_name, selected_download)
                    st.session_state.dl_bytes = file_bytes
                    st.session_state.dl_name = selected_download
                    st.success("✅ File fetched!")
                except Exception as e:
                    st.error(f"❌ Retrieval failed: {str(e)}")
                    
        with dl_status_col:
            if "dl_bytes" in st.session_state and st.session_state.dl_name == selected_download:
                st.download_button(
                    label=f"💾 Save '{selected_download}' to local system",
                    data=st.session_state.dl_bytes,
                    file_name=st.session_state.dl_name,
                    mime="application/octet-stream",
                    use_container_width=True
                )

st.markdown("---")

# --------------------------------------------------
# SECTION 4: Delete Object
# --------------------------------------------------
st.header("🗑️ Delete Object")

if not all_files:
    st.info("📭 No S3 objects available to delete.")
else:
    file_names = [f['Key'] for f in all_files]
    selected_delete = st.selectbox("Choose a file to delete:", options=file_names, key="delete_selector")
    
    if selected_delete:
        confirm_key = f"confirm_del_{selected_delete}"
        if confirm_key not in st.session_state:
            st.session_state[confirm_key] = False
            
        if not st.session_state[confirm_key]:
            if st.button("❌ Delete Object", type="primary", use_container_width=True):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            st.warning(f"⚠️ **Are you sure you want to permanently delete `{selected_delete}` from S3?**")
            yes_btn, no_btn = st.columns(2)
            with yes_btn:
                if st.button("Yes, permanently delete", type="primary", use_container_width=True):
                    try:
                        with st.spinner("Deleting object..."):
                            delete_file(s3_client, bucket_name, selected_delete)
                        st.success(f"🎉 Successfully deleted `{selected_delete}`.")
                        st.session_state[confirm_key] = False
                        st.session_state.refresh_trigger += 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Deletion failed: {str(e)}")
            with no_btn:
                if st.button("Cancel & Go Back", use_container_width=True):
                    st.session_state[confirm_key] = False
                    st.rerun()
