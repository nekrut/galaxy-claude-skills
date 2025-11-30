# Gene ID Mapping Between Annotation Versions

This skill provides tools for mapping gene identifiers between different genome annotation versions when direct ID matching fails. This is common when comparing RNA-seq results across studies that used different annotation releases.

## Problem Statement

When comparing differential expression results between studies or validating published findings:
- Different genome annotation versions may use different gene ID formats
- Gene IDs may be completely reassigned (not just reformatted)
- Direct string matching fails even when the underlying genes are identical

**Example**: NCBI *Candida auris* annotations changed from 6-digit suffixes (B9J08_001458) to 5-digit suffixes (B9J08_03708), with completely different numbering.

## Solution: LFC-Based Correlation Mapping

Since the same genes analyzed from the same data produce nearly identical fold changes, we can use log2 fold change (LFC) values as a unique "fingerprint" to match genes between annotation versions.

## Prerequisites

- Python 3 with pandas, numpy, scipy
- Two DEG result files with gene IDs and LFC values
- Both analyses performed on the same underlying data

## Core Functions

### 1. Load DEG Data

```python
import pandas as pd
import numpy as np
from scipy import stats

def load_deg_file(filepath, gene_col='Gene_ID', lfc_col='LFC', sep=','):
    """
    Load a DEG results file.

    Args:
        filepath: Path to DEG file (CSV, TSV, or Excel)
        gene_col: Column name containing gene IDs
        lfc_col: Column name containing log2 fold change values
        sep: Delimiter for CSV/TSV files

    Returns:
        DataFrame with gene_id and lfc columns
    """
    if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath, sep=sep)

    # Standardize column names
    df = df.rename(columns={gene_col: 'gene_id', lfc_col: 'lfc'})
    df = df[['gene_id', 'lfc']].dropna()
    df['lfc'] = pd.to_numeric(df['lfc'], errors='coerce')
    df = df.dropna()

    return df
```

### 2. Create LFC-Based Gene Mapping

```python
def create_lfc_mapping(source_df, target_df, tolerance=0.1):
    """
    Map genes between two annotation versions using LFC correlation.

    For each gene in source_df, find the gene in target_df with the
    closest matching LFC value.

    Args:
        source_df: DataFrame with 'gene_id' and 'lfc' columns (reference)
        target_df: DataFrame with 'gene_id' and 'lfc' columns (to map)
        tolerance: Maximum LFC difference to consider a valid match

    Returns:
        DataFrame with mapping: source_gene, source_lfc, target_gene, target_lfc, lfc_diff
    """
    mappings = []

    # Create lookup array for target LFCs
    target_lfcs = target_df['lfc'].values
    target_genes = target_df['gene_id'].values

    for _, row in source_df.iterrows():
        source_gene = row['gene_id']
        source_lfc = row['lfc']

        # Find closest match by LFC
        lfc_diffs = np.abs(target_lfcs - source_lfc)
        best_idx = np.argmin(lfc_diffs)
        best_diff = lfc_diffs[best_idx]

        if best_diff <= tolerance or tolerance is None:
            mappings.append({
                'source_gene': source_gene,
                'source_lfc': source_lfc,
                'target_gene': target_genes[best_idx],
                'target_lfc': target_lfcs[best_idx],
                'lfc_diff': best_diff
            })

    result = pd.DataFrame(mappings)
    result = result.sort_values('lfc_diff')

    return result
```

### 3. Validate Mapping Quality

```python
def validate_mapping(mapping_df, source_col='source_lfc', target_col='target_lfc'):
    """
    Calculate validation statistics for gene mapping.

    Args:
        mapping_df: DataFrame from create_lfc_mapping()
        source_col: Column name for source LFC values
        target_col: Column name for target LFC values

    Returns:
        Dictionary with validation statistics
    """
    source_lfc = mapping_df[source_col].values
    target_lfc = mapping_df[target_col].values

    # Correlation statistics
    pearson_r, pearson_p = stats.pearsonr(source_lfc, target_lfc)
    spearman_r, spearman_p = stats.spearmanr(source_lfc, target_lfc)

    # Direction agreement
    source_direction = np.sign(source_lfc)
    target_direction = np.sign(target_lfc)
    direction_match = np.sum(source_direction == target_direction)
    direction_pct = direction_match / len(source_lfc) * 100

    # LFC difference statistics
    lfc_diffs = mapping_df['lfc_diff'].values

    return {
        'n_mapped': len(mapping_df),
        'pearson_r': pearson_r,
        'pearson_r_squared': pearson_r ** 2,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'direction_agreement_pct': direction_pct,
        'direction_matches': direction_match,
        'lfc_diff_mean': np.mean(lfc_diffs),
        'lfc_diff_median': np.median(lfc_diffs),
        'lfc_diff_std': np.std(lfc_diffs),
        'lfc_diff_max': np.max(lfc_diffs)
    }
```

### 4. Generate Validation Plot

```python
def plot_mapping_validation(mapping_df, output_path, title='Gene Mapping Validation'):
    """
    Create scatter plot comparing LFC values between annotation versions.

    Args:
        mapping_df: DataFrame from create_lfc_mapping()
        output_path: Path to save the plot (PNG or PDF)
        title: Plot title
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    source_lfc = mapping_df['source_lfc'].values
    target_lfc = mapping_df['target_lfc'].values

    # Scatter plot
    ax1 = axes[0]
    ax1.scatter(source_lfc, target_lfc, alpha=0.6, s=50)

    # Add regression line
    slope, intercept, r_value, _, _ = stats.linregress(source_lfc, target_lfc)
    x_line = np.linspace(min(source_lfc), max(source_lfc), 100)
    ax1.plot(x_line, slope * x_line + intercept, 'r-',
             linewidth=2, label=f'R² = {r_value**2:.4f}')

    # Add identity line
    lim = max(abs(min(source_lfc)), abs(max(source_lfc)),
              abs(min(target_lfc)), abs(max(target_lfc)))
    ax1.plot([-lim, lim], [-lim, lim], 'k--', alpha=0.5, label='y = x')

    ax1.set_xlabel('Source LFC', fontsize=12)
    ax1.set_ylabel('Target LFC', fontsize=12)
    ax1.set_title(f'{title}\nCorrelation Plot', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Bland-Altman plot
    ax2 = axes[1]
    mean_lfc = (source_lfc + target_lfc) / 2
    diff_lfc = source_lfc - target_lfc

    ax2.scatter(mean_lfc, diff_lfc, alpha=0.6, s=50)

    mean_diff = np.mean(diff_lfc)
    std_diff = np.std(diff_lfc)
    ax2.axhline(y=mean_diff, color='red', linestyle='-',
                label=f'Mean: {mean_diff:.4f}')
    ax2.axhline(y=mean_diff + 1.96*std_diff, color='red',
                linestyle='--', alpha=0.7, label='±1.96 SD')
    ax2.axhline(y=mean_diff - 1.96*std_diff, color='red',
                linestyle='--', alpha=0.7)
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)

    ax2.set_xlabel('Mean LFC', fontsize=12)
    ax2.set_ylabel('Difference (Source - Target)', fontsize=12)
    ax2.set_title('Bland-Altman Agreement Plot', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Validation plot saved to: {output_path}")
```

## Complete Workflow Example

```python
#!/usr/bin/env python3
"""
Gene ID Mapping Between Annotation Versions

Maps gene identifiers between two DEG result files using LFC correlation.
Useful when comparing results from different genome annotation versions.

Usage:
    python gene_mapping.py --source paper_degs.csv --target our_degs.csv \
                           --output mapping.csv --plot validation.png
"""

import argparse
import pandas as pd
import numpy as np
from scipy import stats

def main():
    parser = argparse.ArgumentParser(description='Map gene IDs between annotation versions')
    parser.add_argument('--source', required=True, help='Source DEG file (reference)')
    parser.add_argument('--target', required=True, help='Target DEG file (to map)')
    parser.add_argument('--output', required=True, help='Output mapping file')
    parser.add_argument('--plot', help='Output validation plot (PNG/PDF)')
    parser.add_argument('--source-gene-col', default='Gene_ID', help='Gene ID column in source')
    parser.add_argument('--source-lfc-col', default='LFC', help='LFC column in source')
    parser.add_argument('--target-gene-col', default='Gene_ID', help='Gene ID column in target')
    parser.add_argument('--target-lfc-col', default='log2FoldChange', help='LFC column in target')
    parser.add_argument('--tolerance', type=float, default=None, help='Max LFC difference')

    args = parser.parse_args()

    # Load data
    print(f"Loading source: {args.source}")
    source_df = load_deg_file(args.source, args.source_gene_col, args.source_lfc_col)
    print(f"  Loaded {len(source_df)} genes")

    print(f"Loading target: {args.target}")
    target_df = load_deg_file(args.target, args.target_gene_col, args.target_lfc_col)
    print(f"  Loaded {len(target_df)} genes")

    # Create mapping
    print("Creating LFC-based gene mapping...")
    mapping = create_lfc_mapping(source_df, target_df, args.tolerance)
    print(f"  Mapped {len(mapping)} genes")

    # Validate
    stats_dict = validate_mapping(mapping)
    print("\nValidation Statistics:")
    print(f"  Pearson R²: {stats_dict['pearson_r_squared']:.4f}")
    print(f"  Spearman R: {stats_dict['spearman_r']:.4f}")
    print(f"  Direction Agreement: {stats_dict['direction_agreement_pct']:.1f}%")
    print(f"  Mean LFC Diff: {stats_dict['lfc_diff_mean']:.4f}")
    print(f"  Max LFC Diff: {stats_dict['lfc_diff_max']:.4f}")

    # Save mapping
    mapping.to_csv(args.output, index=False)
    print(f"\nMapping saved to: {args.output}")

    # Generate plot
    if args.plot:
        plot_mapping_validation(mapping, args.plot)

if __name__ == '__main__':
    main()
```

## Quality Thresholds

A successful gene mapping should meet these criteria:

| Metric | Excellent | Acceptable | Poor |
|--------|-----------|------------|------|
| Pearson R² | > 0.99 | > 0.95 | < 0.95 |
| Direction Agreement | 100% | > 95% | < 95% |
| Mean LFC Diff | < 0.01 | < 0.05 | > 0.05 |

## Handling Edge Cases

### 0. Reversed LFC Direction (DESeq2 Reference Swap)

**Problem**: If your DESeq2 analysis used a different reference/treatment assignment than the paper, all LFC signs will be flipped. For example:
- Paper: tnSWI1 vs AR0382 (mutant/wildtype) → SCF1 has LFC = -6.68
- Your analysis: AR0382 vs tnSWI1 (wildtype/mutant) → SCF1 has LFC = +6.82

**Solution**: Use `--auto-direction` flag or the `detect_lfc_direction()` function:

```python
from gene_mapping import detect_lfc_direction, create_lfc_mapping

# Automatic detection and correction
mapping = create_lfc_mapping(source_df, target_df, auto_detect_direction=True)

# Or manual detection
should_negate, r_asis, r_neg = detect_lfc_direction(source_df, target_df)
if should_negate:
    target_df['lfc'] = -target_df['lfc']
    print(f"Direction reversed! (R={r_asis:.3f} → R={r_neg:.3f} after negation)")
```

**Command line**:
```bash
python gene_mapping.py --source paper.csv --target our.csv \
    --auto-direction --output mapping.csv
```

### 1. Duplicate LFC Values

If multiple genes have identical LFC values:

```python
def create_lfc_mapping_unique(source_df, target_df):
    """
    Mapping that ensures one-to-one correspondence.
    Uses Hungarian algorithm for optimal assignment.
    """
    from scipy.optimize import linear_sum_assignment

    # Create cost matrix (LFC differences)
    cost_matrix = np.abs(
        source_df['lfc'].values[:, np.newaxis] -
        target_df['lfc'].values[np.newaxis, :]
    )

    # Find optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    mappings = []
    for i, j in zip(row_ind, col_ind):
        mappings.append({
            'source_gene': source_df.iloc[i]['gene_id'],
            'source_lfc': source_df.iloc[i]['lfc'],
            'target_gene': target_df.iloc[j]['gene_id'],
            'target_lfc': target_df.iloc[j]['lfc'],
            'lfc_diff': cost_matrix[i, j]
        })

    return pd.DataFrame(mappings).sort_values('lfc_diff')
```

### 2. Genes with Extreme Values

Handle genes with extreme or floor/ceiling values:

```python
def filter_extreme_values(df, lfc_col='lfc', threshold=10):
    """
    Filter out genes with extreme LFC values that may be artifacts.
    """
    return df[np.abs(df[lfc_col]) < threshold].copy()
```

### 3. Genes Missing from Target

```python
def identify_unmapped_genes(source_df, mapping_df):
    """
    Find source genes that couldn't be mapped.
    """
    mapped_genes = set(mapping_df['source_gene'])
    all_genes = set(source_df['gene_id'])
    unmapped = all_genes - mapped_genes
    return source_df[source_df['gene_id'].isin(unmapped)]
```

## Integration with Galaxy

### Upload Mapping Results to Galaxy

```bash
# Upload mapping CSV to Galaxy history
python3 << 'EOF'
import requests
import os

api_key = os.environ.get('GALAXY_API_KEY')
history_id = 'YOUR_HISTORY_ID'

with open('gene_mapping.csv', 'rb') as f:
    response = requests.post(
        f'https://usegalaxy.org/api/tools',
        headers={'x-api-key': api_key},
        data={
            'tool_id': 'upload1',
            'history_id': history_id,
            'inputs': '{"file_type": "csv", "files_0|NAME": "gene_mapping.csv"}'
        },
        files={'files_0|file_data': f}
    )
    print(response.json())
EOF
```

## When to Use This Skill

Use LFC-based gene mapping when:

1. **Comparing published results** with your own analysis
2. **Validating reproducibility** across different annotation versions
3. **Integrating datasets** from different studies
4. **Updating legacy analyses** to new genome annotations

Do NOT use when:

1. Different organisms are being compared
2. Substantially different analysis methods were used
3. Raw data or normalization differs significantly
4. Sample compositions are different

## Instructions for Claude

When helping users with gene mapping:

1. **Identify the problem**: Confirm that gene ID mismatch is due to annotation version differences
2. **Check prerequisites**: Ensure both datasets have LFC values from the same underlying comparison
3. **Run the mapping**: Use the functions above to create a mapping
4. **Validate quality**: Check R², direction agreement, and LFC differences
5. **Report outliers**: Flag genes with unusually large LFC differences
6. **Visualize results**: Generate scatter and Bland-Altman plots
7. **Document the mapping**: Save the mapping file for future reference

## Example Output

```
Loading source: paper_degs.csv
  Loaded 76 genes
Loading target: our_degs.csv
  Loaded 73 genes
Creating LFC-based gene mapping...
  Mapped 76 genes

Validation Statistics:
  Pearson R²: 0.9914
  Spearman R: 0.9999
  Direction Agreement: 100.0%
  Mean LFC Diff: 0.0608
  Max LFC Diff: 3.9111

Mapping saved to: gene_mapping.csv
Validation plot saved to: validation.png
```

## References

- DESeq2: Love MI, Huber W, Anders S (2014). Genome Biology 15:550
- Bland-Altman plots: Bland JM, Altman DG (1986). Lancet 327:307-310
- Hungarian algorithm: Kuhn HW (1955). Naval Research Logistics Quarterly 2:83-97
