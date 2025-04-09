"""
FFT annotation callbacks for OpenFAST Plotter
Contains callbacks for managing FFT annotations
"""

from dash import Input, Output, State, html, ctx, ALL
from dash.exceptions import PreventUpdate

# Import local modules
from utils import create_annotation_badges
from user_preferences import save_custom_annotations


def register_annotation_callbacks(app):
    """Register annotation-related callbacks with the Dash app"""
    
    # Add callback to manage annotations
    @app.callback(
        Output("fft-annotations", "data"),
        Output("fft-annotations-display", "children"),
        Output("fft-annotation-freq", "value"),
        Output("fft-annotation-text", "value"),
        Input("fft-add-annotation-btn", "n_clicks"),
        Input("tabs", "active_tab"),  # Reset when switching tabs
        State("fft-annotation-freq", "value"),
        State("fft-annotation-text", "value"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def manage_fft_annotations(add_clicks, active_tab, freq_input, label_input, current_annotations):
        """
        Add and manage annotations for FFT plots
        """
        trigger = ctx.triggered_id
        
        # Don't reset annotations when switching tabs anymore
        if trigger == "tabs":
            # Only clear input fields but keep the annotations
            return current_annotations, create_annotation_badges(current_annotations), None, None
        
        # Skip if no click or no input
        if not add_clicks or not freq_input:
            raise PreventUpdate
        
        # Parse frequency input
        try:
            freqs = [float(f.strip()) for f in freq_input.split(",") if f.strip()]
        except ValueError:
            # Handle parsing error
            return current_annotations, [
                html.Div("Invalid frequency format. Use comma-separated numbers.", 
                         className="text-danger small")
            ] + create_annotation_badges(current_annotations), freq_input, label_input
        
        # Parse labels - if not provided or fewer than freqs, generate automatic labels
        if not label_input:
            labels = [f"F{i+1}" for i in range(len(freqs))]
        else:
            labels = [l.strip() for l in label_input.split(",")]
            # If fewer labels than frequencies, add generic labels
            if len(labels) < len(freqs):
                labels += [f"F{i+1}" for i in range(len(labels), len(freqs))]
        
        # Create new annotations
        new_annotations = current_annotations.copy() if current_annotations else []
        for freq, label in zip(freqs, labels):
            new_annotations.append({"freq": freq, "label": label})
        
        # Sort by frequency
        new_annotations.sort(key=lambda x: x["freq"])
        
        # Save annotations to user preferences
        save_custom_annotations(new_annotations)
        
        # Create badges for visual display
        badges = create_annotation_badges(new_annotations)
        
        return new_annotations, badges, None, None
    
    # Add callback to remove individual annotations
    @app.callback(
        Output("fft-annotations", "data", allow_duplicate=True),
        Output("fft-annotations-display", "children", allow_duplicate=True),
        Input({"type": "remove-annotation", "index": ALL}, "n_clicks"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def remove_annotation(n_clicks, current_annotations):
        """
        Remove an annotation when its delete button is clicked
        """
        if not any(n_clicks):
            raise PreventUpdate
        
        # Find which annotation to remove
        triggered_id = ctx.triggered_id
        if triggered_id and "index" in triggered_id:
            index_to_remove = triggered_id["index"]
            
            # Remove the annotation
            new_annotations = [a for i, a in enumerate(current_annotations) if i != index_to_remove]
            
            # Save to user preferences
            save_custom_annotations(new_annotations)
            
            # Update badges
            badges = create_annotation_badges(new_annotations)
            
            return new_annotations, badges
        
        raise PreventUpdate
    
    # Add callback to generate harmonics from Rotor RPM
    @app.callback(
        Output("fft-annotations", "data", allow_duplicate=True),
        Output("fft-annotations-display", "children", allow_duplicate=True),
        Output("rotor-rpm-input", "value"),
        Input("add-harmonics-btn", "n_clicks"),
        State("rotor-rpm-input", "value"),
        State("fft-annotations", "data"),
        prevent_initial_call=True
    )
    def generate_rotor_harmonics(n_clicks, rpm_value, current_annotations):
        """
        Generate frequency annotations for selected rotor harmonics 
        based on the rotor RPM input.
        """
        if not n_clicks or rpm_value is None or rpm_value <= 0:
            raise PreventUpdate
        
        # Convert RPM to Hz (frequency)
        freq_1p = rpm_value / 60.0
        
        # Define which harmonics to include
        harmonics = [1, 2, 3, 4, 6, 8, 9]
        
        # Generate annotations for selected harmonics
        new_annotations = current_annotations.copy() if current_annotations else []
        for i in harmonics:  # Only selected harmonics
            harmonic_freq = freq_1p * i
            harmonic_label = f"{i}P"
            
            # Check if this harmonic already exists (avoid duplicates)
            exists = any(abs(anno.get('freq', 0) - harmonic_freq) < 0.001 and 
                        anno.get('label', '') == harmonic_label 
                        for anno in new_annotations)
            
            if not exists:
                new_annotations.append({"freq": harmonic_freq, "label": harmonic_label})
        
        # Sort by frequency
        new_annotations.sort(key=lambda x: x["freq"])
        
        # Save to user preferences
        save_custom_annotations(new_annotations)
        
        # Create badges for visual display
        badges = create_annotation_badges(new_annotations)
        
        return new_annotations, badges, None
