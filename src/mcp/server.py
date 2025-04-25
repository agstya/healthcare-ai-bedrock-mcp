from mcp.server.fastmcp import FastMCP
import boto3
import asyncpg
import json
from typing import List, Dict, Optional
from pydantic import Field

# ---------------------------- MCP CONFIGURATION ----------------------------

mcp = FastMCP(instructions="Healthcare AI Agent MCP Server: enables Claude to access EHR data via Postgres.")

# ---------------------------- AWS & SECRETS CONFIG ----------------------------

session = boto3.Session(profile_name="default", region_name="us-east-1")
secrets_manager = session.client("secretsmanager")

def get_postgres_dsn_from_secret(secret_name: str = "mcp/postgres/creds", region_name="us-east-1") -> str:
    try:
        response = secrets_manager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response["SecretString"])
        return (
            f"postgresql://{secret_dict['user']}:{secret_dict['password']}"
            f"@{secret_dict['host']}:{secret_dict['port']}/{secret_dict['database']}"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Postgres DSN from Secrets Manager: {e}")

POSTGRES_DSN = get_postgres_dsn_from_secret()

# ---------------------------- HEALTHCARE TOOLS ----------------------------

@mcp.tool()
async def get_patient_summary(
    patient_id: str = Field(..., description="The patient's unique identifier")
) -> Dict:
    """Retrieve a patient's basic summary from the EHR database."""
    try:
        conn = await asyncpg.connect(dsn=POSTGRES_DSN)
        query = """
            SELECT p.patient_id, p.name, p.gender, p.dob, a.admission_date, a.diagnosis
            FROM patients p
            JOIN admissions a ON p.patient_id = a.patient_id
            WHERE p.patient_id = $1
            ORDER BY a.admission_date DESC
            LIMIT 1;
        """
        row = await conn.fetchrow(query, patient_id)
        await conn.close()
        return dict(row) if row else {"message": "No summary found for this patient."}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_discharge_notes(
    admission_id: str = Field(..., description="Admission ID for the hospital stay")
) -> Dict:
    """Fetch discharge notes for a specific admission ID."""
    try:
        conn = await asyncpg.connect(dsn=POSTGRES_DSN)
        query = "SELECT notes FROM discharges WHERE admission_id = $1;"
        row = await conn.fetchrow(query, admission_id)
        await conn.close()
        return {"notes": row["notes"]} if row else {"message": "No notes found for this admission."}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_lab_results(
    patient_id: str = Field(..., description="The patient ID to fetch lab results for"),
    limit: int = Field(default=5, description="Number of recent lab results to return")
) -> List[Dict]:
    """Get recent lab results for a patient."""
    try:
        conn = await asyncpg.connect(dsn=POSTGRES_DSN)
        query = """
            SELECT test_name, result_value, unit, result_date
            FROM lab_results
            WHERE patient_id = $1
            ORDER BY result_date DESC
            LIMIT $2;
        """
        rows = await conn.fetch(query, patient_id, limit)
        await conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
async def run_custom_query(
    query: str = Field(..., description="Custom SQL query to run (SELECT only)")
) -> List[Dict]:
    """Run a custom SELECT SQL query against the EHR database."""
    try:
        conn = await asyncpg.connect(dsn=POSTGRES_DSN)
        rows = await conn.fetch(query)
        await conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]

# ---------------------------- ENTRY POINT ----------------------------

def main():
    mcp.run()

if __name__ == '__main__':
    main()