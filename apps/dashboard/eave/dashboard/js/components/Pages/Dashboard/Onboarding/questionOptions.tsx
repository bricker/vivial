// TODO: rename this stuff at the very least
export interface ColourOption {
  readonly value: string;
  readonly label: string;
  readonly isFixed?: boolean;
  readonly isDisabled?: boolean;
}

export const platformOptions: ColourOption[] = [
  { value: "web_app", label: "Web App" },
  { value: "mobile", label: "Mobile" },
  { value: "desktop_app", label: "Desktop App" },
  { value: "wear_os", label: "Wear OS" },
  { value: "api", label: "API" },
];

export const databaseOptions: ColourOption[] = [
  { value: "mysql", label: "MySQL" },
  { value: "spanner", label: "Spanner" },
  { value: "mongodb", label: "MongoDB" },
];

export const languagesOptions: ColourOption[] = [
  { value: "python", label: "Python" },
  { value: "ruby", label: "Ruby" },
  { value: "java", label: "Java" },
  { value: "swift", label: "Swift" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "go", label: "Go" },
  { value: "kotlin", label: "Kotlin" },
  { value: "c++", label: "C++" },
];

export const frameworksOptions: ColourOption[] = [
  { value: "flask", label: "Flask" },
  { value: "express", label: "Express.js" },
  { value: "gin", label: "Gin" },
  { value: "fast_api", label: "Fast API" },
  { value: "django", label: "Django" },
  { value: "ror", label: "Ruby on Rails" },
  { value: "nextjs", label: "Next.js" },
];

export const thirdPartyOptions: ColourOption[] = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "gemini", label: "Gemini" },
  { value: "stripe", label: "Stripe" },
  { value: "paypal", label: "PayPal" },
  { value: "plaid", label: "Plaid" },
  { value: "square", label: "Square" },
];

export const copyString = `Getting started with Eave. Please answer the questions below. 
All information is kept confidential and strictly for the purposes of providing you with a proper product intelligence solution. 
Which platform(s) does your product support? E.g. Web, iOS, Android, etc.
Which programming language(s) are used to build your product? E.g. Python, JavaScript, Go, etc.
Which programming libraries and framework(s) are used to build your product? E.g. Flask, Express, Gin, etc. 
Which database(s) are used to store your product data? E.g. MySQL, Spanner, MongoDB, etc. 
Which third party service(s) are integrated into your product? E.g. OpenAI, Anthropic, Gemini, Stripe, PayPal, Plaid, Square`;
