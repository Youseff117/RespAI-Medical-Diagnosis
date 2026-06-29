# report_utils.py

# قائمة الأمراض الـ14
diseases = [
    "Atelectasis",
    "Cardiomegaly",
    "Effusion",
    "Infiltration",
    "Mass",
    "Nodule",
    "Pneumonia",
    "Pneumothorax",
    "Consolidation",
    "Edema",
    "Emphysema",
    "Fibrosis",
    "Pleural_Thickening",
    "Hernia"
]

# وصف كل مرض
disease_descriptions = {
    "Atelectasis": "Partial collapse of the lung or incomplete lung expansion.",
    "Cardiomegaly": "Enlarged heart, often due to underlying heart conditions.",
    "Effusion": "Accumulation of fluid in the pleural space around the lungs.",
    "Infiltration": "Substance denser than air, such as pus, blood, or protein, within lung tissue.",
    "Mass": "A localized lesion or tumor in the lungs.",
    "Nodule": "A small, rounded growth in the lung tissue.",
    "Pneumonia": "Infection causing inflammation of the air sacs in one or both lungs.",
    "Pneumothorax": "Air in the pleural space causing lung collapse.",
    "Consolidation": "Region of lung tissue filled with liquid instead of air.",
    "Edema": "Fluid accumulation in the lung tissue causing swelling.",
    "Emphysema": "Damage to alveoli causing breathlessness and reduced lung function.",
    "Fibrosis": "Thickening and scarring of lung tissue.",
    "Pleural_Thickening": "Thickening of the lining around the lungs, often due to inflammation or exposure to asbestos.",
    "Hernia": "Protrusion of lung tissue through a defect in the chest wall or diaphragm."
}

def generate_report(predictions):
    """
    Generate a readable report from model predictions.
    
    Args:
        predictions (list or array): Probabilities for each of the 14 diseases.
        
    Returns:
        dict: Mapping of disease to probability and description.
    """
    report = {}
    for i, disease in enumerate(diseases):
        probability = float(predictions[i])
        description = disease_descriptions[disease]
        report[disease] = {
            "probability": round(probability, 4),
            "description": description
        }
    return report