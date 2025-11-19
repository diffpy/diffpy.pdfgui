/**
 * JSON-driven form schema types.
 * All forms in the application are defined using these schemas.
 */

export type FieldType =
  | "text"
  | "number"
  | "email"
  | "password"
  | "select"
  | "checkbox"
  | "radio"
  | "textarea"
  | "file"
  | "range"
  | "date"
  | "array"
  | "object";

export interface ValidationRule {
  type:
    | "required"
    | "min"
    | "max"
    | "minLength"
    | "maxLength"
    | "pattern"
    | "custom";
  value?: any;
  message: string;
}

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface FieldSchema {
  name: string;
  type: FieldType;
  label: string;
  description?: string;
  placeholder?: string;
  defaultValue?: any;
  validation?: ValidationRule[];
  options?: SelectOption[]; // For select, radio
  min?: number; // For number, range
  max?: number; // For number, range
  step?: number; // For number, range
  accept?: string; // For file
  multiple?: boolean; // For file, select
  rows?: number; // For textarea
  fields?: FieldSchema[]; // For object type
  itemSchema?: FieldSchema; // For array type
  conditional?: {
    field: string;
    value: any;
  };
  disabled?: boolean;
  readOnly?: boolean;
}

export interface FormSchema {
  id: string;
  title: string;
  description?: string;
  fields: FieldSchema[];
  submitLabel?: string;
  cancelLabel?: string;
}

export interface WizardStepSchema {
  id: string;
  title: string;
  description?: string;
  form: FormSchema;
  optional?: boolean;
}

export interface WizardSchema {
  id: string;
  title: string;
  description?: string;
  steps: WizardStepSchema[];
  allowSkip?: boolean;
  showProgress?: boolean;
}
