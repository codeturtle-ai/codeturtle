# Next.js UI Implementation Plan

## Overview
This plan outlines the creation of a modern, responsive web UI using Next.js for the FastAPI Security Agent. The UI will replace the current Jinja2-based templates with a React-based frontend, providing an interactive experience for PR analysis, results visualization, and reports.

## Architecture
- **Frontend (Next.js)**: Client-side React app handling user interactions, forms, and displays. Communicates with FastAPI via API calls.
- **Backend (FastAPI)**: Unchanged—provides REST API endpoints for data.
- **Deployment**: Next.js can be built as static files and served by FastAPI, or deployed separately (e.g., Vercel for Next.js).
- **Communication**: API calls via `fetch()` or Axios with CORS enabled on FastAPI.

## Tech Stack
- Next.js 14 (React framework with App Router)
- TypeScript for type safety
- Tailwind CSS for responsive styling
- Axios for API requests
- Chart.js for data visualizations
- React Hook Form + Zod for form validation
- Jest for testing

## Key Features
- PR analysis form with real-time validation
- Interactive results display (vulnerability cards, risk score charts)
- Responsive design for mobile/desktop
- Loading states and error handling
- Reports dashboard with visualizations

## Prerequisites
- Node.js 18+ installed
- Basic React/TypeScript knowledge
- FastAPI backend running for integration
- Project repository access

## Step-by-Step Implementation

### 1. Setup Next.js Project (15-30 minutes)
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend
npm install axios chart.js react-chartjs-2 react-hook-form @hookform/resolvers zod
```
- Configure environment: `.env.local` with `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- Update `package.json` for build/export scripts

### 2. Project Structure (10 minutes)
```
frontend/
├── src/
│   ├── app/                 # Next.js app router
│   │   ├── layout.tsx       # Global layout
│   │   ├── page.tsx         # Home page
│   │   ├── analyze/         # Analysis page
│   │   │   ├── page.tsx
│   │   │   ├── loading.tsx  # Loading UI
│   │   ├── reports/         # Reports dashboard
│   ├── components/          # Reusable components
│   │   ├── PRAnalysisForm.tsx
│   │   ├── VulnerabilityCard.tsx
│   │   ├── RiskScoreChart.tsx
│   │   ├── Navbar.tsx
│   ├── lib/                 # Utilities
│   │   ├── api.ts           # API client functions
│   │   ├── types.ts         # TypeScript types
│   ├── styles/              # Global styles
```

### 3. API Integration Layer (20-30 minutes)
Create `src/lib/api.ts`:
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 10000,
});

export const analyzePR = async (url: string) => {
  const response = await api.post('/analyze', { url });
  return response.data;
};

export const getReport = async (prUrl?: string) => {
  const response = await api.get('/report', { params: { pr_url: prUrl } });
  return response.data;
};
```
- Add error handling for rate limits and network issues
- Create `src/lib/types.ts` for shared TypeScript interfaces

### 4. Build Core Components (1-2 hours)

#### Navbar (`src/components/Navbar.tsx`)
- Simple navigation with links to home, analyze, reports

#### PR Analysis Form (`src/components/PRAnalysisForm.tsx`)
- React Hook Form with Zod validation
- PR URL input field with demo examples
- Submit handler calling `analyzePR()`
- Display results on success/error

#### Vulnerability Card (`src/components/VulnerabilityCard.tsx`)
- Displays individual vulnerabilities
- Icons and color-coding by severity
- Description and remediation suggestions

#### Risk Score Chart (`src/components/RiskScoreChart.tsx`)
- Chart.js visualization of risk score
- Gauge or bar chart with severity indicators

### 5. Pages Implementation (45-60 minutes)

#### Home Page (`src/app/page.tsx`)
- Hero section with project description
- Feature highlights
- Call-to-action button to analyze

#### Analyze Page (`src/app/analyze/page.tsx`)
- Embed PRAnalysisForm component
- Loading states during analysis
- Results display with charts and cards

#### Reports Page (`src/app/reports/page.tsx`)
- Fetch and display summary reports
- Charts for vulnerability statistics
- Historical analysis trends

#### Global Layout (`src/app/layout.tsx`)
- Navbar integration
- Tailwind CSS setup
- Metadata and SEO tags

### 6. Styling & Responsiveness (30 minutes)
- Tailwind CSS classes for mobile-first design
- Custom color schemes for severity levels:
  - Low: Green
  - Medium: Yellow
  - High: Orange
  - Critical: Red
- Accessibility features (alt text, keyboard navigation)
- Dark/light mode support (optional)

### 7. Testing & Optimization (30-45 minutes)
- Unit tests with Jest and React Testing Library
- API function mocking for isolated testing
- Performance optimization:
  - Static site generation for fast loading
  - Image optimization and lazy loading
  - Bundle analysis and tree shaking

### 8. Integration & Deployment (30 minutes)
- Enable CORS in FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- Build static files: `npm run build && npm run export`
- Integrate with FastAPI: Mount static files
```python
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/out", html=True), name="static")
```

- Deployment options:
  - Vercel/Netlify for Next.js
  - DigitalOcean App Platform for monolithic deployment
  - Update Dockerfile to include Next.js build

## Timeline & Milestones
- **Total Time**: 4-6 hours
- **Milestone 1 (1 hour)**: Project setup and structure
- **Milestone 2 (2 hours)**: Core components and pages
- **Milestone 3 (1 hour)**: Styling, testing, and optimization
- **Milestone 4 (1 hour)**: Integration and deployment

## Risks & Mitigations
- **CORS Issues**: Properly configure middleware in FastAPI
- **API Rate Limits**: Implement retry logic and user feedback
- **Build Complexity**: Start with minimal features, expand later
- **Fallback**: Keep Jinja2 UI as backup if Next.js integration fails

## Benefits Over Current UI
- **Interactivity**: Real-time updates without page reloads
- **Scalability**: React ecosystem for future enhancements
- **User Experience**: Better forms, animations, and responsiveness
- **Maintainability**: Clear separation of frontend/backend concerns
- **Performance**: Static generation and optimized bundles

## Final Output
A complete Next.js website providing:
- Intuitive PR analysis interface
- Visual results with charts and cards
- Professional, responsive design
- Seamless integration with FastAPI backend
- Production-ready for hackathon demo and beyond
