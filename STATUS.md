# Kuai Project Status

## Phase 2.4

### Blocks (11 total)

| Block | Type | Idempotent | Description |
|-------|------|------------|-------------|
| enter | nav | - | Change working directory |
| list | read | - | List directory contents |
| filter | read | - | Filter by extension |
| pick | nav | - | Select single file/dir |
| copy | write | false | Copy to target dir |
| move | write | false | Move to target dir |
| rename | write | false | Rename single object |
| batch_rename | write | false | Batch prefix, skips existing |
| zip | transform | false | File/collection -> archive |
| unzip | transform | false | Archive -> file collection |
| delete | write | false | Delete file/collection |

### Object Type Flow

file/dir -> zip -> archive -> unzip -> file_collection
file_collection -> zip -> archive
archive -> move/copy/rename (type preserved)

### Test System (78 tests)

L1 Unit: 57 tests (contract, empty, normal, idempotent, pollution, fs)
L2 Integration: 10 tests (object chain, roundtrip, double exec)
L3 Invariants: 11 tests (type preservation, absolute paths, read-only)

### Design Principles

See docs/DESIGN_PRINCIPLES.md

### Resolved Issues

1. State/FS desync after batch_rename
2. Object type overwritten by move/copy
3. Idempotent batch_rename and delete
4. Filter results polluted by batch_rename
5. Parameter field leakage

### Known Limitations

- Most write blocks are non-idempotent
- No execution history (usage.db)
- No conditionals or loops
- No rollback or error recovery
- No parallel execution

### Next Steps

1. Standardize tests for replace/read blocks
2. Add send block
3. Add conditionals
4. Implement usage.db
