export interface Claim {
  id: string;
  content: string;
  verdict: string;
  confidence: number;
}

export interface Section {
  title: string;
  content: string;
  claims: Claim[];
}

export interface Review {
  recommendation: string;
  confidence: number;
  sections: Section[];
}
