
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde, norm, multivariate_normal
from scipy.special import ndtr
from scipy import interpolate
print("=== 1. Data loading and preprocessing ===")

df = pd.read_csv('data/ods032.csv', sep=';')
print(f"Raw data rows: {len(df)}")

df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)

measured = df['Measured & Upscaled'].values
forecast = df['Most recent forecast'].values

mask = (measured != 0) | (forecast != 0)
measured_day = measured[mask]
forecast_day = forecast[mask]

print(f"Rows after filtering night: {len(measured_day)}")

print("\n=== 2. Compute forecast error ===")

error = measured_day - forecast_day

error_norm = error / np.std(measured_day)

print(f"Error statistics:")
print(f"  mean: {np.mean(error_norm):.4f}")
print(f"  std: {np.std(error_norm):.4f}")
print(f"  min: {np.min(error_norm):.4f}")
print(f"  max: {np.max(error_norm):.4f}")

print("\n=== 3. Reshape to time-series structure ===")

n_timepoints = 48
n_days = len(error_norm) // n_timepoints

error_norm = error_norm[:n_days * n_timepoints]

error_matrix = error_norm.reshape(n_days, n_timepoints)

print(f"Error matrix shape: {error_matrix.shape}")
print(f"  periods: {n_days}")
print(f"  timepoints per period: {n_timepoints}")
print(f"  note: these 48 points are all generating periods, night zeros filtered")

print("\n=== 4. Compute temporal correlation ===")

temp_corr = np.corrcoef(error_matrix, rowvar=False)
print(f"Temporal correlation matrix shape: {temp_corr.shape}")

plt.figure(figsize=(10, 10))
mask_upper = np.triu(np.ones_like(temp_corr, dtype=bool))
sns.heatmap(temp_corr, annot=False, fmt=".2f", mask=mask_upper, cmap='coolwarm')
plt.title('Solar Forecasting Error Temporal Correlation')
plt.tight_layout()
plt.savefig('data/solar_error_temporal_correlation.png', dpi=300)
print("Temporal correlation heatmap saved: data/solar_error_temporal_correlation.png")
plt.close()

print("\n=== 5. Fit marginal distribution with KDE ===")

marginal_error = error_matrix.flatten()

kde = gaussian_kde(marginal_error)

x = np.linspace(np.min(marginal_error), np.max(marginal_error), 100)
kde_pdf = kde.pdf(x)

mu, std = np.mean(marginal_error), np.std(marginal_error)
p = norm.pdf(x, mu, std)

plt.figure(figsize=(14, 5))
plt.hist(marginal_error, bins=100, alpha=0.5, label='Original samples', density=True)
plt.plot(x, kde_pdf, 'k', linewidth=2, label='Gaussian KDE')
plt.plot(x, p, 'r', linewidth=2, label='Gaussian fit')
plt.xlabel('Normalized forecasting error')
plt.ylabel('Density')
plt.legend()
plt.title('Solar Forecasting Error Marginal Distribution')
plt.tight_layout()
plt.savefig('data/solar_error_marginal_distribution.png', dpi=300)
print("Marginal distribution figure saved: data/solar_error_marginal_distribution.png")
plt.close()

print("\n=== 6. Generate temporally correlated samples via Copula ===")

n_scenario = 200000
print(f"Number of scenarios: {n_scenario}")

mvnorm = multivariate_normal(mean=np.zeros(temp_corr.shape[0]), cov=temp_corr)
samples_gaussian = mvnorm.rvs(size=n_scenario, random_state=0)
print(f"Multivariate normal samples shape: {samples_gaussian.shape}")

norm_dist = norm()
samples_uniform = norm_dist.cdf(samples_gaussian)
print(f"Uniform samples shape: {samples_uniform.shape}")

stdev = np.sqrt(kde.covariance)[0, 0]
xmax = np.max(marginal_error)
xmin = np.min(marginal_error)
minmax_dist = xmax - xmin

xx = np.linspace(xmin - 0.*minmax_dist, xmax + 0.*minmax_dist, 5000)

print("Computing KDE CDF (batched to save memory)...")
n_resample = 50000
n = kde.resample(n_resample, seed=0).flatten()

batch_size = 1000
kde_cdf = np.zeros(len(xx))
for i in range(0, len(xx), batch_size):
    batch_end = min(i + batch_size, len(xx))
    xx_batch = xx[i:batch_end]
    kde_cdf[i:batch_end] = ndtr(np.subtract.outer(xx_batch, n)/stdev).mean(axis=1)
    if (i // batch_size) % 5 == 0:
        print(f"  progress: {batch_end}/{len(xx)}")

print("KDE CDF computation done")

kde_cdf_inv_func = interpolate.interp1d(kde_cdf, xx, kind='cubic',
                                        bounds_error=False, fill_value='extrapolate')

samples_kde_corr = np.vstack([kde_cdf_inv_func(samples_uniform[:, i])
                               for i in range(temp_corr.shape[0])]).T
print(f"Final temporally correlated samples shape: {samples_kde_corr.shape}")

print("\n=== 7. Validate generated samples ===")

plt.figure(figsize=(14, 5))
plt.hist(samples_kde_corr.flatten(), bins=100, alpha=0.5,
         label='Generated samples', density=True)
plt.hist(marginal_error, bins=100, alpha=0.5,
         label='Original samples', density=True, color='olive')
plt.plot(x, p, 'r', linewidth=2, label='Gaussian fit')
plt.xlim(np.percentile(marginal_error, 1), np.percentile(marginal_error, 99))
plt.xlabel('Normalized forecasting error')
plt.ylabel('Density')
plt.legend()
plt.title('Comparison of Generated and Original Samples')
plt.tight_layout()
plt.savefig('data/solar_error_comparison.png', dpi=300)
print("Sample comparison figure saved: data/solar_error_comparison.png")
plt.close()

temp_corr_gen = np.corrcoef(samples_kde_corr, rowvar=False)

fig, axs = plt.subplots(1, 2, figsize=(16, 7))
axs[0].set_title('Original samples')
sns.heatmap(temp_corr, annot=False, fmt=".2f", mask=mask_upper, ax=axs[0], cmap='coolwarm')
axs[1].set_title('Generated samples')
sns.heatmap(temp_corr_gen, annot=False, fmt=".2f", mask=mask_upper, ax=axs[1], cmap='coolwarm')
axs[0].set_xlabel('Time')
axs[0].set_ylabel('Time')
axs[1].set_xlabel('Time')
plt.tight_layout()
plt.savefig('data/solar_error_temporal_correlation_comparison.png', dpi=300)
print("Temporal correlation comparison figure saved: data/solar_error_temporal_correlation_comparison.png")
plt.close()

print("\n=== 8. Save results ===")

np.save('data/solar_temporal_correlated_error_samples.npy', samples_kde_corr)
print(f"Error samples saved: data/solar_temporal_correlated_error_samples.npy")
print(f"  shape: {samples_kde_corr.shape}")

solar_forecast_prototype = forecast_day[:48]

np.save('data/solar_forecast_prototype.npy', solar_forecast_prototype)
print(f"Solar forecast prototype saved: data/solar_forecast_prototype.npy")
print(f"  shape: {solar_forecast_prototype.shape}")
print(f"  note: these 48 points correspond to daytime generating-period forecasts")

print("\n=== Solar error generalization done ===")
print(f"Generated {n_scenario} solar error scenarios")
print(f"Each scenario has {n_timepoints} timepoints (all daytime generating periods)")
print("\n=== Usage notes ===")
print("When building full 24-hour scenarios:")
print("  1. Night hours (19-4): set directly to 0")
print("  2. Day hours (5-18): use forecast + error samples")
print("  3. Ensure final scenario values are non-negative (clip(0, None))")
