# FFT Annotation Guide

This guide explains how to use the frequency annotation feature in the Remote OpenFAST Plotter.

## Purpose

The frequency annotation feature allows you to mark and label important frequencies in your FFT plots. This is particularly useful for:

- Highlighting structural resonance frequencies
- Marking blade passing frequencies
- Identifying harmonics or other known system frequencies
- Labeling problematic frequencies that need attention

## Using Frequency Annotations

### Manual Annotations

1. Navigate to the **FFT Analysis** tab
2. Enter comma-separated frequencies in the **Frequency Annotations** input field
   ```
   1.1, 3.5, 7.2
   ```
3. Optionally, provide labels (also comma-separated) in the second input field
   ```
   Tower, 1P, 3P
   ```
4. Click the **Add** button to add annotations
5. Calculate your FFT as normal by clicking **Calculate FFT**

### Using Rotor RPM Feature

For wind turbine analysis, you can quickly add harmonic annotations based on rotor speed:

1. Enter the rotor speed in the **Rotor RPM** field
2. Click **Add Harmonics** to automatically generate annotations for 1P through 10P
3. The harmonics are calculated as follows:
   - 1P = RPM ÷ 60 Hz (fundamental rotor frequency)
   - 2P = 2 × 1P
   - 3P = 3 × 1P
   - etc.

## Example Annotations

Here are some common frequencies you might want to annotate in wind turbine analysis:

| Frequency | Common Label | Description |
|-----------|-------------|-------------|
| ~0.32 Hz  | 1P          | Rotor frequency (20 RPM) |
| ~0.64 Hz  | 2P          | Twice-per-revolution |
| ~0.96 Hz  | 3P          | Three-times-per-revolution (important for 3-bladed turbines) |
| ~1.5-2 Hz | Tower       | Tower natural frequency |
| ~3-5 Hz   | Blade Flap  | Blade flapwise natural frequency |

## Managing Annotations

- **Delete**: Click the '×' symbol on any annotation badge to remove it
- **Reset**: Annotations are automatically cleared when you switch to the FFT tab
- **Sort**: Annotations are automatically sorted by frequency
- **Display**: Each annotation shows both the label and frequency value (with 2 decimal precision)

## Tips for Effective Annotations

1. **Use clear, concise labels** that will fit well within the plot
2. **Don't overcrowd** your plot with too many annotations
3. **Use consistent naming conventions** for similar types of frequencies
4. When exporting as HTML, annotations are preserved and visible in the exported file
5. For overlaid FFT plots, consider using fewer annotations to maintain readability
