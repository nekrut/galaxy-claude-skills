# Galaxy Claude Skills

Claude skills for interacting with the [Galaxy](https://galaxyproject.org/) bioinformatics platform without requiring MCP server installation.

## What Are These?

These are markdown-based skill files that teach Claude how to interact with Galaxy servers through direct API calls. No special installation required - just reference the skill file in your Claude conversation!

## Available Skills

### 🐍 galaxy-bioblend.md (Recommended)
Uses the official [BioBlend](https://bioblend.readthedocs.io/) Python library for clean, maintainable Galaxy interactions.

**Requirements:**
- Python 3
- `pip install bioblend`

**Best for:**
- Developers comfortable with Python
- Complex workflows requiring error handling
- When you want readable, maintainable code

### 🌐 galaxy.md (Zero Dependencies)
Uses raw curl commands for Galaxy API interactions.

**Requirements:**
- Just curl (pre-installed on most systems)

**Best for:**
- Minimal environments
- Quick one-off operations
- Systems without Python access

## Quick Start

### 1. Set Up Credentials

```bash
export GALAXY_URL="https://usegalaxy.org"
export GALAXY_API_KEY="your_api_key_here"
```

Get your API key from: User → Preferences → Manage API Key in your Galaxy instance.

### 2. Install Dependencies (for BioBlend skill)

```bash
pip install bioblend
```

### 3. Use with Claude

**Option A: Direct reference in your working directory**
```bash
# Copy the skill to your project
cp galaxy-bioblend.md ~/my-project/

# Use with Claude
cd ~/my-project
claude "Using galaxy-bioblend.md, connect to Galaxy and list my histories"
```

**Option B: Reference by path**
```bash
claude "Using /path/to/galaxy-bioblend.md, help me run FastQC on my FASTQ file"
```

**Option C: Install to skills directory**
```bash
# Create skills directory (if not exists)
mkdir -p ~/.claude/skills

# Copy skills
cp galaxy*.md ~/.claude/skills/

# Reference by name
claude "Using galaxy-bioblend skill, show me my Galaxy histories"
```

## What Can You Do?

Both skills provide complete Galaxy API coverage:

- **Connection Management**: Connect to any Galaxy instance, test credentials
- **History Operations**: Create, list, and manage histories
- **Dataset Management**: Upload, download, view dataset details
- **Tool Execution**: Search tools, view parameters, run analyses
- **Workflow Operations**: List, import, invoke, and monitor workflows
- **Job Tracking**: Monitor job status and progress
- **IWC Integration**: Search and import workflows from the [Intergalactic Workflow Commission](https://iwc.galaxyproject.org/)

## Example Usage

### Example 1: Quality Check a FASTQ File

```bash
claude "Using galaxy-bioblend.md, I have a FASTQ file at /data/reads.fastq.gz.
Please upload it to Galaxy and run FastQC on it."
```

Claude will:
1. Connect to your Galaxy instance
2. Create a new history
3. Upload the file
4. Find and run FastQC
5. Monitor job completion
6. Report results

### Example 2: Import and Run an IWC Workflow

```bash
claude "Using galaxy-bioblend.md, find a ChIP-seq workflow in IWC,
import it, and help me run it on my datasets."
```

### Example 3: Monitor Running Jobs

```bash
claude "Using galaxy-bioblend.md, show me the status of all my running jobs."
```

## Learning Resources

Both skills include references to the [Galaxy Training Network](https://training.galaxyproject.org/), which provides:
- Domain-specific analysis tutorials (genomics, proteomics, climate science, etc.)
- Best practices for tool selection and parameters
- Complete analysis pipelines with example data
- Troubleshooting guides

When you ask Claude about specific analyses, it will suggest relevant GTN tutorials!

## Comparison: MCP Server vs Skills

| Feature | MCP Server | Claude Skills |
|---------|------------|---------------|
| Installation | `uvx galaxy-mcp` + config | Copy markdown file |
| Dependencies | Python, MCP runtime | None (curl) or just BioBlend |
| Setup complexity | Medium (config files) | Low (just env vars) |
| Integration | Native Claude Desktop | Works anywhere Claude runs |
| Maintenance | Auto-updates via pip | Manual file updates |
| Best for | Regular Galaxy users | Occasional use, portability |

If you use Galaxy frequently in Claude Desktop, consider the [MCP server](https://github.com/galaxyproject/galaxy-mcp). For occasional use or maximum portability, use these skills!

## Contributing

Found a useful pattern? Have suggestions? Contributions welcome!

1. Fork the repository
2. Add your improvements
3. Submit a pull request

## Related Projects

- [Galaxy MCP Server](https://github.com/galaxyproject/galaxy-mcp) - Full-featured MCP server for Galaxy
- [Galaxy](https://galaxyproject.org/) - The Galaxy platform
- [BioBlend](https://bioblend.readthedocs.io/) - Python library for Galaxy API
- [Galaxy Training Network](https://training.galaxyproject.org/) - Tutorials and training materials

## License

MIT License - See [LICENSE](LICENSE) file for details

## Support

- **Galaxy Help**: https://help.galaxyproject.org/
- **Galaxy API Docs**: https://docs.galaxyproject.org/en/master/api/
- **BioBlend Docs**: https://bioblend.readthedocs.io/
- **Issues**: Report issues on this repository's issue tracker

---

**Note**: These skills were created to provide an installation-free alternative to the Galaxy MCP server. They provide the same functionality through direct API calls that Claude can execute via bash commands.
