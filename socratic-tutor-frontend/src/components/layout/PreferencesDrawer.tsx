import React from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '../ui/sheet';
import { Label } from '../ui/label';
import { Slider } from '../ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Checkbox } from '../ui/checkbox';

interface PreferencesDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  preferences?: {
    verbosity_level: number;
    explanation_style: 'concise' | 'step_by_step' | 'analogy';
    reading_mode: 'compact' | 'comfortable';
    visual_aids: boolean;
  };
  onPreferencesChange?: (preferences: any) => void;
}

export const PreferencesDrawer: React.FC<PreferencesDrawerProps> = ({ 
  open, 
  onOpenChange,
  preferences,
  onPreferencesChange
}) => {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-[400px] sm:w-[540px]">
        <SheetHeader>
          <SheetTitle>Preferences</SheetTitle>
        </SheetHeader>
        
        <div className="space-y-6 py-6">
          {/* Verbosity Level */}
          <div className="space-y-3">
            <Label htmlFor="verbosity">Verbosity Level</Label>
            <Slider
              id="verbosity"
              value={[preferences?.verbosity_level || 3]}
              max={5}
              min={1}
              step={1}
              className="w-full"
              onValueChange={([value]) => onPreferencesChange?.({
                ...preferences,
                verbosity_level: value
              })}
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Concise</span>
              <span>Verbose</span>
            </div>
          </div>

          {/* Explanation Style */}
          <div className="space-y-3">
            <Label htmlFor="explanation-style">Explanation Style</Label>
            <Select
              value={preferences?.explanation_style || 'step_by_step'}
              onValueChange={(value) => onPreferencesChange?.({
                ...preferences,
                explanation_style: value as 'concise' | 'step_by_step' | 'analogy'
              })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select style" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="concise">Concise</SelectItem>
                <SelectItem value="step_by_step">Step-by-Step</SelectItem>
                <SelectItem value="analogy">Analogy Mode</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Visual Aid Toggle */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox 
                id="visual-aid" 
                checked={preferences?.visual_aids || false}
                onCheckedChange={(checked) => onPreferencesChange?.({
                  ...preferences,
                  visual_aids: checked
                })}
              />
              <Label htmlFor="visual-aid">Enable visual aids</Label>
            </div>
          </div>

          {/* Reading Mode */}
          <div className="space-y-3">
            <Label htmlFor="reading-mode">Reading Mode</Label>
            <Select
              value={preferences?.reading_mode || 'comfortable'}
              onValueChange={(value) => onPreferencesChange?.({
                ...preferences,
                reading_mode: value as 'compact' | 'comfortable'
              })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select mode" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="compact">Compact</SelectItem>
                <SelectItem value="comfortable">Comfortable</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};
