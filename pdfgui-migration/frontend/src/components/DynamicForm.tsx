/**
 * Dynamic form renderer - renders forms from JSON schema.
 * All forms in pdfGUI are generated from this component.
 */
import React from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import type { FormSchema, FieldSchema, ValidationRule } from "../types/forms";

interface DynamicFormProps {
  schema: FormSchema;
  onSubmit: (data: any) => void;
  onCancel?: () => void;
  initialValues?: Record<string, any>;
  isLoading?: boolean;
}

// Build Zod schema from field validation rules
function buildZodSchema(fields: FieldSchema[]): z.ZodObject<any> {
  const shape: Record<string, z.ZodTypeAny> = {};

  fields.forEach((field) => {
    let fieldSchema: z.ZodTypeAny;

    // Base type
    switch (field.type) {
      case "number":
      case "range":
        fieldSchema = z.number();
        break;
      case "checkbox":
        fieldSchema = z.boolean();
        break;
      case "email":
        fieldSchema = z.string().email();
        break;
      case "file":
        fieldSchema = z.any();
        break;
      case "array":
        fieldSchema = z.array(z.any());
        break;
      default:
        fieldSchema = z.string();
    }

    // Apply validation rules
    if (field.validation) {
      field.validation.forEach((rule) => {
        switch (rule.type) {
          case "required":
            if (fieldSchema instanceof z.ZodString) {
              fieldSchema = fieldSchema.min(1, rule.message);
            }
            break;
          case "min":
            if (fieldSchema instanceof z.ZodNumber) {
              fieldSchema = fieldSchema.min(rule.value, rule.message);
            }
            break;
          case "max":
            if (fieldSchema instanceof z.ZodNumber) {
              fieldSchema = fieldSchema.max(rule.value, rule.message);
            }
            break;
          case "minLength":
            if (fieldSchema instanceof z.ZodString) {
              fieldSchema = fieldSchema.min(rule.value, rule.message);
            }
            break;
          case "maxLength":
            if (fieldSchema instanceof z.ZodString) {
              fieldSchema = fieldSchema.max(rule.value, rule.message);
            }
            break;
          case "pattern":
            if (fieldSchema instanceof z.ZodString) {
              fieldSchema = fieldSchema.regex(
                new RegExp(rule.value),
                rule.message,
              );
            }
            break;
        }
      });
    }

    // Make optional if no required validation
    const hasRequired = field.validation?.some((r) => r.type === "required");
    if (!hasRequired) {
      fieldSchema = fieldSchema.optional();
    }

    shape[field.name] = fieldSchema;
  });

  return z.object(shape);
}

// Get default values from schema
function getDefaultValues(fields: FieldSchema[]): Record<string, any> {
  const defaults: Record<string, any> = {};
  fields.forEach((field) => {
    if (field.defaultValue !== undefined) {
      defaults[field.name] = field.defaultValue;
    }
  });
  return defaults;
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  schema,
  onSubmit,
  onCancel,
  initialValues,
  isLoading = false,
}) => {
  const zodSchema = buildZodSchema(schema.fields);
  const defaultValues = {
    ...getDefaultValues(schema.fields),
    ...initialValues,
  };

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm({
    resolver: zodResolver(zodSchema),
    defaultValues,
  });

  const renderField = (field: FieldSchema) => {
    // Check conditional visibility
    if (field.conditional) {
      const watchValue = watch(field.conditional.field);
      if (watchValue !== field.conditional.value) {
        return null;
      }
    }

    const error = errors[field.name];

    return (
      <div key={field.name} className="mb-4">
        <label className="block text-sm font-medium mb-1">
          {field.label}
          {field.validation?.some((r) => r.type === "required") && (
            <span className="text-red-500 ml-1">*</span>
          )}
        </label>

        {field.description && (
          <p className="text-xs text-gray-500 mb-1">{field.description}</p>
        )}

        {renderInput(field)}

        {error && (
          <p className="text-sm text-red-500 mt-1">{error.message as string}</p>
        )}
      </div>
    );
  };

  const renderInput = (field: FieldSchema) => {
    const baseClassName =
      "w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500";

    switch (field.type) {
      case "text":
      case "email":
      case "password":
        return (
          <input
            type={field.type}
            {...register(field.name)}
            placeholder={field.placeholder}
            disabled={field.disabled || isLoading}
            readOnly={field.readOnly}
            className={baseClassName}
          />
        );

      case "number":
      case "range":
        return (
          <Controller
            name={field.name}
            control={control}
            render={({ field: { onChange, value } }) => (
              <input
                type="number"
                value={value ?? ""}
                onChange={(e) =>
                  onChange(e.target.value ? parseFloat(e.target.value) : "")
                }
                min={field.min}
                max={field.max}
                step={field.step}
                disabled={field.disabled || isLoading}
                className={baseClassName}
              />
            )}
          />
        );

      case "textarea":
        return (
          <textarea
            {...register(field.name)}
            placeholder={field.placeholder}
            rows={field.rows || 3}
            disabled={field.disabled || isLoading}
            className={baseClassName}
          />
        );

      case "select":
        return (
          <select
            {...register(field.name)}
            disabled={field.disabled || isLoading}
            multiple={field.multiple}
            className={baseClassName}
          >
            <option value="">Select...</option>
            {field.options?.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      case "checkbox":
        return (
          <input
            type="checkbox"
            {...register(field.name)}
            disabled={field.disabled || isLoading}
            className="h-4 w-4"
          />
        );

      case "radio":
        return (
          <div className="space-y-2">
            {field.options?.map((opt) => (
              <label key={opt.value} className="flex items-center">
                <input
                  type="radio"
                  {...register(field.name)}
                  value={opt.value}
                  disabled={field.disabled || isLoading}
                  className="mr-2"
                />
                {opt.label}
              </label>
            ))}
          </div>
        );

      case "file":
        return (
          <input
            type="file"
            {...register(field.name)}
            accept={field.accept}
            multiple={field.multiple}
            disabled={field.disabled || isLoading}
            className={baseClassName}
          />
        );

      default:
        return (
          <input
            type="text"
            {...register(field.name)}
            disabled={field.disabled || isLoading}
            className={baseClassName}
          />
        );
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {schema.description && (
        <p className="text-gray-600 mb-4">{schema.description}</p>
      )}

      {schema.fields.map(renderField)}

      <div className="flex justify-end space-x-3 pt-4">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            {schema.cancelLabel || "Cancel"}
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? "Loading..." : schema.submitLabel || "Submit"}
        </button>
      </div>
    </form>
  );
};

export default DynamicForm;
