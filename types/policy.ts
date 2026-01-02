/**
 * Core policy/document type that all sources normalize to.
 * This is the single schema used throughout the application.
 */
export interface CharityPolicy {
    // === REQUIRED FIELDS (all sources must provide) ===

    /** Unique identifier: format is {source}_{source_id}_{date} */
    id: string;

    /** Document or case title */
    title: string;

    /** Brief description (aim for 100-300 chars) */
    summary: string;

    /** Link to original source document */
    source_url: string;

    /** When originally published (ISO 8601: YYYY-MM-DD) */
    published_date: string;

    /** When last updated in source (ISO 8601: YYYY-MM-DD) */
    last_updated: string;

    /** Which regulator/body published this */
    regulator: Regulator;

    /** Primary compliance domain */
    domain: ComplianceDomain;

    /** Type of document */
    document_type: DocumentType;


    // === OPTIONAL FIELDS (source-dependent) ===

    /** For cases: the charity's registration number */
    charity_number?: string;

    /** For cases: name of the charity investigated */
    charity_name?: string;

    /** For cases: small (<£25k), medium (£25k-£1m), large (>£1m) */
    charity_income_band?: "small" | "medium" | "large";

    /** For enforcement: severity assessment */
    risk_level?: "low" | "medium" | "high" | "critical";

    /** For CC cases: their internal case reference */
    case_id?: string;

    /** For cases: open, concluded, ongoing-monitoring */
    case_status?: "open" | "concluded" | "monitoring";

    /** For cases: what action was taken */
    outcome?: string;

    /** For cases: CC-provided issue tags */
    issues_identified?: string[];

    /** For sanctions: which regime (Russia, Counter-Terrorism, etc.) */
    sanctions_regime?: string;

    /** For sanctions: who designated (UN, EU, UK) */
    designated_by?: string;

    /** For ICO: monetary penalty amount in GBP */
    fine_amount?: number;

    /** Keywords extracted for search */
    keywords?: string[];

    /** Full text content (for search indexing, not display) */
    full_text?: string;

    // === CHARITY REGISTER API ENRICHMENT FIELDS ===

    /** Official charity registration number from CC Register */
    cc_registered_number?: string;

    /** Charity suffix (usually 0 for main charity) */
    cc_suffix?: string;

    /** Current registration status (Registered, Removed, etc.) */
    cc_status?: string;

    /** Most recent annual income in GBP */
    cc_latest_income?: number;

    /** Type of governing document */
    cc_governing_document?: string;

    /** Primary geographic region of operation */
    cc_primary_region?: string;
}


// === ENUMS ===

export type Regulator =
    | "CC"      // Charity Commission
    | "ICO"     // Information Commissioner's Office
    | "OFSI"    // Office of Financial Sanctions Implementation
    | "HSE"     // Health and Safety Executive
    | "HMRC"    // HM Revenue & Customs
    | "FR"      // Fundraising Regulator
    | "OSCR"    // Scottish Charity Regulator
    | "CCNI"    // Charity Commission for Northern Ireland
    | "ASA";    // Advertising Standards Authority

export type ComplianceDomain =
    | "governance"
    | "safeguarding"
    | "gdpr"
    | "health_safety"
    | "financial_reporting"
    | "risk_management"
    | "anti_fraud"
    | "sanctions";

export type DocumentType =
    | "guidance"      // How-to documents, best practice
    | "case"          // Investigation/enforcement case
    | "enforcement"   // Formal enforcement action (fines, orders)
    | "regulation"    // Legal requirements
    | "alert"         // Warnings, scam alerts
    | "sanction";     // Sanctions list entry


// === FILTER TYPES (for API/UI) ===

export interface PolicyFilters {
    search?: string;
    regulator?: Regulator | Regulator[];
    domain?: ComplianceDomain | ComplianceDomain[];
    document_type?: DocumentType | DocumentType[];
    date_from?: string;
    date_to?: string;
    has_case_id?: boolean;
    risk_level?: string;
}

export interface PaginationParams {
    page: number;
    per_page: number;
    sort_by: "published_date" | "last_updated" | "title";
    sort_order: "asc" | "desc";
}


// === ANALYTICS TYPES ===

export interface DomainStats {
    domain: ComplianceDomain;
    count: number;
    last_updated: string;
}

export interface RegulatorStats {
    regulator: Regulator;
    total_documents: number;
    cases: number;
    guidance: number;
    last_updated: string;
}

export interface TimelineDataPoint {
    month: string;  // YYYY-MM
    count: number;
    by_domain: Record<ComplianceDomain, number>;
}
