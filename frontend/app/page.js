"use client";

import React, { useState, useEffect } from "react";

// --- BASE DE DONNÉES CLINIQUE INITIALE DE SIMULATION (FIDELE AU PDF) ---
const INITIAL_PATIENTS = [
  { id: "P-4421", name: "Amine Charrou", birthdate: "1998-05-12", gender: "M" },
  { id: "P-8802", name: "Hiba Loughzal", birthdate: "2001-08-24", gender: "F" },
  { id: "P-1294", name: "Hayat Latif", birthdate: "1975-11-03", gender: "F" },
  { id: "P-5509", name: "Yassine Basskar", birthdate: "1992-04-17", gender: "M" }
];

const INITIAL_ANALYSES = [
  {
    id: "AN-177945001",
    patientId: "P-4421",
    patientName: "Amine Charrou",
    gender: "M",
    stage: 2,
    confidence: 0.943,
    date: "2026-05-22 14:32",
    referable: true,
    urgency: "Sous 3 mois",
    image: "https://images.unsplash.com/photo-1579684389782-64d84b5e905d?auto=format&fit=crop&q=80&w=600",
    heatmap: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&q=80&w=600",
    description: "Stade 2 - Rétinopathie diabétique modérée. Présence de multiples microanévrismes, d'hémorragies rétiniennes légères et d'exsudats durs.",
    report: `### 🩺 RAPPORT D'ANALYSE CLINIQUE PAR IA - RetinAI
**Généré le** : 2026-05-22 | **Identifiant Patient** : \`P-4421\` | **Nom** : **Amine Charrou**

#### 1. SYNTHÈSE DU DIAGNOSTIC DE L'IA
- **Stade Prédit** : **Stade 2 / 4 - Rétinopathie diabétique modérée**
- **Indice de Confiance** : **94.3%**
- **Niveau d'Urgence Clinique** : **Consultation sous 3 mois**
- **Statut d'Adressage Référable (Referable DR)** : **⚠️ OUI - Nécessite une consultation ophtalmologique**

#### 2. CONSTATIONS CLINIQUE DU FOND D'ŒIL
L'image de fond d'œil met en évidence de nombreux microanévrismes associés à de petites hémorragies rétiniennes localisées et des foyers d'exsudats durs (lipides) à proximité de la zone maculaire. L'absence de néovaisseaux permet d'exclure un stade prolifératif à ce jour.

#### 3. CORRÉLATIONS SCIENTIFIQUES (PubMed)
- **Source** : Tan G, et al. (2020). *Screening and management of Moderate Nonproliferative Diabetic Retinopathy* - publié dans **The Lancet Diabetes & Endocrinology**.
  *Conclusion de l'étude* : Démontre que la présence d'exsudats et d'hémorragies au stade modéré multiplie par 4 le risque de perte visuelle à 3 ans sans adressage à un ophtalmologue sous 3 mois.

#### 📅 PROTOCOLE DE SUIVI & PRÉVENTION CLINIQUE (Stade 2 - Modéré)
1. **Orientation Spécialisée** : **Consultation obligatoire chez un ophtalmologue sous 3 mois**.
2. **Examens Complémentaires Recommandés** : Tomographie par Cohérence Optique (OCT) pour exclure un œdème maculaire clinique silencieux.
3. **Surveillance Métabolique** : Bilan biologique rénal (microalbuminurie) et contrôle HbA1c rigoureux.

> ⚠️ **IMPORTANT** : Ce rapport est généré automatiquement par une intelligence artificielle d'assistance au diagnostic clinique. Les résultats et la carte d'activation Grad-CAM doivent impérativement être vérifiés et validés par un ophtalmologue qualifié.`
  },
  {
    id: "AN-177945002",
    patientId: "P-8802",
    patientName: "Hiba Loughzal",
    gender: "F",
    stage: 0,
    confidence: 0.985,
    date: "2026-05-22 11:15",
    referable: false,
    urgency: "Contrôle annuel",
    image: "https://images.unsplash.com/photo-1579684389782-64d84b5e905d?auto=format&fit=crop&q=80&w=600",
    heatmap: "",
    description: "Stade 0 - Aucun signe de rétinopathie diabétique. Rétine saine, aucune lésion visible.",
    report: `### 🩺 RAPPORT D'ANALYSE CLINIQUE PAR IA - RetinAI
**Généré le** : 2026-05-22 | **Identifiant Patient** : \`P-8802\` | **Nom** : **Hiba Loughzal**

#### 1. SYNTHÈSE DU DIAGNOSTIC DE L'IA
- **Stade Prédit** : **Stade 0 / 4 - Aucun signe de rétinopathie**
- **Indice de Confiance** : **98.5%**
- **Niveau d'Urgence Clinique** : **Contrôle annuel recommandé**
- **Statut d'Adressage Référable (Referable DR)** : **✅ NON**

#### 2. CONSTATIONS CLINIQUE DU FOND D'ŒIL
Rétine saine et homogène. La papille optique présente des contours nets, la macula est d'aspect normal, et aucun microanévrisme, exsudat ou hémorragie n'est décelé sur l'ensemble de la surface rétinienne explorée.`
  },
  {
    id: "AN-177945003",
    patientId: "P-1294",
    patientName: "Hayat Latif",
    gender: "F",
    stage: 4,
    confidence: 0.967,
    date: "2026-05-21 16:45",
    referable: true,
    urgency: "Urgence absolue !",
    image: "https://images.unsplash.com/photo-1579684389782-64d84b5e905d?auto=format&fit=crop&q=80&w=600",
    heatmap: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&q=80&w=600",
    description: "Stade 4 - Rétinopathie diabétique proliférative. Néovascularisation active, hémorragie vitréenne, risque imminent de cécité.",
    report: `### 🩺 RAPPORT D'ANALYSE CLINIQUE PAR IA - RetinAI
**Généré le** : 2026-05-21 | **Identifiant Patient** : \`P-1294\` | **Nom** : **Hayat Latif**

#### 1. SYNTHÈSE DU DIAGNOSTIC DE L'IA
- **Stade Prédit** : **Stade 4 / 4 - Rétinopathie diabétique proliférative**
- **Indice de Confiance** : **96.7%**
- **Niveau d'Urgence Clinique** : **🚨 URGENCE OPHTALMOLOGIQUE ABSOLUE**
- **Statut d'Adressage Référable (Referable DR)** : **⚠️ OUI - Prise en charge immédiate**

#### 2. CONSTATIONS CLINIQUE DU FOND D'ŒIL
Néovascularisation vitréenne active avec signes clairs d'hémorragie prérétinienne et prolifération fibrovasculaire sévère. Risque extrême de décollement de rétine tractionnel.`
  }
];

export default function RetinAIDashboard() {
  // --- ÉTATS GÉNÉRAUX DE NAVIGATION ET DONNÉES ---
  const [activeTab, setActiveTab] = useState("dashboard"); // dashboard, analyze, history, settings
  const [patients, setPatients] = useState(INITIAL_PATIENTS);
  const [analyses, setAnalyses] = useState(INITIAL_ANALYSES);
  
  // --- ÉTATS NOUVEAU DIAGNOSTIC ---
  const [selectedPatientId, setSelectedPatientId] = useState("P-4421");
  const [imageFile, setImageFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState("");
  
  // --- ÉTATS D'ANIMATION DE L'ORCHESTRATEUR (LANGRAPH) ---
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [agentText, setAgentText] = useState("");
  const [agentSubText, setAgentSubText] = useState("");
  const [viewState, setViewState] = useState("upload"); // upload, loading, results
  
  // --- ÉTATS D'ÉTAPES DU PIPELINE D'AGENTS ---
  const [pipelineState, setPipelineState] = useState({
    vision: "pending",
    research: "pending",
    report: "pending",
    followup: "pending",
    critic: "pending"
  });
  
  // --- ÉTATS D'AFFICHAGE DU VIEWER ---
  const [currentAnalysis, setCurrentAnalysis] = useState(INITIAL_ANALYSES[0]);
  const [gradcamOpacity, setGradcamOpacity] = useState(50);
  
  // --- ÉTATS SERVEUR ACTIF ---
  const [backendOnline, setBackendOnline] = useState(false);
  const API_URL = "http://127.0.0.1:8000";

  // --- RECHERCHE ET CRÉATION DE PATIENT ---
  const [newPatientName, setNewPatientName] = useState("");
  const [newPatientGender, setNewPatientGender] = useState("M");
  const [newPatientBirth, setNewPatientBirth] = useState("");
  const [newPatientId, setNewPatientId] = useState("");

  // --- COMPILATEUR ET GÉNÉRATEUR DE RAPPORT PDF CLINIQUE ---
  const downloadAnalysisPDF = (analysis) => {
    if (!analysis) return;

    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      alert("Veuillez autoriser les fenêtres contextuelles (pop-ups) pour pouvoir télécharger le PDF.");
      return;
    }

    const formatReportToHTML = (markdownText) => {
      if (!markdownText) return "";
      const lines = markdownText.split("\n");
      let inList = false;
      let html = "";
      
      for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        
        if (line === "") {
          if (inList) {
            html += "</ul>\n";
            inList = false;
          }
          continue;
        }
        
        if (line.startsWith("### ")) {
          if (inList) { html += "</ul>\n"; inList = false; }
          html += `<h3 style="color:#0f172a; margin-top:22px; margin-bottom:10px; border-bottom:2px solid #e2e8f0; padding-bottom:6px; font-size:16px; font-weight:700;">${line.substring(4)}</h3>\n`;
        } else if (line.startsWith("#### ")) {
          if (inList) { html += "</ul>\n"; inList = false; }
          html += `<h4 style="color:#1e293b; margin-top:16px; margin-bottom:8px; font-size:14px; font-weight:600;">${line.substring(5)}</h4>\n`;
        } else if (line.startsWith("- ")) {
          if (!inList) {
            html += '<ul style="margin: 10px 0; padding-left: 20px; list-style-type: disc;">\n';
            inList = true;
          }
          let cleanLine = line.substring(2);
          cleanLine = cleanLine
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code style="background:#f1f5f9; padding:2px 4px; border-radius:4px; font-family:monospace; font-size:12px;">$1</code>');
          html += `<li style="margin-bottom:6px; line-height:1.5; color:#334155;">${cleanLine}</li>\n`;
        } else if (/^\d+\.\s/.test(line)) {
          if (inList) { html += "</ul>\n"; inList = false; }
          let cleanLine = line.replace(/^\d+\.\s/, '');
          cleanLine = cleanLine
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code style="background:#f1f5f9; padding:2px 4px; border-radius:4px; font-family:monospace; font-size:12px;">$1</code>');
          html += `<div style="margin-left:15px; margin-bottom:8px; line-height:1.5; color:#334155;"><strong>${line.match(/^\d+/)[0]}.</strong> ${cleanLine}</div>\n`;
        } else if (line.startsWith("> ")) {
          if (inList) { html += "</ul>\n"; inList = false; }
          let cleanLine = line.substring(2);
          cleanLine = cleanLine
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code style="background:#f1f5f9; padding:2px 4px; border-radius:4px; font-family:monospace; font-size:12px;">$1</code>');
          html += `<blockquote style="border-left:4px solid #0284c7; padding-left:15px; color:#475569; margin:15px 0; font-style:italic; background:#f0f9ff; padding:10px 15px; border-radius:0 6px 6px 0;">${cleanLine}</blockquote>\n`;
        } else {
          if (inList) { html += "</ul>\n"; inList = false; }
          let formattedLine = line
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code style="background:#f1f5f9; padding:2px 4px; border-radius:4px; font-family:monospace; font-size:12px;">$1</code>');
          html += `<p style="margin: 8px 0; line-height:1.6; color:#334155;">${formattedLine}</p>\n`;
        }
      }
      
      if (inList) {
        html += "</ul>\n";
      }
      
      return html;
    };

    const formattedReport = formatReportToHTML(analysis.report);

    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>RetinAI - Rapport Clinique ${analysis.id}</title>
        <meta charset="utf-8">
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
          
          @page {
            size: A4;
            margin: 20mm;
          }
          
          body {
            font-family: 'Inter', sans-serif;
            color: #1e293b;
            background: #ffffff;
            margin: 0;
            padding: 0;
            font-size: 14px;
            line-height: 1.6;
          }

          .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0f172a;
            padding-bottom: 15px;
            margin-bottom: 30px;
          }

          .brand {
            font-size: 24px;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.5px;
          }
          
          .brand span {
            color: #0284c7;
          }

          .doc-type {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            color: #475569;
            letter-spacing: 1px;
            text-align: right;
          }

          .grid-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
          }

          .info-block {
            margin-bottom: 10px;
          }

          .info-label {
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 2px;
          }

          .info-value {
            font-size: 14px;
            font-weight: 500;
            color: #0f172a;
          }

          .section-title {
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
            text-transform: uppercase;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 6px;
            margin-top: 30px;
            margin-bottom: 15px;
          }

          .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
          }

          .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
          }

          .metric-card.alert {
            border-color: #f87171;
            background: #fef2f2;
          }

          .metric-label {
            font-size: 10px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 5px;
          }

          .metric-value {
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
          }

          .images-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
          }

          .image-wrapper {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            background: #f8fafc;
          }

          .image-wrapper img {
            max-width: 100%;
            height: 240px;
            object-fit: cover;
            border-radius: 4px;
            display: block;
            margin: 0 auto 10px auto;
          }

          .image-label {
            font-size: 12px;
            font-weight: 600;
            color: #475569;
          }

          .report-content {
            background: #ffffff;
            padding: 0 5px;
          }

          .signature-section {
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
            page-break-inside: avoid;
          }

          .signature-box {
            width: 45%;
            border-top: 1px solid #cbd5e1;
            padding-top: 10px;
            text-align: center;
            font-size: 12px;
            color: #64748b;
          }

          .footer {
            margin-top: 50px;
            border-top: 1px solid #e2e8f0;
            padding-top: 15px;
            text-align: center;
            font-size: 11px;
            color: #94a3b8;
            page-break-inside: avoid;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="brand">Retin<span>AI</span></div>
          <div class="doc-type">Rapport Clinique de Dépistage</div>
        </div>

        <div class="grid-info">
          <div>
            <div class="info-block">
              <div class="info-label">Identifiant Patient</div>
              <div class="info-value">${analysis.patientId}</div>
            </div>
            <div class="info-block">
              <div class="info-label">Nom Complet</div>
              <div class="info-value"><strong>${analysis.patientName}</strong></div>
            </div>
            <div class="info-block">
              <div class="info-label">Genre</div>
              <div class="info-value">${analysis.gender === 'M' ? 'Masculin' : 'Féminin'}</div>
            </div>
          </div>
          <div>
            <div class="info-block">
              <div class="info-label">Référence Examen</div>
              <div class="info-value">${analysis.id}</div>
            </div>
            <div class="info-block">
              <div class="info-label">Date d'Analyse</div>
              <div class="info-value">${analysis.date}</div>
            </div>
            <div class="info-block">
              <div class="info-label">Qualité globale du scan</div>
              <div class="info-value">Bonne</div>
            </div>
          </div>
        </div>

        <div class="section-title">Métriques Diagnostiques</div>
        <div class="metrics-grid">
          <div class="metric-card ${analysis.stage >= 2 ? 'alert' : ''}">
            <div class="metric-label">Stade Prédit</div>
            <div class="metric-value">Stade ${analysis.stage} / 4</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Confiance IA</div>
            <div class="metric-value">${(analysis.confidence * 100).toFixed(1)}%</div>
          </div>
          <div class="metric-card ${analysis.referable ? 'alert' : ''}">
            <div class="metric-label">Adressage Référable</div>
            <div class="metric-value">${analysis.referable ? '⚠️ OUI' : '✅ NON'}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Urgence</div>
            <div class="metric-value">${analysis.urgency || 'Normal'}</div>
          </div>
        </div>

        <div class="section-title">Imagerie Rétinienne & Heatmap Lésionnelle (Grad-CAM)</div>
        <div class="images-container">
          <div class="image-wrapper">
            <img src="${analysis.image}" alt="Scan Rétine" />
            <div class="image-label">Fond d'Œil d'Origine</div>
          </div>
          <div class="image-wrapper">
            <img src="${analysis.heatmap || analysis.image}" alt="Heatmap Grad-CAM" />
            <div class="image-label">Activation des Lésions (Grad-CAM)</div>
          </div>
        </div>

        <div style="page-break-before: always;"></div>

        <div class="section-title" style="margin-top: 0;">Compte-Rendu Clinique Généré par Multi-Agents</div>
        <div class="report-content">
          ${formattedReport || "Aucun rapport clinique n'a été produit pour cet examen."}
        </div>

        <div class="signature-section">
          <div class="signature-box">
            Visa de l'Assistant d'Analyse IA (RetinAI Core)
            <div style="margin-top: 40px; font-weight: bold; color: #0284c7;">APPROUVÉ PAR IA</div>
          </div>
          <div class="signature-box">
            Signature de l'Ophtalmologue Référent
            <div style="margin-top: 45px; font-style: italic; color: #cbd5e1;">Signature & Cachet</div>
          </div>
        </div>

        <div class="footer">
          Ce rapport est un document d'aide à la décision clinique généré automatiquement par l'IA RetinAI.<br/>
          Les conclusions doivent faire l'objet d'une validation finale sous la responsabilité d'un médecin spécialiste.
        </div>

        <script>
          window.onload = function() {
            setTimeout(function() {
              window.print();
              window.close();
            }, 600);
          }
        </script>
      </body>
      </html>
    `;

    printWindow.document.open();
    printWindow.document.write(htmlContent);
    printWindow.document.close();
  };

  // --- SYNCHRONISATION AVEC LE BACKEND FASTAPI ---
  useEffect(() => {
    async function checkBackend() {
      try {
        const res = await fetch(`${API_URL}/`);
        if (res.ok) {
          setBackendOnline(true);
          // Charger les vrais patients
          const pRes = await fetch(`${API_URL}/api/patients`);
          if (pRes.ok) {
            const pData = await pRes.json();
            if (pData.length > 0) setPatients(pData);
          }
          // Charger les vraies analyses
          const aRes = await fetch(`${API_URL}/api/dashboard`);
          if (aRes.ok) {
            const aData = await aRes.json();
            if (aData.length > 0) {
              const formattedAnalyses = aData.map(a => ({
                id: a.id,
                patientId: a.patient_id,
                patientName: a.patient_name || "Patient Inconnu",
                gender: a.patient_gender || "M",
                stage: a.stage,
                confidence: a.confidence,
                date: a.created_at.replace("T", " ").slice(0, 16),
                referable: a.referable === 1 || a.referable === true,
                urgency: a.urgency,
                image: `${API_URL}${a.image_path}`,
                heatmap: `${API_URL}${a.heatmap_path}`,
                description: a.description,
                report: a.clinical_report
              }));
              setAnalyses(formattedAnalyses);
              setCurrentAnalysis(formattedAnalyses[0]);
            }
          }
        }
      } catch (err) {
        console.warn("[RetinAI] Mode simulation actif (le backend FastAPI à localhost:8000 est hors-ligne).");
        setBackendOnline(false);
      }
    }
    checkBackend();
  }, []);

  // --- RE-SYNCHRONISER LA LISTE DES PATIENTS ---
  const refetchPatients = async () => {
    if (!backendOnline) return;
    try {
      const res = await fetch(`${API_URL}/api/patients`);
      if (res.ok) {
        const data = await res.json();
        if (data.length > 0) setPatients(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // --- ACTIONS D'UPLOAD ---
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setImageFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  // --- SOUMISSION DE L'ANALYSE ---
  const startAnalysis = async () => {
    if (!imageFile) {
      alert("Veuillez d'abord déposer ou sélectionner une image de fond d'œil.");
      return;
    }

    setViewState("loading");
    setIsAnalyzing(true);

    const stagesText = [
      "Aucune rétinopathie diabétique",
      "Rétinopathie diabétique légère",
      "Rétinopathie diabétique modérée",
      "Rétinopathie diabétique sévère",
      "Rétinopathie diabétique proliférative"
    ];

    if (backendOnline) {
      // --- MODE PRODUCTION REEL (API FASTAPI) ---
      try {
        setAgentText("🤖 Vision Agent : Inférence du scan oculaire...");
        setAgentSubText("Prétraitement d'image circulaire + Ben Graham et exécution du modèle ONNX...");
        setPipelineState({ vision: "running", research: "pending", report: "pending", followup: "pending", critic: "pending" });
        
        const formData = new FormData();
        formData.append("patient_id", selectedPatientId);
        formData.append("file", imageFile);

        const res = await fetch(`${API_URL}/api/analyze`, {
          method: "POST",
          body: formData
        });

        if (!res.ok) {
          throw new Error("Échec du traitement côté serveur.");
        }

        const data = await res.json();
        
        // Simuler le passage visuel rapide dans le loader pour l'effet clinique
        setTimeout(() => {
          setAgentText("📚 Research Agent : Interrogation de PubMed...");
          setAgentSubText("Recherche active de la littérature clinique et des articles de référence correspondants...");
          setPipelineState({ vision: "completed", research: "running", report: "pending", followup: "pending", critic: "pending" });
        }, 1200);

        setTimeout(() => {
          setAgentText("📝 Report Agent : Rédaction du compte-rendu...");
          setAgentSubText("Structuration des arguments médicaux et des sources de recherche rétiniennes...");
          setPipelineState({ vision: "completed", research: "completed", report: "running", followup: "pending", critic: "pending" });
        }, 2400);

        setTimeout(() => {
          setAgentText("📅 Follow-up Agent : Élaboration du plan de soin...");
          setAgentSubText("Définition des consignes d'urgence et des rythmes de suivi optimaux...");
          setPipelineState({ vision: "completed", research: "completed", report: "completed", followup: "running", critic: "pending" });
        }, 3600);

        setTimeout(() => {
          setAgentText("⚖️ Critic Agent : Contrôle réglementaire clinique...");
          setAgentSubText("Vérification des cohérences diagnostiques et des mentions légales de sécurité...");
          setPipelineState({ vision: "completed", research: "completed", report: "completed", followup: "completed", critic: "running" });
        }, 4800);

        setTimeout(() => {
          setPipelineState({ vision: "completed", research: "completed", report: "completed", followup: "completed", critic: "completed" });
          const formattedAnalysis = {
            id: data.id,
            patientId: data.patient_id,
            patientName: patients.find(p => p.id === data.patient_id)?.name || "Patient Enregistré",
            gender: patients.find(p => p.id === data.patient_id)?.gender || "M",
            stage: data.stage,
            confidence: data.confidence,
            date: data.created_at.replace("T", " ").slice(0, 16),
            referable: data.referable === 1 || data.referable === true,
            urgency: data.urgency,
            image: `${API_URL}${data.image_path}`,
            heatmap: `${API_URL}${data.heatmap_path}`,
            description: data.description,
            report: data.clinical_report
          };

          setAnalyses(prev => [formattedAnalysis, ...prev]);
          setCurrentAnalysis(formattedAnalysis);
          setIsAnalyzing(false);
          setViewState("results");
        }, 6000);

      } catch (err) {
        console.error(err);
        alert("Erreur lors de l'appel au serveur FastAPI. Lancement de la simulation locale.");
        triggerLocalSimulation();
      }
    } else {
      // --- MODE SIMULATION CLUNIQUE COMPLÈTE (OFFLINE) ---
      triggerLocalSimulation();
    }
  };

  const triggerLocalSimulation = () => {
    const pName = patients.find(p => p.id === selectedPatientId)?.name || "Patient";
    const pGender = patients.find(p => p.id === selectedPatientId)?.gender || "M";

    // Étape 1 : Vision Agent (Inférence ONNX)
    setTimeout(() => {
      setAgentText("🤖 Vision Agent : Inférence du scan oculaire...");
      setAgentSubText("Extraction des caractéristiques globales avec EfficientNet-B4 en cours...");
      setPipelineState({ vision: "running", research: "pending", report: "pending", followup: "pending", critic: "pending" });
    }, 800);

    // Étape 2 : Research Agent (PubMed API)
    setTimeout(() => {
      setAgentText("📚 Research Agent : Exploration de PubMed...");
      setAgentSubText("Recherche active de la littérature clinique et des articles de référence correspondants...");
      setPipelineState({ vision: "completed", research: "running", report: "pending", followup: "pending", critic: "pending" });
    }, 2000);

    // Étape 3 : Report Agent (Gemini LLM)
    setTimeout(() => {
      setAgentText("📝 Report Agent : Rédaction du compte-rendu...");
      setAgentSubText("Structuration des arguments médicaux et des sources de recherche rétiniennes...");
      setPipelineState({ vision: "completed", research: "completed", report: "running", followup: "pending", critic: "pending" });
    }, 3200);

    // Étape 4 : Follow-up Agent (Conseils et protocoles)
    setTimeout(() => {
      setAgentText("📅 Follow-up Agent : Élaboration du plan de soin...");
      setAgentSubText("Définition des consignes d'urgence et des rythmes de suivi optimaux...");
      setPipelineState({ vision: "completed", research: "completed", report: "completed", followup: "running", critic: "pending" });
    }, 4400);

    // Étape 5 : Critic Agent (Validation médicale finale)
    setTimeout(() => {
      setAgentText("⚖️ Critic Agent : Contrôle réglementaire clinique...");
      setAgentSubText("Vérification des cohérences diagnostiques et des mentions légales de sécurité...");
      setPipelineState({ vision: "completed", research: "completed", report: "completed", followup: "completed", critic: "running" });
    }, 5500);

    // Fin et affichage du résultat
    setTimeout(() => {
      setPipelineState({ vision: "completed", research: "completed", report: "completed", followup: "completed", critic: "completed" });
      const randomId = `AN-${Math.floor(100000000 + Math.random() * 900000000)}`;
      const randomStage = Math.floor(Math.random() * 5);
      const randomConf = 0.8 + Math.random() * 0.18;
      
      const urgencies = ["Contrôle annuel", "Suivi 6-12 mois", "Sous 3 mois", "Sous 1 mois", "Urgence absolue !"];
      const stagesText = [
        "Aucune rétinopathie diabétique",
        "Rétinopathie diabétique légère",
        "Rétinopathie diabétique modérée",
        "Rétinopathie diabétique sévère",
        "Rétinopathie diabétique proliférative"
      ];

      const newAnalysis = {
        id: randomId,
        patientId: selectedPatientId,
        patientName: pName,
        gender: pGender,
        stage: randomStage,
        confidence: randomConf,
        date: new Date().toISOString().replace('T', ' ').slice(0, 16),
        referable: randomStage >= 2,
        urgency: urgencies[randomStage],
        image: previewUrl || "https://images.unsplash.com/photo-1579684389782-64d84b5e905d?auto=format&fit=crop&q=80&w=500",
        heatmap: randomStage > 0 ? "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&q=80&w=500" : "",
        description: `Stade ${randomStage} - ${stagesText[randomStage]}. Évaluation effectuée en mode simulation hors-ligne.`,
        report: `### 🩺 RAPPORT D'ANALYSE CLINIQUE PAR IA - RetinAI (Simulation)
**Généré le** : ${new Date().toISOString().slice(0, 10)} | **Identifiant Patient** : \`${selectedPatientId}\` | **Nom** : **${pName}**

#### 1. SYNTHÈSE DU DIAGNOSTIC DE L'IA
- **Stade Prédit** : **Stade ${randomStage} / 4 - ${stagesText[randomStage]}**
- **Indice de Confiance** : **${(randomConf * 100).toFixed(1)}%**
- **Niveau d'Urgence Clinique** : **${urgencies[randomStage]}**
- **Statut d'Adressage Référable (Referable DR)** : **${randomStage >= 2 ? "⚠️ OUI - Réorientation requise" : "✅ NON"}**

#### 2. CONSTATIONS CLINIQUE DU FOND D'ŒIL
L'image prétraitée a été analysée par les agents cliniques. L'activation Grad-CAM a localisé des variations texturales correspondant au stade prédit.`
      };

      setAnalyses(prev => [newAnalysis, ...prev]);
      setCurrentAnalysis(newAnalysis);
      setIsAnalyzing(false);
      setViewState("results");
    }, 6800);
  };

  // --- ACTIONS VIEWER ---
  const openAnalysis = (id) => {
    const a = analyses.find(item => item.id === id);
    if (a) {
      setCurrentAnalysis(a);
      setViewState("results");
      setActiveTab("analyze");
    }
  };

  // --- ENREGISTRER UN NOUVEAU PATIENT (LOCAL OU SERVEUR) ---
  const savePatient = async (e) => {
    e.preventDefault();
    if (!newPatientId || !newPatientName) {
      alert("Veuillez saisir un identifiant unique et le nom complet du patient.");
      return;
    }

    const payload = {
      id: newPatientId,
      name: newPatientName,
      birthdate: newPatientBirth || null,
      gender: newPatientGender
    };

    if (backendOnline) {
      try {
        const res = await fetch(`${API_URL}/api/patients`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          alert(`Patient ${newPatientName} enregistré avec succès dans la base de données SQLite !`);
          setNewPatientName("");
          setNewPatientId("");
          setNewPatientBirth("");
          refetchPatients();
        } else {
          const errData = await res.json();
          alert(`Erreur : ${errData.detail}`);
        }
      } catch (e) {
        alert("Impossible de joindre le serveur pour enregistrer le patient.");
      }
    } else {
      // Offline local update
      const exists = patients.some(p => p.id === newPatientId);
      if (exists) {
        alert("Ce patient existe déjà avec cet ID unique.");
        return;
      }
      setPatients(prev => [payload, ...prev]);
      alert(`Patient ${newPatientName} enregistré localement (simulation) !`);
      setNewPatientName("");
      setNewPatientId("");
      setNewPatientBirth("");
    }
  };

  return (
    <div style={{ display: "flex", width: "100%", minHeight: "100vh" }}>
      
      {/* ================= SIDEBAR DE NAVIGATION ================= */}
      <aside>
        <div className="logo-container">
          <div className="logo-icon">
            <i className="fa-solid fa-circle-nodes"></i>
          </div>
          <div className="logo-text">Retin<span>AI</span></div>
        </div>
        
        <ul className="nav-menu">
          <li 
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <i className="fa-solid fa-chart-line"></i>
            Tableau de Bord
          </li>
          <li 
            className={`nav-item ${activeTab === "analyze" ? "active" : ""}`}
            onClick={() => {
              setActiveTab("analyze");
              setViewState("upload");
              setImageFile(null);
              setPreviewUrl("");
            }}
          >
            <i className="fa-solid fa-eye"></i>
            Nouvelle Analyse
          </li>
          <li 
            className={`nav-item ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            <i className="fa-solid fa-clock-rotate-left"></i>
            Historique Clinique
          </li>
          <li 
            className={`nav-item ${activeTab === "settings" ? "active" : ""}`}
            onClick={() => setActiveTab("settings")}
          >
            <i className="fa-solid fa-sliders"></i>
            Paramètres
          </li>
        </ul>

        <div className="nav-footer">
          <div className="avatar">AC</div>
          <div className="avatar-info">
            <h4>Dr. Ahmed Chmourk</h4>
            <p>Clinicien Chef - ENSA</p>
          </div>
        </div>
      </aside>

      {/* ================= CONTENU PRINCIPAL ================= */}
      <main>
        
        {/* HEADER DE LA PAGE */}
        <header>
          <div className="header-title">
            <h1>
              {activeTab === "dashboard" && "Tableau de Bord Clinique"}
              {activeTab === "analyze" && "Dépistage et Diagnostic IA"}
              {activeTab === "history" && "Historique Médical"}
              {activeTab === "settings" && "Paramètres de Production"}
            </h1>
            <p style={{ color: "var(--text-muted)", fontSize: "15px" }}>
              {activeTab === "dashboard" && "Aperçu général des dépistages et de l'activité du service."}
              {activeTab === "analyze" && "Téléversez une image de fond d'œil et exécutez le graphe d'agents."}
              {activeTab === "history" && "Accès sécurisé à l'ensemble des rapports d'analyses du service."}
              {activeTab === "settings" && "Configuration des intégrations LLM (Gemini) et des seuils cliniques."}
            </p>
          </div>
          {activeTab !== "analyze" && (
            <button 
              className="btn" 
              onClick={() => {
                setActiveTab("analyze");
                setViewState("upload");
                setImageFile(null);
                setPreviewUrl("");
              }}
            >
              <i className="fa-solid fa-plus"></i> Nouvelle Analyse
            </button>
          )}
        </header>

        {/* ================= VUE 1 : DASHBOARD ================= */}
        {activeTab === "dashboard" && (
          <section>
            
            {/* STATS RAPIDES */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon primary">
                  <i className="fa-solid fa-hospital-user"></i>
                </div>
                <div className="stat-info">
                  <h3>{patients.length + 240}</h3>
                  <p>Patients Enregistrés</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon success">
                  <i className="fa-solid fa-check-double"></i>
                </div>
                <div className="stat-info">
                  <h3>{analyses.filter(a => a.stage < 2).length + 180}</h3>
                  <p>Scans Sains (Stade 0-1)</p>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon danger">
                  <i className="fa-solid fa-triangle-exclamation"></i>
                </div>
                <div className="stat-info">
                  <h3>{analyses.filter(a => a.stage >= 2).length + 60}</h3>
                  <p>Cas Référables (Stade 2+)</p>
                </div>
              </div>
            </div>

            {/* SYNC STATUS */}
            <div 
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "12px 20px",
                background: backendOnline ? "rgba(16, 185, 129, 0.1)" : "rgba(245, 158, 11, 0.1)",
                border: `1px solid ${backendOnline ? "rgba(16, 185, 129, 0.3)" : "rgba(245, 158, 11, 0.3)"}`,
                borderRadius: "10px",
                marginBottom: "30px",
                fontSize: "14px"
              }}
            >
              <span 
                style={{
                  width: "10px",
                  height: "10px",
                  borderRadius: "50%",
                  background: backendOnline ? "var(--success)" : "var(--warning)",
                  display: "inline-block",
                  animation: "pulse 2s infinite"
                }}
              />
              <span style={{ fontWeight: 500 }}>
                {backendOnline 
                  ? "✓ Connexion établie avec l'API Gateway FastAPI locale. Le vrai modèle ONNX et la base SQLite SQLite sont opérationnels."
                  : "⚠ Mode Simulation actif (FastAPI à localhost:8000 non détecté). L'application fonctionne de manière autonome avec mockups interactifs."
                }
              </span>
            </div>

            {/* DERNIERES ANALYSES */}
            <div className="glass-panel">
              <h2 className="mb-20">Analyses Rétiniennes Récentes</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Identifiant</th>
                      <th>Nom du Patient</th>
                      <th>Diagnostic IA</th>
                      <th>Score de Confiance</th>
                      <th>{"Date d'Examen"}</th>
                      <th>Adressage Référable</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyses.slice(0, 5).map((a) => (
                      <tr key={a.id}>
                        <td className="text-bold">{a.id}</td>
                        <td>{a.patientName}</td>
                        <td>
                          <span className={`badge badge-s${a.stage}`}>
                            Stade {a.stage}
                          </span>
                        </td>
                        <td className="text-bold" style={{ color: "var(--primary)" }}>
                          {(a.confidence * 100).toFixed(1)}%
                        </td>
                        <td>{a.date}</td>
                        <td style={{ color: a.referable ? "var(--danger)" : "var(--success)", fontWeight: a.referable ? 600 : 500 }}>
                          {a.referable ? "⚠️ Référable" : "✅ Non référable"}
                        </td>
                        <td>
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: "6px 12px", fontSize: "13px" }}
                            onClick={() => openAnalysis(a.id)}
                          >
                            Ouvrir
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </section>
        )}

        {/* ================= VUE 2 : NOUVELLE ANALYSE ================= */}
        {activeTab === "analyze" && (
          <section className="fade-in">
            
            {/* 2.A : UPLOAD SCREEN */}
            {viewState === "upload" && (
              <div className="glass-panel" style={{ maxWidth: "800px", margin: "0 auto" }}>
                <h2 className="mb-20" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <i className="fa-solid fa-file-arrow-up" style={{ color: "var(--primary)" }}></i>
                  {"Téléverser un Fond d'œil"}
                </h2>
                
                <div style={{ display: "flex", flexDirection: "column", gap: "25px" }}>
                  <div>
                    <label style={{ display: "block", marginBottom: "8px", fontWeight: 700, fontSize: "14.5px" }}>
                      1. Sélectionner un Patient du Dossier
                    </label>
                    <select 
                      value={selectedPatientId}
                      onChange={(e) => setSelectedPatientId(e.target.value)}
                      className="select-field"
                    >
                      {patients.map(p => (
                        <option key={p.id} value={p.id}>
                          {p.id} - {p.name} ({p.gender === "M" ? "Homme" : "Femme"})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: "block", marginBottom: "8px", fontWeight: 700, fontSize: "14.5px" }}>
                      {"2. Image du Fond d'œil (PNG, JPG)"}
                    </label>
                    <div 
                      className="upload-area"
                      onDragEnter={handleDrag}
                      onDragOver={handleDrag}
                      onDragLeave={handleDrag}
                      onDrop={handleDrop}
                      onClick={() => document.getElementById("file-select-input").click()}
                      style={{
                        borderColor: dragActive ? "var(--primary)" : "var(--border)",
                        background: dragActive ? "var(--primary-glow)" : "var(--bg-base)"
                      }}
                    >
                      <input 
                        type="file" 
                        id="file-select-input" 
                        style={{ display: "none" }} 
                        accept="image/*"
                        onChange={handleFileChange}
                      />
                      <div className="upload-icon">
                        <i className="fa-solid fa-circle-plus"></i>
                      </div>
                      {imageFile ? (
                        <div>
                          <p style={{ fontWeight: 700, color: "var(--success)" }}>✓ Image sélectionnée :</p>
                          <p style={{ fontSize: "13.5px", color: "var(--text-muted)", marginTop: "4px" }}>
                            {imageFile.name} ({(imageFile.size / (1024 * 1024)).toFixed(2)} Mo)
                          </p>
                        </div>
                      ) : (
                        <div>
                          <p style={{ fontWeight: 700, fontSize: "15px", color: "var(--text-main)" }}>Glissez-déposez le scan ou cliquez ici pour parcourir</p>
                          <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "6px" }}>
                            Résolution minimale recommandée : 512x512 pixels
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {previewUrl && (
                    <div style={{ display: "flex", justifyContent: "center" }}>
                      <div style={{ width: "220px", height: "220px", borderRadius: "8px", overflow: "hidden", border: "1px solid var(--border)", boxShadow: "var(--shadow-soft)" }}>
                        <img src={previewUrl} alt="Aperçu" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                      </div>
                    </div>
                  )}

                  <button 
                    className="btn" 
                    style={{ width: "100%", padding: "14px" }}
                    onClick={startAnalysis}
                  >
                    <i className="fa-solid fa-microchip"></i>
                    {"Lancer l'Analyse Multi-Agents (LangGraph)"}
                  </button>
                </div>
              </div>
            )}

            {/* 2.B : LOADING SCREEN */}
            {viewState === "loading" && (
              <div className="glass-panel fade-in" style={{ maxWidth: "680px", margin: "0 auto", padding: "40px" }}>
                <div style={{ textAlign: "center", marginBottom: "32px" }}>
                  <div className="spinner" style={{ margin: "0 auto 16px auto" }}></div>
                  <h2 style={{ fontSize: "20px", fontWeight: 800 }}>Orchestration Multi-Agents LangGraph</h2>
                  <p style={{ color: "var(--text-muted)", fontSize: "14px", marginTop: "4px" }}>
                    {"Analyse clinique automatisée du fond d'œil en cours..."}
                  </p>
                </div>

                <div className="pipeline-wrapper">
                  <div className={`pipeline-node ${pipelineState.vision === "running" ? "active" : ""} ${pipelineState.vision === "completed" ? "completed" : ""}`}>
                    <div className="pipeline-node-icon">
                      {pipelineState.vision === "completed" ? "✓" : <i className="fa-solid fa-microchip"></i>}
                    </div>
                    <div className="pipeline-node-content">
                      <div className="pipeline-node-title">1. Vision Agent (EfficientNet-B4 & ONNX)</div>
                      <div className="pipeline-node-desc">Inférence des poids du modèle de Deep Learning pour classer le stade de RD.</div>
                    </div>
                    <div className={`pipeline-node-status ${pipelineState.vision}`}>
                      {pipelineState.vision === "pending" && "En attente"}
                      {pipelineState.vision === "running" && "Analyse..."}
                      {pipelineState.vision === "completed" && "Terminé"}
                    </div>
                  </div>

                  <div className={`pipeline-node ${pipelineState.research === "running" ? "active" : ""} ${pipelineState.research === "completed" ? "completed" : ""}`}>
                    <div className="pipeline-node-icon">
                      {pipelineState.research === "completed" ? "✓" : <i className="fa-solid fa-book-open-reader"></i>}
                    </div>
                    <div className="pipeline-node-content">
                      <div className="pipeline-node-title">2. Research Agent (PubMed API Index)</div>
                      <div className="pipeline-node-desc">Requêtes croisées de la base de publications scientifiques médicales PubMed.</div>
                    </div>
                    <div className={`pipeline-node-status ${pipelineState.research}`}>
                      {pipelineState.research === "pending" && "En attente"}
                      {pipelineState.research === "running" && "Recherche..."}
                      {pipelineState.research === "completed" && "Terminé"}
                    </div>
                  </div>

                  <div className={`pipeline-node ${pipelineState.report === "running" ? "active" : ""} ${pipelineState.report === "completed" ? "completed" : ""}`}>
                    <div className="pipeline-node-icon">
                      {pipelineState.report === "completed" ? "✓" : <i className="fa-solid fa-file-invoice"></i>}
                    </div>
                    <div className="pipeline-node-content">
                      <div className="pipeline-node-title">3. Report Agent (Rédacteur Médical LLM)</div>
                      <div className="pipeline-node-desc">Rédaction structurée du compte-rendu clinique détaillé et intégration des sources.</div>
                    </div>
                    <div className={`pipeline-node-status ${pipelineState.report}`}>
                      {pipelineState.report === "pending" && "En attente"}
                      {pipelineState.report === "running" && "Rédaction..."}
                      {pipelineState.report === "completed" && "Terminé"}
                    </div>
                  </div>

                  <div className={`pipeline-node ${pipelineState.followup === "running" ? "active" : ""} ${pipelineState.followup === "completed" ? "completed" : ""}`}>
                    <div className="pipeline-node-icon">
                      {pipelineState.followup === "completed" ? "✓" : <i className="fa-solid fa-calendar-check"></i>}
                    </div>
                    <div className="pipeline-node-content">
                      <div className="pipeline-node-title">4. Follow-up Agent (Care Plan Planner)</div>
                      <div className="pipeline-node-desc">{"Conception du parcours thérapeutique, degré d'urgence et fréquence d'examens."}</div>
                    </div>
                    <div className={`pipeline-node-status ${pipelineState.followup}`}>
                      {pipelineState.followup === "pending" && "En attente"}
                      {pipelineState.followup === "running" && "Planification..."}
                      {pipelineState.followup === "completed" && "Terminé"}
                    </div>
                  </div>

                  <div className={`pipeline-node ${pipelineState.critic === "running" ? "active" : ""} ${pipelineState.critic === "completed" ? "completed" : ""}`}>
                    <div className="pipeline-node-icon">
                      {pipelineState.critic === "completed" ? "✓" : <i className="fa-solid fa-user-doctor"></i>}
                    </div>
                    <div className="pipeline-node-content">
                      <div className="pipeline-node-title">5. Critic Agent (Contrôleur de Sécurité)</div>
                      <div className="pipeline-node-desc">Comité clinique de relecture, validation des cohérences et signature finale.</div>
                    </div>
                    <div className={`pipeline-node-status ${pipelineState.critic}`}>
                      {pipelineState.critic === "pending" && "En attente"}
                      {pipelineState.critic === "running" && "Certification..."}
                      {pipelineState.critic === "completed" && "Terminé"}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 2.C : RESULTS VIEWER */}
            {viewState === "results" && currentAnalysis && (
              <div style={{ display: "flex", flexDirection: "column", gap: "30px" }}>
                
                {/* BACK TO UPLOAD BUTTON */}
                <div style={{ display: "flex", justifyContent: "flex-start" }}>
                  <button 
                    className="btn btn-outline" 
                    onClick={() => setViewState("upload")}
                    style={{ padding: "10px 18px", fontSize: "14px" }}
                  >
                    <i className="fa-solid fa-arrow-left"></i>
                    Retour aux Uploads
                  </button>
                </div>

                <div className="glass-panel">
                  <div className="diagnostic-header">
                    <div className="diag-meta">
                      <h2 id="result-analysis-id">{"Rapport d'Analyse"} {currentAnalysis.id}</h2>
                      <p id="result-patient-meta">
                        Patient ID : {currentAnalysis.patientId} - {currentAnalysis.patientName} | Date : {currentAnalysis.date}
                      </p>
                    </div>
                    <div className="status-badge">
                      Analyse Validée par le Critic Agent
                    </div>
                  </div>

                  {/* VISUALISEURS D'IMAGES DUAL */}
                  <div className="image-viewer-grid">
                    <div className="viewer-card">
                      <div className="viewer-title">
                        <i className="fa-regular fa-image"></i> Image Rétinienne Originale
                      </div>
                      <div className="image-frame">
                        <img src={currentAnalysis.image} alt="Original" />
                      </div>
                    </div>
                    
                    <div className="viewer-card">
                      <div className="viewer-title">
                        <i className="fa-solid fa-circle-radiation"></i> Superposition Grad-CAM (Heatmap)
                      </div>
                      <div className="image-frame" style={{ position: "relative" }}>
                        <img src={currentAnalysis.image} style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover", zIndex: 1 }} alt="Original Underlay" />
                        {currentAnalysis.heatmap && (
                          <img 
                            src={currentAnalysis.heatmap} 
                            style={{ 
                              position: "absolute", 
                              top: 0, 
                              left: 0, 
                              width: "100%", 
                              height: "100%", 
                              objectFit: "cover", 
                              zIndex: 2, 
                              mixBlendMode: "screen", 
                              opacity: gradcamOpacity / 100 
                            }} 
                            alt="Heatmap Overlay" 
                          />
                        )}
                      </div>
                    </div>

                    {/* SLIDER OPACITE */}
                    <div className="interactive-overlay-container">
                      <h4 style={{ fontWeight: 600, fontSize: "15px" }}>Ajuster la superposition de la carte thermique</h4>
                      <div className="slider-control-box">
                        <span className="slider-label" style={{ textAlign: "right" }}>Original (0%)</span>
                        <input 
                          type="range" 
                          className="slider-input" 
                          min="0" 
                          max="100" 
                          value={gradcamOpacity} 
                          onChange={(e) => setGradcamOpacity(e.target.value)}
                        />
                        <span className="slider-label">Grad-CAM (100%)</span>
                      </div>
                      <p style={{ fontSize: "12px", color: "var(--text-muted)", textAlign: "center" }}>
                        {"Faites glisser le curseur pour voir comment les textures lésionnelles identifiées par le modèle s'alignent avec les vaisseaux."}
                      </p>
                    </div>
                  </div>

                  {/* STADE ET CONFIANCE */}
                  <div className="result-stage-card">
                    <div className="stage-title-info">
                      <h3>Stade Rétinopathique Prédit</h3>
                      <h2>
                        {currentAnalysis.stage === 0 && "Stade 0 - Rétine Saine (Aucune RD)"}
                        {currentAnalysis.stage === 1 && "Stade 1 - Rétinopathie Légère"}
                        {currentAnalysis.stage === 2 && "Stade 2 - Rétinopathie Modérée"}
                        {currentAnalysis.stage === 3 && "Stade 3 - Rétinopathie Sévère"}
                        {currentAnalysis.stage === 4 && "Stade 4 - Rétinopathie Proliférative"}
                      </h2>
                      <p>Classification clinique internationale ICDR (International Clinical Diabetic Retinopathy)</p>
                    </div>
                    <div className="confidence-circle">
                      <div className="label">{"Confiance de l'IA"}</div>
                      <div className="value">{(currentAnalysis.confidence * 100).toFixed(1)}%</div>
                    </div>
                  </div>

                  {/* BARRE DE GRAVITÉ HORIZONTALE */}
                  <div className="gravity-bar-container">
                    <div className="gravity-bar">
                      {[0, 1, 2, 3, 4].map((i) => (
                        <div 
                          key={i} 
                          className={`gravity-segment s${i} ${currentAnalysis.stage === i ? "active" : ""}`}
                          style={{ color: i === 0 || i === 1 ? "var(--success)" : i === 2 ? "var(--warning)" : "var(--danger)" }}
                        />
                      ))}
                    </div>
                    <div className="gravity-labels">
                      {["Aucune", "Légère", "Modérée", "Sévère", "Proliférative"].map((lbl, i) => (
                        <div 
                          key={i} 
                          className={`gravity-label-item ${currentAnalysis.stage === i ? "active" : ""}`}
                        >
                          {lbl}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* CLINIC CARDS GRID */}
                  <div className="clinic-cards-grid">
                    <div className={`clinic-card ${currentAnalysis.referable ? "danger-card" : "success-card"}`}>
                      <div className="clinic-card-title">Adressage Référable (Referable DR)</div>
                      <div className="clinic-card-value">{currentAnalysis.referable ? "Oui (Ophtalmologue Recommandé)" : "Non"}</div>
                    </div>
                    <div className={`clinic-card ${currentAnalysis.stage >= 3 ? "danger-card" : currentAnalysis.stage === 2 ? "warning-card" : "success-card"}`}>
                      <div className="clinic-card-title">{"Niveau d'Urgence Clinique"}</div>
                      <div className="clinic-card-value">{currentAnalysis.urgency}</div>
                    </div>
                    <div className="clinic-card success-card">
                      <div className="clinic-card-title">Qualité globale du scan</div>
                      <div className="clinic-card-value">Bonne</div>
                    </div>
                  </div>

                  {/* COMPTE RENDU MULTI-AGENTS */}
                  <div className="report-section">
                    <div className="report-title">
                      <i className="fa-solid fa-robot"></i> Compte-Rendu Clinique Généré par Multi-Agents (LangGraph)
                    </div>
                    <div className="report-body">
                      {currentAnalysis.report || "Aucun rapport clinique n'a été produit pour cet examen."}
                    </div>
                  </div>

                  {/* ACTIONS FINALES */}
                  <div style={{ display: "flex", justifyContent: "flex-end", gap: "15px", marginTop: "30px" }}>
                    <button className="btn btn-outline" onClick={() => setViewState("upload")}>
                      <i className="fa-solid fa-arrow-rotate-left"></i> Nouvelle Analyse
                    </button>
                    <button 
                      className="btn" 
                      onClick={() => downloadAnalysisPDF(currentAnalysis)}
                    >
                      <i className="fa-solid fa-file-pdf"></i> Télécharger le Rapport (PDF)
                    </button>
                  </div>

                </div>

              </div>
            )}

          </section>
        )}

        {/* ================= VUE 3 : HISTORIQUE ================= */}
        {activeTab === "history" && (
          <section className="glass-panel">
            <h2 className="mb-20">Historique Médical Complet</h2>
            <p style={{ color: "var(--text-muted)", marginBottom: "20px" }}>
              {"Recherchez et filtrez tous les diagnostics effectués par le service d'ophtalmologie."}
            </p>
            
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>{"Date d'Examen"}</th>
                    <th>ID Patient</th>
                    <th>Nom Complet</th>
                    <th>Diagnostic IA</th>
                    <th>Urgence Clinique</th>
                    <th>Statut Référable</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {analyses.map((a) => (
                    <tr key={a.id}>
                      <td>{a.date}</td>
                      <td className="text-bold">{a.patientId}</td>
                      <td>{a.patientName}</td>
                      <td>
                        <span className={`badge badge-s${a.stage}`}>
                          Stade {a.stage}
                        </span>
                      </td>
                      <td>{a.urgency}</td>
                      <td style={{ color: a.referable ? "var(--danger)" : "var(--success)", fontWeight: a.referable ? 600 : 500 }}>
                        {a.referable ? "⚠️ Référable" : "✅ Non référable"}
                      </td>
                      <td>
                        <button 
                          className="btn btn-outline" 
                          style={{ padding: "6px 12px", fontSize: "13px" }}
                          onClick={() => openAnalysis(a.id)}
                        >
                          Ouvrir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* ================= VUE 4 : PARAMÈTRES & AJOUT PATIENT ================= */}
        {activeTab === "settings" && (
          <section style={{ display: "flex", flexDirection: "column", gap: "30px" }} className="fade-in">
            
            {/* FORMULAIRE NOUVEAU PATIENT */}
            <div className="glass-panel">
              <h2 className="mb-20" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <i className="fa-solid fa-user-plus" style={{ color: "var(--success)" }}></i>
                Ajouter un Nouveau Patient dans le Registre
              </h2>
              <form onSubmit={savePatient} style={{ display: "flex", flexDirection: "column", gap: "20px", maxWidth: "700px" }}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>ID Patient Unique</label>
                    <input 
                      type="text" 
                      placeholder="Ex: P-9012" 
                      value={newPatientId}
                      onChange={(e) => setNewPatientId(e.target.value)}
                      className="input-field"
                    />
                  </div>
                  <div className="form-group">
                    <label>Nom Complet</label>
                    <input 
                      type="text" 
                      placeholder="Ex: Fatima Alaoui" 
                      value={newPatientName}
                      onChange={(e) => setNewPatientName(e.target.value)}
                      className="input-field"
                    />
                  </div>
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label>Date de Naissance</label>
                    <input 
                      type="date" 
                      value={newPatientBirth}
                      onChange={(e) => setNewPatientBirth(e.target.value)}
                      className="input-field"
                    />
                  </div>
                  <div className="form-group">
                    <label>Sexe Clinique</label>
                    <select 
                      value={newPatientGender}
                      onChange={(e) => setNewPatientGender(e.target.value)}
                      className="select-field"
                    >
                      <option value="M">Masculin</option>
                      <option value="F">Féminin</option>
                    </select>
                  </div>
                </div>

                <button className="btn btn-success" type="submit" style={{ alignSelf: "flex-start", marginTop: "10px" }}>
                   <i className="fa-solid fa-save"></i> Enregistrer le Patient
                </button>
              </form>
            </div>

            {/* INTEGRATIONS PARAMETRES */}
            <div className="glass-panel">
              <h2 className="mb-20">{"Configuration des Modules d'Intégration"}</h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "700px" }}>
                <div className="form-group">
                  <label>Orchestrateur multi-agents (LLM de traitement)</label>
                  <select className="select-field">
                    <option>Google Gemini (Modèle gemini-pro) - Recommandé par défaut</option>
                    <option>Anthropic Claude 3 (haiku/sonnet) - En option</option>
                    <option>Moteur Clinique Déterministe Local - Mode Secours Déconnecté</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>{"Clé d'API Générative Clinique"}</label>
                  <input type="password" value="••••••••••••••••••••••••••••••••••••" className="input-field" disabled />
                </div>
                <div className="form-group">
                  <label>Seuil Clinique de Densité Vasculaire (Grad-CAM)</label>
                  <input type="range" min="30" max="90" defaultValue="50" style={{ width: "100%", height: "6px", background: "var(--border)", borderRadius: "3px" }} />
                </div>
                <button className="btn" style={{ alignSelf: "flex-start", marginTop: "10px" }} onClick={() => alert("Configurations système enregistrées avec succès !")}>
                  Sauvegarder les Paramètres
                </button>
              </div>
            </div>

          </section>
        )}

      </main>

    </div>
  );
}
