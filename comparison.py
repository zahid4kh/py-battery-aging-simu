import matplotlib.pyplot as plt
import numpy as np


def plot_krupp_comparison(results):
    plt.figure(figsize=(12, 8))

    dod_20 = [r for r in results if r['dod'] == 0.2]
    dod_50 = [r for r in results if r['dod'] == 0.5]
    dod_80 = [r for r in results if r['dod'] == 0.8]

    plt.subplot(2, 2, 1)
    plt.bar(['20% DoD', '50% DoD', '80% DoD'],
            [np.mean([r['capacity_loss_percent'] for r in dod_20]),
             np.mean([r['capacity_loss_percent'] for r in dod_50]),
             np.mean([r['capacity_loss_percent'] for r in dod_80])])
    plt.title('Capacity Loss vs DoD')
    plt.ylabel('Capacity Loss (%)')

    plt.tight_layout()
    plt.savefig('krupp_validation_results.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    print("Run krupp_validation.py first to generate results!")
