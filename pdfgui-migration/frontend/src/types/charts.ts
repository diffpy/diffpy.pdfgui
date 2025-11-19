/**
 * Chart configuration types for template-based plotting.
 */

export type ChartType = 'line' | 'scatter' | 'bar' | 'histogram' | 'heatmap' | '3d';

export interface AxisConfig {
  title: string;
  range?: [number, number];
  autorange?: boolean;
  type?: 'linear' | 'log' | 'date' | 'category';
  tickformat?: string;
  showgrid?: boolean;
  zeroline?: boolean;
}

export interface DataSeries {
  name: string;
  x: number[];
  y: number[];
  z?: number[];  // For 3D plots
  type: 'scatter' | 'line' | 'bar';
  mode?: 'lines' | 'markers' | 'lines+markers';
  line?: {
    color?: string;
    width?: number;
    dash?: 'solid' | 'dot' | 'dash';
  };
  marker?: {
    color?: string;
    size?: number;
    symbol?: string;
  };
  fill?: 'none' | 'tozeroy' | 'tonexty';
  visible?: boolean | 'legendonly';
}

export interface ChartConfig {
  id: string;
  title: string;
  type: ChartType;
  xaxis: AxisConfig;
  yaxis: AxisConfig;
  zaxis?: AxisConfig;  // For 3D
  series: DataSeries[];
  showLegend?: boolean;
  legendPosition?: 'top' | 'bottom' | 'left' | 'right';
  width?: number;
  height?: number;
  margin?: {
    t: number;
    b: number;
    l: number;
    r: number;
  };
}

export interface PDFPlotConfig extends ChartConfig {
  showObserved: boolean;
  showCalculated: boolean;
  showDifference: boolean;
  differenceOffset: number;
  datasetOffsets: number[];
}

export interface StructurePlotConfig {
  showBonds: boolean;
  bondCutoff: number;
  atomScale: number;
  showUnitCell: boolean;
  supercell: [number, number, number];
  colorScheme: 'element' | 'custom';
}
