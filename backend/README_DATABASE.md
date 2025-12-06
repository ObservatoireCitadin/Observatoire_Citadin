# Supabase Database Documentation

## Overview

This document describes the database structure hosted on Supabase (PostgreSQL) for the Observatoire Citadin application. The database contains data from French municipal elections, including cities, electoral lists, promises, and criteria for comparison.

**Database Details:**
- **Host:** aws-1-eu-west-3.pooler.supabase.com
- **Database:** postgres
- **Total Tables:** 21
- **Total Records:** ~1,146,000 rows

---

## Table Categories

### 1. Django Authentication & Admin Tables

#### `auth_user`
**Purpose:** Stores user accounts for the Django application.

**Key Fields:**
- `id` (PK) - User ID
- `username` - Login username
- `password` - Hashed password
- `email` - User email address
- `first_name`, `last_name` - User's name
- `is_staff` - Can access Django admin interface
- `is_superuser` - Has all permissions
- `is_active` - Account is enabled
- `date_joined`, `last_login` - Timestamps

**Relationships:**
- Referenced by `django_admin_log` (admin actions)
- Referenced by `compare_liste_auteur` (list authors)
- Referenced by `users_profile` (extended profile)
- Referenced by `auth_user_groups` (group membership)
- Referenced by `auth_user_user_permissions` (individual permissions)

---

#### `auth_permission`
**Purpose:** Defines all available permissions in the system (add, change, delete, view for each model).

**Key Fields:**
- `id` (PK) - Permission ID
- `name` - Human-readable permission name
- `content_type_id` (FK) → `django_content_type` - What model this applies to
- `codename` - Short permission code (e.g., 'add_ville', 'change_liste')

**Records:** 60 permissions (4 per model: add, change, delete, view)

**Relationships:**
- Links to `django_content_type` to specify which model
- Referenced by `auth_group_permissions` (group permissions)
- Referenced by `auth_user_user_permissions` (user permissions)

---

#### `auth_group`
**Purpose:** Groups for organizing users with common permissions.

**Key Fields:**
- `id` (PK) - Group ID
- `name` - Group name

**Relationships:**
- Referenced by `auth_group_permissions` (permissions for the group)
- Referenced by `auth_user_groups` (users in the group)

---

#### `auth_group_permissions`
**Purpose:** Junction table linking groups to their permissions.

**Key Fields:**
- `id` (PK)
- `group_id` (FK) → `auth_group`
- `permission_id` (FK) → `auth_permission`

---

#### `auth_user_groups`
**Purpose:** Junction table linking users to groups.

**Key Fields:**
- `id` (PK)
- `user_id` (FK) → `auth_user`
- `group_id` (FK) → `auth_group`

---

#### `auth_user_user_permissions`
**Purpose:** Junction table for individual permissions assigned directly to users (not via groups).

**Key Fields:**
- `id` (PK)
- `user_id` (FK) → `auth_user`
- `permission_id` (FK) → `auth_permission`

**Records:** 94 rows

---

#### `django_admin_log`
**Purpose:** Audit log of all actions performed in the Django admin interface.

**Key Fields:**
- `id` (PK) - Log entry ID
- `action_time` - When the action occurred
- `user_id` (FK) → `auth_user` - Who performed the action
- `content_type_id` (FK) → `django_content_type` - What type of object
- `object_id` - Which specific object
- `object_repr` - String representation of the object
- `action_flag` - Type of action (1=add, 2=change, 3=delete)
- `change_message` - Description of changes

**Records:** 2,268 entries

---

#### `django_content_type`
**Purpose:** Registry of all models in the Django application.

**Key Fields:**
- `id` (PK) - Content type ID
- `app_label` - Django app name (e.g., 'compare', 'auth')
- `model` - Model name (e.g., 'ville', 'liste')

**Records:** 15 content types

**Relationships:**
- Referenced by `auth_permission` (permissions for each model)
- Referenced by `django_admin_log` (log entries)

---

#### `django_migrations`
**Purpose:** Tracks which Django migrations have been applied to the database.

**Key Fields:**
- `id` (PK)
- `app` - Django app name
- `name` - Migration file name
- `applied` - When the migration was applied

**Records:** 70 migrations

---

#### `django_session`
**Purpose:** Stores user session data for logged-in users.

**Key Fields:**
- `session_key` (PK) - Unique session identifier
- `session_data` - Encrypted session data
- `expire_date` - When the session expires

**Records:** 184 sessions

---

### 2. User Profile Table

#### `users_profile`
**Purpose:** Extended user profile information beyond the basic auth_user fields.

**Key Fields:**
- `id` (PK) - Profile ID
- `user_id` (FK) → `auth_user` - Associated user account
- `image` - Profile picture path

**Records:** Currently empty

---

### 3. Application Data Tables

#### `compare_ville` (Cities)
**Purpose:** Stores information about French municipalities.

**Key Fields:**
- `id` (PK) - City ID
- `nom` - City name (unique)
- `url` - URL-friendly slug
- `description` - City description
- `population` - Population count
- `departement` - Department (administrative region)
- `codeCommune` - Official INSEE commune code
- `prenomMaire`, `nomMaire` - Mayor's name
- `dateNaissanceMaire`, `ageMaire` - Mayor's birth date and age
- `sexMaire` - Mayor's gender (M/F)
- `professionMaire` - Mayor's profession
- `ouverte` (boolean) - Whether the city is "open" for data entry
- `nbInscrits` - Number of registered voters
- `AbstentionPremierTour` - First round abstention rate (%)
- `votesBlancPremierTour` - First round blank votes (%)
- `votesNulsPremierTour` - First round null votes (%)

**Records:** 34,092 cities

**Relationships:**
- Referenced by `compare_liste` (electoral lists in this city)
- Many-to-Many with `compare_critere` via `compare_ville_criteres`

---

#### `compare_liste` (Electoral Lists)
**Purpose:** Electoral lists (candidate teams) that ran in municipal elections.

**Key Fields:**
- `id` (PK) - List ID
- `nom` - List name
- `slogan` - Campaign slogan
- `teteDeListe` - Lead candidate name
- `presentation` - List presentation text
- `ville_id` (FK) → `compare_ville` - Which city this list ran in
- `couleur` - Political color/affiliation
- `lienPhoto`, `photo` - List photo
- `site` - Campaign website URL
- `twitter` - Twitter handle
- `validee` (boolean) - Whether the list is validated
- `score` - First round score (%)
- `scoreInscrit` - Score based on registered voters (%)
- `scoreVoix` - Number of votes received
- `secondTour` (boolean) - Advanced to second round
- `fusionAvec_id` (FK) → `compare_liste` (self-reference) - List merged with
- `elu` (boolean) - Whether the list won

**Records:** 489 lists

**Relationships:**
- Belongs to `compare_ville` (one city has many lists)
- Self-referencing via `fusionAvec_id` (list mergers)
- Referenced by `compare_promesse` (promises made by the list)
- Referenced by `compare_contact` (contact requests for the list)
- Many-to-Many with `auth_user` via `compare_liste_auteur` (list authors)
- Many-to-Many with `compare_charte` via `compare_liste_chartes` (charter commitments)

---

#### `compare_liste_auteur`
**Purpose:** Junction table linking electoral lists to their authors (users who created/manage them).

**Key Fields:**
- `id` (PK)
- `liste_id` (FK) → `compare_liste`
- `user_id` (FK) → `auth_user`

**Records:** 2,040 associations

---

#### `compare_critere` (Criteria)
**Purpose:** Evaluation criteria used to compare electoral programs.

**Key Fields:**
- `id` (PK) - Criterion ID
- `titre` - Criterion title
- `description` - Detailed description
- `categorie_id` (FK) → `compare_categorie` - Category this belongs to
- `estStandard` (boolean) - Whether this is a standard criterion for all cities

**Records:** 39 criteria

**Relationships:**
- Belongs to `compare_categorie`
- Referenced by `compare_promesse` (promises addressing this criterion)
- Many-to-Many with `compare_ville` via `compare_ville_criteres`

---

#### `compare_categorie` (Categories)
**Purpose:** Categories for organizing evaluation criteria.

**Key Fields:**
- `id` (PK) - Category ID
- `titre` - Category title

**Records:** 5 categories

**Relationships:**
- Referenced by `compare_critere` (criteria in this category)

---

#### `compare_promesse` (Promises)
**Purpose:** Electoral promises/commitments made by lists on specific criteria.

**Key Fields:**
- `id` (PK) - Promise ID
- `titre` - Promise title/text
- `description` - Detailed description
- `liste_id` (FK) → `compare_liste` - Which list made this promise
- `critere_id` (FK) → `compare_critere` - Which criterion it addresses
- `estUnePriorite` (boolean) - Whether this is a priority promise

**Records:** 15,448 promises

**Relationships:**
- Belongs to `compare_liste` (the list that made the promise)
- Belongs to `compare_critere` (what topic it addresses)

---

#### `compare_ville_criteres`
**Purpose:** Junction table linking cities to the criteria used for evaluation.

**Key Fields:**
- `id` (PK)
- `ville_id` (FK) → `compare_ville`
- `critere_id` (FK) → `compare_critere`

**Records:** 1,090,945 associations (most populous table)

---

#### `compare_charte` (Charters)
**Purpose:** Charters or commitments that electoral lists can sign up to.

**Key Fields:**
- `id` (PK) - Charter ID
- `titre` - Charter title
- `description` - Charter description
- `lienPhoto`, `photo` - Charter logo/image
- `site` - Charter website

**Records:** 13 charters

**Relationships:**
- Many-to-Many with `compare_liste` via `compare_liste_chartes`

---

#### `compare_liste_chartes`
**Purpose:** Junction table linking lists to charters they've signed.

**Key Fields:**
- `id` (PK)
- `liste_id` (FK) → `compare_liste`
- `charte_id` (FK) → `compare_charte`

**Records:** 30 associations

---

#### `compare_contact`
**Purpose:** Contact requests and inquiries submitted through the website.

**Key Fields:**
- `id` (PK) - Contact ID
- `email` - Contact email address
- `ville` - City name (text field)
- `liste_id` (FK) → `compare_liste` - Related list (if applicable)
- `comment` - Contact message
- `source` - Source of contact (ACC=Contact form, VSL=City without list, etc.)
- `date` - Submission timestamp
- `traite` (boolean) - Whether the contact has been processed
- `resteInforme` (boolean) - Whether user wants to stay informed

**Records:** 1 contact (currently only contains ronan.brnrd@gmail.com)

**Relationships:**
- Optionally links to `compare_liste` (if contact is about a specific list)

---

## Database Relationships Diagram

```
┌─────────────────┐
│   auth_user     │
└────────┬────────┘
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
┌────────────────────┐        ┌──────────────────┐
│ django_admin_log   │        │ users_profile    │
└────────────────────┘        └──────────────────┘
         │
         │
┌────────────────────┐        ┌──────────────────────┐
│ auth_permission    │◄───────│ django_content_type  │
└─────────┬──────────┘        └──────────────────────┘
          │
          ├────────────┐
          │            │
          ▼            ▼
┌──────────────────┐  ┌──────────────────────┐
│ auth_group       │  │ auth_user_user_      │
│ _permissions     │  │ permissions          │
└──────────────────┘  └──────────────────────┘


Application Data:

┌──────────────────┐
│ compare_         │
│ categorie        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐        ┌──────────────────┐
│ compare_critere  │◄───────│ compare_ville    │
└────────┬─────────┘        └────────┬─────────┘
         │                           │
         │        ┌──────────────────┘
         │        │
         │        ▼
         │  ┌──────────────────┐
         │  │ compare_liste    │
         │  └────────┬─────────┘
         │           │
         │           ├──────────────┐
         │           │              │
         ▼           ▼              ▼
┌──────────────────┐ ┌────────────┐ ┌──────────────────┐
│ compare_         │ │ compare_   │ │ compare_contact  │
│ promesse         │ │ liste_     │ └──────────────────┘
└──────────────────┘ │ auteur     │
                     └────────────┘
                     ┌────────────┐
                     │ compare_   │
                     │ charte     │
                     └────────────┘
                     ┌────────────┐
                     │ compare_   │
                     │ liste_     │
                     │ chartes    │
                     └────────────┘
```

---

## Foreign Key Constraints

### Validated Constraints (✅ VALID)
These constraints check all data including existing records:

1. `fk_liste_chartes_charte`: compare_liste_chartes → compare_charte
2. `fk_group_permissions_permission`: auth_group_permissions → auth_permission
3. `fk_group_permissions_group`: auth_group_permissions → auth_group
4. `fk_permission_content_type`: auth_permission → django_content_type
5. `fk_admin_log_content_type`: django_admin_log → django_content_type
6. `fk_profile_user`: users_profile → auth_user
7. `fk_user_groups_user`: auth_user_groups → auth_user
8. `fk_user_groups_group`: auth_user_groups → auth_group
9. `fk_user_permissions_permission`: auth_user_user_permissions → auth_permission
10. `fk_critere_categorie`: compare_critere → compare_categorie
11. `fk_ville_criteres_ville`: compare_ville_criteres → compare_ville
12. `fk_ville_criteres_critere`: compare_ville_criteres → compare_critere

### NOT VALID Constraints (⚠️)
These constraints only validate NEW data (legacy data may have orphaned references):

1. `fk_user_permissions_user`: auth_user_user_permissions → auth_user
2. `fk_contact_liste`: compare_contact → compare_liste
3. `fk_liste_ville`: compare_liste → compare_ville
4. `fk_liste_fusion`: compare_liste → compare_liste (self-reference)
5. `fk_liste_auteur_liste`: compare_liste_auteur → compare_liste
6. `fk_liste_auteur_user`: compare_liste_auteur → auth_user
7. `fk_liste_chartes_liste`: compare_liste_chartes → compare_liste
8. `fk_promesse_liste`: compare_promesse → compare_liste
9. `fk_promesse_critere`: compare_promesse → compare_critere
10. `fk_admin_log_user`: django_admin_log → auth_user

---

## Data Migration Notes

- **Source:** MySQL database from September 2020 (Data2020.txt)
- **Target:** Supabase PostgreSQL (EU West 3)
- **Migration Date:** December 2025
- **Total Rows Imported:** 1,146,003

### Key Conversions:
- MySQL `int(11)` → PostgreSQL `INTEGER`
- MySQL `tinyint(1)` → PostgreSQL `BOOLEAN`
- MySQL `datetime` → PostgreSQL `TIMESTAMP`
- MySQL backticks → PostgreSQL double quotes
- Added primary keys and sequences to all tables
- Established 22 foreign key relationships

### Known Issues:
- `auth_user` table is empty (no user accounts migrated)
- Some legacy data has orphaned foreign key references (handled with NOT VALID constraints)
- 10 foreign key constraints marked as NOT VALID due to orphaned data

---

## Connection Information

The database credentials are stored in `/backend/.env.supabase` (not in version control).

**Django Configuration:**
The Django frontend is configured to connect to this database in:
`/frontend/src/cyw/settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.tphkceccsjdvxgzowzqv',
        'PASSWORD': '[see .env.supabase]',
        'HOST': 'aws-1-eu-west-3.pooler.supabase.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

---

## Next Steps

1. **Create Superuser:** Run `python manage.py createsuperuser` to create an admin account
2. **Validate Constraints:** Clean up orphaned data and validate NOT VALID constraints
3. **Add Indexes:** Consider adding indexes on frequently queried foreign key columns
4. **Configure RLS:** Set up Row Level Security policies in Supabase if needed for public access
5. **Backup Strategy:** Implement regular database backups through Supabase dashboard

---

## Useful Queries

### Check all table sizes:
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;
```

### Check foreign key constraints:
```sql
SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;
```

### Check record counts:
```sql
SELECT 
    'compare_ville' as table_name, 
    COUNT(*) as count 
FROM compare_ville
UNION ALL
SELECT 'compare_liste', COUNT(*) FROM compare_liste
UNION ALL
SELECT 'compare_promesse', COUNT(*) FROM compare_promesse
UNION ALL
SELECT 'compare_critere', COUNT(*) FROM compare_critere
ORDER BY count DESC;
```
