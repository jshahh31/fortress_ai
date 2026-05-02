export interface HelpArticle {
  id: string;
  title: string;
  body: string;
}

export interface HelpCategory {
  slug: string;
  title: string;
  description: string;
  icon: string;
  articles: HelpArticle[];
}

export const HELP_DATA: HelpCategory[] = [
  {
    slug: "getting-started",
    title: "Getting Started",
    description: "Learn the basics of Fortress AI and run your first contract analysis.",
    icon: "Rocket",
    articles: [
      { id: "gs-1", title: "Creating your account", body: "Visit auth.fortressai.com/signup and choose your account type — **Attorney** or **Individual**. Each type receives tailored analysis output. You can change your account type later in Account Settings." },
      { id: "gs-2", title: "Uploading your first contract", body: "From the chat interface, click the **📎 button** or drag and drop a file into the upload zone. We support **PDF, DOCX, TXT, and photo** formats up to 25 MB." },
      { id: "gs-3", title: "Understanding your risk report", body: "Every analysis produces a structured report with: **Verdict** (Sign/Negotiate/Reject/Seek Counsel), **Risk Matrix**, **Clause-by-Clause Analysis**, **Red Flags**, and **Recommendations**." },
    ],
  },
  {
    slug: "using-reports",
    title: "Using Reports",
    description: "Get the most from your risk assessment reports.",
    icon: "FileCheck",
    articles: [
      { id: "ur-1", title: "Understanding the verdict", body: "The verdict is the top-level recommendation: **SIGN** (safe to proceed), **NEGOTIATE** (address concerns first), **REJECT** (critical risks), or **SEEK COUNSEL** (complex issues requiring professional review)." },
      { id: "ur-2", title: "Reading the risk matrix", body: "The risk matrix visually categorizes findings into four tiers: **Critical** (immediate attention), **High** (significant concern), **Medium** (review recommended), and **Low** (standard/acceptable)." },
      { id: "ur-3", title: "Exporting reports", body: "Click the **PDF** or **DOCX** export buttons at the bottom of any completed report. The exported file includes all sections and maintains professional formatting." },
    ],
  },
  {
    slug: "contract-types",
    title: "Contract Types",
    description: "Supported contract types and analysis capabilities.",
    icon: "FileText",
    articles: [
      { id: "ct-1", title: "Supported contract types", body: "Fortress AI supports 8 contract types: **Residential Lease**, **Employment Agreement**, **Freelance/Contractor**, **NDA (Personal)**, **Partnership Agreement**, **Vendor/Service Agreement**, **NDA (Business)**, and **Consulting Agreement**." },
      { id: "ct-2", title: "Auto-detection", body: "When you upload a contract, our AI automatically identifies the contract type. You can confirm or override this detection before analysis begins." },
    ],
  },
  {
    slug: "for-attorneys",
    title: "For Attorneys",
    description: "Professional features for legal practitioners.",
    icon: "Scale",
    articles: [
      { id: "fa-1", title: "Attorney mode features", body: "Attorney mode provides: legal citations (UCC, Restatement), negotiation leverage points, redline-ready suggested language, industry benchmark comparisons, and client-sharable reports." },
      { id: "fa-2", title: "Sharing reports with clients", body: "Export any report as PDF or DOCX and share directly with your clients. Reports generated in Attorney mode use professional legal language suitable for client communications." },
    ],
  },
  {
    slug: "for-individuals",
    title: "For Individuals",
    description: "Plain-language guidance for non-lawyers.",
    icon: "User",
    articles: [
      { id: "fi-1", title: "Individual mode features", body: "Individual mode explains everything in **plain English**: \"What this means for you\" summaries, simplified risk descriptions, step-by-step action items, and guidance on when to consult a lawyer." },
      { id: "fi-2", title: "When to hire a lawyer", body: "If your report verdict is **REJECT** or **SEEK COUNSEL**, we strongly recommend consulting with a qualified attorney. We also flag situations where professional legal advice is especially important." },
    ],
  },
  {
    slug: "pricing-billing",
    title: "Pricing & Billing",
    description: "Plans, billing, and subscription management.",
    icon: "CreditCard",
    articles: [
      { id: "pb-1", title: "Free plan", body: "Every account includes **3 free contract analyses per month**. Free plan reports include all features — verdict, risk matrix, clause analysis, and recommendations." },
      { id: "pb-2", title: "Upgrading your plan", body: "Visit **Account Settings** to upgrade to Professional or Firm plans. Upgrades take effect immediately and include priority processing and unlimited analyses." },
    ],
  },
  {
    slug: "faq",
    title: "FAQ",
    description: "Frequently asked questions about Fortress AI.",
    icon: "HelpCircle",
    articles: [
      { id: "faq-1", title: "Is my data secure?", body: "Yes. Your documents are **never stored** after analysis. All processing happens on isolated infrastructure, and all connections are encrypted with TLS 1.3." },
      { id: "faq-2", title: "Can Fortress AI replace a lawyer?", body: "No. Fortress AI is a **risk assessment tool**, not a substitute for legal advice. Always consult a qualified attorney for important legal decisions. Our reports are designed to help you make more informed decisions." },
      { id: "faq-3", title: "What file formats are supported?", body: "We support **PDF, DOCX, TXT, PNG, JPG, JPEG, WebP, and HEIC**. Maximum file size is 25 MB." },
    ],
  },
  {
    slug: "contact-support",
    title: "Contact Support",
    description: "Get help from our team.",
    icon: "MessageCircle",
    articles: [
      { id: "cs-1", title: "How to reach us", body: "Email us at **support@fortressai.com** or use the in-app chat. We typically respond within 24 hours on business days." },
      { id: "cs-2", title: "Bug reports", body: "Found a bug? Email **bugs@fortressai.com** with a description of the issue, your browser/OS, and any screenshots. We appreciate your help improving the platform." },
    ],
  },
];
