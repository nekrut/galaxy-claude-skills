# Data Download Log

## Date: 2025-11-23

### Galaxy History Created
- **Name:** Scf1 Candida auris Re-analysis - Santana 2023
- **History ID:** bbd44e69cb8906b5315d31f78779a72a
- **URL:** https://usegalaxy.org/histories/view?id=bbd44e69cb8906b5315d31f78779a72a

### SRA Data Download

**Method:** IWC parallel download workflow
**Workflow:** sra_manifest_to_concatenated_fastqs_parallel
**Workflow ID:** 56501e2fdae0d764
**Invocation ID:** c0df4861a635a879
**Status:** Running

#### RNA-Seq Data (PRJNA904261)
6 runs from transcriptomic analysis:
- SRR22376027
- SRR22376028
- SRR22376029
- SRR22376030
- SRR22376031
- SRR22376032

#### Whole Genome Sequencing (PRJNA904262)
2 runs from insertional mutant WGS:
- SRR22376033
- SRR22376034

### Workflow Details
- Downloads FASTQ files from SRA in parallel
- Automatically handles paired-end reads
- Concatenates technical replicates
- Output: Ready-to-use FASTQ files for analysis

### Next Steps
1. Wait for workflow to complete
2. Verify FASTQ files downloaded correctly
3. Run FastQC on all samples
4. Begin RNA-seq analysis pipeline

### Notes
- All 8 datasets being downloaded simultaneously using Galaxy's parallel processing
- Data will be ready for immediate analysis in Galaxy
- No need for local SRA toolkit installation
