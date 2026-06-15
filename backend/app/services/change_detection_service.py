from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Child, Observation, DevelopmentalDomain, LongitudinalChangeSummary

def detect_and_save_changes(db: Session, child_id: Any) -> List[Dict[str, Any]]:
    """
    Compares observations count in last 30 days vs 30-60 days ago.
    Saves a LongitudinalChangeSummary if it deviates, and returns the latest list.
    """
    domains = db.query(DevelopmentalDomain).all()
    now = datetime.utcnow()
    t30 = now - timedelta(days=30)
    t60 = now - timedelta(days=60)
    
    results = []

    for d in domains:
        # 1. Count current 30 days
        current_count = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.domain_id == d.id,
            Observation.observed_at >= t30,
            Observation.deleted_at.is_(None)
        ).count()

        # 2. Count previous 30 days (30 to 60 days ago)
        previous_count = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.domain_id == d.id,
            Observation.observed_at >= t60,
            Observation.observed_at < t30,
            Observation.deleted_at.is_(None)
        ).count()

        # 3. Formulate summary
        if current_count > previous_count + 1:
            summary_text = f"Recently logged more observations involving {d.name.lower()} interactions."
        elif current_count < previous_count - 1:
            summary_text = f"Fewer observations logged involving {d.name.lower()} compared to the previous period."
        else:
            if current_count > 0:
                summary_text = f"Observation frequency for {d.name.lower()} has remained steady."
            else:
                summary_text = f"No recent observations logged for {d.name.lower()} developmental area."

        # Check if latest record matches this summary to avoid spamming the table
        latest = db.query(LongitudinalChangeSummary).filter(
            LongitudinalChangeSummary.child_id == child_id,
            LongitudinalChangeSummary.domain_id == d.id
        ).order_by(LongitudinalChangeSummary.detected_at.desc()).first()

        if not latest or latest.summary_text != summary_text:
            change_record = LongitudinalChangeSummary(
                child_id=child_id,
                domain_id=d.id,
                summary_text=summary_text,
                detected_at=now
            )
            db.add(change_record)
            db.commit()
            latest = change_record

        results.append({
            "domain_name": d.name,
            "summary": latest.summary_text,
            "detected_at": latest.detected_at.isoformat()
        })

    return results
