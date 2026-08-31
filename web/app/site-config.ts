import { validatedStreamlitUrl } from "../url-policy";

export const repositoryUrl = "https://github.com/DevenGaikwad/NewsLens-AI";

export const documentationLinks = [
  ["Project report", "docs/NewsLens_AI_Project_Report.docx"],
  ["Setup and run guide", "docs/NewsLens_AI_Setup_and_Run_Guide.docx"],
  ["Developer guide", "docs/NewsLens_AI_Code_Explanation_and_Developer_Guide.docx"],
  ["Concepts and methodology guide", "docs/NewsLens_AI_Complete_Concepts_Methodologies_and_Terminology_Guide.docx"],
  ["Research paper matrix", "docs/NewsLens_AI_Research_Paper_Matrix.xlsx"],
  ["Editorial AI case study", "docs/EDITORIAL_AI_CASE_STUDY.md"],
  ["Placement interview guide", "docs/PLACEMENT_INTERVIEW_GUIDE.md"],
  ["Model card", "docs/MODEL_CARD.md"],
] as const;

export function repositoryPath(path = ""): string {
  const suffix = path ? `/blob/main/${path}` : "";
  return `${repositoryUrl}${suffix}`;
}

export function streamlitUrl(): string {
  return validatedStreamlitUrl();
}
