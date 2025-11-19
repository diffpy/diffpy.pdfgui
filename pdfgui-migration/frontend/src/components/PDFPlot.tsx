/**
 * PDF Plot component - renders PDF data using Plotly.
 * Uses chart template configuration.
 */
import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import type { PDFPlotConfig, DataSeries } from '../types/charts';

interface PDFPlotProps {
  config: PDFPlotConfig;
  data: {
    observed?: { r: number[]; G: number[]; dG?: number[] };
    calculated?: { r: number[]; G: number[] };
    difference?: { r: number[]; G: number[] };
  };
  width?: number;
  height?: number;
  onZoom?: (xRange: [number, number], yRange: [number, number]) => void;
}

export const PDFPlot: React.FC<PDFPlotProps> = ({
  config,
  data,
  width = 800,
  height = 500,
  onZoom
}) => {
  const plotData = useMemo(() => {
    const traces: any[] = [];

    // Observed data
    if (config.showObserved && data.observed) {
      traces.push({
        name: 'Observed',
        x: data.observed.r,
        y: data.observed.G,
        type: 'scatter',
        mode: 'markers',
        marker: {
          color: '#1f77b4',
          size: 4,
          symbol: 'circle'
        },
        error_y: data.observed.dG ? {
          type: 'data',
          array: data.observed.dG,
          visible: true,
          color: '#1f77b4',
          thickness: 1
        } : undefined
      });
    }

    // Calculated data
    if (config.showCalculated && data.calculated) {
      traces.push({
        name: 'Calculated',
        x: data.calculated.r,
        y: data.calculated.G,
        type: 'scatter',
        mode: 'lines',
        line: {
          color: '#ff7f0e',
          width: 1.5
        }
      });
    }

    // Difference curve
    if (config.showDifference && data.difference) {
      const offset = config.differenceOffset || 0;
      traces.push({
        name: 'Difference',
        x: data.difference.r,
        y: data.difference.G.map(g => g - offset),
        type: 'scatter',
        mode: 'lines',
        line: {
          color: '#2ca02c',
          width: 1
        }
      });
    }

    return traces;
  }, [config, data]);

  const layout = useMemo(() => ({
    title: config.title,
    xaxis: {
      title: config.xaxis.title,
      autorange: config.xaxis.autorange,
      range: config.xaxis.range,
      showgrid: config.xaxis.showgrid,
      zeroline: config.xaxis.zeroline
    },
    yaxis: {
      title: config.yaxis.title,
      autorange: config.yaxis.autorange,
      range: config.yaxis.range,
      showgrid: config.yaxis.showgrid,
      zeroline: config.yaxis.zeroline
    },
    showlegend: config.showLegend,
    legend: {
      x: 1,
      xanchor: 'right',
      y: 1
    },
    margin: config.margin || { t: 50, b: 60, l: 70, r: 30 },
    width,
    height
  }), [config, width, height]);

  const handleRelayout = (event: any) => {
    if (onZoom && event['xaxis.range[0]'] !== undefined) {
      onZoom(
        [event['xaxis.range[0]'], event['xaxis.range[1]']],
        [event['yaxis.range[0]'], event['yaxis.range[1]']]
      );
    }
  };

  return (
    <div className="pdf-plot">
      <Plot
        data={plotData}
        layout={layout}
        onRelayout={handleRelayout}
        config={{
          displayModeBar: true,
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
          toImageButtonOptions: {
            format: 'png',
            filename: 'pdf_plot'
          }
        }}
      />
    </div>
  );
};

export default PDFPlot;
