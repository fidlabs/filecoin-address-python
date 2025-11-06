#!/bin/bash
# Build script that fixes metadata version compatibility issue

set -e

echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "Building package..."
python -m build

echo "Fixing metadata version for twine compatibility..."
cd dist

# Fix wheel
if [ -f filecoin_address-*.whl ]; then
    WHEEL_FILE=$(ls filecoin_address-*.whl | head -1)
    echo "Fixing $WHEEL_FILE..."
    
    # Extract METADATA
    unzip -q "$WHEEL_FILE" filecoin_address-*.dist-info/METADATA
    
    # Fix metadata version
    METADATA_FILE=$(ls filecoin_address-*.dist-info/METADATA | head -1)
    sed -i '' 's/Metadata-Version: 2.4/Metadata-Version: 2.3/' "$METADATA_FILE"
    
    # Update wheel
    zip -q "$WHEEL_FILE" "$METADATA_FILE"
    
    # Cleanup
    rm -rf filecoin_address-*.dist-info
    
    echo "Fixed metadata version in $WHEEL_FILE"
fi

# Fix source distribution using Python to preserve tar metadata
if [ -f filecoin_address-*.tar.gz ]; then
    TAR_FILE=$(ls filecoin_address-*.tar.gz | head -1)
    echo "Fixing $TAR_FILE..."
    
    python3 << 'PYTHON_SCRIPT'
import tarfile
import os
import re
from io import BytesIO

tar_file = [f for f in os.listdir('.') if f.endswith('.tar.gz')][0]
temp_tar = tar_file + '.tmp'

# Read original tar and create new one with fixed metadata
with tarfile.open(tar_file, 'r:gz') as tar_in, tarfile.open(temp_tar, 'w:gz') as tar_out:
    for member in tar_in:
        # Read the file content
        file_obj = tar_in.extractfile(member)
        if file_obj:
            data = file_obj.read()
            
            # Fix metadata version in PKG-INFO files
            if member.name.endswith('PKG-INFO'):
                data = re.sub(b'Metadata-Version: 2.4', b'Metadata-Version: 2.3', data)
            
            # Update member size and create BytesIO object for the data
            member.size = len(data)
            data_io = BytesIO(data)
            tar_out.addfile(member, data_io)
        else:
            # Directory or other non-file entry
            tar_out.addfile(member)

# Replace original with fixed version
os.replace(temp_tar, tar_file)
print(f"Fixed metadata version in {tar_file}")
PYTHON_SCRIPT
    
    echo "Fixed metadata version in $TAR_FILE"
fi

cd ..

echo "Verifying build..."
python -m twine check dist/*

echo "Build complete! Files in dist/:"
ls -lh dist/

