from app.schemas.contract_schema import ContractResponse

def analyze_contract(filename: str) -> ContractResponse:
    # Minimal placeholder logic
    return ContractResponse(
        filename=filename,
        risk="low",
        issues=["missing clause"]
    )
