# Processed Jail Data: README

This README describes the structure and logic behind the processed jail datasets, derived from raw administrative records.

---

## `bookings`
- **Primary key**: `booking_id` (one row per booking)
- **Final output includes**:
  - `booking_id`, `group_type` (primary or secondary)
  - `gender`, `age_at_booking`
  - `booking_date_time`, `release_date_time`
  - `release_date_or_last_date_of_record` (fills with '2019-02-28' for bookings not released during the observation window)
  - `intermediate_release_date` (captures earlier release dates if any)
  - `status` (Released / Not Released)
  - `length_of_stay` (in days, using `release_date_or_last_date_of_record`)
  - `race`, `all_crime_types`, `most_severe_crime_type` (only for primary group)

---

## `bed_move_event`
- **Primary key**: `event_id` = `'bm_' + booking_id + bed_start_date_time`
- **Final output includes**:  
  - `event_id`, `booking_id`, `bed_start_date_time`
  - `bed_assignment`, `facility`, `section`, `cell`

---

## `scan_movement_event`
- **Primary key**: `event_id` = `'me_' + booking_id + booking_movement_number + count_within_booking_and_time`
- **Filters out** rows without `movement_date_time`
- **Final output includes**:
  - `event_id`, `booking_id`, `movement_date_time`
  - `movement_reason`, `scan_location`, `move_from`, `move_to`

---

## `disciplinary_event`
- **Primary key**: `event_id` = `'de_' + booking_id + disciplinary_event_network_id`
- Renames `incident_number` to `disciplinary_event_network_id`
- Combines `incidents` and `infractions` using `booking_id` and `disciplinary_event_network_id`
- Populates `incident_detail_id` and `infraction_detail_id`
- Groups to ensure one row per unique disciplinary event per booking

---

## `incident_details` and `infraction_details`
- **Primary key**: `'inc_' or 'inf_' + booking_id + disciplinary_event_network_id + _ + details_count`
- `incident_details` captures:
  - Type of incident (e.g., physical altercation)
  - Broad category (e.g., violence)
  - `incident_details_count`
- `infraction_details` captures:
  - Type of infraction
  - `infraction_details_count`

---

## `events_log`
- **Primary key**: `event_id`
- Combines:
  - `bed_move_event`, `scan_movement_event`, `disciplinary_event`
- `event_category`: one of `'bed_move_event'`, `'scan_movement_event'`, `'disciplinary_event'`
- `event_description`:
  - `bed_assignment` for bed moves
  - `movement_reason` for scan movements
  - `'incident'`, `'infraction'`, or `'incident and infraction'` based on presence of detail IDs
- **Final columns**:
  - `event_id`, `booking_id`, `event_date_time`
  - `event_category`, `event_description`


---

## Additional Processing Notes

For all datasets, column names are standardized to lowercase and use underscores.

### Bookings
- Combines booking sample and non-sample spreadsheets.
- Adds `group_type` column:
  - `'primary group'` for bookings in the sample
  - `'secondary group'` for others
  - In 1,004 cases where a `booking_id` appears in both, it is assigned to the primary group.
- Deduplicates bookings with multiple release dates:
  - Keeps the latest `release_date_time`
  - Stores other distinct release dates (on a different day) as `intermediate_release_date`
- Adds `release_date_or_last_date_of_record` to fill missing values using the latest observation date.
- Calculates `length_of_stay` as the difference between `booking_date_time` and `release_date_or_last_date_of_record`.
- Merges in `race` and `charge` data (race only for primary group).
- Aggregates `all_crime_types` and identifies `most_severe_crime_type` (F/M/O).

### Housing
- Cleans sample and non-sample datasets separately with identical logic.
- Deduplicates rows with the same `bed_assignment` and `bed_start_date_time` but different end times:
  - Keeps the row with the latest `bed_end_date_time`
- Removes rows where `bed_start_date_time == bed_end_date_time`
- If multiple rows share a `bed_start_date_time`, keeps the one with the longest `bed_end_date_time`.

### Movements
- Drops exact duplicate rows.
- Removes rows where `movement_date_time` is null.

### Incidents / Infractions
- Removes duplicate rows.
- Adds `incident_detail_id` and `infraction_detail_id` for linking with structured detail tables.

### Disciplinary Events
- Combines incidents and infractions using shared keys: `booking_id`, `incident_number`, `incident_date_time`, `location`, and `facility`.
- Retains a separate row for each unique `booking_id` + `disciplinary_event_network_id`
- Adds detail IDs for reference.

### Events Log
- Merges `bed_move_event`, `scan_movement_event`, and `disciplinary_event`.
- Standardizes into: `event_id`, `booking_id`, `event_date_time`, `event_category`, `event_description`
- `event_description` values:
  - `bed_assignment` for bed moves
  - `movement_reason` for scan movements
  - `'incident'`, `'infraction'`, or `'incident and infraction'` for disciplinary events
