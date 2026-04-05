"""
modules/orchestrator/observe.py - Buoc OBSERVE (Ghi nhan)
Ghi lai ket qua thuc te de AI hoc tu kinh nghiem
"""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from models.incident import IncidentObservation


async def observe(
    db: AsyncSession,
    incident_id,
    rca_result_id,
    action_taken: str = "analysis_completed",
    actual_outcome: str = "pending_verification",
    prediction_delta: str = "not_yet_compared",
):
    """
    Ghi nhan ket qua quan sat sau moi vong P->R->A->O.
    Data nay se duoc doc lai trong PART 2 cua prompt lan sau.
    """
    obs = IncidentObservation(
        id=uuid.uuid4(),
        incident_id=incident_id,
        rca_result_id=rca_result_id,
        action_taken=action_taken,
        actual_outcome=actual_outcome,
        prediction_delta=prediction_delta,
    )
    db.add(obs)
    return obs
