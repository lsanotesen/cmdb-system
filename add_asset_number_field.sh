#!/bin/bash
mysql -h localhost -P 3308 -u cmdb -pcmdb123 cmdb << 'EOF'
ALTER TABLE cmdb_officepart ADD COLUMN asset_number VARCHAR(100) NULL UNIQUE AFTER model;
EOF