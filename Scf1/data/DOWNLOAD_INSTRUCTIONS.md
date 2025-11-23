# Data Download Instructions

## Paper Information

- **Title:** A *Candida auris*-specific adhesin, Scf1, governs surface association, colonization, and virulence
- **Authors:** Santana DJ, Anku JAE, Zhao G, et al.
- **Journal:** Science (2023)
- **DOI:** 10.1126/science.adf8972
- **PMID:** 37769084
- **PMCID:** PMC11235122

## Downloaded Files

✅ **Main Paper PDF:** `Santana_2023_Science_Scf1.pdf`
- Downloaded from: NCBI PMC

## Supplementary Materials (Manual Download Required)

PMC blocks programmatic downloads. Please download manually:

### 1. Supplementary PDF (8.6 MB)
**File:** Figures S1-S15, Tables S1-S2, additional methods

**Download from:**
https://pmc.ncbi.nlm.nih.gov/articles/PMC11235122/

Click on "Supplementary Materials" section and download:
- `NIHMS2004453-supplement-2.pdf`

**Save as:** `Santana_2023_Supplementary.pdf`

### 2. Source Data Excel File (1.1 MB)
**File:** Raw experimental data and quantitative results

**Download from:**
https://pmc.ncbi.nlm.nih.gov/articles/PMC11235122/

Click on "Data 1 Source Data" and download:
- `NIHMS2004453-supplement-Data_1_Source_Data.xlsx`

**Save as:** `Santana_2023_SourceData.xlsx`

## Sequence Data (Available via SRA)

The paper includes RNA-seq and genomic sequencing data deposited in NCBI:

### RNA-Seq Data
- **BioProject:** PRJNA904261
- **URL:** https://www.ncbi.nlm.nih.gov/bioproject/PRJNA904261
- **Description:** Transcriptomic analysis

### Whole Genome Sequencing
- **BioProject:** PRJNA904262
- **URL:** https://www.ncbi.nlm.nih.gov/bioproject/PRJNA904262
- **Description:** Insertional mutant whole genome sequencing

## Downloading SRA Data

To download the sequencing data for re-analysis:

```bash
# Install SRA Toolkit (if not already installed)
# sudo apt install sra-toolkit

# Download RNA-seq data
prefetch PRJNA904261

# Download WGS data
prefetch PRJNA904262

# Convert to FASTQ
fastq-dump --split-files SRR*.sra
```

## Data Files Checklist

- [x] Main paper PDF
- [ ] Supplementary materials PDF
- [ ] Source data Excel file
- [ ] RNA-seq data (SRA)
- [ ] WGS data (SRA)

## Notes

- Large sequencing files should be downloaded directly to the data directory
- Make sure .gitignore excludes large FASTQ files
- Document data provenance and download dates
