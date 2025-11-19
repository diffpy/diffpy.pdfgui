/**
 * Wizard component - multi-step form wizard.
 * Renders steps from JSON wizard schema.
 */
import React, { useState } from 'react';
import { DynamicForm } from './DynamicForm';
import type { WizardSchema } from '../types/forms';

interface WizardProps {
  schema: WizardSchema;
  onComplete: (data: Record<string, any>) => void;
  onCancel?: () => void;
  initialData?: Record<string, any>;
}

export const Wizard: React.FC<WizardProps> = ({
  schema,
  onComplete,
  onCancel,
  initialData = {}
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, any>>(initialData);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const totalSteps = schema.steps.length;
  const currentStepSchema = schema.steps[currentStep];
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === totalSteps - 1;

  const handleStepSubmit = (stepData: any) => {
    // Merge step data
    const newData = {
      ...formData,
      [currentStepSchema.id]: stepData
    };
    setFormData(newData);

    // Mark step as completed
    setCompletedSteps(prev => new Set([...prev, currentStep]));

    if (isLastStep) {
      // Complete wizard
      onComplete(newData);
    } else {
      // Go to next step
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleStepClick = (stepIndex: number) => {
    // Allow navigation to completed steps or current step
    if (stepIndex <= currentStep || completedSteps.has(stepIndex - 1)) {
      setCurrentStep(stepIndex);
    }
  };

  return (
    <div className="wizard">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold">{schema.title}</h2>
        {schema.description && (
          <p className="text-gray-600 mt-1">{schema.description}</p>
        )}
      </div>

      {/* Progress indicator */}
      {schema.showProgress && (
        <div className="mb-8">
          <div className="flex justify-between">
            {schema.steps.map((step, index) => (
              <div
                key={step.id}
                className={`flex flex-col items-center cursor-pointer ${
                  index <= currentStep ? 'text-blue-600' : 'text-gray-400'
                }`}
                onClick={() => handleStepClick(index)}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                    completedSteps.has(index)
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : index === currentStep
                      ? 'border-blue-600 text-blue-600'
                      : 'border-gray-300'
                  }`}
                >
                  {completedSteps.has(index) ? '✓' : index + 1}
                </div>
                <span className="text-xs mt-1 text-center max-w-20">
                  {step.title}
                </span>
              </div>
            ))}
          </div>
          {/* Progress bar */}
          <div className="mt-2 h-1 bg-gray-200 rounded">
            <div
              className="h-1 bg-blue-600 rounded transition-all"
              style={{ width: `${(currentStep / (totalSteps - 1)) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Current step */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-2">
          {currentStepSchema.title}
        </h3>
        {currentStepSchema.description && (
          <p className="text-gray-600 mb-4">{currentStepSchema.description}</p>
        )}

        <DynamicForm
          schema={currentStepSchema.form}
          onSubmit={handleStepSubmit}
          initialValues={formData[currentStepSchema.id]}
        />

        {/* Navigation */}
        <div className="flex justify-between mt-6 pt-4 border-t">
          <div>
            {onCancel && (
              <button
                onClick={onCancel}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
            )}
          </div>
          <div className="flex space-x-3">
            {!isFirstStep && (
              <button
                onClick={handleBack}
                className="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                Back
              </button>
            )}
            {schema.allowSkip && !isLastStep && currentStepSchema.optional && (
              <button
                onClick={() => setCurrentStep(prev => prev + 1)}
                className="px-4 py-2 text-blue-600 hover:text-blue-800"
              >
                Skip
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Wizard;
