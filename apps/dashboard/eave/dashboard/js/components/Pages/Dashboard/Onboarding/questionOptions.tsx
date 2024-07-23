// colorOptions.ts
export interface ColourOption {
  readonly value: string;
  readonly label: string;
  readonly isFixed?: boolean;
  readonly isDisabled?: boolean;
}

export const platformOptions: ColourOption[] = [
  { value: "web_app", label: "Web App", isFixed: true },
  { value: "mobile", label: "Mobile" },
  { value: "desktop_app", label: "Desktop App" },
  { value: "wear_os", label: "Wear OS" },
  { value: "api", label: "API" },
];

export const languagesOptions: ColourOption[] = [
  { value: "python", label: "Python" },
  { value: "ruby", label: "Ruby" },
  { value: "java", label: "Java" },
  { value: "swift", label: "Swift" },
  { value: "javascript", label: "Javascript" },
  { value: "go", label: "Go" },
  { value: "kotlin", label: "Kotlin" },
  { value: "sql", label: "SQL" },
  { value: "c++", label: "C++" },
];

export const frameworksOptions: ColourOption[] = [
  { value: "red", label: "Red" },
  { value: "orange", label: "Orange" },
  { value: "yellow", label: "Yellow" },
];

export const aiOptions: ColourOption[] = [
  { value: "purple", label: "Purple" },
  { value: "violet", label: "Violet" },
  { value: "lavender", label: "Lavender" },
];

export const copyString =
  "Getting started with Eave. Please answer the questions below. All information is kept confidential and strictly for the purposes of providing you with a proper product intelligence solution. Which platform(s) does your product support? E.g. Web, iOS, Android, etc.Which programming language(s) are used to build your product? E.g. Python, JavaScript, Go, etc. Which programming libraries and framework(s) are used to build your product? E.g. Flask, Express, Gin, etc. Which database(s) are used to store your product data? E.g. MySQL, Spanner, MongoDB, etc. Which third party service(s) are integrated into your product? E.g. OpenAI, Anthropic, Stripe, etc.";
