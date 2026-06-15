import os
import re

def scan_a11y(src_dir: str) -> dict:
    """
    Statically scans TSX/TS files under src_dir to evaluate WCAG AA alignment.
    Returns counts of:
    - contrast_violations (hardcoded low-contrast gray colors)
    - missing_labels (buttons, inputs, selects without aria-labels or matching labels)
    - missing_aria (image elements without alt, or interactive elements without role)
    - accessibility_score (0-100 index)
    """
    contrast_violations = 0
    missing_labels = 0
    missing_aria = 0
    total_files = 0
    violations_details = []

    # Regex patterns
    # Hardcoded low-contrast color classes (e.g. text-slate-300, text-gray-400 etc.)
    contrast_pattern = re.compile(
        r'class(?:Name)?=["\'].*?\btext-(?:slate|gray|zinc|neutral|blue|green|red)-(?:300|400)\b.*?["\']',
        re.IGNORECASE
    )
    
    # Interactive elements patterns
    button_pattern = re.compile(r'<button\b([^>]*?)>', re.IGNORECASE)
    input_pattern = re.compile(r'<input\b([^>]*?)>', re.IGNORECASE)
    select_pattern = re.compile(r'<select\b([^>]*?)>', re.IGNORECASE)
    img_pattern = re.compile(r'<(?:img|Image)\b([^>]*?)>', re.IGNORECASE)
    
    # Elements with onClick handlers
    onclick_pattern = re.compile(r'<\w+\b[^>]*?onClick\s*=\s*\{[^>]*?>', re.IGNORECASE)

    if not os.path.exists(src_dir):
        return {
            "accessibility_score": 100,
            "contrast_violations": 0,
            "missing_labels": 0,
            "missing_aria": 0,
            "total_files_scanned": 0,
            "violations": []
        }

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.tsx', '.ts')) and 'node_modules' not in root and '.next' not in root:
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    continue

                # Remove comments to reduce false positives
                content_clean = re.sub(r'{\s*/\*.*?\*/\s*}', '', content, flags=re.DOTALL)
                content_clean = re.sub(r'//.*', '', content_clean)

                # 1. Analyze contrast colors
                contrast_matches = contrast_pattern.findall(content_clean)
                for match in contrast_matches:
                    # Filter out slate-900 / dark variables if context is dark-mode flipped
                    contrast_violations += 1
                    violations_details.append({
                        "file": file,
                        "type": "Low Contrast Color Class",
                        "snippet": match[:120]
                    })

                # 2. Analyze buttons
                buttons = button_pattern.findall(content_clean)
                for btn_attrs in buttons:
                    # If button does not have aria-label, aria-labelledby, or descriptive properties, flag it
                    if 'aria-label' not in btn_attrs and 'aria-labelledby' not in btn_attrs:
                        # Icon buttons are particularly prone to missing labels
                        if any(x in btn_attrs.lower() for x in ['icon', 'btn-icon', 'w-10', 'h-10', 'p-1', 'p-2', 'h-8', 'w-8']):
                            missing_labels += 1
                            violations_details.append({
                                "file": file,
                                "type": "Missing Button Label",
                                "snippet": f"<button {btn_attrs.strip()}>"
                            })

                # Analyze inputs
                inputs = input_pattern.findall(content_clean)
                for inp_attrs in inputs:
                    if 'aria-label' not in inp_attrs and 'aria-labelledby' not in inp_attrs and 'placeholder' not in inp_attrs and 'id=' not in inp_attrs:
                        missing_labels += 1
                        violations_details.append({
                            "file": file,
                            "type": "Missing Input Label / Descriptor",
                            "snippet": f"<input {inp_attrs.strip()}>"
                        })

                # Analyze selects
                selects = select_pattern.findall(content_clean)
                for sel_attrs in selects:
                    if 'aria-label' not in sel_attrs and 'aria-labelledby' not in sel_attrs and 'id=' not in sel_attrs:
                        missing_labels += 1
                        violations_details.append({
                            "file": file,
                            "type": "Missing Select Label",
                            "snippet": f"<select {sel_attrs.strip()}>"
                        })

                # 3. Analyze image alt tags
                imgs = img_pattern.findall(content_clean)
                for img_attrs in imgs:
                    if 'alt=' not in img_attrs:
                        missing_aria += 1
                        violations_details.append({
                            "file": file,
                            "type": "Missing Image Alt Attribute",
                            "snippet": f"<img {img_attrs.strip()}>"
                        })

                # Analyze onClick divs/spans
                div_clicks = onclick_pattern.findall(content_clean)
                for tag in div_clicks:
                    # If interactive click handler is placed on non-button/non-anchor and lacks role/aria
                    if 'role=' not in tag and 'aria-label' not in tag and '<button' not in tag.lower() and '<a ' not in tag.lower():
                        missing_aria += 1
                        violations_details.append({
                            "file": file,
                            "type": "Interactive Element Lacks Role / ARIA",
                            "snippet": tag[:120].strip()
                        })

    # Calculate overall compliance score
    deductions = (contrast_violations * 2) + (missing_labels * 3) + (missing_aria * 3)
    score = max(0, 100 - deductions)

    return {
        "accessibility_score": score,
        "contrast_violations": contrast_violations,
        "missing_labels": missing_labels,
        "missing_aria": missing_aria,
        "total_files_scanned": total_files,
        "violations": violations_details[:10]  # Cap at top 10 violations for rendering
    }
