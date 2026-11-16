"""Create synthetic distributions that have identical group means and sample SDs.

Inspired by Fig. 1 of Weissgerber et al. (2015):
https://doi.org/10.1371/journal.pbio.1002128

Run from the repository root:
    uv run python src/data_processing/candidates/create_same_mean_sd_data.py

These are deliberately constructed teaching data, not the paper's observations.
Distribution quantiles give reproducible shapes; an affine transformation makes
the sample mean and SD match exactly up to floating-point precision. Observation
order is shuffled with a fixed seed. No inferential tests are performed.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import expon, norm


OUTPUT = Path(__file__).resolve().parents[3] / 'data' / 'same_mean_sd.csv'
SCENARIOS = ['Symmetric', 'Outlier', 'Bimodal', 'Right-skewed', 'Unequal n']
MEANS = {'A': 12.0, 'B': 17.0}
SD = 4.0


def normal_quantiles(n):
    return norm.ppf((np.arange(n) + 0.5) / n)


def match_mean_sd(values, mean, sd):
    values = np.asarray(values, dtype=float)
    return mean + sd * (values - values.mean()) / values.std(ddof=1)


def create_dataset():
    rng = np.random.default_rng(42)
    records = []
    for dataset in SCENARIOS:
        for group, mean in MEANS.items():
            n = 8 if dataset == 'Unequal n' and group == 'B' else 24
            if dataset == 'Outlier' and group == 'B':
                values = np.r_[0.15 * normal_quantiles(n - 1), 5.5]
            elif dataset == 'Bimodal':
                cluster = 0.18 * normal_quantiles(n // 2)
                values = np.r_[cluster - 1.5, cluster + 1.5]
            elif dataset == 'Right-skewed':
                values = expon.ppf((np.arange(n) + 0.5) / n)
            else:
                values = normal_quantiles(n)

            values = rng.permutation(match_mean_sd(values, mean, SD))
            for observation, value in enumerate(values, start=1):
                records.append({
                    'dataset': dataset,
                    'group': group,
                    'observation': observation,
                    'value': value,
                })

    data = pd.DataFrame(records)
    summaries = data.groupby(['dataset', 'group'])['value'].agg(['mean', 'std'])
    expected_means = summaries.index.get_level_values('group').map(MEANS).to_numpy()
    np.testing.assert_allclose(summaries['mean'], expected_means, rtol=0, atol=1e-12)
    np.testing.assert_allclose(summaries['std'], SD, rtol=0, atol=1e-12)
    return data


if __name__ == '__main__':
    data = create_dataset()
    data.to_csv(OUTPUT, index=False)
    print(f'Saved {len(data)} observations to {OUTPUT}')
    print(data.groupby(['dataset', 'group'], sort=False)['value'].agg(['size', 'mean', 'std']))
