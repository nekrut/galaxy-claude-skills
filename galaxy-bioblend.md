# Galaxy BioBlend Integration Skill

This skill enables interaction with Galaxy bioinformatics servers using BioBlend, the official Python library for Galaxy API.

## Prerequisites

**Install BioBlend:**
```bash
pip install bioblend
```

**Set up credentials:**
```bash
export GALAXY_URL="https://usegalaxy.org"
export GALAXY_API_KEY="your_api_key_here"
```

Get your API key from: User → Preferences → Manage API Key in your Galaxy instance.

## Learning Resources

**Galaxy Training Network**: https://training.galaxyproject.org/

The Galaxy Training Network (GTN) provides extensive tutorials, workflows, and usage patterns for Galaxy. When helping users with Galaxy tasks, Claude should reference GTN materials for:
- Domain-specific analysis workflows (genomics, proteomics, climate science, etc.)
- Best practices for tool selection and parameter configuration
- Complete analysis pipelines with example data
- Tool-specific tutorials and troubleshooting guides

Browse GTN topics to find relevant tutorials that match the user's analysis goals. Many GTN tutorials include API usage examples that complement this skill.

## Core Python Helper Template

All BioBlend operations follow this pattern:

```python
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json

# Connect to Galaxy
gi = GalaxyInstance(
    url=os.environ['GALAXY_URL'],
    key=os.environ['GALAXY_API_KEY']
)

# Your operation here
result = gi.histories.get_histories()

# Print formatted output
print(json.dumps(result, indent=2))
"
```

## 1. Connection and Server Info

### Test Connection
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
user = gi.users.get_current_user()
print(json.dumps(user, indent=2))
print(f\"\nConnected as: {user['email']}\")
"
```

### Get Server Information
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])

# Get version
version = gi.config.get_version()
print(f\"Galaxy version: {version['version_major']}.{version.get('version_minor', 0')}\")

# Get configuration
config = gi.config.get_config()
print(f\"Server brand: {config.get('brand', 'Galaxy')}\")
print(f\"User creation allowed: {config.get('allow_user_creation', False)}\")
print(f\"Quotas enabled: {config.get('enable_quotas', False)}\")
"
```

## 2. History Management

### List All Histories
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
histories = gi.histories.get_histories()

for h in histories:
    print(f\"{h['id']}: {h['name']} (updated: {h['update_time']})\")
"
```

### Get History Details
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
history_id = sys.argv[1] if len(sys.argv) > 1 else None

if not history_id:
    print('Usage: provide history_id as argument')
    sys.exit(1)

history = gi.histories.show_history(history_id)
print(json.dumps(history, indent=2))
" "${HISTORY_ID}"
```

### Create New History
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
name = sys.argv[1] if len(sys.argv) > 1 else 'New History'

history = gi.histories.create_history(name)
print(f\"Created history: {history['id']}\")
print(f\"Name: {history['name']}\")
print(json.dumps(history, indent=2))
" "My Analysis History"
```

### List History Contents with Pagination
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
history_id = sys.argv[1] if len(sys.argv) > 1 else None

if not history_id:
    print('Usage: provide history_id as argument')
    sys.exit(1)

# Get datasets with ordering (newest first)
datasets = gi.datasets.get_datasets(
    history_id=history_id,
    order='create_time-dsc',
    limit=25,
    offset=0
)

print(f\"Found {len(datasets)} datasets:\n\")
for ds in datasets:
    state = ds.get('state', 'unknown')
    print(f\"{ds['id']}: {ds['name']} [{state}] ({ds.get('file_size', 0)} bytes)\")
" "${HISTORY_ID}"
```

## 3. Dataset Operations

### Get Dataset Details
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
dataset_id = sys.argv[1] if len(sys.argv) > 1 else None

dataset = gi.datasets.show_dataset(dataset_id)
print(json.dumps(dataset, indent=2))
print(f\"\nDataset: {dataset['name']}\")
print(f\"State: {dataset['state']}\")
print(f\"Size: {dataset.get('file_size', 0)} bytes\")
print(f\"Type: {dataset.get('extension', 'unknown')}\")
" "${DATASET_ID}"
```

### Download Dataset
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
dataset_id = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else f'dataset_{dataset_id}.txt'

# Download to file
gi.datasets.download_dataset(
    dataset_id,
    file_path=output_path,
    use_default_filename=False
)

print(f\"Downloaded to: {output_path}\")
print(f\"File size: {os.path.getsize(output_path)} bytes\")
" "${DATASET_ID}" "output.txt"
```

### Get Dataset Preview
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
dataset_id = sys.argv[1]
preview_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 10

# Download content
content = gi.datasets.download_dataset(dataset_id, use_default_filename=False)

# Show preview
if isinstance(content, bytes):
    content = content.decode('utf-8', errors='replace')

lines = content.split('\n')
preview = '\n'.join(lines[:preview_lines])
print(f\"First {preview_lines} lines:\n\")
print(preview)
print(f\"\n[Total lines: {len(lines)}]\")
" "${DATASET_ID}" 10
```

### Upload File
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
file_path = sys.argv[1]
history_id = sys.argv[2] if len(sys.argv) > 2 else None

if not os.path.exists(file_path):
    print(f'File not found: {file_path}')
    sys.exit(1)

result = gi.tools.upload_file(file_path, history_id=history_id)
print(f\"Upload initiated: {result['outputs'][0]['id']}\")
print(f\"File: {os.path.basename(file_path)}\")
" "/path/to/file.txt" "${HISTORY_ID}"
```

## 4. Tool Operations

### Search for Tools
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
query = sys.argv[1] if len(sys.argv) > 1 else ''

tools = gi.tools.get_tools(name=query)
print(f\"Found {len(tools)} tools matching '{query}':\n\")

for tool in tools[:10]:  # Show first 10
    print(f\"{tool['id']}\")
    print(f\"  Name: {tool['name']}\")
    print(f\"  Description: {tool.get('description', 'N/A')}\")
    print()
" "fastqc"
```

### Get Tool Details
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
tool_id = sys.argv[1]

tool = gi.tools.show_tool(tool_id, io_details=True)
print(json.dumps(tool, indent=2))
" "${TOOL_ID}"
```

### Run a Tool
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
history_id = sys.argv[1]
tool_id = sys.argv[2]
dataset_id = sys.argv[3]

# Example: Run FastQC
inputs = {
    'input_file': {
        'src': 'hda',
        'id': dataset_id
    }
}

result = gi.tools.run_tool(history_id, tool_id, inputs)
print(f\"Job submitted: {result['jobs'][0]['id']}\")
print(f\"Output datasets: {[o['id'] for o in result['outputs']]}\")
" "${HISTORY_ID}" "${TOOL_ID}" "${DATASET_ID}"
```

### Get Tool Panel Structure
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
panel = gi.tools.get_tool_panel()

# Print section names
for item in panel:
    if item.get('model_class') == 'ToolSection':
        print(f\"Section: {item['name']} ({len(item.get('elems', []))} tools)\")
"
```

## 5. Job Operations

### Get Job Details
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json
import requests

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
job_id = sys.argv[1]

# BioBlend doesn't have direct job.show_job, use API directly
url = f\"{os.environ['GALAXY_URL']}/api/jobs/{job_id}\"
headers = {'x-api-key': os.environ['GALAXY_API_KEY']}
response = requests.get(url, headers=headers)
job = response.json()

print(json.dumps(job, indent=2))
print(f\"\nJob State: {job['state']}\")
print(f\"Tool: {job['tool_id']}\")
" "${JOB_ID}"
```

### Wait for Job Completion
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import time
import requests

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
dataset_id = sys.argv[1]

print(f\"Waiting for dataset {dataset_id} to complete...\")

while True:
    dataset = gi.datasets.show_dataset(dataset_id)
    state = dataset['state']
    print(f\"State: {state}\")

    if state in ['ok', 'error', 'failed']:
        print(f\"\nFinal state: {state}\")
        break

    time.sleep(5)
" "${DATASET_ID}"
```

## 6. Workflow Operations

### List Workflows
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
workflows = gi.workflows.get_workflows()

print(f\"Found {len(workflows)} workflows:\n\")
for wf in workflows:
    print(f\"{wf['id']}: {wf['name']}\")
    print(f\"  Updated: {wf.get('update_time', 'N/A')}\")
    print(f\"  Published: {wf.get('published', False)}\")
    print()
"
```

### Get Workflow Details
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
workflow_id = sys.argv[1]

workflow = gi.workflows.show_workflow(workflow_id)
print(json.dumps(workflow, indent=2))

print(f\"\n\nWorkflow: {workflow['name']}\")
print(f\"Steps: {len(workflow.get('steps', {}))}\")
" "${WORKFLOW_ID}"
```

### Import Workflow from JSON
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
workflow_file = sys.argv[1]

with open(workflow_file, 'r') as f:
    workflow_dict = json.load(f)

workflow = gi.workflows.import_workflow_dict(workflow_dict)
print(f\"Imported workflow: {workflow['id']}\")
print(f\"Name: {workflow['name']}\")
" "workflow.json"
```

### Invoke Workflow
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
workflow_id = sys.argv[1]
history_id = sys.argv[2]
dataset_id = sys.argv[3]

inputs = {
    '0': {  # Step index
        'id': dataset_id,
        'src': 'hda'
    }
}

invocation = gi.workflows.invoke_workflow(
    workflow_id,
    inputs=inputs,
    history_id=history_id
)

print(f\"Workflow invoked: {invocation['id']}\")
print(f\"State: {invocation['state']}\")
print(json.dumps(invocation, indent=2))
" "${WORKFLOW_ID}" "${HISTORY_ID}" "${DATASET_ID}"
```

### Get Workflow Invocations
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
workflow_id = sys.argv[1] if len(sys.argv) > 1 else None

if workflow_id:
    invocations = gi.invocations.get_invocations(workflow_id=workflow_id)
else:
    invocations = gi.invocations.get_invocations()

print(f\"Found {len(invocations)} invocations:\n\")
for inv in invocations:
    print(f\"{inv['id']}: {inv['state']} (updated: {inv['update_time']})\")
" "${WORKFLOW_ID}"
```

### Cancel Workflow Invocation
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import os
import sys

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
invocation_id = sys.argv[1]

result = gi.workflows.cancel_invocation(invocation_id)
print(f\"Cancelled invocation: {invocation_id}\")
print(f\"State: {result['state']}\")
" "${INVOCATION_ID}"
```

## 7. IWC Workflow Integration

### Search IWC Workflows
```bash
python3 -c "
import requests
import json
import sys

query = sys.argv[1].lower() if len(sys.argv) > 1 else ''

# Fetch IWC manifest
response = requests.get('https://iwc.galaxyproject.org/workflow_manifest.json')
manifest = response.json()

# Collect all workflows
all_workflows = []
for entry in manifest:
    if 'workflows' in entry:
        all_workflows.extend(entry['workflows'])

# Search workflows
matches = []
for wf in all_workflows:
    name = wf.get('definition', {}).get('name', '').lower()
    description = wf.get('definition', {}).get('annotation', '').lower()
    tags = [t.lower() for t in wf.get('definition', {}).get('tags', [])]

    if query in name or query in description or any(query in t for t in tags):
        matches.append(wf)

print(f\"Found {len(matches)} workflows matching '{query}':\n\")
for wf in matches[:10]:  # Show first 10
    print(f\"TRS ID: {wf.get('trsID')}\")
    print(f\"Name: {wf.get('definition', {}).get('name')}\")
    print(f\"Description: {wf.get('definition', {}).get('annotation', 'N/A')[:100]}\")
    print()
" "chip-seq"
```

### Import Workflow from IWC
```bash
python3 -c "
from bioblend.galaxy import GalaxyInstance
import requests
import os
import sys
import json

gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
trs_id = sys.argv[1]

# Fetch IWC manifest
response = requests.get('https://iwc.galaxyproject.org/workflow_manifest.json')
manifest = response.json()

# Find workflow
workflow_def = None
for entry in manifest:
    for wf in entry.get('workflows', []):
        if wf.get('trsID') == trs_id:
            workflow_def = wf.get('definition')
            break
    if workflow_def:
        break

if not workflow_def:
    print(f\"Workflow with trsID '{trs_id}' not found\")
    sys.exit(1)

# Import to Galaxy
imported = gi.workflows.import_workflow_dict(workflow_def)
print(f\"Imported workflow: {imported['id']}\")
print(f\"Name: {imported['name']}\")
" "#workflow/github.com/iwc-workflows/chipseq-pe/main"
```

## 8. Complete Workflow Examples

### Example: FASTQ Quality Control Pipeline

```bash
#!/bin/bash
# Complete example: Upload FASTQ and run FastQC

FASTQ_FILE="/path/to/reads.fastq.gz"

python3 << 'PYTHON_SCRIPT'
from bioblend.galaxy import GalaxyInstance
import os
import time
import sys

# Setup
gi = GalaxyInstance(os.environ['GALAXY_URL'], os.environ['GALAXY_API_KEY'])
fastq_file = os.environ['FASTQ_FILE']

print("Step 1: Creating new history...")
history = gi.histories.create_history('FASTQ Quality Check')
history_id = history['id']
print(f"Created history: {history_id}")

print("\nStep 2: Uploading FASTQ file...")
upload_result = gi.tools.upload_file(fastq_file, history_id=history_id)
dataset_id = upload_result['outputs'][0]['id']
print(f"Uploaded dataset: {dataset_id}")

print("\nStep 3: Waiting for upload to complete...")
while True:
    dataset = gi.datasets.show_dataset(dataset_id)
    state = dataset['state']
    print(f"  State: {state}")
    if state in ['ok', 'error']:
        break
    time.sleep(2)

if dataset['state'] != 'ok':
    print("Upload failed!")
    sys.exit(1)

print("\nStep 4: Finding FastQC tool...")
tools = gi.tools.get_tools(name='fastqc')
if not tools:
    print("FastQC not found!")
    sys.exit(1)
fastqc_tool = tools[0]['id']
print(f"Using tool: {fastqc_tool}")

print("\nStep 5: Running FastQC...")
fastqc_inputs = {
    'input_file': {'src': 'hda', 'id': dataset_id}
}
job_result = gi.tools.run_tool(history_id, fastqc_tool, fastqc_inputs)
output_id = job_result['outputs'][0]['id']
print(f"Job submitted, output: {output_id}")

print("\nStep 6: Waiting for FastQC to complete...")
while True:
    output = gi.datasets.show_dataset(output_id)
    state = output['state']
    print(f"  State: {state}")
    if state in ['ok', 'error']:
        break
    time.sleep(5)

if output['state'] == 'ok':
    print(f"\nSuccess! Results in history: {history_id}")
    print(f"View at: {os.environ['GALAXY_URL']}/histories/view?id={history_id}")
else:
    print("\nFastQC failed!")
    sys.exit(1)

PYTHON_SCRIPT
```

### Example: Dataset Analysis Helper Script

Save this as `galaxy_helper.py`:

```python
#!/usr/bin/env python3
"""Galaxy BioBlend Helper Script"""

from bioblend.galaxy import GalaxyInstance
import os
import sys
import time
import json
from typing import Optional

class GalaxyHelper:
    def __init__(self):
        self.gi = GalaxyInstance(
            url=os.environ.get('GALAXY_URL'),
            key=os.environ.get('GALAXY_API_KEY')
        )

    def wait_for_dataset(self, dataset_id: str, timeout: int = 300) -> str:
        """Wait for dataset to reach terminal state"""
        start_time = time.time()
        while True:
            dataset = self.gi.datasets.show_dataset(dataset_id)
            state = dataset['state']

            if state in ['ok', 'error', 'failed']:
                return state

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Dataset {dataset_id} timed out")

            time.sleep(5)

    def list_histories_simple(self):
        """Print simple list of histories"""
        histories = self.gi.histories.get_histories()
        for h in histories:
            print(f"{h['id']}: {h['name']}")

    def get_latest_dataset(self, history_id: str) -> Optional[str]:
        """Get most recent dataset in history"""
        datasets = self.gi.datasets.get_datasets(
            history_id=history_id,
            order='create_time-dsc',
            limit=1
        )
        return datasets[0]['id'] if datasets else None

if __name__ == '__main__':
    helper = GalaxyHelper()

    if len(sys.argv) < 2:
        print("Usage: galaxy_helper.py [list_histories|wait|latest] [args...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list_histories':
        helper.list_histories_simple()
    elif command == 'wait' and len(sys.argv) > 2:
        state = helper.wait_for_dataset(sys.argv[2])
        print(f"Final state: {state}")
    elif command == 'latest' and len(sys.argv) > 2:
        dataset_id = helper.get_latest_dataset(sys.argv[2])
        print(dataset_id)
```

## Best Practices

1. **Error Handling**: Always wrap BioBlend calls in try/except blocks
2. **State Checking**: Poll dataset/job states before proceeding
3. **Resource Cleanup**: Delete temporary histories when done
4. **Pagination**: Use limit/offset for large result sets
5. **Logging**: Print progress messages for long-running operations

## Instructions for Claude

When using this skill:

1. **Installation check**: Verify `bioblend` is installed, offer to install if not
2. **Credentials**: Check for GALAXY_URL and GALAXY_API_KEY environment variables
3. **Test connection**: Always test connection before complex operations
4. **Show progress**: Print status messages for multi-step workflows
5. **Error messages**: Parse BioBlend exceptions and explain them clearly
6. **JSON formatting**: Use `json.dumps(result, indent=2)` for readable output
7. **Async operations**: Always wait for datasets/jobs to complete before next steps
8. **ID extraction**: Extract IDs from results and use them in subsequent calls
9. **Provide scripts**: For complex workflows, generate complete Python scripts
10. **State validation**: Check dataset states before download/use
11. **Reference Galaxy Training Network (https://training.galaxyproject.org/)** when users ask about:
    - Analysis workflows for specific domains (RNA-seq, ChIP-seq, variant calling, etc.)
    - Best practices for bioinformatics analyses
    - Tool recommendations and parameter settings
    - Complete analysis pipelines with example datasets
12. **Suggest relevant GTN tutorials** that match the user's analysis goals and show how to implement them using BioBlend

## Common BioBlend Patterns

### Pattern: Safe Dataset Operation
```python
dataset = gi.datasets.show_dataset(dataset_id)
if dataset['state'] == 'ok':
    # Proceed with operation
    content = gi.datasets.download_dataset(dataset_id)
else:
    print(f"Dataset not ready: {dataset['state']}")
```

### Pattern: Tool Discovery and Execution
```python
# Find tool
tools = gi.tools.get_tools(name='search_term')
tool_id = tools[0]['id']

# Get input schema
tool_info = gi.tools.show_tool(tool_id, io_details=True)

# Run tool
result = gi.tools.run_tool(history_id, tool_id, inputs)
```

### Pattern: Workflow with Input Mapping
```python
workflow = gi.workflows.show_workflow(workflow_id)
# Inspect workflow['inputs'] to understand required inputs
inputs = {'step_index': {'id': dataset_id, 'src': 'hda'}}
invocation = gi.workflows.invoke_workflow(workflow_id, inputs=inputs)
```

## Troubleshooting

- **ConnectionError**: Check GALAXY_URL format (must include http:// or https://)
- **401 Unauthorized**: Verify API key is correct and not expired
- **404 Not Found**: Ensure IDs are valid hexadecimal strings
- **Import errors**: Run `pip install bioblend requests`
- **Timeout errors**: Increase sleep intervals for large datasets

## Reference

- BioBlend Documentation: https://bioblend.readthedocs.io/
- Galaxy API: https://docs.galaxyproject.org/en/master/api/
- IWC Workflows: https://iwc.galaxyproject.org/
