# CloudSync Code Examples

## Python SDK

### Basic Authentication
```python
from cloudsync import CloudSyncClient

# Initialize client
client = CloudSyncClient(api_key="YOUR_API_KEY")

# Or with environment variable
# export CLOUDSYNC_API_KEY=YOUR_API_KEY
client = CloudSyncClient()
```

### File Upload
```python
# Simple upload
file_info = client.upload_file("/path/to/document.pdf")
print(f"Uploaded file ID: {file_info.id}")

# Upload with metadata
file_info = client.upload_file(
    "/path/to/document.pdf",
    folder_id="FOLDER_123",
    tags=["important", "contracts"],
    description="Q4 2024 contract"
)

# Upload with progress callback
def progress_callback(bytes_uploaded, total_bytes):
    percent = (bytes_uploaded / total_bytes) * 100
    print(f"Upload progress: {percent:.1f}%")

client.upload_file(
    "/path/to/large-file.zip",
    progress_callback=progress_callback
)
```

### File Download
```python
# Download to file
client.download_file("FILE_ID", "/path/to/save/document.pdf")

# Download to memory
file_content = client.download_file_content("FILE_ID")
with open("output.pdf", "wb") as f:
    f.write(file_content)

# Stream download for large files
with client.stream_download("FILE_ID") as stream:
    with open("large-file.zip", "wb") as f:
        for chunk in stream:
            f.write(chunk)
```

### Sync Operations
```python
from cloudsync import SyncManager

# Initialize sync manager
sync = SyncManager(client)

# Add folder to sync
sync.add_folder(
    local_path="/Users/john/Documents/Projects",
    remote_folder_id="FOLDER_456",
    bidirectional=True
)

# Start syncing
sync.start()

# Check sync status
status = sync.get_status()
print(f"Files synced: {status.synced_count}")
print(f"Pending uploads: {status.pending_uploads}")

# Handle conflicts
conflicts = sync.get_conflicts()
for conflict in conflicts:
    # Resolve using local version
    sync.resolve_conflict(conflict.file_id, strategy="local")
```

## JavaScript/Node.js

### Setup and Authentication
```javascript
const CloudSync = require('@cloudsync/sdk');

// Initialize client
const client = new CloudSync({
  apiKey: process.env.CLOUDSYNC_API_KEY
});

// With async/await
async function setupClient() {
  const client = new CloudSync({
    apiKey: 'YOUR_API_KEY',
    apiUrl: 'https://api.cloudsync.io/v2' // optional
  });
  
  // Verify authentication
  const user = await client.auth.getCurrentUser();
  console.log(`Authenticated as: ${user.email}`);
  
  return client;
}
```

### File Operations
```javascript
// Upload file
async function uploadFile() {
  try {
    const file = await client.files.upload({
      path: './document.pdf',
      folderId: 'FOLDER_123',
      onProgress: (progress) => {
        console.log(`Upload progress: ${progress.percent}%`);
      }
    });
    
    console.log(`File uploaded: ${file.id}`);
  } catch (error) {
    console.error('Upload failed:', error.message);
  }
}

// List files with pagination
async function listFiles() {
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const response = await client.files.list({
      folderId: 'FOLDER_123',
      page: page,
      limit: 50
    });
    
    response.files.forEach(file => {
      console.log(`${file.name} (${file.size} bytes)`);
    });
    
    hasMore = page < response.pagination.totalPages;
    page++;
  }
}

// Download with error handling
async function downloadFile(fileId) {
  try {
    await client.files.download(fileId, {
      destination: './downloads/file.pdf',
      verifyChecksum: true
    });
    console.log('Download completed');
  } catch (error) {
    if (error.code === 'CHECKSUM_MISMATCH') {
      console.error('File integrity check failed');
    } else {
      console.error('Download error:', error);
    }
  }
}
```

### Real-time Sync
```javascript
const { SyncClient } = require('@cloudsync/sync');

// Initialize sync client
const sync = new SyncClient(client);

// Setup bidirectional sync
sync.addSyncFolder({
  localPath: '/Users/john/CloudSync',
  remoteFolderId: 'ROOT',
  excludePatterns: ['*.tmp', 'node_modules/**']
});

// Listen for sync events
sync.on('file:uploaded', (file) => {
  console.log(`Uploaded: ${file.name}`);
});

sync.on('file:downloaded', (file) => {
  console.log(`Downloaded: ${file.name}`);
});

sync.on('conflict', (conflict) => {
  console.log(`Conflict detected: ${conflict.file.name}`);
  // Auto-resolve using newer file
  sync.resolveConflict(conflict.id, 'newer');
});

// Start syncing
sync.start();
```

## Go SDK

### Client Setup
```go
package main

import (
    "fmt"
    "log"
    "github.com/cloudsync/go-sdk"
)

func main() {
    // Create client
    client, err := cloudsync.NewClient(
        cloudsync.WithAPIKey("YOUR_API_KEY"),
        cloudsync.WithTimeout(30 * time.Second),
    )
    if err != nil {
        log.Fatal(err)
    }

    // Verify connection
    user, err := client.GetCurrentUser()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Authenticated as: %s\n", user.Email)
}
```

### Concurrent Uploads
```go
func uploadFiles(client *cloudsync.Client, filePaths []string) error {
    var wg sync.WaitGroup
    errors := make(chan error, len(filePaths))
    
    // Limit concurrent uploads
    semaphore := make(chan struct{}, 5)
    
    for _, path := range filePaths {
        wg.Add(1)
        go func(p string) {
            defer wg.Done()
            
            semaphore <- struct{}{}
            defer func() { <-semaphore }()
            
            file, err := client.UploadFile(p, &cloudsync.UploadOptions{
                FolderID: "FOLDER_123",
            })
            
            if err != nil {
                errors <- fmt.Errorf("failed to upload %s: %w", p, err)
                return
            }
            
            fmt.Printf("Uploaded: %s (ID: %s)\n", file.Name, file.ID)
        }(path)
    }
    
    wg.Wait()
    close(errors)
    
    // Check for errors
    for err := range errors {
        if err != nil {
            return err
        }
    }
    
    return nil
}
```

## Ruby SDK

### Basic Usage
```ruby
require 'cloudsync'

# Configure client
client = CloudSync::Client.new(
  api_key: ENV['CLOUDSYNC_API_KEY'],
  logger: Logger.new(STDOUT)
)

# Upload with metadata
file = client.files.upload(
  path: '/path/to/file.pdf',
  folder_id: 'FOLDER_123',
  metadata: {
    author: 'John Doe',
    department: 'Engineering',
    project: 'Project Alpha'
  }
)

puts "Uploaded file: #{file.id}"

# Batch operations
files_to_upload = Dir.glob('/documents/*.pdf')
results = client.files.batch_upload(files_to_upload) do |file, result|
  if result.success?
    puts "✓ #{file}"
  else
    puts "✗ #{file}: #{result.error}"
  end
end
```

## Error Handling Best Practices

### Python
```python
from cloudsync.exceptions import (
    AuthenticationError,
    RateLimitError,
    NetworkError,
    StorageQuotaError
)

def safe_upload(client, file_path):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            return client.upload_file(file_path)
        except RateLimitError as e:
            wait_time = e.retry_after or (retry_delay * (2 ** attempt))
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        except NetworkError:
            if attempt < max_retries - 1:
                print(f"Network error. Retrying ({attempt + 1}/{max_retries})...")
                time.sleep(retry_delay * (2 ** attempt))
            else:
                raise
        except StorageQuotaError:
            print("Storage quota exceeded. Please upgrade your plan.")
            raise
        except AuthenticationError:
            print("Authentication failed. Please check your API key.")
            raise
```

### JavaScript
```javascript
// Exponential backoff with jitter
async function uploadWithRetry(client, filePath, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await client.files.upload({ path: filePath });
    } catch (error) {
      if (error.code === 'RATE_LIMIT') {
        const delay = error.retryAfter || Math.pow(2, attempt) * 1000;
        const jitter = Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay + jitter));
      } else if (error.code === 'NETWORK_ERROR' && attempt < maxRetries - 1) {
        continue;
      } else {
        throw error;
      }
    }
  }
}
```

## Webhook Integration

### Express.js Webhook Handler
```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// Verify webhook signature
function verifyWebhookSignature(payload, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return hash === signature;
}

// Webhook endpoint
app.post('/webhooks/cloudsync', (req, res) => {
  const signature = req.headers['x-cloudsync-signature'];
  const payload = JSON.stringify(req.body);
  
  if (!verifyWebhookSignature(payload, signature, process.env.WEBHOOK_SECRET)) {
    return res.status(401).send('Invalid signature');
  }
  
  const { event, data } = req.body;
  
  switch (event) {
    case 'file.created':
      console.log(`New file: ${data.file.name}`);
      // Process new file
      break;
    case 'file.updated':
      console.log(`File updated: ${data.file.name}`);
      // Handle file update
      break;
    case 'file.deleted':
      console.log(`File deleted: ${data.file_id}`);
      // Handle deletion
      break;
    case 'sync.completed':
      console.log(`Sync completed for folder: ${data.folder_id}`);
      // Post-sync processing
      break;
  }
  
  res.status(200).send('OK');
});

app.listen(3000, () => {
  console.log('Webhook server listening on port 3000');
});
```