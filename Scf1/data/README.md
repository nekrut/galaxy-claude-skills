# Data Directory

## Paper Files

### To Download Manually:

**Main Paper PDF:**
- Visit: https://pmc.ncbi.nlm.nih.gov/articles/PMC11235122/
- Download the PDF version
- Save as: `Santana_2023_Science_Scf1.pdf`

**Supplementary Materials PDF (8.6 MB):**
- Visit: https://pmc.ncbi.nlm.nih.gov/articles/PMC11235122/
- Find "Supplementary Materials" section
- Download: `NIHMS2004453-supplement-2.pdf`
- Contains: Figures S1-S15, Tables S1-S2
- Save as: `Santana_2023_Supplementary.pdf`

**Source Data Excel File (1.1 MB):**
- Visit: https://pmc.ncbi.nlm.nih.gov/articles/PMC11235122/
- Download: `NIHMS2004453-supplement-Data_1_Source_Data.xlsx`
- Contains: Raw experimental data
- Save as: `Santana_2023_SourceData.xlsx`

## Sequence Data

### RNA-Seq Data (PRJNA904261)

To download using SRA Toolkit:

```bash
# Install SRA Toolkit if needed
# conda install -c bioconda sra-tools

# Download RNA-seq project
prefetch -O . PRJNA904261

# Or download individual runs:
# (Get SRR accessions from BioProject page)
prefetch SRR_NUMBER
fastq-dump --split-files --gzip SRR_NUMBER.sra
```

### Whole Genome Sequencing (PRJNA904262)

Insertional mutant WGS data:

```bash
prefetch -O . PRJNA904262
```

## Data Organization

```
data/
├── README.md (this file)
├── DOWNLOAD_INSTRUCTIONS.md
├── Santana_2023_Science_Scf1.pdf (download manually)
├── Santana_2023_Supplementary.pdf (download manually)
├── Santana_2023_SourceData.xlsx (download manually)
├── sra/                    # SRA data (will be large!)
│   ├── PRJNA904261/       # RNA-seq
│   └── PRJNA904262/       # WGS
└── processed/             # Processed datasets
```

## Important Notes

- **Don't commit large files to git!** The .gitignore is configured to exclude:
  - FASTQ files (*.fastq, *.fastq.gz, *.fq)
  - BAM files (*.bam)
  - SAM files (*.sam)
- SRA data can be very large (GBs) - make sure you have enough disk space
- Document all download dates and versions for reproducibility

## Data Provenance

- **Downloaded on:** [Add date when you download]
- **Downloaded from:** NCBI PMC and SRA
- **Reference:** Santana et al. Science 2023. DOI: 10.1126/science.adf8972
