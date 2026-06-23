# SkillBridge AI - API Documentation for Frontend Integration

Welcome! This documentation is designed to help frontend developers integrate with the SkillBridge AI backend. The backend is built using FastAPI and exposes endpoints for career recommendation, semantic match scoring, skill gap analysis, and personalized learning roadmaps.

## 🚀 Base URL
During local development, the API runs at:
```
http://localhost:8501
```

---

## 📌 Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| [`/`](#1-root-status) | `GET` | Check if the API is running and get the current version. |
| [`/health`](#2-health-check) | `GET` | Health check endpoint for container/service monitoring. |
| [`/recommend`](#3-recommend-careers) | `POST` | Suggest top $N$ careers based on user's current skills. |
| [`/match-score`](#4-calculate-match-score) | `POST` | Calculate semantic similarity and job readiness scores. |
| [`/skill-gap`](#5-analyze-skill-gap) | `POST` | Identify missing skills for a target career. |
| [`/roadmap`](#6-generate-learning-roadmap) | `POST` | Create an AI-guided weekly learning curriculum to bridge the gap. |
| [`/analyze`](#7-unified-analysis) | `POST` | Perform all analyses in a single request (Recommended for dashboard loading). |

---

## 🔍 Endpoint Details

### 1. Root Status
Verify the server status.

* **URL:** `/`
* **Method:** `GET`
* **Response Example (200 OK):**
```json
{
  "success": true,
  "message": "SkillBridgeAI API Running",
  "version": "1.0.0"
}
```

---

### 2. Health Check
Basic status check.

* **URL:** `/health`
* **Method:** `GET`
* **Response Example (200 OK):**
```json
{
  "success": true,
  "status": "healthy"
}
```

---

### 3. Recommend Careers
Fetch the top career matches matching the user's skill set.

* **URL:** `/recommend`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Request Body Schema:**
  * `skills` (string, required): Comma-separated list of user skills.
  * `top_k` (integer, optional, default: `5`): Maximum number of careers to return.
* **Request Body Example:**
```json
{
  "skills": "python, sql, machine learning",
  "top_k": 3
}
```
* **Response Body Example (200 OK):**
```json
{
  "success": true,
  "recommendations": [
    {
      "career": "Fintech Engineer",
      "score": 93.5,
      "suitability": "Sangat Cocok (High Suitability)",
      "explanation": "Sangat direkomendasikan karena memiliki tingkat kesamaan semantik profil latar belakang yang sangat tinggi sebesar 93.5%.",
      "description": "Mengembangkan aplikasi mobile lintas platform, AI, dan sistem data untuk industri finansial..."
    },
    {
      "career": "Data Analyst",
      "score": 85.2,
      "suitability": "Sangat Cocok (High Suitability)",
      "explanation": "Sangat direkomendasikan karena memiliki tingkat kesamaan semantik profil latar belakang yang sangat tinggi sebesar 85.2%.",
      "description": "Mengolah, membersihkan, dan memvisualisasikan data untuk memberikan wawasan bisnis..."
    }
  ]
}
```

---

### 4. Calculate Match Score
Calculates semantic similarity and explicit skill readiness score for a chosen career.

* **URL:** `/match-score`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Request Body Schema:**
  * `skills` (string, required): Comma-separated list of user skills.
  * `target_career` (string, required): Exact name of the target career.
* **Request Body Example:**
```json
{
  "skills": "python, sql, machine learning",
  "target_career": "Data Analyst"
}
```
* **Response Body Example (200 OK):**
```json
{
  "job": "Data Analyst",
  "semantic_match": "38.16%",
  "matched_skills": [
    "python",
    "sql"
  ],
  "missing_skills": [
    "data analysis",
    "excel",
    "leadership",
    "mysql",
    "postgresql",
    "power bi",
    "statistics",
    "tableau"
  ],
  "readiness_score": "12.20%",
  "gap_percentage": "87.80%"
}
```

---

### 5. Analyze Skill Gap
Get the list of missing skills for a chosen career.

* **URL:** `/skill-gap`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Request Body Schema:**
  * `skills` (string, required): Comma-separated list of user skills.
  * `target_career` (string, required): Exact name of the target career.
* **Request Body Example:**
```json
{
  "skills": "python, sql, machine learning",
  "target_career": "Data Analyst"
}
```
* **Response Body Example (200 OK):**
```json
{
  "success": true,
  "career": "Data Analyst",
  "matched_skills": ["python", "sql"],
  "missing_skills": [
    "data analysis",
    "excel",
    "leadership",
    "mysql",
    "postgresql",
    "power bi",
    "statistics",
    "tableau"
  ]
}
```

---

### 6. Generate Learning Roadmap
Queries the Gemini Generative AI API to produce a personal learning curriculum.

* **URL:** `/roadmap`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Request Body Schema:**
  * `skills` (string, required): Comma-separated list of user skills.
  * `target_career` (string, required): Target career title.
  * `missing_skills` (array of strings, required): List of missing skills.
  * `gap_percentage` (string, optional, default: `"100.00%"`): Current gap score.
  * `readiness_score` (string, optional, default: `"0.00%"`): Readiness score.
* **Request Body Example:**
```json
{
  "skills": "python, sql, machine learning",
  "target_career": "Data Analyst",
  "missing_skills": ["tableau", "statistics"],
  "gap_percentage": "30%",
  "readiness_score": "70%"
}
```
* **Response Body Example (200 OK):**
```json
{
  "success": true,
  "data": {
    "skill_gap_analysis": [
      "Analisis kritis mengenai gap skill pengguna berdasarkan data input..."
    ],
    "roadmap": {
      "W1": {
        "tag": "Fokus Topik Utama Minggu 1",
        "title": "Pengenalan Visualisasi Data dengan Tableau",
        "d1": {
          "title": "Dasar Antarmuka Tableau",
          "desc": "Mempelajari workspace Tableau dan cara menghubungkan dataset csv.",
          "resources": [
            { "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+Tableau+bahasa+indonesia" },
            { "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+Tableau+bahasa+indonesia" }
          ]
        },
        "d2": { "title": "...", "desc": "...", "resources": [] }
      },
      "W2": null
    },
    "note": "Catatan motivasi atau instruksi tambahan."
  }
}
```

---

### 7. Unified Analysis
Runs all tasks (recommendation, scoring, gap analysis, and roadmap generation) in one round-trip. **Highly recommended for initial loading of a dashboard page.**

* **URL:** `/analyze`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Request Body Schema:**
  * `skills` (string, required): Comma-separated list of user skills.
  * `selected_career` (string, optional, default: `null`): Target career. If null, the API auto-selects the top career from the recommendations.
  * `top_k` (integer, optional, default: `5`): Number of career recommendations to evaluate.
* **Request Body Example:**
```json
{
  "skills": "python, sql, machine learning",
  "selected_career": "Data Analyst",
  "top_k": 3
}
```
* **Response Body Example (200 OK):**
```json
{
  "success": true,
  "timestamp": "2026-06-17T20:41:00.000Z",
  "selected_career": "Data Analyst",
  "recommendations": [
    { "career": "Data Analyst", "score": 85.2, "suitability": "..." }
  ],
  "match_score": {
    "job": "Data Analyst",
    "semantic_match": "38.16%",
    "matched_skills": ["python", "sql"],
    "missing_skills": ["excel", "tableau"],
    "readiness_score": "12.20%",
    "gap_percentage": "87.80%"
  },
  "skill_gap": {
    "success": true,
    "career": "Data Analyst",
    "matched_skills": ["python", "sql"],
    "missing_skills": ["excel", "tableau"]
  },
  "roadmap": {
    "success": true,
    "data": {
      "skill_gap_analysis": [],
      "roadmap": { ... },
      "note": "..."
    }
  }
}
```

---

## 🛠️ Frontend Integration Best Practices

1. **Handling Response Times (Gemini API):**
   Calls to `/roadmap` or `/analyze` make an external request to the Google Gemini API. This call typically takes **3–6 seconds**. 
   * **Tip:** Show a loading skeleton or a progress indicator (e.g., *"Generating your personalized roadmap..."*) on the frontend while these requests are pending.
   * **Alternative:** You can first request `/recommend` (extremely fast, offline ML) to display the career cards instantly, and only fetch `/roadmap` when the user clicks a specific career.

2. **Parsing Roadmap Output:**
   * In the `/roadmap` response, the `data` object might be a pre-parsed JSON dictionary or a raw JSON string depending on edge cases in model serialization. 
   * **Tip:** Always check the type of `data`. If it is a string, run `JSON.parse(data)` on the frontend before rendering.

3. **CORS Configuration:**
   * The backend has CORS middleware enabled with `allow_origins=["*"]`, allowing direct fetches from any frontend origin (`localhost:3000`, `localhost:5173`, etc.) without preflight issues.
