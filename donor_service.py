
from sqlalchemy import text
from database import engine


# ============================================================
# GET DONOR LIST
# ============================================================

def get_donor_list(search="", blood_group="All", eligibility="All"):

    sql = """
        SELECT
            d.id,
            d.donor_code,
            d.full_name,
            d.gender,
            d.date_of_birth,
            d.blood_group,
            d.phone,
            d.email,
            d.city,
            d.last_donation_date,
            d.is_eligible,
            COUNT(b.id) AS units_donated

        FROM donors d

        LEFT JOIN blood_inventory b
            ON b.donor_id = d.id

        WHERE 1 = 1
    """

    params = {}

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:
        sql += """
            AND (
                d.full_name LIKE :search
                OR d.donor_code LIKE :search
                OR d.phone LIKE :search
            )
        """

        params["search"] = f"%{search}%"

    # --------------------------------------------------------
    # BLOOD GROUP
    # --------------------------------------------------------

    if blood_group != "All":

        sql += """
            AND d.blood_group = :blood_group
        """

        params["blood_group"] = blood_group

    # --------------------------------------------------------
    # ELIGIBILITY
    # --------------------------------------------------------

    if eligibility == "Eligible":

        sql += """
            AND d.is_eligible = 1
        """

    elif eligibility == "Not eligible":

        sql += """
            AND d.is_eligible = 0
        """

    # --------------------------------------------------------
    # GROUP / SORT
    # --------------------------------------------------------

    sql += """
        GROUP BY d.id
        ORDER BY d.full_name ASC
    """

    with engine.connect() as conn:

        rows = conn.execute(
            text(sql),
            params
        ).mappings().all()

    return [
        dict(r)
        for r in rows
    ]


# ============================================================
# ADD DONOR
# ============================================================

def add_donor(
    full_name,
    gender,
    date_of_birth,
    blood_group,
    phone,
    email,
    city,
    last_donation_date,
    is_eligible
):

    from datetime import date

    phone = phone.strip()

    # --------------------------------------------------------
    # PHONE VALIDATION
    # --------------------------------------------------------

    if not (phone.isdigit() and len(phone) == 10):
        raise ValueError(
            "Phone number must be exactly 10 digits."
        )

    # --------------------------------------------------------
    # AGE VALIDATION
    # --------------------------------------------------------

    today = date.today()

    age = (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (
                date_of_birth.month,
                date_of_birth.day
            )
        )
    )

    if age < 18 or age > 65:
        raise ValueError(
            "Donor age must be between 18 and 65 years."
        )

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    with engine.begin() as conn:

        # SQLite-compatible donor code generation
        last = conn.execute(
            text("""
                SELECT
                    MAX(
                        CAST(
                            SUBSTR(donor_code, 2) AS INTEGER
                        )
                    )
                FROM donors
                WHERE donor_code LIKE 'D%'
            """)
        ).scalar() or 0

        donor_code = f"D{int(last) + 1:03d}"

        conn.execute(
            text("""
                INSERT INTO donors
                (
                    donor_code,
                    full_name,
                    gender,
                    date_of_birth,
                    blood_group,
                    phone,
                    email,
                    city,
                    last_donation_date,
                    is_eligible,
                    created_at,
                    updated_at
                )

                VALUES
                (
                    :donor_code,
                    :full_name,
                    :gender,
                    :date_of_birth,
                    :blood_group,
                    :phone,
                    :email,
                    :city,
                    :last_donation_date,
                    :is_eligible,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
            """),
            {
                "donor_code": donor_code,
                "full_name": full_name.strip(),
                "gender": gender,
                "date_of_birth": date_of_birth,
                "blood_group": blood_group,
                "phone": phone,
                "email": email.strip() or None,
                "city": city.strip(),
                "last_donation_date": last_donation_date,
                "is_eligible": 1 if is_eligible else 0,
            },
        )

    return donor_code


# ============================================================
# UPDATE DONOR
# ============================================================

def update_donor(
    donor_id,
    full_name,
    gender,
    date_of_birth,
    blood_group,
    phone,
    email,
    city,
    last_donation_date,
    is_eligible
):

    from datetime import date

    phone = phone.strip()

    # --------------------------------------------------------
    # PHONE VALIDATION
    # --------------------------------------------------------

    if not (phone.isdigit() and len(phone) == 10):
        raise ValueError(
            "Phone number must be exactly 10 digits."
        )

    # --------------------------------------------------------
    # AGE VALIDATION
    # --------------------------------------------------------

    today = date.today()

    age = (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (
                date_of_birth.month,
                date_of_birth.day
            )
        )
    )

    if age < 18 or age > 65:
        raise ValueError(
            "Donor age must be between 18 and 65 years."
        )

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    with engine.begin() as conn:

        result = conn.execute(
            text("""
                UPDATE donors

                SET
                    full_name = :full_name,
                    gender = :gender,
                    date_of_birth = :date_of_birth,
                    blood_group = :blood_group,
                    phone = :phone,
                    email = :email,
                    city = :city,
                    last_donation_date = :last_donation_date,
                    is_eligible = :is_eligible,
                    updated_at = CURRENT_TIMESTAMP

                WHERE id = :id
            """),
            {
                "id": donor_id,
                "full_name": full_name.strip(),
                "gender": gender,
                "date_of_birth": date_of_birth,
                "blood_group": blood_group,
                "phone": phone,
                "email": email.strip() or None,
                "city": city.strip(),
                "last_donation_date": last_donation_date,
                "is_eligible": 1 if is_eligible else 0,
            },
        )

        if result.rowcount == 0:
            raise ValueError(
                "Donor not found."
            )


# ============================================================
# DELETE DONOR
# ============================================================

def delete_donor(donor_id):

    with engine.begin() as conn:

        # ----------------------------------------------------
        # CHECK BLOOD INVENTORY
        # ----------------------------------------------------

        used = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM blood_inventory
                WHERE donor_id = :id
            """),
            {
                "id": donor_id
            }
        ).scalar()

        if used:

            raise ValueError(
                "This donor has blood units on record and "
                "cannot be deleted. Mark the donor as "
                "not eligible instead."
            )

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        result = conn.execute(
            text("""
                DELETE FROM donors
                WHERE id = :id
            """),
            {
                "id": donor_id
            }
        )

        if result.rowcount == 0:
            raise ValueError(
                "Donor not found."
            )


# ============================================================
# DONOR HISTORY
# ============================================================

def get_donor_history(donor_id):

    with engine.connect() as conn:

        rows = conn.execute(
            text("""
                SELECT
                    unit_code,
                    blood_group,
                    quantity_ml,
                    collection_date,
                    expiry_date,
                    status

                FROM blood_inventory

                WHERE donor_id = :id

                ORDER BY collection_date DESC
            """),
            {
                "id": donor_id
            }
        ).mappings().all()

    return [
        dict(r)
        for r in rows
    ]

