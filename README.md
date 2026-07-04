# RespAI – AI-Powered Chest X-ray Clinical Decision Support System

![RespAI Overview](screenshots/respai-overview.png)

RespAI is an AI-powered Clinical Decision Support System (CDSS) developed to assist healthcare professionals in the analysis of chest X-ray images. The platform combines deep learning, explainable AI (Grad-CAM), and physician verification to support accurate and transparent clinical decision-making.

---

## Features

- AI-powered chest X-ray analysis
- Disease probability estimation
- Explainable AI using Grad-CAM heatmaps
- AI-generated clinical summary
- Preliminary AI diagnosis for patient review
- Doctor approval and validation workflow
- Final physician-verified diagnosis
- Secure patient and doctor authentication
- Patient Dashboard
- Doctor Dashboard
- Professional PDF medical report generation
- Medication and doctor notes after approval

---

## Workflow

1. Patient registers and logs into the system.
2. Patient uploads a chest X-ray image.
3. RespAI analyzes the image using a deep learning model.
4. Disease probabilities are calculated.
5. A Grad-CAM heatmap highlights suspicious regions.
6. The patient receives a **Preliminary AI Result**.
7. The assigned physician reviews the case.
8. The physician approves, rejects, or updates the diagnosis.
9. A **Final Medical Report** becomes available after approval.

---

## Technologies Used

- Python
- Flask
- PyTorch
- TorchXRayVision
- SQLite
- HTML5
- CSS3
- JavaScript
- Pillow
- NumPy
- Scikit-Image

---

## Screenshots

The overview image above demonstrates the main workflow of RespAI, including:

- Landing Page
- Patient Registration
- Login
- Chest X-ray Upload
- AI Analysis
- Disease Probability Results
- Grad-CAM Visualization
- Patient Dashboard
- Doctor Dashboard
- Doctor Approval
- Final Medical Report

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Youseff117/RespAI-Medical-Diagnosis.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## Project Structure

```
RespAI/
│
├── app.py
├── dashboard.py
├── result_filter.py
├── templates/
├── static/
├── screenshots/
├── uploads/
├── dataset/
├── requirements.txt
└── README.md
```

---

## Medical Report

After physician approval, RespAI generates a professional PDF report that includes:

- Patient information
- AI analysis summary
- Disease probabilities
- Clinical summary
- Physician approval status
- Final diagnosis
- Prescribed medications (if applicable)
- Doctor notes

---

## Security & Privacy

- Passwords are securely hashed.
- Sensitive configuration is managed using environment variables.
- Patient reports are released only after physician approval.
- The system separates preliminary AI findings from the final physician-approved diagnosis.

---

## Disclaimer

RespAI is intended to assist healthcare professionals and should not be considered a replacement for clinical judgment, radiologist interpretation, or physician diagnosis.

---

## Future Improvements

- DICOM image support
- PACS integration
- Electronic Health Record (EHR) integration
- Cloud deployment
- Mobile application
- Multi-language support
- AI model performance enhancement
- Hospital management integration

---

## Author

**Youssef Nour**

Respiratory Therapist

AI & Medical Imaging Enthusiast

---

⭐ If you found this project useful, consider giving it a star on GitHub.
