# Schema Update Plan - Add New Columns

**Date**: 2026-01-24  
**Version**: 0.3.0 → 0.4.0  
**New Columns**: `n_catch`, `tot_catch_kg`, `tot_catch_price`

---

## Summary

Adding 3 new columns to the API schema:
- **`n_catch`**: Catch sequence number within a trip (catch-level)
- **`tot_catch_kg`**: Total catch weight for entire trip in kg (trip-level aggregate)
- **`tot_catch_price`**: Total price for entire trip in local currency (trip-level aggregate)

**Total columns**: 18 → 20

---

## Implementation Checklist

### Phase 1: Core Schema Updates

- [ ] **1.1** Update `src/peskas_api/schema/scopes.py`
  - Add `n_catch` to `catch_info` scope (6 → 7 columns)
  - Add `tot_catch_kg` and `tot_catch_price` to `trip_info` scope (13 → 15 columns)
  - Total: 20 columns across both scopes

### Phase 2: Documentation Updates

- [ ] **2.1** Update `README.md`
  - Section: "Data Schema" (line ~260)
  - Update column counts: 18 → 20
  - Add new column descriptions
  - Update trip-level columns: 13 → 15
  - Update catch-level columns: 6 → 7

- [ ] **2.2** Update `docs/API_REFERENCE.md`
  - Update any references to column counts
  - Add examples showing new columns

- [ ] **2.3** Update `NEWS.md`
  - Add entry for v0.4.0 with new columns

### Phase 3: Metadata (if applicable)

- [ ] **3.1** Check `src/peskas_api/schema/field_metadata.py`
  - Verify `n_catch` definition exists
  - Add `tot_catch_kg` definition
  - Add `tot_catch_price` definition

### Phase 4: Testing & Verification

- [ ] **4.1** Run all tests to ensure nothing breaks
- [ ] **4.2** Verify scope queries return correct columns
- [ ] **4.3** Test with actual data if available
- [ ] **4.4** Check linting

### Phase 5: Examples & Integration Guides

- [ ] **5.1** Update example responses in README
- [ ] **5.2** Update response format examples
- [ ] **5.3** Verify interactive docs (/docs) show new fields

---

## Detailed Changes

### 1. scopes.py

**BEFORE**:
```python
"trip_info": [
    "survey_id", "trip_id", "landing_date", "gaul_1_code", "gaul_1_name",
    "gaul_2_code", "gaul_2_name", "n_fishers", "trip_duration_hrs",
    "gear", "vessel_type", "catch_habitat", "catch_outcome",
],  # 13 columns

"catch_info": [
    "survey_id", "trip_id", "catch_taxon", "length_cm", "catch_kg", "catch_price",
],  # 6 columns
```

**AFTER**:
```python
"trip_info": [
    "survey_id", "trip_id", "landing_date", "gaul_1_code", "gaul_1_name",
    "gaul_2_code", "gaul_2_name", "n_fishers", "trip_duration_hrs",
    "gear", "vessel_type", "catch_habitat", "catch_outcome",
    "tot_catch_kg", "tot_catch_price",  # NEW: trip-level aggregates
],  # 15 columns

"catch_info": [
    "survey_id", "trip_id", "catch_taxon", "n_catch", "length_cm", 
    "catch_kg", "catch_price",  # NEW: n_catch added
],  # 7 columns
```

### 2. README.md - Data Schema Section

**Update from**:
```markdown
The current schema includes 18 columns per record:

**Trip-level columns** (13 columns):
...

**Catch-level columns** (6 columns):
...
```

**Update to**:
```markdown
The current schema includes 20 columns per record:

**Trip-level columns** (15 columns):
- ... (existing columns)
- `tot_catch_kg`: Total catch weight for entire trip (kg)
- `tot_catch_price`: Total price for entire trip (local currency)

**Catch-level columns** (7 columns):
- ... (existing columns)
- `n_catch`: Catch sequence number within trip
```

### 3. Column Placement Logic

**`n_catch`** → catch_info:
- Rationale: Identifies individual catches within a trip
- Position: After `catch_taxon`, before `length_cm`

**`tot_catch_kg`, `tot_catch_price`** → trip_info:
- Rationale: Aggregated metrics at trip level
- Position: At end of trip_info scope

---

## Expected Outcomes

After implementation:

1. **API Responses**:
   - No scope: Returns all 20 columns
   - `scope=trip_info`: Returns 15 columns (including new totals)
   - `scope=catch_info`: Returns 7 columns (including n_catch)

2. **Documentation**:
   - All column counts updated
   - New columns clearly described
   - Examples show new fields

3. **Tests**:
   - All existing tests still pass
   - Scope queries work correctly

4. **Backward Compatibility**:
   - ✅ Fully backward compatible (adding columns only)
   - ✅ Existing queries continue to work
   - ✅ New columns available immediately

---

## Rollout Plan

1. Update schema files (scopes.py)
2. Update all documentation
3. Run tests
4. Update NEWS.md
5. Commit changes
6. Deploy (no breaking changes)

---

**Status**: Ready to execute
**Breaking Changes**: None
**Migration Required**: No
