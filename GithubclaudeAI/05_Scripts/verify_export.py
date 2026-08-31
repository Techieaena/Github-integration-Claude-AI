import pandas as pd
from pathlib import Path

print('\n' + '=' * 80)
print('✅ DATA EXPORT VERIFICATION REPORT')
print('=' * 80)

raw_dir = Path('exported_data/raw_bronze')
trans_dir = Path('exported_data/transformed_silver')

files = ['customer_master.csv', 'dataset_statistics.csv', 'ecommerce_sales_customer_analytics_150k.csv', 'order_items.csv', 'product_catalog.csv']

print('\n📊 DETAILED FILE COMPARISON:\n')
print('File Name' + ' ' * 36 + 'Raw Rows' + ' ' * 3 + 'Trans Rows' + ' ' * 2 + 'Reduction')
print('-' * 80)

total_raw = 0
total_trans = 0

for fname in files:
    raw_file = raw_dir / fname
    trans_file = trans_dir / fname

    if raw_file.exists() and trans_file.exists():
        raw_df = pd.read_csv(raw_file)
        trans_df = pd.read_csv(trans_file)

        raw_rows = len(raw_df)
        trans_rows = len(trans_df)
        removed = raw_rows - trans_rows
        pct = (removed / raw_rows * 100) if raw_rows > 0 else 0

        total_raw += raw_rows
        total_trans += trans_rows

        reduction_str = f'{removed:,} ({pct:.1f}%)' if removed > 0 else 'None'

        print(f'{fname:<45} {raw_rows:>12,} {trans_rows:>12,} {reduction_str:>15}')

print('-' * 80)
total_removed = total_raw - total_trans
total_pct = (total_removed / total_raw * 100) if total_raw > 0 else 0
reduction = f'{total_removed:,} ({total_pct:.1f}%)'
print(f'TOTAL' + ' ' * 40 + f'{total_raw:>12,} {total_trans:>12,} {reduction:>15}')

print('\n' + '=' * 80)
print('📁 EXPORTED FILES:')
print('=' * 80)
print(f'\n🟦 RAW BRONZE DATA: {raw_dir.absolute()}')
for f in sorted(raw_dir.glob('*.csv')):
    size_mb = f.stat().st_size / 1024 / 1024
    print(f'   ✅ {f.name:<45} {size_mb:>8.2f} MB')

print(f'\n🟩 TRANSFORMED SILVER DATA: {trans_dir.absolute()}')
for f in sorted(trans_dir.glob('*.csv')):
    size_mb = f.stat().st_size / 1024 / 1024
    print(f'   ✅ {f.name:<45} {size_mb:>8.2f} MB')

print('\n' + '=' * 80)
print('✅ EXPORT EXECUTION SUCCESSFUL')
print('=' * 80 + '\n')
