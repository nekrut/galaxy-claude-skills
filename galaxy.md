# Galaxy Bioinformatics Platform Integration

This skill enables interaction with Galaxy bioinformatics servers through direct API calls.

## Prerequisites

Before using Galaxy commands, you need:
- A Galaxy server URL (e.g., `https://usegalaxy.org`)
- A valid API key from your Galaxy account (get it from User > Preferences > Manage API Key)

Store these as environment variables:
```bash
export GALAXY_URL="https://usegalaxy.org"
export GALAXY_API_KEY="your_api_key_here"
```

## Learning Resources

**Galaxy Training Network**: https://training.galaxyproject.org/

The Galaxy Training Network (GTN) provides extensive tutorials, workflows, and usage patterns for Galaxy. When helping users with Galaxy tasks, Claude should reference GTN materials for:
- Domain-specific analysis workflows (genomics, proteomics, climate science, etc.)
- Best practices for tool selection and parameter configuration
- Complete analysis pipelines with example data
- Tool-specific tutorials and troubleshooting guides

Browse GTN topics to find relevant tutorials that match the user's analysis goals.

## Core Capabilities

### 1. Connection and Server Info

**Test Connection and Get User Info:**
```bash
curl -s "${GALAXY_URL}/api/users/current" -H "x-api-key: ${GALAXY_API_KEY}"
```

**Get Server Information:**
```bash
# Get server version
curl -s "${GALAXY_URL}/api/version" -H "x-api-key: ${GALAXY_API_KEY}"

# Get server configuration
curl -s "${GALAXY_URL}/api/configuration" -H "x-api-key: ${GALAXY_API_KEY}"
```

### 2. History Management

**List All Histories:**
```bash
curl -s "${GALAXY_URL}/api/histories" -H "x-api-key: ${GALAXY_API_KEY}"
```

**Get Specific History Details:**
```bash
HISTORY_ID="your_history_id"
curl -s "${GALAXY_URL}/api/histories/${HISTORY_ID}" -H "x-api-key: ${GALAXY_API_KEY}"
```

**Create New History:**
```bash
curl -s -X POST "${GALAXY_URL}/api/histories" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Analysis History"}'
```

**List History Contents (Datasets):**
```bash
HISTORY_ID="your_history_id"
curl -s "${GALAXY_URL}/api/histories/${HISTORY_ID}/contents" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Get History Contents with Pagination and Ordering:**
```bash
# Get newest datasets first (most recent 25 items)
curl -s "${GALAXY_URL}/api/datasets?history_id=${HISTORY_ID}&order=create_time-dsc&limit=25&offset=0" \
  -H "x-api-key: ${GALAXY_API_KEY}"

# Order options:
# - create_time-dsc: newest first
# - create_time-asc: oldest first
# - hid-asc: history ID ascending
# - hid-dsc: history ID descending
# - name-asc: alphabetical by name
# - update_time-dsc: most recently modified first
```

### 3. Dataset Operations

**Get Dataset Details:**
```bash
DATASET_ID="your_dataset_id"
curl -s "${GALAXY_URL}/api/datasets/${DATASET_ID}" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Download Dataset:**
```bash
DATASET_ID="your_dataset_id"
curl -s "${GALAXY_URL}/api/datasets/${DATASET_ID}/display" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -o output_file.txt
```

**Get Dataset Preview (first lines):**
```bash
# Get peek/preview of dataset content
DATASET_ID="your_dataset_id"
HISTORY_ID="your_history_id"
curl -s "${GALAXY_URL}/api/histories/${HISTORY_ID}/contents/${DATASET_ID}" \
  -H "x-api-key: ${GALAXY_API_KEY}" | jq -r '.peek'
```

**Upload File to Galaxy:**
```bash
HISTORY_ID="your_history_id"
FILE_PATH="/path/to/your/file.txt"

curl -s -X POST "${GALAXY_URL}/api/tools" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"tool_id\": \"upload1\",
    \"history_id\": \"${HISTORY_ID}\",
    \"inputs\": {
      \"files_0|file_data\": \"$(cat ${FILE_PATH} | base64)\",
      \"files_0|NAME\": \"$(basename ${FILE_PATH})\"
    }
  }"
```

### 4. Tool Operations

**Search for Tools:**
```bash
SEARCH_QUERY="fastqc"
curl -s "${GALAXY_URL}/api/tools?name=${SEARCH_QUERY}" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Get Tool Details:**
```bash
TOOL_ID="toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.73"
curl -s "${GALAXY_URL}/api/tools/${TOOL_ID}" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Get Tool Input Schema (with I/O details):**
```bash
TOOL_ID="your_tool_id"
curl -s "${GALAXY_URL}/api/tools/${TOOL_ID}?io_details=true" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Run a Tool:**
```bash
HISTORY_ID="your_history_id"
TOOL_ID="your_tool_id"
DATASET_ID="input_dataset_id"

curl -s -X POST "${GALAXY_URL}/api/tools" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"tool_id\": \"${TOOL_ID}\",
    \"history_id\": \"${HISTORY_ID}\",
    \"inputs\": {
      \"input\": {
        \"src\": \"hda\",
        \"id\": \"${DATASET_ID}\"
      }
    }
  }"
```

**Get Tool Panel (Toolbox Structure):**
```bash
curl -s "${GALAXY_URL}/api/tools?in_panel=true" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

### 5. Job Operations

**Get Job Details:**
```bash
JOB_ID="your_job_id"
curl -s "${GALAXY_URL}/api/jobs/${JOB_ID}" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Get Dataset Provenance (Find Creating Job):**
```bash
HISTORY_ID="your_history_id"
DATASET_ID="your_dataset_id"
curl -s "${GALAXY_URL}/api/histories/${HISTORY_ID}/contents/${DATASET_ID}/provenance" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**List All Jobs:**
```bash
curl -s "${GALAXY_URL}/api/jobs" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

### 6. Workflow Operations

**List Available Workflows:**
```bash
curl -s "${GALAXY_URL}/api/workflows" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Get Workflow Details:**
```bash
WORKFLOW_ID="your_workflow_id"
curl -s "${GALAXY_URL}/api/workflows/${WORKFLOW_ID}" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Import Workflow from JSON:**
```bash
curl -s -X POST "${GALAXY_URL}/api/workflows" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @workflow_definition.json
```

**Invoke (Run) Workflow:**
```bash
WORKFLOW_ID="your_workflow_id"
HISTORY_ID="your_history_id"
INPUT_DATASET_ID="your_input_dataset_id"

curl -s -X POST "${GALAXY_URL}/api/workflows/${WORKFLOW_ID}/invocations" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"history_id\": \"${HISTORY_ID}\",
    \"inputs\": {
      \"0\": {
        \"id\": \"${INPUT_DATASET_ID}\",
        \"src\": \"hda\"
      }
    }
  }"
```

**Get Workflow Invocations:**
```bash
# List all invocations
curl -s "${GALAXY_URL}/api/invocations" \
  -H "x-api-key: ${GALAXY_API_KEY}"

# Get specific invocation details
INVOCATION_ID="your_invocation_id"
curl -s "${GALAXY_URL}/api/invocations/${INVOCATION_ID}" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

**Cancel Workflow Invocation:**
```bash
INVOCATION_ID="your_invocation_id"
curl -s -X DELETE "${GALAXY_URL}/api/invocations/${INVOCATION_ID}" \
  -H "x-api-key: ${GALAXY_API_KEY}"
```

### 7. IWC (Intergalactic Workflow Commission) Integration

**Search IWC Workflow Registry:**
```bash
# Get all workflows from IWC
curl -s "https://iwc.galaxyproject.org/workflow_manifest.json" | jq '.'

# Search for specific workflows (using jq to filter)
SEARCH_TERM="chip-seq"
curl -s "https://iwc.galaxyproject.org/workflow_manifest.json" | \
  jq --arg term "$SEARCH_TERM" '[.[] | .workflows[]? | select(.definition.name | ascii_downcase | contains($term))]'
```

**Import Workflow from IWC:**
```bash
# First, get the workflow definition from IWC
TRS_ID="#workflow/github.com/iwc-workflows/chipseq-pe/main"
curl -s "https://iwc.galaxyproject.org/workflow_manifest.json" | \
  jq --arg trs "$TRS_ID" '[.[] | .workflows[]? | select(.trsID == $trs)][0].definition' > /tmp/workflow.json

# Then import to your Galaxy instance
curl -s -X POST "${GALAXY_URL}/api/workflows" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @/tmp/workflow.json
```

## Common Workflows

### Complete Analysis Example: Quality Check a FASTQ File

```bash
# 1. Create a new history
HISTORY_ID=$(curl -s -X POST "${GALAXY_URL}/api/histories" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name": "FASTQ Quality Check"}' | jq -r '.id')

echo "Created history: ${HISTORY_ID}"

# 2. Upload FASTQ file
UPLOAD_RESULT=$(curl -s -X POST "${GALAXY_URL}/api/tools" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -F "tool_id=upload1" \
  -F "history_id=${HISTORY_ID}" \
  -F "files_0|file_data=@/path/to/reads.fastq.gz")

DATASET_ID=$(echo "$UPLOAD_RESULT" | jq -r '.outputs[0].id')
echo "Uploaded dataset: ${DATASET_ID}"

# 3. Search for FastQC tool
FASTQC_TOOL=$(curl -s "${GALAXY_URL}/api/tools?name=fastqc" \
  -H "x-api-key: ${GALAXY_API_KEY}" | jq -r '.[0].id')

echo "Using FastQC tool: ${FASTQC_TOOL}"

# 4. Run FastQC
JOB_RESULT=$(curl -s -X POST "${GALAXY_URL}/api/tools" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"tool_id\": \"${FASTQC_TOOL}\",
    \"history_id\": \"${HISTORY_ID}\",
    \"inputs\": {
      \"input_file\": {
        \"src\": \"hda\",
        \"id\": \"${DATASET_ID}\"
      }
    }
  }")

echo "Started FastQC job"
echo "$JOB_RESULT" | jq '.'
```

### Check Job Status and Download Results

```bash
# Get the output dataset from job result
OUTPUT_DATASET_ID=$(echo "$JOB_RESULT" | jq -r '.outputs[0].id')

# Poll dataset status until complete
while true; do
  STATE=$(curl -s "${GALAXY_URL}/api/datasets/${OUTPUT_DATASET_ID}" \
    -H "x-api-key: ${GALAXY_API_KEY}" | jq -r '.state')

  echo "Dataset state: ${STATE}"

  if [ "$STATE" = "ok" ]; then
    echo "Analysis complete!"
    break
  elif [ "$STATE" = "error" ]; then
    echo "Analysis failed!"
    break
  fi

  sleep 5
done

# Download the results
curl -s "${GALAXY_URL}/api/datasets/${OUTPUT_DATASET_ID}/display" \
  -H "x-api-key: ${GALAXY_API_KEY}" \
  -o fastqc_report.html
```

## Helper Functions

### Extract IDs from JSON Responses

```bash
# Get history ID by name
get_history_id_by_name() {
  local name="$1"
  curl -s "${GALAXY_URL}/api/histories" \
    -H "x-api-key: ${GALAXY_API_KEY}" | \
    jq -r --arg name "$name" '.[] | select(.name == $name) | .id'
}

# Get most recent dataset in history
get_latest_dataset() {
  local history_id="$1"
  curl -s "${GALAXY_URL}/api/histories/${history_id}/contents" \
    -H "x-api-key: ${GALAXY_API_KEY}" | \
    jq -r 'sort_by(.create_time) | .[-1].id'
}

# Wait for dataset to complete
wait_for_dataset() {
  local dataset_id="$1"
  while true; do
    state=$(curl -s "${GALAXY_URL}/api/datasets/${dataset_id}" \
      -H "x-api-key: ${GALAXY_API_KEY}" | jq -r '.state')

    if [ "$state" = "ok" ] || [ "$state" = "error" ]; then
      echo "$state"
      break
    fi
    sleep 5
  done
}
```

## Error Handling

Common HTTP status codes and their meanings:

- **401 Unauthorized**: Invalid or missing API key
- **403 Forbidden**: Valid API key but insufficient permissions
- **404 Not Found**: Resource (history, dataset, tool) doesn't exist
- **500 Server Error**: Galaxy server issue - check server logs

### Debug Mode

Add `-v` flag to curl commands for verbose output:
```bash
curl -v "${GALAXY_URL}/api/histories" -H "x-api-key: ${GALAXY_API_KEY}"
```

## Best Practices

1. **Always validate IDs**: Ensure history_id, dataset_id, etc. are valid hexadecimal strings (typically 16 characters)

2. **Check dataset states**: Datasets can be in states: `new`, `queued`, `running`, `ok`, `error`, `paused`, `deleted`

3. **Use pagination**: For large result sets, use `limit` and `offset` parameters

4. **Handle async operations**: Tool execution and workflows are asynchronous - poll for completion

5. **Store credentials securely**: Use environment variables, never hardcode API keys

6. **URL formatting**: Ensure GALAXY_URL ends with `/` or adjust API paths accordingly

## Reference Documentation

- Galaxy API Docs: https://docs.galaxyproject.org/en/master/api/
- BioBlend (Python library): https://bioblend.readthedocs.io/
- IWC Workflows: https://iwc.galaxyproject.org/
- Galaxy Training: https://training.galaxyproject.org/

## Dataset Source Types

When referencing datasets in tool/workflow inputs, use these `src` values:
- `hda`: HistoryDatasetAssociation (regular dataset in history)
- `hdca`: HistoryDatasetCollectionAssociation (dataset collection)
- `ldda`: LibraryDatasetDatasetAssociation (library dataset)
- `ld`: LibraryDataset

## Instructions for Claude

When the user invokes this skill:

1. Ask for Galaxy URL and API key if not already in environment
2. Test connection with a simple API call first
3. Use jq for JSON parsing when available
4. Show clear progress messages for long-running operations
5. Extract and display relevant information from JSON responses
6. Handle errors gracefully with helpful suggestions
7. For complex workflows, break into clear numbered steps
8. Always verify IDs before using them in subsequent calls
9. Provide the actual curl commands so users can reproduce results
10. When uploading files, verify the file path exists first
11. **Reference Galaxy Training Network (https://training.galaxyproject.org/)** when users ask about:
    - Analysis workflows for specific domains (RNA-seq, ChIP-seq, variant calling, etc.)
    - Best practices for bioinformatics analyses
    - Tool recommendations and parameter settings
    - Complete analysis pipelines with example datasets
12. **Suggest relevant GTN tutorials** that match the user's analysis goals

Remember: All Galaxy operations are asynchronous. Always check job/dataset states before assuming completion.
