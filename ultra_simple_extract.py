# 最简单的解压脚本
import zipfile

# 直接指定路径
zip_path = 'epass_flasher/buildroot-a2.6.0.zip'
out_path = 'epass_flasher'

print('Starting extraction...')

# 尝试解压
try:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        print('Opening zip file...')
        print(f'Files in zip: {len(zf.namelist())}')
        print('Extracting...')
        zf.extractall(out_path)
        print('Extraction completed successfully!')
except Exception as e:
    print(f'Error: {e}')

print('Script finished.')
