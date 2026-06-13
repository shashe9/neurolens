import os
import json
import time
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set database URL to sqlite memory instance before imports
os.environ["DATABASE_URL"] = "sqlite://"

from app.database.session import Base
from app.database.seed import seed_db
from app.services.ai_service import ai_engine
from app.models.models import Milestone, DevelopmentalDomain

def run_evaluation():
    print("Initializing in-memory SQLite database for evaluation...")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("Seeding database...")
    seed_db(db)
    
    print("Initializing AI engine cache...")
    ai_engine.initialize_cache(db)
    
    # Map of milestone title (normalized) to its age ranges
    milestone_metadata_map = {}
    for m in db.query(Milestone).all():
        milestone_metadata_map[m.title.lower().strip()] = {
            "title": m.title,
            "age_low": m.age_range_low,
            "age_high": m.age_range_high,
            "domain": m.domain.name
        }
        
    eval_json_path = Path(__file__).resolve().parent.parent / "app" / "database" / "evaluation_seed_dataset.json"
    if not eval_json_path.exists():
        raise FileNotFoundError(f"Evaluation seed dataset not found at {eval_json_path}")
        
    with open(eval_json_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
        
    print(f"Loaded {len(eval_data)} evaluation records. Running benchmarking...")
    
    total = 0
    top_1_hits = 0
    top_3_hits = 0
    domain_hits = 0
    
    # Confusion matrix structure: actual -> predicted -> count
    domains_list = ["Communication", "Social Emotional", "Cognitive", "Gross Motor", "Fine Motor"]
    confusion_matrix = defaultdict(lambda: defaultdict(int))
    
    failure_cases = []
    success_cases = []
    
    for record in eval_data:
        text = record["observation_text"]
        gt_domain = record["ground_truth_domain"]
        gt_title = record["ground_truth_milestone_title"]
        
        # Determine appropriate child age based on ground truth milestone
        meta = milestone_metadata_map.get(gt_title.lower().strip())
        if meta:
            # Use midpoint of low/high age range
            child_age = (meta["age_low"] + meta["age_high"]) // 2
        else:
            print(f"Warning: Ground truth milestone '{gt_title}' not found in database. Defaulting age to 18.")
            child_age = 18
            
        preprocessed = ai_engine.preprocess_text(text)
        obs_vector = ai_engine.model.encode(preprocessed, convert_to_numpy=True)
        norm = np.linalg.norm(obs_vector)
        if norm > 0:
            obs_vector /= norm
            
        # Retrieve suggestions using threshold = 0.0 to search the full space
        suggestions = ai_engine.retrieve_milestones(obs_vector, child_age, threshold=0.0)
        
        total += 1
        
        top_s = suggestions[0] if suggestions else None
        
        # Check Top-1 Hit
        is_top_1 = False
        if top_s and top_s["title"].lower().strip() == gt_title.lower().strip():
            top_1_hits += 1
            is_top_1 = True
            
        # Check Top-3 Hit
        is_top_3 = False
        if any(s["title"].lower().strip() == gt_title.lower().strip() for s in suggestions):
            top_3_hits += 1
            is_top_3 = True
            
        # Check Domain Hit
        is_domain_hit = False
        pred_domain = "None"
        if top_s:
            pred_domain = ai_engine.milestone_metadata[top_s["milestone_id"]]["domain_name"]
            if pred_domain.lower().strip() == gt_domain.lower().strip():
                domain_hits += 1
                is_domain_hit = True
                
        # Record confusion matrix
        confusion_matrix[gt_domain][pred_domain] += 1
        
        # Record success example
        if is_top_1 and len(success_cases) < 3:
            success_cases.append({
                "observation": text,
                "child_age": child_age,
                "ground_truth": gt_title,
                "domain": gt_domain,
                "score": top_s["relevance_score"]
            })
            
        # Record failure example
        if not is_top_3:
            failure_cases.append({
                "observation": text,
                "child_age": child_age,
                "ground_truth": gt_title,
                "ground_truth_domain": gt_domain,
                "retrieved": [
                    {
                        "title": s["title"],
                        "domain": ai_engine.milestone_metadata[s["milestone_id"]]["domain_name"],
                        "score": s["relevance_score"]
                    }
                    for s in suggestions
                ]
            })
            
    # Calculate percentages
    top_1_acc = (top_1_hits / total) * 100 if total > 0 else 0
    top_3_acc = (top_3_hits / total) * 100 if total > 0 else 0
    domain_acc = (domain_hits / total) * 100 if total > 0 else 0
    
    print("\n--- Evaluation Summary ---")
    print(f"Total Evaluated: {total}")
    print(f"Top-1 Milestone Accuracy: {top_1_acc:.2f}%")
    print(f"Top-3 Milestone Accuracy: {top_3_acc:.2f}%")
    print(f"Domain Accuracy: {domain_acc:.2f}%")
    
    # Generate Report Content
    report_lines = [
        "# Neurolens Observation Intelligence Engine (OIE) Evaluation Report",
        "",
        f"This report presents the live evaluation and benchmarking of the Neurolens retrieval engine, executed on **{time.strftime('%Y-%m-%d %H:%M:%S')}**.",
        "",
        "## 1. Overall Benchmarking Metrics",
        "",
        f"The evaluation was performed against the complete gold-standard benchmark dataset comprising **{total} labeled parent observations** representing realistic inputs across all 5 active developmental domains.",
        "",
        "| Metric | Result | Target / Standard | Description |",
        "| :--- | :---: | :---: | :--- |",
        f"| **Top-1 Milestone Accuracy** | **{top_1_acc:.2f}%** | > 65.0% | Ground-truth milestone matches the absolute top recommended suggestion. |",
        f"| **Top-3 Milestone Accuracy** | **{top_3_acc:.2f}%** | > 85.0% | Ground-truth milestone is present within the top 3 recommendations. |",
        f"| **Domain Classification Accuracy** | **{domain_acc:.2f}%** | > 90.0% | The domain of the top recommendation matches the ground-truth domain. |",
        "",
        "---",
        "",
        "## 2. Domain-Level Confusion Matrix",
        "",
        "The following matrix shows the counts of ground-truth domains (rows) versus domain classifications predicted by the top retrieval result (columns).",
        "",
    ]
    
    # Build Confusion Matrix Table
    headers = ["Actual \\ Predicted"] + domains_list
    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| :--- | " + " | ".join([":---:" for _ in domains_list]) + " |"
    report_lines.append(header_line)
    report_lines.append(divider_line)
    
    for actual in domains_list:
        row_vals = [f"**{actual}**"]
        for pred in domains_list:
            count = confusion_matrix[actual][pred]
            row_vals.append(str(count))
        report_lines.append("| " + " | ".join(row_vals) + " |")
        
    report_lines.extend([
        "",
        "---",
        "",
        "## 3. Representative Success Cases",
        "",
        "Below are three examples of observations where the SentenceTransformer model successfully identified the correct milestone as the top suggestion at Rank 1.",
        ""
    ])
    
    for idx, succ in enumerate(success_cases):
        report_lines.extend([
            f"### Success Case {idx + 1}",
            f"*   **Observation Text:** *\"{succ['observation']}\"*",
            f"*   **Child Age:** {succ['child_age']} months",
            f"*   **Domain:** {succ['domain']}",
            f"*   **Matched Milestone:** **{succ['ground_truth']}**",
            f"*   **Cosine Similarity Score:** {succ['score']:.4f}",
            ""
        ])
        
    report_lines.extend([
        "---",
        "",
        "## 4. Analysis of Retrieval Failure Cases",
        "",
        f"Out of {total} test samples, there were **{len(failure_cases)} failure cases** where the correct ground-truth milestone was NOT returned within the top 3 recommendations. Below is the detailed analysis of all failure cases.",
        ""
    ])
    
    if failure_cases:
        for idx, fail in enumerate(failure_cases):
            retrieved_titles = [f"\"{r['title']}\" ({r['domain']}, score: {r['score']:.4f})" for r in fail["retrieved"]]
            report_lines.extend([
                f"### Failure Case {idx + 1}",
                f"*   **Observation Text:** *\"{fail['observation']}\"*",
                f"*   **Child Age:** {fail['child_age']} months",
                f"*   **Ground-Truth Domain:** {fail['ground_truth_domain']}",
                f"*   **Expected Milestone:** **{fail['ground_truth']}**",
                f"*   **Retrieved Top 3 Suggestions:**",
                f"    1. {retrieved_titles[0] if len(retrieved_titles) > 0 else 'None'}",
                f"    2. {retrieved_titles[1] if len(retrieved_titles) > 1 else 'None'}",
                f"    3. {retrieved_titles[2] if len(retrieved_titles) > 2 else 'None'}",
                ""
            ])
    else:
        report_lines.append("*No failure cases were observed! 100% Top-3 retrieval accuracy was achieved.*")
        
    report_lines.append("")
    
    # Write report file
    report_path = Path(__file__).resolve().parent.parent / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Successfully generated evaluation report at: {report_path}")
    db.close()

if __name__ == "__main__":
    run_evaluation()
