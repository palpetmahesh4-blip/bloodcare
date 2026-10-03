from sqlalchemy import text
from database import engine


# ============================================================
# GET INVENTORY
# ============================================================

def get_inventory(
    search="",
    blood_group="All",
    status="All"
):

    sql = """
        SELECT
            b.id,
            b.unit_code,
            d.full_name AS donor_name,
            b.blood_group,
            b.quantity_ml,
            b.collection_date,
            b.expiry_date,
            b.status,
            b.storage_location

        FROM blood_inventory b

        JOIN donors d
            ON d.id = b.donor_id

        WHERE 1 = 1
    """

    params = {}


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:

        sql += """
            AND (
                b.unit_code LIKE :search
                OR d.full_name LIKE :search
            )
        """

        params["search"] = f"%{search}%"


    # --------------------------------------------------------
    # BLOOD GROUP
    # --------------------------------------------------------

    if blood_group != "All":

        sql += """
            AND b.blood_group = :blood_group
        """

        params["blood_group"] = blood_group


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if status != "All":

        sql += """
            AND b.status = :status
        """

        params["status"] = status


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    sql += """
        ORDER BY b.expiry_date ASC
    """


    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    with engine.connect() as conn:

        rows = conn.execute(
            text(sql),
            params
        ).mappings().all()


    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET DONORS
# ============================================================

def get_donors():

    sql = """
        SELECT
            id,
            donor_code,
            full_name,
            blood_group

        FROM donors

        ORDER BY full_name
    """

    with engine.connect() as conn:

        rows = conn.execute(
            text(sql)
        ).mappings().all()


    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# ADD BLOOD UNIT
# ============================================================

def add_unit(
    donor_id,
    quantity_ml,
    collection_date,
    expiry_date,
    status,
    storage_location
):

    with engine.begin() as conn:

        # ----------------------------------------------------
        # GET DONOR
        # ----------------------------------------------------

        donor = conn.execute(
            text("""
                SELECT
                    blood_group

                FROM donors

                WHERE id = :id
            """),
            {
                "id": donor_id
            }
        ).mappings().first()


        if donor is None:

            raise ValueError(
                "Donor not found."
            )


        # ----------------------------------------------------
        # GENERATE UNIT CODE
        # ----------------------------------------------------

        last = conn.execute(
            text("""
                SELECT
                    MAX(
                        CAST(
                            SUBSTRING(unit_code, 2)
                            AS UNSIGNED
                        )
                    )

                FROM blood_inventory
            """)
        ).scalar()


        last = last or 0

        unit_code = (
            f"U{int(last) + 1:03d}"
        )


        # ----------------------------------------------------
        # INSERT UNIT
        # ----------------------------------------------------

        conn.execute(
            text("""
                INSERT INTO blood_inventory
                (
                    unit_code,
                    donor_id,
                    blood_group,
                    quantity_ml,
                    collection_date,
                    expiry_date,
                    status,
                    storage_location,
                    created_at,
                    updated_at
                )

                VALUES
                (
                    :unit_code,
                    :donor_id,
                    :blood_group,
                    :quantity_ml,
                    :collection_date,
                    :expiry_date,
                    :status,
                    :storage_location,
                    NOW(),
                    NOW()
                )
            """),

            {
                "unit_code": unit_code,
                "donor_id": donor_id,
                "blood_group": donor["blood_group"],
                "quantity_ml": quantity_ml,
                "collection_date": collection_date,
                "expiry_date": expiry_date,
                "status": status,
                "storage_location": storage_location,
            }
        )


    return unit_code


# ============================================================
# UPDATE BLOOD UNIT
# ============================================================

def update_unit(
    unit_id,
    quantity_ml,
    collection_date,
    expiry_date,
    status,
    storage_location
):

    with engine.begin() as conn:

        result = conn.execute(
            text("""
                UPDATE blood_inventory

                SET
                    quantity_ml = :quantity_ml,
                    collection_date = :collection_date,
                    expiry_date = :expiry_date,
                    status = :status,
                    storage_location = :storage_location,
                    updated_at = NOW()

                WHERE id = :id
            """),

            {
                "id": unit_id,
                "quantity_ml": quantity_ml,
                "collection_date": collection_date,
                "expiry_date": expiry_date,
                "status": status,
                "storage_location": storage_location,
            }
        )


        if result.rowcount == 0:

            raise ValueError(
                "Blood unit not found."
            )


# ============================================================
# DELETE BLOOD UNIT
# ============================================================

def delete_unit(unit_id):

    with engine.begin() as conn:

        # ----------------------------------------------------
        # CHECK DISTRIBUTION
        # ----------------------------------------------------

        used = conn.execute(
            text("""
                SELECT
                    COUNT(*)

                FROM blood_distribution

                WHERE inventory_id = :id
            """),
            {
                "id": unit_id
            }
        ).scalar()


        if used:

            raise ValueError(
                "This unit has distribution records "
                "and cannot be deleted."
            )


        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        result = conn.execute(
            text("""
                DELETE FROM blood_inventory

                WHERE id = :id
            """),
            {
                "id": unit_id
            }
        )


        if result.rowcount == 0:

            raise ValueError(
                "Blood unit not found."
            )