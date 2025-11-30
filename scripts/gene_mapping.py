#!/usr/bin/env python3
"""
Gene ID Mapping Between Annotation Versions

Maps gene identifiers between two DEG result files using LFC correlation.
Useful when comparing results from different genome annotation versions.

Usage:
    python gene_mapping.py --source paper_degs.csv --target our_degs.csv \
                           --output mapping.csv --plot validation.png

Example:
    # Map paper gene IDs to our annotation
    python gene_mapping.py \
        --source paper_invitro_degs.csv \
        --target deseq2_results.tsv \
        --source-gene-col Gene_ID \
        --source-lfc-col LFC \
        --target-gene-col gene_id \
        --target-lfc-col log2FoldChange \
        --output gene_mapping.csv \
        --plot mapping_validation.png
"""

import argparse
import sys
import pandas as pd
import numpy as np
from scipy import stats


def load_deg_file(filepath, gene_col='Gene_ID', lfc_col='LFC', sep=None):
    """
    Load a DEG results file.

    Args:
        filepath: Path to DEG file (CSV, TSV, or Excel)
        gene_col: Column name containing gene IDs
        lfc_col: Column name containing log2 fold change values
        sep: Delimiter for CSV/TSV files (auto-detected if None)

    Returns:
        DataFrame with gene_id and lfc columns
    """
    if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath)
    elif filepath.endswith('.tsv') or filepath.endswith('.tab'):
        df = pd.read_csv(filepath, sep='\t')
    elif sep is not None:
        df = pd.read_csv(filepath, sep=sep)
    else:
        # Auto-detect delimiter
        df = pd.read_csv(filepath, sep=None, engine='python')

    # Find columns case-insensitively
    col_map = {c.lower(): c for c in df.columns}

    actual_gene_col = col_map.get(gene_col.lower(), gene_col)
    actual_lfc_col = col_map.get(lfc_col.lower(), lfc_col)

    if actual_gene_col not in df.columns:
        raise ValueError(f"Gene column '{gene_col}' not found. Available: {list(df.columns)}")
    if actual_lfc_col not in df.columns:
        raise ValueError(f"LFC column '{lfc_col}' not found. Available: {list(df.columns)}")

    # Standardize column names
    result = pd.DataFrame({
        'gene_id': df[actual_gene_col],
        'lfc': pd.to_numeric(df[actual_lfc_col], errors='coerce')
    }).dropna()

    return result


def create_lfc_mapping(source_df, target_df, tolerance=None, unique=False):
    """
    Map genes between two annotation versions using LFC correlation.

    For each gene in source_df, find the gene in target_df with the
    closest matching LFC value.

    Args:
        source_df: DataFrame with 'gene_id' and 'lfc' columns (reference)
        target_df: DataFrame with 'gene_id' and 'lfc' columns (to map)
        tolerance: Maximum LFC difference to consider a valid match (None = no limit)
        unique: If True, ensure one-to-one mapping using Hungarian algorithm

    Returns:
        DataFrame with mapping: source_gene, source_lfc, target_gene, target_lfc, lfc_diff
    """
    if unique:
        return _create_unique_mapping(source_df, target_df, tolerance)

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

        if tolerance is None or best_diff <= tolerance:
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


def _create_unique_mapping(source_df, target_df, tolerance=None):
    """
    Create one-to-one mapping using Hungarian algorithm.
    """
    try:
        from scipy.optimize import linear_sum_assignment
    except ImportError:
        print("Warning: scipy.optimize not available, falling back to greedy matching")
        return create_lfc_mapping(source_df, target_df, tolerance, unique=False)

    # Create cost matrix (LFC differences)
    cost_matrix = np.abs(
        source_df['lfc'].values[:, np.newaxis] -
        target_df['lfc'].values[np.newaxis, :]
    )

    # Find optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    mappings = []
    for i, j in zip(row_ind, col_ind):
        diff = cost_matrix[i, j]
        if tolerance is None or diff <= tolerance:
            mappings.append({
                'source_gene': source_df.iloc[i]['gene_id'],
                'source_lfc': source_df.iloc[i]['lfc'],
                'target_gene': target_df.iloc[j]['gene_id'],
                'target_lfc': target_df.iloc[j]['lfc'],
                'lfc_diff': diff
            })

    return pd.DataFrame(mappings).sort_values('lfc_diff')


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
        'direction_matches': int(direction_match),
        'lfc_diff_mean': np.mean(lfc_diffs),
        'lfc_diff_median': np.median(lfc_diffs),
        'lfc_diff_std': np.std(lfc_diffs),
        'lfc_diff_max': np.max(lfc_diffs),
        'lfc_diff_min': np.min(lfc_diffs)
    }


def plot_mapping_validation(mapping_df, output_path, title='Gene Mapping Validation'):
    """
    Create scatter plot comparing LFC values between annotation versions.

    Args:
        mapping_df: DataFrame from create_lfc_mapping()
        output_path: Path to save the plot (PNG or PDF)
        title: Plot title
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not available, skipping plot generation")
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    source_lfc = mapping_df['source_lfc'].values
    target_lfc = mapping_df['target_lfc'].values

    # Scatter plot
    ax1 = axes[0]
    ax1.scatter(source_lfc, target_lfc, alpha=0.6, s=50, c='steelblue',
                edgecolors='white', linewidth=0.5)

    # Add regression line
    slope, intercept, r_value, _, _ = stats.linregress(source_lfc, target_lfc)
    x_line = np.linspace(min(source_lfc), max(source_lfc), 100)
    ax1.plot(x_line, slope * x_line + intercept, 'r-',
             linewidth=2, label=f'R² = {r_value**2:.4f}')

    # Add identity line
    lim = max(abs(min(source_lfc)), abs(max(source_lfc)),
              abs(min(target_lfc)), abs(max(target_lfc))) * 1.1
    ax1.plot([-lim, lim], [-lim, lim], 'k--', alpha=0.5, label='y = x')

    ax1.set_xlabel('Source LFC', fontsize=12)
    ax1.set_ylabel('Target LFC', fontsize=12)
    ax1.set_title(f'{title}\n(n={len(mapping_df)} genes)', fontsize=12)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax1.axvline(x=0, color='gray', linestyle='-', alpha=0.3)

    # Bland-Altman plot
    ax2 = axes[1]
    mean_lfc = (source_lfc + target_lfc) / 2
    diff_lfc = source_lfc - target_lfc

    ax2.scatter(mean_lfc, diff_lfc, alpha=0.6, s=50, c='steelblue',
                edgecolors='white', linewidth=0.5)

    mean_diff = np.mean(diff_lfc)
    std_diff = np.std(diff_lfc)
    ax2.axhline(y=mean_diff, color='red', linestyle='-',
                label=f'Mean: {mean_diff:.4f}')
    ax2.axhline(y=mean_diff + 1.96*std_diff, color='red',
                linestyle='--', alpha=0.7, label=f'±1.96 SD')
    ax2.axhline(y=mean_diff - 1.96*std_diff, color='red',
                linestyle='--', alpha=0.7)
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)

    ax2.set_xlabel('Mean LFC (Source + Target)/2', fontsize=12)
    ax2.set_ylabel('Difference (Source - Target)', fontsize=12)
    ax2.set_title('Bland-Altman Agreement Plot', fontsize=12)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Validation plot saved to: {output_path}")


def print_validation_report(stats_dict):
    """Print a formatted validation report."""
    print("\n" + "=" * 60)
    print("GENE MAPPING VALIDATION REPORT")
    print("=" * 60)

    print(f"\nMapped Genes: {stats_dict['n_mapped']}")

    print("\nCorrelation Statistics:")
    print(f"  Pearson R²:  {stats_dict['pearson_r_squared']:.4f}")
    print(f"  Pearson R:   {stats_dict['pearson_r']:.4f} (p={stats_dict['pearson_p']:.2e})")
    print(f"  Spearman R:  {stats_dict['spearman_r']:.4f} (p={stats_dict['spearman_p']:.2e})")

    print("\nDirection Agreement:")
    print(f"  Matching:    {stats_dict['direction_matches']}/{stats_dict['n_mapped']} "
          f"({stats_dict['direction_agreement_pct']:.1f}%)")

    print("\nLFC Difference Statistics:")
    print(f"  Mean:        {stats_dict['lfc_diff_mean']:.6f}")
    print(f"  Median:      {stats_dict['lfc_diff_median']:.6f}")
    print(f"  Std Dev:     {stats_dict['lfc_diff_std']:.6f}")
    print(f"  Min:         {stats_dict['lfc_diff_min']:.6f}")
    print(f"  Max:         {stats_dict['lfc_diff_max']:.6f}")

    # Quality assessment
    print("\nQuality Assessment:")
    r_sq = stats_dict['pearson_r_squared']
    dir_pct = stats_dict['direction_agreement_pct']

    if r_sq > 0.99 and dir_pct == 100:
        print("  Status: EXCELLENT - Near-perfect mapping")
    elif r_sq > 0.95 and dir_pct > 95:
        print("  Status: GOOD - High-quality mapping")
    elif r_sq > 0.90 and dir_pct > 90:
        print("  Status: ACCEPTABLE - Reasonable mapping with some discrepancies")
    else:
        print("  Status: POOR - Mapping may not be reliable")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Map gene IDs between annotation versions using LFC correlation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--source', required=True,
                        help='Source DEG file (reference, e.g., paper results)')
    parser.add_argument('--target', required=True,
                        help='Target DEG file (to map, e.g., your results)')
    parser.add_argument('--output', required=True,
                        help='Output mapping file (CSV)')
    parser.add_argument('--plot',
                        help='Output validation plot (PNG/PDF)')

    parser.add_argument('--source-gene-col', default='Gene_ID',
                        help='Gene ID column name in source file (default: Gene_ID)')
    parser.add_argument('--source-lfc-col', default='LFC',
                        help='LFC column name in source file (default: LFC)')
    parser.add_argument('--target-gene-col', default='Gene_ID',
                        help='Gene ID column name in target file (default: Gene_ID)')
    parser.add_argument('--target-lfc-col', default='log2FoldChange',
                        help='LFC column name in target file (default: log2FoldChange)')

    parser.add_argument('--tolerance', type=float, default=None,
                        help='Maximum LFC difference for valid match (default: no limit)')
    parser.add_argument('--unique', action='store_true',
                        help='Ensure one-to-one mapping (uses Hungarian algorithm)')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress detailed output')

    args = parser.parse_args()

    # Load data
    if not args.quiet:
        print(f"Loading source: {args.source}")
    source_df = load_deg_file(args.source, args.source_gene_col, args.source_lfc_col)
    if not args.quiet:
        print(f"  Loaded {len(source_df)} genes")

    if not args.quiet:
        print(f"Loading target: {args.target}")
    target_df = load_deg_file(args.target, args.target_gene_col, args.target_lfc_col)
    if not args.quiet:
        print(f"  Loaded {len(target_df)} genes")

    # Create mapping
    if not args.quiet:
        print("Creating LFC-based gene mapping...")
    mapping = create_lfc_mapping(source_df, target_df, args.tolerance, args.unique)
    if not args.quiet:
        print(f"  Mapped {len(mapping)} genes")

    if len(mapping) == 0:
        print("ERROR: No genes could be mapped!")
        sys.exit(1)

    # Validate
    stats_dict = validate_mapping(mapping)

    if not args.quiet:
        print_validation_report(stats_dict)

    # Save mapping
    mapping.to_csv(args.output, index=False)
    print(f"Mapping saved to: {args.output}")

    # Generate plot
    if args.plot:
        plot_mapping_validation(mapping, args.plot)


if __name__ == '__main__':
    main()
